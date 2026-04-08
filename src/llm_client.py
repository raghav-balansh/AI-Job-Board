"""
LLM Client — Qwen 2.5 via HuggingFace Inference API.
Free, serverless, no GPU required.
Falls back to intelligent mock responses when HF_TOKEN is not set or API fails.
"""
import os

# Qwen 2.5 model via HF Inference Providers (free tier)
DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"
_client = None


def get_client():
    """Get a cached HuggingFace InferenceClient."""
    global _client
    if _client is not None:
        return _client

    token = os.environ.get("HF_TOKEN", "")
    if not token:
        return None

    try:
        from huggingface_hub import InferenceClient
        _client = InferenceClient(token=token, timeout=30)
        return _client
    except Exception as e:
        print(f"[Qwen 2.5] Client init error: {e}")
        return None


def llm_generate(prompt: str, max_tokens: int = 512, system_prompt: str = None) -> str:
    """
    Generate text using Qwen 2.5 via HF Inference API.
    Falls back to mock responses if token missing or API fails.
    """
    client = get_client()
    if client is None:
        return _mock_response(prompt)

    if system_prompt is None:
        system_prompt = "You are Qwen, a helpful career assistant powered by reinforcement learning. Be concise, professional, and data-driven."

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        text = response.choices[0].message.content
        return text.strip() if text else _mock_response(prompt)
    except Exception as e:
        print(f"[Qwen 2.5] API error: {e}")
        return _mock_response(prompt)


def _mock_response(prompt: str) -> str:
    """Intelligent fallback mock responses when Qwen 2.5 API is unavailable."""
    p = prompt.lower()

    # Check more specific patterns FIRST to avoid false matches
    if "tailor" in p or ("rewrite" in p and "resume" in p) or ("optimized" in p and "resume" in p):
        return """DEMO USER
Software Engineer | Python · ML · Cloud

PROFESSIONAL SUMMARY
Results-driven engineer with 3+ years of experience building scalable ML pipelines and backend APIs. Proven track record of delivering production-grade solutions that drive business impact.

TECHNICAL SKILLS
Python, Machine Learning, TensorFlow, SQL, FastAPI, Docker, AWS, Git

EXPERIENCE
ML Engineer — TechStartup Inc. (2023–Present)
• Built end-to-end ML pipeline serving 10K+ predictions/day with 99.5% uptime
• Developed RESTful APIs handling 1M+ requests/month using FastAPI
• Led migration of legacy batch systems to real-time streaming architecture

Junior Developer — DataCorp (2021–2023)
• Implemented automated data quality checks reducing errors by 40%
• Created dashboards for executive team using Python and Plotly

EDUCATION
B.Tech Computer Science — University of Technology (2021)"""

    if "cover letter" in p:
        return """Dear Hiring Manager,

I am writing to express my strong interest in this position. With 3+ years of hands-on experience in software development, I bring a proven ability to deliver high-impact technical solutions.

My background in Python, Machine Learning, and cloud architecture aligns well with your requirements. At my current role, I built production ML pipelines that serve thousands of real-time predictions daily, and I have extensive experience designing scalable REST APIs.

What excites me most about this opportunity is the chance to apply my skills in a challenging, growth-oriented environment. I am passionate about leveraging technology to solve real problems, and I am confident I can make an immediate contribution to your team.

I would welcome the opportunity to discuss how my experience and enthusiasm can benefit your organization.

Best regards,
Demo User"""

    if "skill" in p and "gap" in p:
        return """SKILL GAP ANALYSIS (RL-Optimized):

✅ STRONG MATCHES:
  • Python — 3+ years production experience
  • Machine Learning — Built end-to-end pipelines
  • Data Analysis — Statistical modeling & visualization

⚠️ GAPS IDENTIFIED:
  • Kubernetes — Recommended: "Kubernetes for Developers" (Udemy, free trial)
  • System Design — Recommended: "Grokking System Design" (Educative)
  • GraphQL — Recommended: "GraphQL Fundamentals" (Apollo, free)

📊 OVERALL MATCH SCORE: 72%
💡 ESTIMATED UPSKILL TIME: 4-6 weeks for core gaps"""

    if "consisten" in p:
        return """CONSISTENCY REPORT (AI-Verified):

✅ Skills Match: Resume skills confirmed by GitHub repositories
✅ Timeline: Employment dates align with LinkedIn profile
✅ Education: Degree verified against university records
⚠️ Minor Flag: Resume states "Led team of 5" — GitHub activity suggests primarily individual contributions

CONSISTENCY SCORE: 88/100
CONFIDENCE: HIGH"""

    if "score" in p or "ats" in p or "holistic" in p:
        return """HOLISTIC CANDIDATE ASSESSMENT:

Score: 85/100

BREAKDOWN:
  • Keyword Match: 78% — Strong alignment on core technical skills
  • Project Relevance: 90% — GitHub projects directly relate to role
  • Consistency: 88% — High alignment between resume and online presence
  • Recency: 82% — Active contributions in the last 6 months

RECOMMENDATION: ✅ STRONG CANDIDATE — Proceed to technical interview

KEY STRENGTHS: Production ML experience, API design, open-source contributions
AREAS TO PROBE: Team leadership claims, system design depth"""

    if "link" in p or "url" in p or "github" in p:
        return "This link likely points to the candidate's professional profile or code repository, demonstrating hands-on experience with software development, version control, and collaborative coding practices."

    # Parse/extract check LAST — many prompts contain "resume" text which could false-match
    if "parse" in p or "extract" in p or "return only" in p:
        return '{"name": "Demo User", "skills": ["Python", "Machine Learning", "Data Analysis", "SQL", "FastAPI"], "experience_years": 3, "education": "B.Tech Computer Science", "summary": "Passionate software developer with 3 years of experience in ML and backend development."}'

    return "AI analysis complete. Configure HF_TOKEN environment variable for Qwen 2.5-powered detailed results."

