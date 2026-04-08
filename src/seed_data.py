"""Seed realistic demo data into the OpenEnv environment."""
from datetime import datetime, timedelta
import random


def seed_demo_data(env):
    """Populate the environment with realistic job postings and demo profiles."""

    # ── Demo Users (created via auth, but seed profiles here) ────
    from auth import hash_password

    # Create demo accounts if they don't exist
    if not env.get_user("seeker@demo.com"):
        env.create_user("seeker@demo.com", hash_password("demo123"), "Alex Johnson", "seeker")
    if not env.get_user("recruiter@demo.com"):
        env.create_user("recruiter@demo.com", hash_password("demo123"), "Sarah Chen", "recruiter")

    # ── Job Postings ─────────────────────────────────────────────
    jobs = [
        {
            "id": "job_001", "title": "Senior Python Engineer",
            "company": "TechFlow AI", "location": "San Francisco, CA",
            "job_type": "Full-time", "salary_range": "$150K - $200K",
            "description": "Join our core platform team to build scalable ML infrastructure. You'll design and implement data pipelines, optimize model serving, and mentor junior engineers.",
            "requirements": {"skills": ["Python", "Machine Learning", "Docker", "Kubernetes", "SQL"], "experience": "5+ years"},
            "posted_by": "recruiter@demo.com"
        },
        {
            "id": "job_002", "title": "Full Stack Developer",
            "company": "NovaSoft", "location": "New York, NY",
            "job_type": "Full-time", "salary_range": "$120K - $160K",
            "description": "Build modern web applications using React and Node.js. Work on our SaaS platform serving 50K+ users.",
            "requirements": {"skills": ["React", "Node.js", "TypeScript", "PostgreSQL", "AWS"], "experience": "3+ years"},
            "posted_by": "recruiter@demo.com"
        },
        {
            "id": "job_003", "title": "Data Scientist",
            "company": "QuantumLeap Analytics", "location": "Remote",
            "job_type": "Full-time", "salary_range": "$130K - $180K",
            "description": "Develop predictive models and drive data-informed decisions. Work with large-scale datasets and cutting-edge ML techniques.",
            "requirements": {"skills": ["Python", "TensorFlow", "Statistics", "SQL", "Data Visualization"], "experience": "3+ years"},
            "posted_by": "recruiter@demo.com"
        },
        {
            "id": "job_004", "title": "DevOps Engineer",
            "company": "CloudNine Systems", "location": "Austin, TX",
            "job_type": "Full-time", "salary_range": "$140K - $185K",
            "description": "Architect and maintain CI/CD pipelines, manage cloud infrastructure on AWS/GCP, and ensure 99.99% uptime for production services.",
            "requirements": {"skills": ["AWS", "Terraform", "Docker", "Kubernetes", "CI/CD", "Linux"], "experience": "4+ years"},
            "posted_by": "recruiter@demo.com"
        },
        {
            "id": "job_005", "title": "ML Engineer",
            "company": "DeepVision Labs", "location": "Seattle, WA",
            "job_type": "Full-time", "salary_range": "$160K - $220K",
            "description": "Build and deploy computer vision models at scale. Work on real-time object detection and image classification systems.",
            "requirements": {"skills": ["Python", "PyTorch", "Computer Vision", "CUDA", "MLOps"], "experience": "4+ years"},
            "posted_by": "recruiter@demo.com"
        },
        {
            "id": "job_006", "title": "Frontend Developer",
            "company": "PixelPerfect Design", "location": "Los Angeles, CA",
            "job_type": "Contract", "salary_range": "$80/hr - $120/hr",
            "description": "Create stunning, responsive user interfaces. Collaborate closely with designers to implement pixel-perfect designs with smooth animations.",
            "requirements": {"skills": ["React", "CSS", "JavaScript", "Figma", "Accessibility"], "experience": "2+ years"},
            "posted_by": "recruiter@demo.com"
        },
        {
            "id": "job_007", "title": "Backend Engineer",
            "company": "FinSecure", "location": "Chicago, IL",
            "job_type": "Full-time", "salary_range": "$135K - $175K",
            "description": "Build highly secure, compliant financial APIs. Work with microservices architecture and event-driven systems.",
            "requirements": {"skills": ["Java", "Spring Boot", "Kafka", "PostgreSQL", "Security"], "experience": "5+ years"},
            "posted_by": "recruiter@demo.com"
        },
        {
            "id": "job_008", "title": "AI Research Engineer",
            "company": "CogniTech", "location": "Remote",
            "job_type": "Full-time", "salary_range": "$170K - $250K",
            "description": "Push the boundaries of NLP and generative AI. Publish papers, develop novel architectures, and transition research into production.",
            "requirements": {"skills": ["Python", "Transformers", "NLP", "Research", "PyTorch"], "experience": "3+ years"},
            "posted_by": "recruiter@demo.com"
        },
        {
            "id": "job_009", "title": "Product Manager - AI",
            "company": "InnovateCo", "location": "Boston, MA",
            "job_type": "Full-time", "salary_range": "$140K - $190K",
            "description": "Lead AI product strategy. Define roadmaps, conduct user research, and drive cross-functional teams to ship world-class AI features.",
            "requirements": {"skills": ["Product Management", "AI/ML Understanding", "Agile", "Data Analysis", "Communication"], "experience": "5+ years"},
            "posted_by": "recruiter@demo.com"
        },
        {
            "id": "job_010", "title": "Junior Data Analyst",
            "company": "GrowthMetrics", "location": "Remote",
            "job_type": "Part-time", "salary_range": "$50K - $75K",
            "description": "Support the analytics team with data extraction, dashboard creation, and basic statistical analysis. Great for career starters!",
            "requirements": {"skills": ["SQL", "Excel", "Python", "Data Visualization", "Communication"], "experience": "0-2 years"},
            "posted_by": "recruiter@demo.com"
        },
    ]

    existing = env.get_all_jobs()
    existing_ids = {j["id"] for j in existing}

    for job in jobs:
        if job["id"] not in existing_ids:
            env.store_job(
                job["id"], job["title"], job["description"], job["requirements"],
                company=job["company"], location=job["location"],
                job_type=job["job_type"], salary_range=job["salary_range"],
                posted_by=job["posted_by"]
            )

    # ── Demo Profiles ────────────────────────────────────────────
    if not env.get_profile("seeker@demo.com"):
        env.store_profile("seeker@demo.com", {
            "name": "Alex Johnson",
            "skills": ["Python", "Machine Learning", "Data Analysis", "SQL", "FastAPI", "Docker"],
            "experience_years": 3,
            "education": "B.Tech Computer Science — MIT",
            "summary": "Passionate ML engineer with 3 years building production data pipelines and predictive models.",
            "links": ["https://github.com/alexjohnson", "https://linkedin.com/in/alexjohnson"]
        })

    # ── Demo Applications ────────────────────────────────────────
    user_apps = env.get_applications_by_user("seeker@demo.com")
    if not user_apps:
        env.store_application("seeker@demo.com", "job_001", "Interview", {
            "resume": "Tailored resume for Senior Python Engineer",
            "cover_letter": "Cover letter for TechFlow AI"
        })
        env.store_application("seeker@demo.com", "job_003", "Applied", {
            "resume": "Tailored resume for Data Scientist",
            "cover_letter": "Cover letter for QuantumLeap Analytics"
        })
        env.store_application("seeker@demo.com", "job_005", "Reviewed", {
            "resume": "Tailored resume for ML Engineer",
            "cover_letter": "Cover letter for DeepVision Labs"
        })
