// Note: GOAL_ROLES should be imported from roles.js instead
export const PROFICIENCY_LEVELS = [
  "Beginner",
  "Intermediate", 
  "Advanced",
  "Expert"
];

export const SKILL_SUGGESTIONS = {
  "Java Full Stack Developer": [
    // Frontend
    "HTML", "CSS", "JavaScript", "TypeScript", "React", "Angular", "Vue.js", "Responsive Design", "Tailwind CSS",

    // Backend
    "Java", "Spring Boot", "RESTful APIs", "GraphQL",

    // Databases
    "SQL", "MySQL", "PostgreSQL", "MongoDB",

    // Tools
    "Git", "GitHub", "CI/CD", "Docker", "Kubernetes", "Microservices"
  ],

  "Data Scientist": [
    "Python", "R", "Pandas", "NumPy", "Matplotlib", "Seaborn",
    "Statistics", "SQL", "MySQL", "PostgreSQL",
    "Data Visualization", "Feature Engineering", "Big Data (Hadoop, Spark)"
  ],

  "Machine Learning Engineer": [
    "Python", "R", "Scikit-learn", "TensorFlow", "Keras", "PyTorch",
    "Deep Learning", "Natural Language Processing (NLP)", "Computer Vision",
    "Feature Engineering", "Model Deployment", "ML Ops", "SQL", "MySQL"
  ],

  "DevOps Engineer": [
    "Git", "GitHub", "CI/CD", "Jenkins", "Docker", "Kubernetes",
    "Terraform", "AWS", "Azure", "Google Cloud",
    "Linux", "Shell Scripting", "Monitoring & Logging (Prometheus, Grafana)",
    "Cloud Security", "Serverless"
  ]
};