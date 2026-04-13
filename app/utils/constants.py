"""
SkillMatch Pro — Comprehensive Skill & Role Taxonomy
Covers all major industry domains with hundreds of skills and job roles.
"""

SKILL_TAXONOMY = {
    "Programming Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C#", "C++", "C",
        "Go", "Rust", "Swift", "Kotlin", "Ruby", "PHP", "Scala", "Perl",
        "R", "MATLAB", "Dart", "Lua", "Haskell", "Elixir", "Clojure",
        "F#", "Objective-C", "Assembly", "COBOL", "Fortran", "Julia",
        "Groovy", "Visual Basic", "Shell Scripting", "PowerShell"
    ],
    "Web Frontend": [
        "HTML5", "CSS3", "React", "Angular", "Vue.js", "Svelte",
        "Next.js", "Nuxt.js", "Tailwind CSS", "Bootstrap", "SASS/SCSS",
        "jQuery", "Webpack", "Vite", "Redux", "MobX", "GraphQL Client",
        "Web Components", "PWA Development", "Responsive Design",
        "Cross-Browser Compatibility", "Web Accessibility (WCAG)",
        "SEO Technical", "Web Performance Optimisation"
    ],
    "Web Backend": [
        "Node.js", "Express.js", "Django", "Flask", "FastAPI",
        "Spring Boot", "ASP.NET Core", "Ruby on Rails", "Laravel",
        "NestJS", "Gin (Go)", "Actix (Rust)", "Phoenix (Elixir)",
        "REST API Design", "GraphQL Server", "gRPC", "WebSocket",
        "Microservices Architecture", "Serverless Architecture",
        "API Gateway", "OAuth/OpenID Connect", "JWT Authentication",
        "Rate Limiting", "Caching Strategies"
    ],
    "Mobile Development": [
        "iOS Development", "Android Development", "Flutter", "React Native",
        "Xamarin", "SwiftUI", "Jetpack Compose", "Ionic", "Capacitor",
        "Mobile UI/UX", "App Store Optimisation", "Push Notifications",
        "Mobile Security", "Offline-First Architecture",
        "Mobile Performance Optimisation", "AR/VR Mobile"
    ],
    "Databases": [
        "PostgreSQL", "MySQL", "SQLite", "Microsoft SQL Server",
        "Oracle Database", "MongoDB", "Redis", "Cassandra",
        "DynamoDB", "Elasticsearch", "Neo4j", "CouchDB", "Firebase",
        "InfluxDB", "TimescaleDB", "MariaDB", "Memcached",
        "Database Design", "SQL Advanced", "NoSQL Modelling",
        "Database Performance Tuning", "Data Migration",
        "Replication & Sharding", "Backup & Recovery"
    ],
    "Cloud & Infrastructure": [
        "AWS", "Microsoft Azure", "Google Cloud Platform",
        "AWS Lambda", "EC2", "S3", "CloudFormation",
        "Azure Functions", "Azure DevOps", "GCP Compute Engine",
        "Kubernetes", "Docker", "Terraform", "Ansible",
        "Jenkins", "GitHub Actions", "GitLab CI/CD", "CircleCI",
        "Nginx", "Apache", "Load Balancing", "CDN Management",
        "Cloud Security", "Infrastructure as Code",
        "Service Mesh", "Istio", "Helm Charts"
    ],
    "Data Science & Analytics": [
        "Pandas", "NumPy", "SciPy", "Scikit-learn",
        "Statistical Analysis", "Hypothesis Testing",
        "Regression Analysis", "Time Series Analysis",
        "A/B Testing", "Bayesian Statistics",
        "Data Wrangling", "Feature Engineering",
        "Exploratory Data Analysis", "Data Storytelling",
        "Jupyter Notebooks", "Apache Spark", "Hadoop",
        "ETL Pipelines", "Data Warehousing",
        "Power BI", "Tableau", "Looker", "Metabase",
        "Google Analytics", "Mixpanel"
    ],
    "Machine Learning & AI": [
        "TensorFlow", "PyTorch", "Keras", "XGBoost", "LightGBM",
        "Natural Language Processing", "Computer Vision",
        "Deep Learning", "Reinforcement Learning",
        "Generative AI", "LLM Fine-Tuning", "Prompt Engineering",
        "MLOps", "Model Deployment", "Feature Stores",
        "Recommendation Systems", "Anomaly Detection",
        "Speech Recognition", "Image Classification",
        "Object Detection", "Transformers", "GANs",
        "Transfer Learning", "AutoML", "Edge AI"
    ],
    "Cybersecurity": [
        "Network Security", "Application Security", "Cloud Security",
        "Penetration Testing", "Vulnerability Assessment",
        "SIEM Tools", "Incident Response", "Digital Forensics",
        "Identity & Access Management", "Zero Trust Architecture",
        "Encryption & Cryptography", "Security Compliance",
        "OWASP Top 10", "SOC Operations", "Threat Modelling",
        "Firewall Management", "Endpoint Security",
        "Security Auditing", "Risk Assessment",
        "Data Loss Prevention", "Malware Analysis"
    ],
    "DevOps & SRE": [
        "CI/CD Pipeline Design", "Infrastructure Monitoring",
        "Prometheus", "Grafana", "Datadog", "New Relic",
        "ELK Stack", "Log Management", "Incident Management",
        "SLA/SLO Management", "Chaos Engineering",
        "Blue-Green Deployment", "Canary Releases",
        "Container Orchestration", "GitOps",
        "Configuration Management", "Capacity Planning",
        "Disaster Recovery", "High Availability Design"
    ],
    "UI/UX Design": [
        "User Research", "Wireframing", "Prototyping",
        "Figma", "Sketch", "Adobe XD", "InVision",
        "Interaction Design", "Information Architecture",
        "Usability Testing", "Design Systems",
        "Typography", "Colour Theory", "Layout Design",
        "Responsive Design Principles", "Accessibility Design",
        "Motion Design", "Micro-Interactions",
        "User Journey Mapping", "Persona Development",
        "Heuristic Evaluation", "Card Sorting"
    ],
    "Graphic Design & Multimedia": [
        "Adobe Photoshop", "Adobe Illustrator", "Adobe InDesign",
        "Adobe After Effects", "Adobe Premiere Pro",
        "Canva", "CorelDRAW", "Blender", "Cinema 4D",
        "3D Modelling", "Video Editing", "Motion Graphics",
        "Brand Identity Design", "Print Design",
        "Photo Editing", "Icon Design", "Infographic Design",
        "Storyboarding", "Visual Communication"
    ],
    "Project Management": [
        "Agile Methodology", "Scrum", "Kanban", "SAFe",
        "Waterfall Methodology", "PRINCE2",
        "Jira", "Asana", "Trello", "Monday.com", "Basecamp",
        "Microsoft Project", "Confluence",
        "Sprint Planning", "Backlog Grooming",
        "Stakeholder Management", "Risk Management",
        "Resource Allocation", "Budget Management",
        "Gantt Charts", "Critical Path Method",
        "Change Management", "Earned Value Management"
    ],
    "Marketing": [
        "Digital Marketing Strategy", "Content Marketing",
        "SEO (Search Engine Optimisation)", "SEM / PPC",
        "Google Ads", "Facebook Ads", "LinkedIn Ads",
        "Social Media Marketing", "Email Marketing",
        "Marketing Automation", "HubSpot", "Mailchimp",
        "Brand Strategy", "Market Research",
        "Competitive Analysis", "Customer Segmentation",
        "Conversion Rate Optimisation", "Funnel Optimisation",
        "Influencer Marketing", "Affiliate Marketing",
        "Public Relations", "Event Marketing",
        "Growth Hacking", "Product Marketing",
        "Community Management", "Copywriting"
    ],
    "Sales": [
        "B2B Sales", "B2C Sales", "Inside Sales",
        "Sales Strategy", "Lead Generation", "Cold Outreach",
        "Salesforce CRM", "HubSpot CRM", "Pipeline Management",
        "Account Management", "Enterprise Sales",
        "Solution Selling", "Consultative Selling",
        "Contract Negotiation", "Sales Forecasting",
        "Territory Management", "Upselling/Cross-selling",
        "Demo Presentation", "Proposal Writing"
    ],
    "Finance & Accounting": [
        "Financial Analysis", "Financial Modelling",
        "Budgeting & Forecasting", "Variance Analysis",
        "Management Accounting", "Cost Accounting",
        "Tax Planning", "Tax Compliance",
        "Accounts Payable/Receivable", "General Ledger",
        "Cash Flow Management", "Treasury Management",
        "Audit (Internal)", "Audit (External)",
        "IFRS", "GAAP", "SOX Compliance",
        "SAP Finance", "Oracle Financials", "QuickBooks",
        "Xero", "Financial Reporting", "Mergers & Acquisitions",
        "Investment Analysis", "Credit Risk Analysis",
        "Payroll Processing", "Revenue Recognition"
    ],
    "Human Resources": [
        "Talent Acquisition", "Recruitment",
        "Employee Onboarding", "Performance Management",
        "Compensation & Benefits", "Employee Relations",
        "HR Analytics", "Workforce Planning",
        "Learning & Development", "Training Design",
        "Succession Planning", "Diversity & Inclusion",
        "Employment Law", "HRIS Management",
        "Workday", "BambooHR", "SAP SuccessFactors",
        "Conflict Resolution", "Employee Engagement",
        "Organisational Development", "Job Evaluation",
        "Exit Interviews", "Employer Branding"
    ],
    "Legal": [
        "Contract Law", "Corporate Law", "Intellectual Property",
        "Employment Law", "Data Privacy Law",
        "GDPR Compliance", "Regulatory Compliance",
        "Legal Research", "Contract Drafting",
        "Contract Review", "Litigation Support",
        "Legal Project Management", "E-Discovery",
        "Risk & Compliance", "Corporate Governance",
        "Mergers & Acquisitions Law", "International Law",
        "Arbitration", "Mediation"
    ],
    "Operations & Supply Chain": [
        "Operations Management", "Supply Chain Management",
        "Procurement", "Vendor Management",
        "Inventory Management", "Logistics",
        "Warehouse Management", "Demand Planning",
        "Lean Manufacturing", "Six Sigma",
        "Quality Assurance", "Quality Control",
        "Process Improvement", "Process Mapping",
        "ERP Systems", "SAP MM", "Oracle SCM",
        "Fleet Management", "Distribution Planning",
        "Import/Export Compliance"
    ],
    "Customer Support & Success": [
        "Customer Success Management", "Account Management",
        "Technical Support", "Help Desk Management",
        "Zendesk", "Freshdesk", "Intercom", "ServiceNow",
        "Ticket Management", "SLA Management",
        "Customer Onboarding", "Churn Prevention",
        "Escalation Handling", "Knowledge Base Management",
        "Customer Satisfaction (CSAT)", "NPS Analysis",
        "Live Chat Support", "Phone Support"
    ],
    "Business Analysis": [
        "Requirements Gathering", "Business Process Analysis",
        "Use Case Modelling", "User Stories",
        "Gap Analysis", "Feasibility Study",
        "SWOT Analysis", "Cost-Benefit Analysis",
        "Data Flow Diagrams", "Entity Relationship Diagrams",
        "Business Intelligence", "KPI Development",
        "Dashboard Design", "Report Automation",
        "Process Re-engineering", "Stakeholder Analysis"
    ],
    "Communication & Soft Skills": [
        "Technical Writing", "Business Writing",
        "Presentation Skills", "Public Speaking",
        "Negotiation", "Persuasion",
        "Active Listening", "Conflict Resolution",
        "Cross-Cultural Communication", "Team Leadership",
        "Mentoring & Coaching", "Facilitation",
        "Emotional Intelligence", "Critical Thinking",
        "Problem Solving", "Decision Making",
        "Time Management", "Adaptability",
        "Collaboration", "Creativity",
        "Strategic Thinking", "Attention to Detail"
    ],
    "Industry-Specific": [
        "Healthcare IT (HL7/FHIR)", "Electronic Health Records",
        "Clinical Data Management", "Pharmaceutical Regulations",
        "Fintech", "Payment Systems", "Blockchain",
        "Smart Contracts", "DeFi Protocols",
        "E-Commerce Platforms", "Shopify", "Magento", "WooCommerce",
        "Real Estate Technology", "PropTech",
        "EdTech", "LMS Administration", "Moodle",
        "Automotive Engineering", "IoT Development",
        "Embedded Systems", "RTOS",
        "Robotics", "Drone Technology",
        "Gaming Development", "Unity", "Unreal Engine",
        "GIS / Geospatial Analysis", "CAD/CAM",
        "BIM (Building Information Modelling)",
        "Telecommunications", "5G Technology",
        "Energy & Utilities", "Oil & Gas Software"
    ],
    "Testing & QA": [
        "Manual Testing", "Automated Testing",
        "Selenium", "Cypress", "Playwright",
        "JUnit", "pytest", "Jest",
        "API Testing", "Postman", "SoapUI",
        "Performance Testing", "JMeter", "Gatling",
        "Load Testing", "Stress Testing",
        "Security Testing", "Accessibility Testing",
        "Mobile Testing", "Appium",
        "Test Strategy", "Test Plan Development",
        "BDD/TDD", "Regression Testing",
        "UAT Management", "Bug Tracking"
    ],
    "Data Engineering": [
        "Apache Kafka", "Apache Airflow", "Apache Beam",
        "dbt (Data Build Tool)", "Snowflake", "BigQuery",
        "Redshift", "Delta Lake", "Apache Flink",
        "Data Pipeline Design", "Data Modelling",
        "Star Schema", "Snowflake Schema",
        "Data Governance", "Data Quality Management",
        "Master Data Management", "Data Cataloguing",
        "Real-Time Streaming", "Batch Processing",
        "Data Lake Architecture", "Data Mesh"
    ],
    "Emerging Technologies": [
        "Quantum Computing Basics", "AR/VR Development",
        "WebXR", "Digital Twins", "Edge Computing",
        "Federated Learning", "Homomorphic Encryption",
        "Zero-Knowledge Proofs", "Web3 Development",
        "NFT Technology", "Metaverse Development",
        "Low-Code/No-Code Platforms", "RPA (Robotic Process Automation)",
        "UiPath", "Automation Anywhere", "Blue Prism",
        "Computer-Aided Design (CAD)", "3D Printing/Additive Mfg",
        "Bioinformatics", "Computational Biology"
    ]
}


JOB_ROLES = {
    "Engineering": [
        "Junior Software Engineer", "Software Engineer", "Senior Software Engineer",
        "Staff Engineer", "Principal Engineer", "Distinguished Engineer",
        "Frontend Developer", "Backend Developer", "Full Stack Developer",
        "Mobile Developer (iOS)", "Mobile Developer (Android)", "Mobile Developer (Cross-Platform)",
        "DevOps Engineer", "Site Reliability Engineer", "Platform Engineer",
        "Cloud Engineer", "Cloud Architect", "Solutions Architect",
        "Infrastructure Engineer", "Network Engineer", "Systems Administrator",
        "Database Administrator", "Data Engineer", "Senior Data Engineer",
        "ML Engineer", "AI Engineer", "NLP Engineer", "Computer Vision Engineer",
        "Embedded Systems Engineer", "Firmware Engineer",
        "IoT Engineer", "Robotics Engineer",
        "Security Engineer", "Application Security Engineer", "Penetration Tester",
        "QA Engineer", "QA Automation Engineer", "SDET",
        "Performance Engineer", "Reliability Engineer",
        "Blockchain Developer", "Smart Contract Developer",
        "Game Developer", "Graphics Programmer",
        "Technical Lead", "Engineering Manager", "VP of Engineering",
        "CTO", "Chief Architect"
    ],
    "Data & Analytics": [
        "Data Analyst", "Senior Data Analyst", "Business Intelligence Analyst",
        "Data Scientist", "Senior Data Scientist", "Lead Data Scientist",
        "Research Scientist", "Applied Scientist",
        "Quantitative Analyst", "Statistician",
        "Analytics Engineer", "BI Developer",
        "Data Architect", "Chief Data Officer",
        "Data Governance Analyst", "Data Quality Analyst",
        "Marketing Analyst", "Financial Analyst (Data)",
        "Product Analyst", "Growth Analyst"
    ],
    "Design": [
        "UI Designer", "UX Designer", "UI/UX Designer",
        "Senior Product Designer", "Lead Designer",
        "Interaction Designer", "Visual Designer",
        "Motion Designer", "Graphic Designer",
        "Brand Designer", "Illustrator",
        "Design Systems Lead", "Design Manager",
        "Creative Director", "Art Director",
        "UX Researcher", "UX Writer",
        "Content Designer", "Service Designer",
        "Accessibility Specialist"
    ],
    "Product": [
        "Associate Product Manager", "Product Manager", "Senior Product Manager",
        "Group Product Manager", "Director of Product", "VP of Product",
        "Chief Product Officer", "Product Owner",
        "Technical Product Manager", "Growth Product Manager",
        "Platform Product Manager", "Data Product Manager"
    ],
    "Marketing": [
        "Marketing Coordinator", "Marketing Specialist", "Marketing Manager",
        "Digital Marketing Manager", "Content Marketing Manager",
        "SEO Specialist", "SEM Specialist", "PPC Manager",
        "Social Media Manager", "Social Media Specialist",
        "Email Marketing Specialist", "Marketing Automation Specialist",
        "Brand Manager", "Brand Strategist",
        "Growth Marketing Manager", "Performance Marketing Manager",
        "Content Strategist", "Content Writer", "Copywriter",
        "PR Manager", "Communications Manager",
        "Event Manager", "Community Manager",
        "Marketing Analyst", "Marketing Director",
        "VP of Marketing", "Chief Marketing Officer"
    ],
    "Sales": [
        "Sales Development Representative", "Business Development Representative",
        "Account Executive", "Senior Account Executive",
        "Enterprise Account Executive", "Strategic Account Manager",
        "Sales Manager", "Regional Sales Manager",
        "Sales Director", "VP of Sales",
        "Chief Revenue Officer",
        "Sales Operations Manager", "Sales Engineer",
        "Pre-Sales Consultant", "Solutions Consultant",
        "Channel Sales Manager", "Partner Manager",
        "Customer Success Manager", "Key Account Manager"
    ],
    "Finance": [
        "Accountant", "Senior Accountant", "Staff Accountant",
        "Financial Analyst", "Senior Financial Analyst",
        "FP&A Analyst", "FP&A Manager",
        "Controller", "Assistant Controller",
        "Treasury Analyst", "Treasury Manager",
        "Tax Analyst", "Tax Manager",
        "Internal Auditor", "External Auditor",
        "Revenue Analyst", "Billing Specialist",
        "Accounts Payable Specialist", "Accounts Receivable Specialist",
        "Payroll Specialist", "Payroll Manager",
        "Finance Manager", "Director of Finance",
        "VP of Finance", "Chief Financial Officer"
    ],
    "Human Resources": [
        "HR Coordinator", "HR Generalist", "HR Specialist",
        "Recruiter", "Senior Recruiter", "Technical Recruiter",
        "Recruiting Manager", "Talent Acquisition Manager",
        "HR Business Partner", "Senior HR Business Partner",
        "Compensation Analyst", "Benefits Administrator",
        "L&D Specialist", "Training Manager",
        "Employee Relations Specialist",
        "HR Analytics Specialist",
        "Diversity & Inclusion Manager",
        "HR Manager", "HR Director",
        "VP of People", "Chief People Officer"
    ],
    "Operations": [
        "Operations Coordinator", "Operations Analyst", "Operations Manager",
        "Director of Operations", "VP of Operations", "Chief Operating Officer",
        "Supply Chain Analyst", "Supply Chain Manager",
        "Procurement Specialist", "Procurement Manager",
        "Logistics Coordinator", "Logistics Manager",
        "Warehouse Manager", "Inventory Manager",
        "Quality Assurance Manager", "Quality Control Inspector",
        "Process Improvement Specialist", "Lean/Six Sigma Consultant",
        "Facilities Manager", "Office Manager"
    ],
    "Customer Support": [
        "Customer Support Representative", "Customer Support Specialist",
        "Senior Support Engineer", "Technical Support Engineer",
        "Help Desk Analyst", "IT Support Specialist",
        "Customer Success Manager", "Senior Customer Success Manager",
        "Customer Success Director",
        "Support Team Lead", "Support Manager",
        "Customer Experience Manager",
        "Implementation Specialist", "Onboarding Specialist"
    ],
    "Legal & Compliance": [
        "Legal Assistant", "Paralegal", "Legal Counsel",
        "Senior Legal Counsel", "General Counsel",
        "Contract Manager", "Contract Specialist",
        "Compliance Analyst", "Compliance Officer",
        "Senior Compliance Officer", "Chief Compliance Officer",
        "Privacy Officer", "Data Protection Officer",
        "Regulatory Affairs Specialist",
        "IP Specialist", "Patent Attorney"
    ],
    "Executive & Strategy": [
        "Business Analyst", "Senior Business Analyst",
        "Management Consultant", "Strategy Analyst",
        "Strategy Director", "Chief Strategy Officer",
        "CEO", "COO", "CFO", "CTO", "CMO", "CIO", "CISO", "CPO",
        "General Manager", "Programme Manager",
        "Portfolio Manager", "Transformation Lead",
        "Innovation Manager"
    ],
    "Content & Communication": [
        "Technical Writer", "Senior Technical Writer",
        "Documentation Manager", "Content Writer",
        "Blog Writer", "Journalist",
        "Editor", "Managing Editor",
        "Translator", "Localisation Specialist",
        "Video Producer", "Podcast Producer",
        "Multimedia Specialist", "Communications Specialist",
        "Internal Communications Manager"
    ],
    "IT & Administration": [
        "IT Administrator", "Systems Administrator",
        "Network Administrator", "IT Manager",
        "IT Director", "Chief Information Officer",
        "Help Desk Manager", "IT Project Manager",
        "IT Asset Manager", "Vendor Manager",
        "ERP Administrator", "Salesforce Administrator",
        "ServiceNow Administrator", "Jira Administrator",
        "IT Security Administrator", "IT Compliance Officer"
    ]
}


CERTIFICATIONS = [
    "AWS Certified Solutions Architect", "AWS Certified Developer",
    "AWS Certified DevOps Engineer", "AWS Certified Data Analytics",
    "Azure Fundamentals (AZ-900)", "Azure Administrator (AZ-104)",
    "Azure Solutions Architect (AZ-305)", "Azure Data Engineer (DP-203)",
    "Google Cloud Professional Architect", "Google Cloud Data Engineer",
    "Google Cloud ML Engineer",
    "Certified Kubernetes Administrator (CKA)", "Certified Kubernetes Developer (CKAD)",
    "Docker Certified Associate",
    "CompTIA Security+", "CompTIA Network+", "CompTIA A+",
    "CISSP", "CEH (Certified Ethical Hacker)", "CISM",
    "PMP (Project Management Professional)", "PRINCE2 Foundation",
    "PRINCE2 Practitioner", "Certified ScrumMaster (CSM)",
    "Certified Scrum Product Owner (CSPO)", "PMI-ACP",
    "SAFe Agilist", "SAFe Practitioner",
    "ITIL Foundation", "ITIL Practitioner",
    "Cisco CCNA", "Cisco CCNP", "Cisco CCIE",
    "Oracle Certified Professional (Java)", "Oracle Database Administrator",
    "Microsoft Certified: Data Analyst (Power BI)",
    "Microsoft 365 Certified", "Microsoft Certified: Azure AI Engineer",
    "Salesforce Certified Administrator", "Salesforce Certified Developer",
    "HubSpot Inbound Marketing", "HubSpot Content Marketing",
    "Google Ads Certification", "Google Analytics Certification",
    "Facebook Blueprint Certification",
    "Tableau Desktop Certified", "Tableau Server Certified",
    "Snowflake SnowPro Core",
    "Databricks Certified Data Engineer", "Databricks Certified ML Associate",
    "TensorFlow Developer Certificate", "AWS Machine Learning Specialty",
    "CPA (Certified Public Accountant)", "CFA (Chartered Financial Analyst)",
    "ACCA", "CIMA",
    "Six Sigma Green Belt", "Six Sigma Black Belt",
    "TOGAF Certified", "Certified Business Analyst Professional (CBAP)",
    "SHRM-CP", "SHRM-SCP", "PHR", "SPHR",
    "Certified Information Privacy Professional (CIPP)",
    "ISO 27001 Lead Auditor", "ISO 9001 Lead Auditor"
]

DEPARTMENTS = [
    "Engineering", "Data Science", "Product", "Design",
    "Marketing", "Sales", "Finance", "Human Resources",
    "Operations", "Legal", "Customer Support",
    "IT & Infrastructure", "Research & Development",
    "Quality Assurance", "Business Development",
    "Content & Communications", "Strategy & Consulting",
    "Compliance & Risk", "Administration"
]

LOCATIONS = [
    "London, UK", "Manchester, UK", "Birmingham, UK", "Edinburgh, UK",
    "Bristol, UK", "Leeds, UK", "Glasgow, UK", "Liverpool, UK",
    "Cambridge, UK", "Oxford, UK", "Belfast, UK", "Cardiff, UK",
    "New York, US", "San Francisco, US", "Remote"
]
