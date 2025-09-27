import os
import json
import logging
from typing import List, Dict, Any
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseSeeder:
    def __init__(self):
        """Initialize database seeder."""
        self.connection_string = os.getenv(
            "MONGODB_CONNECTION_STRING"
        )
        
        # Connect to MongoDB
        try:
            self.client = MongoClient(self.connection_string, server_api=ServerApi('1'))
            self.client.admin.command('ping')
            logger.info("Connected to MongoDB for seeding")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
        
        self.db = self.client[os.getenv("MONGODB_DB", "upskill_advisor")]
        self.collection = self.db[os.getenv("MONGODB_COLLECTION", "courses")]
    
    def load_courses_from_json(self, file_path: str) -> List[Dict[str, Any]]:
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
    
    def create_text_index(self, course: Dict[str, Any]) -> Dict[str, Any]:
        """Create searchable text index for course."""
        # Combine searchable fields
        searchable_text = f"{course.get('title', '')} {course.get('description', '')} {' '.join(course.get('skills', []))} {' '.join(course.get('outcomes', []))}"
        
        # Add search metadata
        course_with_index = {
            **course,
            'searchable_text': searchable_text.lower(),
            'skill_count': len(course.get('skills', [])),
            'indexed_at': None  # Will be set during upload
        }
        
        return course_with_index
    
    def seed_courses(self, courses: List[Dict[str, Any]], clear_existing: bool = False) -> Dict[str, Any]:
        """Seed courses into MongoDB."""
        try:
            if clear_existing:
                deleted_count = self.collection.delete_many({}).deleted_count
                logger.info(f"Cleared {deleted_count} existing courses")
            
            uploaded_count = 0
            updated_count = 0
            
            for course in courses:
                # Add search indexing
                course_indexed = self.create_text_index(course)
                
                # Set indexed timestamp
                from datetime import datetime
                course_indexed['indexed_at'] = datetime.utcnow().isoformat()
                
                # Upsert course (update if exists, insert if new)
                try:
                    result = self.collection.replace_one(
                        {"course_id": course.get("course_id")},
                        course_indexed,
                        upsert=True
                    )
                    
                    if result.upserted_id:
                        uploaded_count += 1
                    elif result.modified_count:
                        updated_count += 1
                        
                except Exception as e:
                    logger.error(f"Error upserting course {course.get('course_id', 'unknown')}: {e}")
                    continue
            
            # Create text index for search performance
            try:
                self.collection.create_index([
                    ("searchable_text", "text"),
                    ("skills", "text"),
                    ("title", "text")
                ])
                logger.info("Created text search index")
            except Exception as e:
                logger.warning(f"Could not create text index: {e}")
            
            total_courses = self.collection.count_documents({})
            
            logger.info(f"Seeding complete - Uploaded: {uploaded_count}, Updated: {updated_count}, Total: {total_courses}")
            
            return {
                "success": True,
                "uploaded_count": uploaded_count,
                "updated_count": updated_count,
                "total_count": total_courses,
                "cleared_existing": clear_existing
            }
            
        except Exception as e:
            logger.error(f"Error seeding courses: {e}")
            return {"success": False, "error": str(e)}
    
    def get_seeding_stats(self) -> Dict[str, Any]:
        """Get database statistics after seeding."""
        try:
            total = self.collection.count_documents({})
            with_skills = self.collection.count_documents({"skills.0": {"$exists": True}})
            difficulties = list(self.collection.distinct("difficulty"))
            
            # Sample course for verification
            sample = self.collection.find_one({})
            
            return {
                "total_courses": total,
                "courses_with_skills": with_skills,
                "available_difficulties": difficulties,
                "sample_course_id": sample.get("course_id") if sample else None,
                "database_name": self.db.name,
                "collection_name": self.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting seeding stats: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

def seed_from_json(json_file: str = "courses.json", clear_existing: bool = False) -> bool:
    """Convenience function to seed database from JSON file."""
    seeder = None
    try:
        seeder = DatabaseSeeder()
        
        # Load courses
        courses = seeder.load_courses_from_json(json_file)
        if not courses:
            logger.error("No courses to seed")
            return False
        
        # Seed database
        result = seeder.seed_courses(courses, clear_existing=clear_existing)
        
        if result["success"]:
            # Get stats
            stats = seeder.get_seeding_stats()
            logger.info(f"Seeding stats: {stats}")
            return True
        else:
            logger.error(f"Seeding failed: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"Seeding error: {e}")
        return False
    finally:
        if seeder:
            seeder.close()

# Sample course data for testing
SAMPLE_COURSES = [
    {
        "course_id": "java-fs-101",
        "title": "Java Full-Stack Developer Specialization",
        "description": "Comprehensive full-stack development using Java, Spring Boot, React, and SQL fundamentals.",
        "skills": ["java", "spring boot", "sql", "javascript", "react", "html", "css", "git"],
        "difficulty": "intermediate",
        "duration_weeks": 16,
        "prerequisites": ["java", "html", "css"],
        "outcomes": ["Build full-stack apps", "Integrate frontend & backend"],
        "url": "https://www.coursera.org/specializations/java-full-stack"
    },
    {
        "course_id": "spring-boot-msc",
        "title": "Spring Boot and Microservices Masterclass",
        "description": "Master backend development with Spring Boot, REST APIs, and microservices architecture.",
        "skills": ["java", "spring boot", "microservices", "restful apis", "mysql"],
        "difficulty": "advanced",
        "duration_weeks": 10,
        "prerequisites": ["java"],
        "outcomes": ["Build robust REST APIs", "Design microservices"],
        "url": "https://www.udemy.com/course/spring-boot-microservices-and-spring-cloud/"
    },
    {
        "course_id": "react-frontend",
        "title": "React and Modern JavaScript for Front-End",
        "description": "A comprehensive course on React for front-end development, covering hooks and state management.",
        "skills": ["javascript", "react", "html", "css", "nodejs", "testing"],
        "difficulty": "intermediate",
        "duration_weeks": 8,
        "prerequisites": ["javascript"],
        "outcomes": ["Build SPAs with React", "State management"],
        "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/"
    },
    {
        "course_id": "sql-pro-db",
        "title": "Advanced SQL & Database Design",
        "description": "Focuses on complex joins, stored procedures, and efficient database schema design.",
        "skills": ["sql", "mysql", "postgresql", "data analysis", "database design"],
        "difficulty": "advanced",
        "duration_weeks": 5,
        "prerequisites": ["sql"],
        "outcomes": ["Optimize queries", "Design relational databases"],
        "url": "https://www.edx.org/course/advanced-sql-for-data-scientists"
    },
    {
        "course_id": "java-testing",
        "title": "Unit Testing and TDD in Java (JUnit & Mockito)",
        "description": "Learn Test-Driven Development (TDD) principles and use JUnit and Mockito for robust Java applications.",
        "skills": ["java", "testing", "git", "tdd"],
        "difficulty": "intermediate",
        "duration_weeks": 4,
        "prerequisites": ["java"],
        "outcomes": ["Write unit tests", "Improve code reliability"],
        "url": "https://www.udemy.com/course/unit-testing-with-junit-and-mockito/"
    },
    {
        "course_id": "data-science-pro",
        "title": "IBM Data Science Professional Certificate",
        "description": "Master Python, data analysis, visualization, SQL, and machine learning basics.",
        "skills": ["python", "sql", "pandas", "numpy", "matplotlib", "statistics", "data analysis"],
        "difficulty": "intermediate",
        "duration_weeks": 12,
        "prerequisites": ["python"],
        "outcomes": ["Analyze data", "Create visualizations", "Basic ML algorithms"],
        "url": "https://www.coursera.org/professional-certificates/ibm-data-science"
    },
    {
        "course_id": "sql-ds-4",
        "title": "SQL for Data Science and Engineering",
        "description": "Learn advanced SQL queries, window functions, and database design for large datasets.",
        "skills": ["sql", "mysql", "postgresql", "data analysis", "data engineering"],
        "difficulty": "beginner",
        "duration_weeks": 4,
        "prerequisites": [],
        "outcomes": ["Write complex SQL queries", "Manage database schemas"],
        "url": "https://www.coursera.org/learn/sql-for-data-science"
    },
    {
        "course_id": "data-viz-p",
        "title": "Data Visualization with Python and Tableau",
        "description": "Techniques for effective data storytelling using Matplotlib, Seaborn, and Tableau.",
        "skills": ["python", "matplotlib", "data visualization", "pandas", "data analysis"],
        "difficulty": "intermediate",
        "duration_weeks": 6,
        "prerequisites": ["python", "pandas"],
        "outcomes": ["Create interactive dashboards", "Tell data stories"],
        "url": "https://www.coursera.org/specializations/data-visualization-tableau-python"
    },
    {
        "course_id": "stat-for-ds",
        "title": "Statistics and Probability for Data Science",
        "description": "Fundamental concepts in statistics, probability, and hypothesis testing.",
        "skills": ["statistics", "probability", "data analysis", "python"],
        "difficulty": "beginner",
        "duration_weeks": 8,
        "prerequisites": ["python"],
        "outcomes": ["Perform hypothesis testing", "Understand distributions"],
        "url": "https://www.edx.org/course/statistics-and-probability-for-data-science"
    },
    {
        "course_id": "big-data-p",
        "title": "Introduction to Big Data with PySpark",
        "description": "Learn to process large datasets using Apache Spark and Python.",
        "skills": ["python", "data engineering", "big data", "pyspark"],
        "difficulty": "advanced",
        "duration_weeks": 7,
        "prerequisites": ["python", "data analysis"],
        "outcomes": ["Process large data sets", "Use PySpark APIs"],
        "url": "https://www.coursera.org/learn/introduction-big-data-pyspark"
    },
    {
        "course_id": "ml-spec",
        "title": "Machine Learning Specialization by Andrew Ng",
        "description": "Learn supervised, unsupervised learning, deep learning, and practical ML deployment.",
        "skills": ["machine learning", "deep learning", "tensorflow", "pytorch", "model deployment", "statistics"],
        "difficulty": "intermediate",
        "duration_weeks": 12,
        "prerequisites": ["python", "statistics"],
        "outcomes": ["Build ML models", "Train neural networks", "Deploy AI systems"],
        "url": "https://www.coursera.org/specializations/machine-learning-introduction"
    },
    {
        "course_id": "dl-tf-adv",
        "title": "Deep Learning with TensorFlow and Keras",
        "description": "Hands-on advanced deep learning focusing on computer vision and NLP with TensorFlow.",
        "skills": ["deep learning", "tensorflow", "neural networks", "nlp", "computer vision"],
        "difficulty": "advanced",
        "duration_weeks": 10,
        "prerequisites": ["python", "machine learning"],
        "outcomes": ["Apply CNNs & RNNs", "Develop NLP models", "Deploy complex models"],
        "url": "https://www.udemy.com/course/deep-learning-tensorflow-2/"
    },
    {
        "course_id": "nlp-p",
        "title": "Natural Language Processing with Deep Learning",
        "description": "Focuses on Transformer models, BERT, and advanced NLP techniques.",
        "skills": ["nlp", "deep learning", "pytorch", "python", "machine learning"],
        "difficulty": "advanced",
        "duration_weeks": 8,
        "prerequisites": ["deep learning"],
        "outcomes": ["Build custom language models", "Sentiment analysis"],
        "url": "https://www.coursera.org/specializations/natural-language-processing"
    },
    {
        "course_id": "cv-p",
        "title": "Computer Vision Fundamentals",
        "description": "Introduction to image processing, object detection, and segmentation using OpenCV and TensorFlow.",
        "skills": ["computer vision", "tensorflow", "python", "machine learning"],
        "difficulty": "intermediate",
        "duration_weeks": 6,
        "prerequisites": ["python"],
        "outcomes": ["Implement image filters", "Train detection models"],
        "url": "https://www.udemy.com/course/computer-vision-a-to-z/"
    },
    {
        "course_id": "mlops-e",
        "title": "MLOps Engineering on AWS",
        "description": "Building, deploying, and monitoring scalable ML pipelines using AWS services.",
        "skills": ["model deployment", "aws", "docker", "ci/cd", "machine learning"],
        "difficulty": "advanced",
        "duration_weeks": 14,
        "prerequisites": ["aws", "docker", "machine learning"],
        "outcomes": ["Manage model lifecycle", "Implement CI/CD for ML"],
        "url": "https://www.coursera.org/specializations/mlops-engineering-on-aws"
    },
    {
        "course_id": "devops-aws",
        "title": "DevOps on AWS Specialization",
        "description": "Master CI/CD, Docker, Kubernetes, Terraform, and AWS cloud deployment practices.",
        "skills": ["aws", "docker", "kubernetes", "terraform", "ci/cd", "git", "cloud security"],
        "difficulty": "intermediate",
        "duration_weeks": 14,
        "prerequisites": ["linux", "git", "aws"],
        "outcomes": ["Automate pipelines", "Deploy on AWS", "Manage Kubernetes clusters"],
        "url": "https://www.coursera.org/specializations/devops-on-aws"
    },
    {
        "course_id": "k8s-basics",
        "title": "Kubernetes for the Absolute Beginners",
        "description": "Learn Kubernetes fundamentals, orchestration of containers, and kubectl commands.",
        "skills": ["kubernetes", "docker", "containers", "deployment", "linux"],
        "difficulty": "beginner",
        "duration_weeks": 6,
        "prerequisites": ["docker"],
        "outcomes": ["Deploy apps in Kubernetes", "Manage clusters"],
        "url": "https://www.udemy.com/course/kubernetes-for-the-absolute-beginners-hands-on/"
    },
    {
        "course_id": "terraform-a",
        "title": "Terraform and Infrastructure as Code",
        "description": "Learn to manage infrastructure across multiple clouds (AWS, Azure) using HashiCorp Terraform.",
        "skills": ["terraform", "aws", "azure", "ci/cd", "shell scripting"],
        "difficulty": "advanced",
        "duration_weeks": 8,
        "prerequisites": ["aws", "linux"],
        "outcomes": ["Automate infrastructure", "Manage cloud resources"],
        "url": "https://www.udemy.com/course/terraform-and-aws-masterclass/"
    },
    {
        "course_id": "linux-b",
        "title": "Linux Fundamentals and Shell Scripting",
        "description": "Essential course for system administration, basic commands, and automation scripts.",
        "skills": ["linux", "shell scripting", "git"],
        "difficulty": "beginner",
        "duration_weeks": 4,
        "prerequisites": [],
        "outcomes": ["Navigate the Linux CLI", "Write basic shell scripts"],
        "url": "https://www.coursera.org/learn/linux-command-line"
    },
    {
        "course_id": "monitoring-p",
        "title": "Cloud Monitoring with Prometheus and Grafana",
        "description": "Set up and manage monitoring and alerting for cloud-native applications.",
        "skills": ["monitoring", "kubernetes", "prometheus", "grafana", "linux"],
        "difficulty": "advanced",
        "duration_weeks": 5,
        "prerequisites": ["kubernetes", "linux"],
        "outcomes": ["Deploy centralized logging", "Set up robust alerting"],
        "url": "https://www.udemy.com/course/prometheus-and-grafana-for-devops-and-monitoring/"
    },
    {
        "course_id": "python-b",
        "title": "Python Basics for Data Analysis",
        "description": "A beginner's guide to Python syntax and essential libraries for data handling.",
        "skills": ["python"],
        "difficulty": "beginner",
        "duration_weeks": 3,
        "prerequisites": [],
        "outcomes": ["Write basic Python scripts", "Understand fundamental data types"],
        "url": "https://www.udemy.com/course/python-for-data-analysis-and-visualization-essentials/"
    },
    {
        "course_id": "js-b",
        "title": "JavaScript Fundamentals",
        "description": "Covers core JavaScript concepts, DOM manipulation, and modern ES6 features.",
        "skills": ["javascript", "html", "css"],
        "difficulty": "beginner",
        "duration_weeks": 4,
        "prerequisites": [],
        "outcomes": ["Write clean JS code", "Manipulate the DOM"],
        "url": "https://www.udemy.com/course/javascript-the-complete-guide-incl-es6-and-beyond/"
    },
    {
        "course_id": "git-b",
        "title": "Git and GitHub Crash Course",
        "description": "Essential version control for software development teams.",
        "skills": ["git"],
        "difficulty": "beginner",
        "duration_weeks": 2,
        "prerequisites": [],
        "outcomes": ["Master basic Git commands", "Collaborate on GitHub"],
        "url": "https://www.coursera.org/learn/introduction-git-github"
    },
    {
        "course_id": "db-design",
        "title": "Relational Database Design",
        "description": "Principles of normalization, entity-relationship modeling, and schema optimization.",
        "skills": ["database design", "sql", "mysql"],
        "difficulty": "intermediate",
        "duration_weeks": 4,
        "prerequisites": ["sql"],
        "outcomes": ["Design optimized schemas", "Apply normalization rules"],
        "url": "https://www.edx.org/course/relational-database-design-in-data-science"
    },
    {
        "course_id": "backend-sec",
        "title": "Backend Security and API Hardening (Java focus)",
        "description": "Securing REST APIs, handling authentication (OAuth, JWT), and preventing common attacks.",
        "skills": ["java", "spring boot", "restful apis", "cloud security"],
        "difficulty": "advanced",
        "duration_weeks": 6,
        "prerequisites": ["spring boot"],
        "outcomes": ["Implement robust security", "Understand web vulnerabilities"],
        "url": "https://www.udemy.com/course/spring-security-masterclass/"
    },
    {
        "course_id": "azure-devops",
        "title": "Microsoft Azure DevOps Solutions",
        "description": "Implementing continuous integration and delivery using Azure DevOps tools.",
        "skills": ["azure", "ci/cd", "git", "docker", "terraform"],
        "difficulty": "intermediate",
        "duration_weeks": 10,
        "prerequisites": ["git"],
        "outcomes": ["Pass Azure DevOps exam", "Set up CI/CD pipelines"],
        "url": "https://www.coursera.org/specializations/azure-devops"
    },
    {
        "course_id": "gcp-cloud",
        "title": "Google Cloud Platform Fundamentals",
        "description": "Core GCP services including Compute Engine, Cloud Storage, and Networking.",
        "skills": ["google cloud", "docker", "kubernetes"],
        "difficulty": "beginner",
        "duration_weeks": 5,
        "prerequisites": [],
        "outcomes": ["Deploy basic apps on GCP", "Understand cloud concepts"],
        "url": "https://www.coursera.org/professional-certificates/google-cloud-computing-foundations"
    },
    {
        "course_id": "adv-stats",
        "title": "Advanced Statistical Modeling",
        "description": "In-depth look at regression, time series, and Bayesian methods.",
        "skills": ["statistics", "python", "data analysis"],
        "difficulty": "advanced",
        "duration_weeks": 8,
        "prerequisites": ["statistics"],
        "outcomes": ["Build advanced predictive models", "Analyze complex data"],
        "url": "https://www.edx.org/course/advanced-statistical-methods"
    },
    {
        "course_id": "data-eng-etl",
        "title": "Data Engineering: ETL and Data Pipelines",
        "description": "Focuses on designing and implementing ETL (Extract, Transform, Load) pipelines for data warehouses.",
        "skills": ["data engineering", "sql", "python", "pyspark", "big data"],
        "difficulty": "advanced",
        "duration_weeks": 10,
        "prerequisites": ["sql", "python"],
        "outcomes": ["Design reliable ETLs", "Manage data quality"],
        "url": "https://www.udemy.com/course/data-engineering-and-etl-pipelines/"
    },
    {
        "course_id": "pytorch-dl",
        "title": "Deep Learning with PyTorch",
        "description": "Hands-on course focusing exclusively on PyTorch for building neural networks.",
        "skills": ["pytorch", "deep learning", "neural networks", "python"],
        "difficulty": "intermediate",
        "duration_weeks": 7,
        "prerequisites": ["python", "machine learning"],
        "outcomes": ["Use PyTorch API", "Implement custom layers"],
        "url": "https://www.coursera.org/specializations/deep-learning-pytorch"
    },
    {
        "course_id": "adv-ci-cd",
        "title": "Advanced CI/CD with Jenkins and GitOps",
        "description": "Advanced techniques in continuous delivery, focusing on Jenkins, ArgoCD, and automation.",
        "skills": ["ci/cd", "git", "kubernetes", "shell scripting", "automation"],
        "difficulty": "advanced",
        "duration_weeks": 7,
        "prerequisites": ["git", "docker"],
        "outcomes": ["Implement GitOps workflows", "Master Jenkins pipeline"],
        "url": "https://www.udemy.com/course/advanced-ci-cd-jenkins-and-gitops/"
    },
    {
        "course_id": "model-deploy",
        "title": "Productionizing Machine Learning Models",
        "description": "Covers model serving, containerization, and API creation for ML products.",
        "skills": ["model deployment", "docker", "fastapi", "python"],
        "difficulty": "intermediate",
        "duration_weeks": 5,
        "prerequisites": ["python", "machine learning"],
        "outcomes": ["Deploy models via API", "Containerize ML apps"],
        "url": "https://www.coursera.org/learn/production-machine-learning-model"
    },
    {
        "course_id": "agile-s",
        "title": "Agile Development and Scrum Master Certification Prep",
        "description": "Learn Scrum, Kanban, and Agile methodologies for project management.",
        "skills": ["git", "automation", "tdd"],
        "difficulty": "beginner",
        "duration_weeks": 4,
        "prerequisites": [],
        "outcomes": ["Lead Scrum teams", "Manage agile projects"],
        "url": "https://www.udemy.com/course/agile-scrum-master-certification/"
    },
    {
        "course_id": "adv-javascript",
        "title": "Advanced JavaScript Topics (Design Patterns, Async/Await)",
        "description": "Deep dive into complex JavaScript features and modern asynchronous programming.",
        "skills": ["javascript", "nodejs", "restful apis"],
        "difficulty": "advanced",
        "duration_weeks": 6,
        "prerequisites": ["javascript"],
        "outcomes": ["Write efficient asynchronous code", "Apply design patterns"],
        "url": "https://www.udemy.com/course/advanced-javascript-concepts/"
    },
  {
    "course_id": "java-spring-security",
    "title": "Spring Security and JWT Authentication",
    "description": "Master security implementation in Spring Boot applications with JWT tokens, OAuth2, and role-based access control.",
    "skills": ["java", "spring boot", "spring security", "jwt", "oauth2", "restful apis"],
    "difficulty": "advanced",
    "duration_weeks": 6,
    "prerequisites": ["java", "spring boot"],
    "outcomes": ["Implement authentication", "Secure REST APIs", "Role-based authorization"],
    "url": "https://www.udemy.com/course/spring-security-complete/"
  },
  {
    "course_id": "java-hibernate-jpa",
    "title": "Hibernate and JPA with Spring Data",
    "description": "Database persistence layer development using Hibernate, JPA, and Spring Data repositories.",
    "skills": ["java", "hibernate", "jpa", "spring boot", "mysql", "sql"],
    "difficulty": "intermediate",
    "duration_weeks": 8,
    "prerequisites": ["java", "sql"],
    "outcomes": ["ORM implementation", "Database relationships", "Repository patterns"],
    "url": "https://www.udemy.com/course/hibernate-and-spring-data-jpa/"
  },
  {
    "course_id": "java-maven-gradle",
    "title": "Java Build Tools: Maven and Gradle",
    "description": "Project management and build automation using Maven and Gradle for Java applications.",
    "skills": ["java", "maven", "gradle", "build automation", "dependency management"],
    "difficulty": "intermediate",
    "duration_weeks": 4,
    "prerequisites": ["java"],
    "outcomes": ["Manage dependencies", "Build automation", "Project structure"],
    "url": "https://www.udemy.com/course/java-build-tools-maven-gradle/"
  },
  {
    "course_id": "react-typescript",
    "title": "React with TypeScript for Enterprise Apps",
    "description": "Build type-safe React applications using TypeScript with advanced patterns and testing.",
    "skills": ["react", "typescript", "javascript", "testing", "html", "css"],
    "difficulty": "advanced",
    "duration_weeks": 10,
    "prerequisites": ["react", "javascript"],
    "outcomes": ["Type-safe React apps", "Advanced component patterns", "Testing strategies"],
    "url": "https://www.udemy.com/course/react-typescript-enterprise/"
  },
  {
    "course_id": "java-kafka-messaging",
    "title": "Apache Kafka with Spring Boot",
    "description": "Event-driven architecture using Apache Kafka for messaging between microservices.",
    "skills": ["java", "spring boot", "kafka", "microservices", "event-driven architecture"],
    "difficulty": "advanced",
    "duration_weeks": 7,
    "prerequisites": ["java", "spring boot", "microservices"],
    "outcomes": ["Event streaming", "Microservice communication", "Kafka integration"],
    "url": "https://www.udemy.com/course/apache-kafka-spring-boot/"
  },
  {
    "course_id": "pandas-advanced",
    "title": "Advanced Pandas for Data Analysis",
    "description": "Master advanced Pandas techniques for complex data manipulation, time series, and performance optimization.",
    "skills": ["python", "pandas", "data analysis", "numpy", "data cleaning"],
    "difficulty": "advanced",
    "duration_weeks": 6,
    "prerequisites": ["python", "pandas"],
    "outcomes": ["Complex data transformations", "Time series analysis", "Performance optimization"],
    "url": "https://www.udemy.com/course/advanced-pandas-data-analysis/"
  },
  {
    "course_id": "feature-engineering",
    "title": "Feature Engineering for Machine Learning",
    "description": "Comprehensive course on feature selection, engineering, and preprocessing for ML models.",
    "skills": ["python", "feature engineering", "machine learning", "scikit-learn", "data preprocessing"],
    "difficulty": "intermediate",
    "duration_weeks": 8,
    "prerequisites": ["python", "machine learning"],
    "outcomes": ["Feature selection techniques", "Data preprocessing", "Model performance improvement"],
    "url": "https://www.coursera.org/learn/feature-engineering"
  },
  {
    "course_id": "time-series-analysis",
    "title": "Time Series Analysis and Forecasting",
    "description": "Statistical methods and machine learning approaches for time series data analysis and forecasting.",
    "skills": ["python", "statistics", "time series", "forecasting", "data analysis"],
    "difficulty": "advanced",
    "duration_weeks": 10,
    "prerequisites": ["python", "statistics"],
    "outcomes": ["Time series modeling", "Forecasting techniques", "Trend analysis"],
    "url": "https://www.coursera.org/learn/time-series-analysis"
  },
  {
    "course_id": "ab-testing",
    "title": "A/B Testing and Experimental Design",
    "description": "Design and analyze experiments, A/B testing, and statistical inference for data-driven decisions.",
    "skills": ["statistics", "experimental design", "hypothesis testing", "python", "data analysis"],
    "difficulty": "intermediate",
    "duration_weeks": 6,
    "prerequisites": ["statistics", "python"],
    "outcomes": ["Design experiments", "Statistical testing", "Business impact analysis"],
    "url": "https://www.udemy.com/course/ab-testing-experimental-design/"
  },
  {
    "course_id": "neural-networks-scratch",
    "title": "Neural Networks from Scratch",
    "description": "Build neural networks from fundamental mathematical concepts without using high-level frameworks.",
    "skills": ["python", "neural networks", "deep learning", "mathematics", "numpy"],
    "difficulty": "advanced",
    "duration_weeks": 12,
    "prerequisites": ["python", "statistics", "linear algebra"],
    "outcomes": ["Understand neural network fundamentals", "Implement backpropagation", "Custom architectures"],
    "url": "https://www.coursera.org/learn/neural-networks-deep-learning"
  },
  {
    "course_id": "reinforcement-learning",
    "title": "Reinforcement Learning with Python",
    "description": "Learn Q-learning, policy gradients, and deep reinforcement learning for decision-making systems.",
    "skills": ["python", "reinforcement learning", "machine learning", "deep learning", "algorithms"],
    "difficulty": "advanced",
    "duration_weeks": 14,
    "prerequisites": ["python", "machine learning", "deep learning"],
    "outcomes": ["Implement RL algorithms", "Game AI development", "Decision systems"],
    "url": "https://www.udemy.com/course/reinforcement-learning-with-python/"
  },
  {
    "course_id": "model-interpretability",
    "title": "Machine Learning Model Interpretability",
    "description": "Techniques for explaining and interpreting machine learning models including SHAP, LIME, and feature importance.",
    "skills": ["python", "machine learning", "model interpretability", "explainable ai", "visualization"],
    "difficulty": "intermediate",
    "duration_weeks": 6,
    "prerequisites": ["python", "machine learning"],
    "outcomes": ["Model explanation techniques", "Feature importance analysis", "Bias detection"],
    "url": "https://www.coursera.org/learn/machine-learning-interpretability"
  },
  {
    "course_id": "docker-fundamentals",
    "title": "Docker Fundamentals for DevOps",
    "description": "Container technology basics, Docker commands, image creation, and container orchestration fundamentals.",
    "skills": ["docker", "containers", "linux", "virtualization", "deployment"],
    "difficulty": "beginner",
    "duration_weeks": 5,
    "prerequisites": ["linux"],
    "outcomes": ["Create Docker images", "Container management", "Multi-container apps"],
    "url": "https://www.udemy.com/course/docker-fundamentals/"
  },
  {
    "course_id": "ansible-automation",
    "title": "Ansible for Configuration Management",
    "description": "Infrastructure automation using Ansible playbooks, roles, and configuration management at scale.",
    "skills": ["ansible", "automation", "linux", "configuration management", "yaml"],
    "difficulty": "intermediate",
    "duration_weeks": 8,
    "prerequisites": ["linux", "shell scripting"],
    "outcomes": ["Automate deployments", "Configuration management", "Infrastructure as code"],
    "url": "https://www.udemy.com/course/ansible-automation/"
  },
  {
    "course_id": "gitlab-cicd",
    "title": "GitLab CI/CD Pipeline Mastery",
    "description": "Advanced CI/CD pipeline creation using GitLab, including testing, security scanning, and deployment strategies.",
    "skills": ["gitlab", "ci/cd", "git", "docker", "testing", "deployment"],
    "difficulty": "advanced",
    "duration_weeks": 9,
    "prerequisites": ["git", "docker"],
    "outcomes": ["Build complex pipelines", "Automated testing", "Deployment strategies"],
    "url": "https://www.udemy.com/course/gitlab-cicd-pipelines/"
  },
  {
    "course_id": "helm-kubernetes",
    "title": "Helm Charts for Kubernetes Applications",
    "description": "Package and deploy Kubernetes applications using Helm charts with templating and lifecycle management.",
    "skills": ["kubernetes", "helm", "yaml", "package management", "deployment"],
    "difficulty": "intermediate",
    "duration_weeks": 6,
    "prerequisites": ["kubernetes", "docker"],
    "outcomes": ["Create Helm charts", "Application packaging", "Release management"],
    "url": "https://www.udemy.com/course/helm-kubernetes-packaging/"
  },
  {
    "course_id": "aws-eks",
    "title": "Amazon EKS (Elastic Kubernetes Service)",
    "description": "Deploy and manage Kubernetes clusters on AWS using EKS with networking, security, and scaling.",
    "skills": ["aws", "kubernetes", "eks", "cloud security", "networking"],
    "difficulty": "advanced",
    "duration_weeks": 10,
    "prerequisites": ["aws", "kubernetes"],
    "outcomes": ["Deploy EKS clusters", "AWS integration", "Production Kubernetes"],
    "url": "https://www.coursera.org/learn/aws-eks-kubernetes/"
  },
  {
    "course_id": "infrastructure-monitoring",
    "title": "Infrastructure Monitoring and Alerting",
    "description": "Comprehensive monitoring strategy using Prometheus, Grafana, ELK stack, and alerting systems.",
    "skills": ["monitoring", "prometheus", "grafana", "elk stack", "alerting", "observability"],
    "difficulty": "advanced",
    "duration_weeks": 8,
    "prerequisites": ["linux", "docker"],
    "outcomes": ["Monitoring infrastructure", "Log analysis", "Alerting strategies"],
    "url": "https://www.udemy.com/course/infrastructure-monitoring-complete/"
  },
  {
    "course_id": "istio-service-mesh",
    "title": "Istio Service Mesh for Microservices",
    "description": "Advanced microservice communication, security, and observability using Istio service mesh.",
    "skills": ["istio", "kubernetes", "microservices", "service mesh", "security"],
    "difficulty": "advanced",
    "duration_weeks": 7,
    "prerequisites": ["kubernetes", "microservices"],
    "outcomes": ["Service mesh implementation", "Traffic management", "Security policies"],
    "url": "https://www.udemy.com/course/istio-service-mesh/"
  },
  {
    "course_id": "cloud-cost-optimization",
    "title": "Multi-Cloud Cost Optimization",
    "description": "Strategies for optimizing costs across AWS, Azure, and Google Cloud platforms with automation tools.",
    "skills": ["aws", "azure", "google cloud", "cost optimization", "automation", "finops"],
    "difficulty": "intermediate",
    "duration_weeks": 6,
    "prerequisites": ["cloud platforms"],
    "outcomes": ["Cost analysis", "Resource optimization", "Budget management"],
    "url": "https://www.coursera.org/learn/cloud-cost-optimization"
  }

]

def main():
    """Main seeding function."""
    print("Database Seeding Tool")
    print("=" * 30)
    
    # Check if courses.json exists
    if os.path.exists("courses.json"):
        print("Found courses.json file")
        success = seed_from_json("courses.json", clear_existing=True)
    else:
        print("courses.json not found, using sample data")
        seeder = None
        try:
            seeder = DatabaseSeeder()
            result = seeder.seed_courses(SAMPLE_COURSES, clear_existing=True)
            success = result["success"]
            if success:
                stats = seeder.get_seeding_stats()
                print(f"Seeding stats: {stats}")
        except Exception as e:
            print(f"Seeding failed: {e}")
            success = False
        finally:
            if seeder:
                seeder.close()
    
    if success:
        print("Database seeding completed successfully!")
    else:
        print("Database seeding failed!")

if __name__ == "__main__":
    main()