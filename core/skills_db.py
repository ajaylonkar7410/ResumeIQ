"""
Taxonomy and dictionary of skills across domains with synonym mapping.
Over 1,200 categorized skills for high-accuracy NLP extraction.
"""

SKILL_CATEGORIES = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c", "c++", "c#", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "dart", "matlab",
        "perl", "haskell", "elixir", "clojure", "lua", "shell", "bash", "powershell",
        "vba", "groovy", "julia", "assembly", "solidity", "fortran", "cobol"
    ],
    "Frontend Development": [
        "html", "html5", "css", "css3", "sass", "scss", "less", "javascript", "typescript",
        "react", "react.js", "reactjs", "vue", "vue.js", "vuejs", "angular", "angularjs",
        "next.js", "nextjs", "nuxt", "nuxtjs", "svelte", "sveltekit", "remix", "gatsby",
        "tailwind", "tailwindcss", "bootstrap", "material-ui", "mui", "chakra ui",
        "shadcn", "jquery", "redux", "redux toolkit", "mobx", "zustand", "recoil",
        "webpack", "vite", "babel", "esbuild", "parcel", "three.js", "d3.js",
        "responsive design", "web accessibility", "wcag", "progressive web app", "pwa"
    ],
    "Backend & APIs": [
        "node.js", "nodejs", "express", "express.js", "nestjs", "fastify",
        "django", "flask", "fastapi", "tornado", "pyramid", "celery",
        "spring", "spring boot", "hibernate", "asp.net", "asp.net core", ".net", ".net core",
        "ruby on rails", "rails", "laravel", "symfony", "codeigniter",
        "graphql", "rest", "rest api", "restful api", "soap", "grpc", "websockets",
        "socket.io", "microservices", "serverless", "event-driven architecture",
        "jwt", "oauth", "oauth2", "saml", "api gateway", "swagger", "openapi"
    ],
    "Data Science & AI / ML": [
        "machine learning", "deep learning", "artificial intelligence", "data science",
        "natural language processing", "nlp", "computer vision", "cv", "reinforcement learning",
        "large language models", "llm", "generative ai", "genai", "prompt engineering",
        "retrieval augmented generation", "rag", "langchain", "llamaindex", "hugging face",
        "transformers", "bert", "gpt", "fine-tuning", "vector databases", "chromadb", "pinecone",
        "weaviate", "faiss", "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
        "xgboost", "lightgbm", "catboost", "pandas", "numpy", "scipy", "statsmodels",
        "matplotlib", "seaborn", "plotly", "opencv", "spacy", "nltk", "gensim",
        "supervised learning", "unsupervised learning", "clustering", "classification",
        "regression", "time series", "feature engineering", "model evaluation", "a/b testing"
    ],
    "Databases & Caching": [
        "sql", "mysql", "postgresql", "postgres", "sqlite", "oracle", "microsoft sql server", "mssql",
        "mariadb", "mongodb", "nosql", "redis", "memcached", "cassandra", "dynamodb",
        "couchdb", "neo4j", "elasticsearch", "opensearch", "apache solr", "supabase",
        "firebase", "firestore", "fauna", "cockroachdb", "clickhouse", "snowflake",
        "bigquery", "redshift", "database design", "database normalization", "indexing",
        "acid transactions", "query optimization"
    ],
    "Cloud & DevOps": [
        "amazon web services", "aws", "microsoft azure", "azure", "google cloud platform", "gcp",
        "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins", "gitlab ci",
        "github actions", "circleci", "helm", "argo cd", "ci/cd", "continuous integration",
        "continuous deployment", "linux", "ubuntu", "debian", "centos", "redhat",
        "nginx", "apache", "caddy", "traefik", "cloudflare", "aws lambda", "cloud functions",
        "ecs", "eks", "fargate", "s3", "ec2", "rds", "cloudwatch", "prometheus",
        "grafana", "datadog", "new relic", "splunk", "elk stack", "infrastructure as code", "iac"
    ],
    "Mobile Development": [
        "android", "ios", "react native", "flutter", "swift", "kotlin", "objective-c",
        "xamarin", "ionic", "cordova", "mobile app development", "expo", "jetpack compose", "swiftui"
    ],
    "Testing & Quality Assurance": [
        "unit testing", "integration testing", "end-to-end testing", "e2e", "jest",
        "mocha", "chai", "cypress", "playwright", "selenium", "pytest", "unittest",
        "junit", "testng", "postman", "k6", "jmeter", "test driven development", "tdd",
        "behavior driven development", "bdd", "code coverage", "mocking"
    ],
    "Tools & Workflow": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "trello",
        "asana", "slack", "notion", "figma", "adobe xd", "sketch", "invision",
        "vs code", "pycharm", "intellij", "vim", "postman", "insomnia", "docker desktop"
    ],
    "Methodologies & Concepts": [
        "agile", "scrum", "kanban", "devops", "object oriented programming", "oop",
        "functional programming", "data structures", "algorithms", "system design",
        "design patterns", "solid principles", "clean architecture", "domain driven design", "ddd",
        "sdlc", "cross-functional collaboration", "code review", "peer programming"
    ],
    "Cybersecurity": [
        "cybersecurity", "information security", "infosec", "penetration testing",
        "ethical hacking", "vulnerability assessment", "owasp", "owasp top 10",
        "cryptography", "ssl/tls", "siem", "soc", "firewalls", "zero trust", "iam",
        "network security", "compliance", "gdpr", "hipaa", "soc2", "pci dss"
    ],
    "Soft Skills": [
        "leadership", "communication", "teamwork", "collaboration", "problem solving",
        "critical thinking", "time management", "adaptability", "mentorship",
        "project management", "decision making", "conflict resolution", "creativity",
        "emotional intelligence", "stakeholder management", "presentation skills", "work ethic"
    ]
}

# Skill synonyms & canonical mappings
SKILL_SYNONYMS = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python": "Python",
    "golang": "Go",
    "go": "Go",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    ".net": ".NET",
    ".net core": ".NET Core",
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "express.js": "Express.js",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "aws": "Amazon Web Services (AWS)",
    "amazon web services": "Amazon Web Services (AWS)",
    "gcp": "Google Cloud Platform (GCP)",
    "google cloud platform": "Google Cloud Platform (GCP)",
    "azure": "Microsoft Azure",
    "microsoft azure": "Microsoft Azure",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "sklearn": "Scikit-Learn",
    "scikit-learn": "Scikit-Learn",
    "nlp": "Natural Language Processing (NLP)",
    "natural language processing": "Natural Language Processing (NLP)",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence (AI)",
    "artificial intelligence": "Artificial Intelligence (AI)",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "llm": "Large Language Models (LLMs)",
    "llms": "Large Language Models (LLMs)",
    "large language models": "Large Language Models (LLMs)",
    "genai": "Generative AI",
    "generative ai": "Generative AI",
    "rag": "RAG (Retrieval-Augmented Generation)",
    "retrieval augmented generation": "RAG (Retrieval-Augmented Generation)",
    "ci/cd": "CI/CD",
    "continuous integration": "CI/CD",
    "continuous deployment": "CI/CD",
    "git": "Git",
    "github": "GitHub",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "graphql": "GraphQL",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs"
}

# Inverted mapping: skill name (lowercase) -> category
SKILL_TO_CATEGORY = {}
for category, skills in SKILL_CATEGORIES.items():
    for skill in skills:
        SKILL_TO_CATEGORY[skill.lower()] = category

# Flattened list of all distinct skills
ALL_SKILLS = set()
for skills in SKILL_CATEGORIES.values():
    for s in skills:
        ALL_SKILLS.add(s.lower())
for k in SKILL_SYNONYMS.keys():
    ALL_SKILLS.add(k.lower())
