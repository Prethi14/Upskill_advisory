import os
import json
import logging
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class MongoVectorStore:
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize MongoDB Vector Store with embeddings."""
        # Use connection string from env or parameter
        self.connection_string = connection_string or os.getenv(
            "MONGODB_CONNECTION_STRING"
        )
        
        # Initialize MongoDB client
        try:
            self.client = MongoClient(self.connection_string, server_api=ServerApi('1'))
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB!")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
        
        # Database and collection setup
        self.db = self.client[os.getenv("MONGODB_DB", "upskill_advisor")]
        self.collection = self.db[os.getenv("MONGODB_COLLECTION", "courses")]
        
        # Initialize sentence transformer for embeddings
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for given text."""
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            return []
    
    def upload_courses(self, courses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Upload courses to MongoDB with embeddings."""
        try:
            uploaded_count = 0
            
            for course in courses:
                # Create embedding for course description and skills
                text_to_embed = f"{course.get('title', '')} {course.get('description', '')} {' '.join(course.get('skills', []))}"
                embedding = self.create_embedding(text_to_embed)
                
                # Add embedding to course data
                course_with_embedding = {
                    **course,
                    'embedding': embedding,
                    'text_for_search': text_to_embed
                }
                
                # Upsert course (update if exists, insert if not)
                try:
                    self.collection.replace_one(
                        {"course_id": course.get("course_id")},
                        course_with_embedding,
                        upsert=True
                    )
                    uploaded_count += 1
                except Exception as e:
                    logger.error(f"Error uploading course {course.get('course_id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Uploaded {uploaded_count} courses to MongoDB")
            return {"success": True, "uploaded_count": uploaded_count}
            
        except Exception as e:
            logger.error(f"Error uploading courses: {e}")
            return {"success": False, "error": str(e)}
    
    def search_courses(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search courses using vector similarity."""
        try:
            # Create embedding for search query
            query_embedding = self.create_embedding(query)
            
            if not query_embedding:
                return []
            
            # Get all courses with embeddings
            courses = list(self.collection.find({"embedding": {"$exists": True}}))
            
            if not courses:
                return []
            
            # Calculate similarities
            course_similarities = []
            for course in courses:
                if 'embedding' in course and course['embedding']:
                    similarity = cosine_similarity(
                        [query_embedding], 
                        [course['embedding']]
                    )[0][0]
                    course['relevance_score'] = float(similarity)
                    course_similarities.append((similarity, course))
            
            # Sort by similarity and return top results
            course_similarities.sort(key=lambda x: x[0], reverse=True)
            results = [course for _, course in course_similarities[:limit]]
            
            # Clean up MongoDB ObjectId for JSON serialization
            for result in results:
                if '_id' in result:
                    del result['_id']
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching courses: {e}")
            return []
    
    def search_courses_with_ai(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Enhanced search with AI reasoning."""
        # For now, use the same vector search
        # This can be enhanced with LLM-based ranking/filtering
        results = self.search_courses(query, limit)
        
        # Add AI flags
        for result in results:
            result['ai_recommended'] = True
            result['ai_reasoning'] = f"Recommended based on similarity to: {query}"
        
        return results
    
    def get_course_recommendation(self, user_skills: List[str], target_role: str) -> str:
        """Generate AI reasoning for course recommendations."""
        skills_text = ", ".join(user_skills) if user_skills else "no specific skills"
        
        reasoning = f"Based on your current skills ({skills_text}) and target role ({target_role}), these courses are recommended to fill knowledge gaps and advance your career. The recommendations prioritize practical skills and industry relevance."
        
        return reasoning.strip()
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            total_courses = self.collection.count_documents({})
            courses_with_embeddings = self.collection.count_documents({"embedding": {"$exists": True}})
            
            return {
                "total_courses": total_courses,
                "courses_with_embeddings": courses_with_embeddings,
                "collection_name": self.collection.name,
                "database_name": self.db.name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


def load_courses_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Load courses from JSON file."""
    try:
        if not os.path.exists(file_path):
            logger.warning(f"Course file {file_path} not found")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            courses = data
        elif isinstance(data, dict) and 'courses' in data:
            courses = data['courses']
        else:
            logger.error(f"Unexpected JSON structure in {file_path}")
            return []
        
        logger.info(f"Loaded {len(courses)} courses from {file_path}")
        return courses
        
    except Exception as e:
        logger.error(f"Error loading courses from {file_path}: {e}")
        return []


# Sample courses data for testing
SAMPLE_COURSES = [
    {
        "course_id": "java_spring_001",
        "title": "Java Spring Boot Microservices",
        "description": "Learn to build scalable microservices with Spring Boot, including REST APIs, database integration, and deployment strategies.",
        "skills": ["java", "spring boot", "microservices", "restful apis", "mysql"],
        "difficulty": "intermediate",
        "duration_weeks": 8,
        "prerequisites": ["java basics", "object-oriented programming"],
        "outcomes": ["Build microservices", "Deploy to cloud", "Database integration"],
        "url": "https://example.com/java-spring-boot"
    },
    {
        "course_id": "python_ml_001",
        "title": "Machine Learning with Python",
        "description": "Complete machine learning course covering algorithms, data preprocessing, model evaluation, and deployment using Python.",
        "skills": ["python", "machine learning", "data analysis", "pandas", "numpy", "scikit-learn"],
        "difficulty": "intermediate",
        "duration_weeks": 10,
        "prerequisites": ["python basics", "statistics"],
        "outcomes": ["Build ML models", "Data analysis", "Model deployment"],
        "url": "https://example.com/python-ml"
    },
    {
        "course_id": "react_frontend_001",
        "title": "Modern React Development",
        "description": "Master React development with hooks, context, testing, and modern development practices.",
        "skills": ["javascript", "react", "html", "css", "testing"],
        "difficulty": "intermediate",
        "duration_weeks": 6,
        "prerequisites": ["javascript fundamentals", "html/css"],
        "outcomes": ["Build React apps", "Component testing", "State management"],
        "url": "https://example.com/react-dev"
    },
    {
        "course_id": "devops_kubernetes_001",
        "title": "DevOps with Kubernetes and Docker",
        "description": "Learn container orchestration, CI/CD pipelines, and cloud deployment strategies.",
        "skills": ["docker", "kubernetes", "ci/cd", "aws", "monitoring"],
        "difficulty": "advanced",
        "duration_weeks": 8,
        "prerequisites": ["linux basics", "docker fundamentals"],
        "outcomes": ["Container orchestration", "CI/CD setup", "Cloud deployment"],
        "url": "https://example.com/devops-k8s"
    }
]

if __name__ == "__main__":
    # Test the MongoDB Vector Store
    try:
        store = MongoVectorStore()
        
        # Upload sample courses
        result = store.upload_courses(SAMPLE_COURSES)
        print(f"Upload result: {result}")
        
        # Test search
        search_results = store.search_courses("java spring boot", limit=2)
        print(f"Search results: {len(search_results)} courses found")
        for course in search_results:
            print(f"- {course['title']} (similarity: {course.get('relevance_score', 'N/A')})")
        
        # Get stats
        stats = store.get_collection_stats()
        print(f"Collection stats: {stats}")
        
    except Exception as e:
        print(f"Error testing MongoDB Vector Store: {e}")