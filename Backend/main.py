from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Union, Dict, Any
import json
import asyncio
from datetime import datetime
import PyPDF2
import io
import re
import os
import logging
from pymongo import MongoClient  # Only using synchronous pymongo
from pymongo.server_api import ServerApi
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Upskill Advisor API", version="2.0.0", description="AI-powered upskill advisor using MongoDB")

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class Skill(BaseModel):
    name: str = Field(..., description="Skill name")
    proficiency: str = Field(..., description="Proficiency level: beginner, intermediate, advanced")

class AdviseRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    goal_role: str = Field(..., description="Target career role")
    skills: Optional[List[Skill]] = Field(default=[], description="User's current skills")

class Course(BaseModel):
    course_id: str
    title: str
    description: str
    skills: List[str]
    difficulty: str
    duration_weeks: int
    prerequisites: List[str] = []
    outcomes: List[str] = []
    url: Optional[str] = None
    relevance_score: Optional[float] = None
    ai_recommended: Optional[bool] = False
    ai_reasoning: Optional[str] = None

class AdviseResponse(BaseModel):
    recommended_courses: List[Course]
    gap_map: Dict[str, str]
    timeline_weeks: int
    notes: str
    ai_reasoning: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    results: List[Course]
    total: int
    search_type: str = "text_search"

# Global variables
mongo_vector_store = None
mongodb_client = None

# Updated Role → Skills mapping (only 4 roles as requested)
ROLE_SKILLS_MAP = {
    "Java Full Stack Developer": [
        "java", "spring boot", "microservices", "restful apis", "mysql", "sql",
        "javascript", "react", "html", "css", "git", "testing"
    ],
    "Data Scientist": [
        "python", "data analysis", "statistics", "data visualization", "pandas",
        "numpy", "matplotlib", "sql", "mysql", "big data", "machine learning"
    ],
    "DevOps Engineer": [
        "git", "ci/cd", "docker", "kubernetes", "terraform", "aws", "azure",
        "google cloud", "linux", "shell scripting", "monitoring", "cloud security"
    ],
    "Machine Learning Engineer": [
        "python", "machine learning", "deep learning", "tensorflow", "pytorch",
        "neural networks", "data analysis", "statistics", "model deployment", "git", "docker"
    ]
}

def extract_skills_from_pdf(file_content: bytes) -> List[str]:
    """Extract skills from PDF resume content using improved parsing."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + " "
        
        # Enhanced skill extraction with more comprehensive skill list
        common_skills = [
            # Programming Languages
            "python", "javascript", "java", "typescript", "go", "rust", "c++", "c#", "php", "ruby",
            # Frontend Technologies
            "react", "vue", "angular", "html", "css", "sass", "tailwind", "bootstrap",
            # Backend Technologies
            "nodejs", "express", "spring boot", "django", "flask", "fastapi",
            # Databases
            "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
            # Cloud & DevOps
            "aws", "azure", "google cloud", "docker", "kubernetes", "terraform", "jenkins",
            "git", "ci/cd", "linux", "shell scripting", "monitoring", "prometheus", "grafana",
            # Data & ML
            "machine learning", "deep learning", "data analysis", "pandas", "numpy", "tensorflow", 
            "pytorch", "scikit-learn", "matplotlib", "seaborn", "big data", "spark", "hadoop",
            # Other
            "restful apis", "microservices", "testing", "automation", "agile", "scrum"
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        # More sophisticated matching
        for skill in common_skills:
            skill_lower = skill.lower()
            # Check for exact match or skill as part of a word boundary
            if re.search(r'\b' + re.escape(skill_lower) + r'\b', text_lower):
                found_skills.append(skill)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in found_skills:
            if skill not in seen:
                seen.add(skill)
                unique_skills.append(skill)
        
        logger.info(f"Extracted {len(unique_skills)} skills from PDF: {unique_skills}")
        return unique_skills
        
    except Exception as e:
        logger.error(f"Error extracting skills from PDF: {e}")
        return []

def analyze_skill_gap(user_skills: List[str], target_role: str) -> Dict[str, str]:
    """Analyze the gap between user skills and target role requirements."""
    required_skills = ROLE_SKILLS_MAP.get(target_role, [])
    user_skill_names = [skill.lower().strip() for skill in user_skills]
    
    gap_map = {}
    for required_skill in required_skills:
        required_skill_lower = required_skill.lower().strip()
        if required_skill_lower in user_skill_names:
            gap_map[required_skill] = "Present - Good foundation"
        else:
            gap_map[required_skill] = "Missing - Need to learn"
    
    # Add any additional skills the user has that aren't in the required list
    for user_skill in user_skills:
        user_skill_clean = user_skill.strip()
        if user_skill_clean and not any(user_skill.lower() == req.lower() for req in required_skills):
            gap_map[user_skill_clean] = "Additional - Bonus skill"
    
    return gap_map

async def recommend_courses_with_ai(user_skills: List[str], target_role: str, gap_map: Dict[str, str]) -> List[Course]:
    """Recommend courses using MongoDB search."""
    try:
        missing_skills = [skill for skill, status in gap_map.items() if "Missing" in status]
        
        if not missing_skills:
            logger.info("No missing skills found, getting general recommendations")
            search_query = f"{target_role} skills development"
        else:
            search_query = f"{target_role} {' '.join(missing_skills[:3])}"  # Limit query length
        
        logger.info(f"Searching courses for: {search_query}")
        
        # Use AI-enhanced search from MongoDB
        recommended_courses = mongo_vector_store.search_courses_with_ai(search_query, limit=3)
        
        # Convert to Course models and add additional metadata
        course_models = []
        for i, course_data in enumerate(recommended_courses):
            try:
                # Ensure all required fields are present
                course_model = Course(
                    course_id=course_data.get("course_id", f"unknown_{i}"),
                    title=course_data.get("title", "Unknown Course"),
                    description=course_data.get("description", "No description available"),
                    skills=course_data.get("skills", []),
                    difficulty=course_data.get("difficulty", "intermediate"),
                    duration_weeks=course_data.get("duration_weeks", 8),
                    prerequisites=course_data.get("prerequisites", []),
                    outcomes=course_data.get("outcomes", []),
                    url=course_data.get("url"),
                    relevance_score=course_data.get("relevance_score"),
                    ai_recommended=course_data.get("ai_recommended", True),
                    ai_reasoning=course_data.get("ai_reasoning")
                )
                course_models.append(course_model)
            except Exception as e:
                logger.error(f"Error creating course model: {e}")
                continue
        
        if not course_models:
            logger.warning("No valid courses found, returning empty list")
        
        return course_models
        
    except Exception as e:
        logger.error(f"Error recommending courses: {e}")
        return []

def create_simple_mongo_client():
    """Create simple MongoDB client with text search capabilities."""
    connection_string = os.getenv(
        "MONGODB_CONNECTION_STRING"
    )
    
    client = MongoClient(connection_string, server_api=ServerApi('1'))
    db = client[os.getenv("MONGODB_DB", "upskill_advisor")]
    collection = db[os.getenv("MONGODB_COLLECTION", "courses")]
    
    # Test connection
    client.admin.command('ping')
    
    class SimpleMongoStore:
        def __init__(self, collection):
            self.collection = collection
        
        def search_courses(self, query: str, limit: int = 5):
            """Search courses using MongoDB text search."""
            try:
                # Try text search first
                results = list(self.collection.find(
                    {"$text": {"$search": query}},
                    {"score": {"$meta": "textScore"}}
                ).sort([("score", {"$meta": "textScore"})]).limit(limit))
                
                if not results:
                    # Fallback to regex search on multiple fields
                    regex_pattern = {"$regex": query, "$options": "i"}
                    results = list(self.collection.find({
                        "$or": [
                            {"title": regex_pattern},
                            {"description": regex_pattern},
                            {"skills": {"$in": [regex_pattern]}},
                            {"searchable_text": regex_pattern}
                        ]
                    }).limit(limit))
                
                # Clean up results
                for result in results:
                    if '_id' in result:
                        del result['_id']
                    result['relevance_score'] = result.get('score', 0.5)
                
                return results
                
            except Exception as e:
                logger.error(f"Search error: {e}")
                return []
        
        def search_courses_with_ai(self, query: str, limit: int = 5):
            """Enhanced search with AI reasoning."""
            results = self.search_courses(query, limit)
            for result in results:
                result['ai_recommended'] = True
                result['ai_reasoning'] = f"Recommended based on relevance to: {query}"
            return results
        
        def get_course_recommendation(self, user_skills, target_role):
            """Generate recommendation reasoning."""
            skills_text = ", ".join(user_skills) if user_skills else "no specific skills"
            return f"Based on your current skills ({skills_text}) and target role ({target_role}), these courses are recommended to fill knowledge gaps and advance your career."
        
        def get_collection_stats(self):
            """Get collection statistics."""
            try:
                return {
                    "total_courses": self.collection.count_documents({}),
                    "collection_name": self.collection.name,
                    "database_name": self.collection.database.name
                }
            except Exception as e:
                return {"error": str(e)}
        
        def close(self):
            """Close connection (placeholder for compatibility)."""
            pass
    
    return SimpleMongoStore(collection)

@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB and seed database on startup."""
    global mongo_vector_store, mongodb_client
    
    try:
        # Import and run seeding
        from seed import seed_from_json
        
        logger.info("Seeding database with courses...")
        seed_success = seed_from_json("courses.json", clear_existing=False)
        
        if seed_success:
            logger.info("Database seeded successfully")
        else:
            logger.warning("Database seeding failed, continuing with existing data...")
        
        # Initialize MongoDB connection
        mongo_vector_store = create_simple_mongo_client()
        logger.info("MongoDB connection initialized")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Still try to create basic connection
        try:
            mongo_vector_store = create_simple_mongo_client()
        except Exception as inner_e:
            logger.error(f"Critical error: Cannot connect to MongoDB: {inner_e}")
            raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB client closed")

@app.post("/advise", response_model=AdviseResponse)
async def get_learning_advice(
    email: EmailStr = Form(...),
    goal_role: str = Form(...),
    skills: Optional[str] = Form(None),
    resume: Optional[UploadFile] = File(None)
):
    """Generate personalized learning recommendations."""
    try:
        user_skills = []
        
        # Process skills input
        if resume:
            # Extract skills from uploaded resume
            logger.info(f"Processing resume for {email}")
            file_content = await resume.read()
            extracted_skills = extract_skills_from_pdf(file_content)
            user_skills.extend(extracted_skills)
            logger.info(f"Extracted {len(extracted_skills)} skills from resume")
        
        if skills:
            # Process manual skills input
            try:
                skills_data = json.loads(skills)
                if isinstance(skills_data, dict):
                    # Handle format: {"skill_name": "proficiency"}
                    user_skills.extend(list(skills_data.keys()))
                elif isinstance(skills_data, list):
                    # Handle format: [{"name": "skill", "proficiency": "level"}]
                    manual_skills = [skill.get("name", "").strip() for skill in skills_data if skill.get("name")]
                    user_skills.extend(manual_skills)
                logger.info(f"Added {len(skills_data)} manual skills")
            except json.JSONDecodeError:
                logger.error("Invalid skills JSON format")
                raise HTTPException(status_code=400, detail="Invalid skills format")
        
        # Remove duplicates and empty strings
        user_skills = list(set([skill.strip() for skill in user_skills if skill.strip()]))
        
        if not user_skills:
            raise HTTPException(status_code=400, detail="No skills found in resume or manual input")
        
        logger.info(f"Processing request for {email}: {goal_role} with {len(user_skills)} skills")
        
        # Analyze skill gap
        gap_map = analyze_skill_gap(user_skills, goal_role)
        
        # Get AI-powered course recommendations
        recommended_courses = await recommend_courses_with_ai(user_skills, goal_role, gap_map)
        
        if not recommended_courses:
            logger.warning("No recommended courses found, using fallback")
            # Fallback: search for basic courses related to the role
            fallback_query = f"{goal_role} beginner courses"
            fallback_courses = mongo_vector_store.search_courses(fallback_query, limit=3)
            recommended_courses = [
                Course(
                    course_id=course.get("course_id", f"fallback_{i}"),
                    title=course.get("title", "Programming Fundamentals"),
                    description=course.get("description", "Basic programming course"),
                    skills=course.get("skills", ["programming"]),
                    difficulty="beginner",
                    duration_weeks=course.get("duration_weeks", 8),
                    prerequisites=course.get("prerequisites", []),
                    outcomes=course.get("outcomes", []),
                    url=course.get("url")
                ) for i, course in enumerate(fallback_courses)
            ]
        
        # Calculate timeline
        timeline_weeks = sum(course.duration_weeks for course in recommended_courses)
        
        # Get AI reasoning for the recommendations
        ai_reasoning = mongo_vector_store.get_course_recommendation(user_skills, goal_role)
        
        return AdviseResponse(
            recommended_courses=recommended_courses,
            gap_map=gap_map,
            timeline_weeks=timeline_weeks,
            notes=f"Complete these courses sequentially for optimal learning progression.",
            ai_reasoning=ai_reasoning[:500] + "..." if len(ai_reasoning) > 500 else ai_reasoning
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/advise_json", response_model=AdviseResponse)
async def get_learning_advice_json(request: AdviseRequest):
    """JSON endpoint for learning recommendations."""
    try:
        user_skills = [skill.name for skill in request.skills] if request.skills else []
        
        if not user_skills:
            raise HTTPException(status_code=400, detail="No skills provided")
        
        logger.info(f"JSON request for {request.email}: {request.goal_role} with {len(user_skills)} skills")
        
        # Analyze skill gap
        gap_map = analyze_skill_gap(user_skills, request.goal_role)
        
        # Get AI-powered course recommendations
        recommended_courses = await recommend_courses_with_ai(user_skills, request.goal_role, gap_map)
        
        if not recommended_courses:
            # Fallback: search for basic courses related to the role
            fallback_query = f"{request.goal_role} beginner courses"
            fallback_courses = mongo_vector_store.search_courses(fallback_query, limit=3)
            recommended_courses = [
                Course(
                    course_id=course.get("course_id", f"fallback_{i}"),
                    title=course.get("title", "Programming Fundamentals"),
                    description=course.get("description", "Basic programming course"),
                    skills=course.get("skills", ["programming"]),
                    difficulty="beginner",
                    duration_weeks=course.get("duration_weeks", 8),
                    prerequisites=course.get("prerequisites", []),
                    outcomes=course.get("outcomes", []),
                    url=course.get("url")
                ) for i, course in enumerate(fallback_courses)
            ]
        
        # Calculate timeline
        timeline_weeks = sum(course.duration_weeks for course in recommended_courses)
        
        # Get AI reasoning
        ai_reasoning = mongo_vector_store.get_course_recommendation(user_skills, request.goal_role)
        
        return AdviseResponse(
            recommended_courses=recommended_courses,
            gap_map=gap_map,
            timeline_weeks=timeline_weeks,
            notes=f"Personalized recommendations generated for {request.email}. Focus on missing skills first for maximum impact.",
            ai_reasoning=ai_reasoning[:500] + "..." if len(ai_reasoning) > 500 else ai_reasoning
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing JSON request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/course/{course_id}", response_model=Course)
async def get_course(course_id: str):
    """Get detailed course information by ID."""
    try:
        # Search in MongoDB
        course_doc = mongo_vector_store.collection.find_one({"course_id": course_id})
        
        if not course_doc:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return Course(
            course_id=course_doc.get("course_id"),
            title=course_doc.get("title"),
            description=course_doc.get("description"),
            skills=course_doc.get("skills", []),
            difficulty=course_doc.get("difficulty"),
            duration_weeks=course_doc.get("duration_weeks"),
            prerequisites=course_doc.get("prerequisites", []),
            outcomes=course_doc.get("outcomes", []),
            url=course_doc.get("url")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving course {course_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving course: {str(e)}")

@app.get("/courses/search", response_model=SearchResponse)
async def search_courses(query: str, limit: int = 5, use_ai: bool = True):
    """Search courses using text search and optional AI enhancement."""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Searching courses: '{query}' (limit: {limit}, AI: {use_ai})")
        
        if use_ai:
            # Use AI-enhanced search
            results = mongo_vector_store.search_courses_with_ai(query, limit)
            search_type = "ai_enhanced_text"
        else:
            # Use basic text search
            results = mongo_vector_store.search_courses(query, limit)
            search_type = "text_search"
        
        # Convert to Course models
        course_results = []
        for result in results:
            try:
                course = Course(
                    course_id=result.get("course_id", "unknown"),
                    title=result.get("title", "Unknown Course"),
                    description=result.get("description", ""),
                    skills=result.get("skills", []),
                    difficulty=result.get("difficulty", "intermediate"),
                    duration_weeks=result.get("duration_weeks", 8),
                    prerequisites=result.get("prerequisites", []),
                    outcomes=result.get("outcomes", []),
                    url=result.get("url"),
                    relevance_score=result.get("relevance_score"),
                    ai_recommended=result.get("ai_recommended", False),
                    ai_reasoning=result.get("ai_reasoning")
                )
                course_results.append(course)
            except Exception as e:
                logger.error(f"Error converting search result to Course model: {e}")
                continue
        
        return SearchResponse(
            query=query,
            results=course_results,
            total=len(course_results),
            search_type=search_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching courses: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/courses/recommend")
async def get_general_recommendations(role: str, skills: str = "", limit: int = 3):
    """Get general course recommendations for a role."""
    try:
        user_skills = [s.strip() for s in skills.split(",") if s.strip()] if skills else []
        
        # Create search query based on role and skills
        if user_skills:
            query = f"{role} courses for someone with {' '.join(user_skills[:3])}"
        else:
            query = f"{role} beginner courses"
        
        # Use AI-enhanced search
        results = mongo_vector_store.search_courses_with_ai(query, limit)
        
        # Get AI reasoning
        ai_reasoning = mongo_vector_store.get_course_recommendation(user_skills, role)
        
        return {
            "role": role,
            "user_skills": user_skills,
            "recommended_courses": results,
            "ai_reasoning": ai_reasoning,
            "total": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error getting general recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")

@app.get("/roles", response_model=List[str])
async def get_available_roles():
    """Get list of available career roles."""
    return list(ROLE_SKILLS_MAP.keys())

@app.get("/roles/{role}/skills", response_model=List[str])
async def get_role_skills(role: str):
    """Get required skills for a specific role."""
    if role not in ROLE_SKILLS_MAP:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return ROLE_SKILLS_MAP[role]

@app.get("/stats")
async def get_system_stats():
    """Get system statistics and health information."""
    try:
        # Get MongoDB stats
        mongo_stats = mongo_vector_store.get_collection_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "database": mongo_stats,
            "available_roles": len(ROLE_SKILLS_MAP),
            "total_skills_mapped": sum(len(skills) for skills in ROLE_SKILLS_MAP.values())
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test MongoDB connection
        mongo_vector_store.collection.find_one()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "mongodb": "connected",
                "seeding": "integrated"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )