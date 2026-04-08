"""
Job Seeker Agents — RL-powered + Qwen 2.5.

- JobMatcherAgent uses the PyTorch Actor-Critic policy network for ranking
- ResumeTailorAgent uses ResumeOptimizer NN + Qwen 2.5 for text generation
- ProfileParserAgent / CoverLetterWriter / SkillGapAnalyzer use Qwen 2.5
- All agents record interactions for RL training via OpenEnv
"""
import json
import re
from typing import Dict, Any


class ProfileParserAgent:
    """Extracts structured profile data from raw resume text using Qwen 2.5."""

    def __init__(self, env):
        self.env = env

    def parse(self, raw_text: str, profile_id: str) -> Dict[str, Any]:
        from llm_client import llm_generate

        prompt = f"""Extract structured information from this resume text. Return ONLY valid JSON with these fields:
- "name": full name
- "skills": list of technical/professional skills
- "experience_years": integer
- "education": highest degree
- "summary": 2-sentence professional summary

Resume text:
---
{raw_text[:2000]}
---

Return ONLY the JSON object, no other text."""

        response = llm_generate(prompt, max_tokens=400)

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                structured_data = json.loads(json_match.group())
            else:
                structured_data = json.loads(response)
        except (json.JSONDecodeError, Exception):
            structured_data = {
                "name": profile_id.split("@")[0].replace(".", " ").title(),
                "skills": ["Python", "Data Analysis"],
                "experience_years": 2,
                "education": "Not specified",
                "summary": raw_text[:200]
            }

        self.env.store_profile(profile_id, structured_data)
        self.env.publish_event("ProfileParserAgent", "ProfileParsed", {"profile_id": profile_id})
        return structured_data


class JobMatcherAgent:
    """
    RL-POWERED job matching using Actor-Critic policy network.
    The PyTorch network learns to rank jobs based on user feedback over time.
    Falls back to keyword matching if RL trainer is not available.
    """

    def __init__(self, env, rl_trainer=None):
        self.env = env
        self.rl_trainer = rl_trainer

    def match_jobs(self, profile_id: str) -> list:
        profile = self.env.get_profile(profile_id)
        if not profile:
            return []

        all_jobs = self.env.get_all_jobs(status_filter="Active")

        # ── RL-based ranking ──
        if self.rl_trainer is not None:
            try:
                user_skills = profile.get("skills", [])
                exp = profile.get("experience_years", 0)
                ranked = self.rl_trainer.job_matcher.rank_jobs(user_skills, all_jobs, exp)
                matched_ids = [jid for jid, score in ranked if score > 0]

                self.env.publish_event("JobMatcherAgent", "JobsMatched_RL", {
                    "profile_id": profile_id, "matched_count": len(matched_ids),
                    "method": "Actor-Critic RL Policy"
                })
                if matched_ids:
                    return matched_ids
            except Exception as e:
                print(f"[JobMatcherAgent] RL fallback: {e}")

        # ── Keyword fallback ──
        user_skills = set(s.lower() for s in profile.get("skills", []))
        scored = []
        for job in all_jobs:
            job_skills = set(s.lower() for s in job["requirements"].get("skills", []))
            overlap = user_skills.intersection(job_skills)
            if overlap:
                scored.append((job["id"], len(overlap) / max(len(job_skills), 1)))

        scored.sort(key=lambda x: x[1], reverse=True)
        matched_ids = [jid for jid, _ in scored]

        self.env.publish_event("JobMatcherAgent", "JobsMatched_Keyword", {
            "profile_id": profile_id, "matched_count": len(matched_ids),
            "method": "Keyword Fallback"
        })
        return matched_ids


class ResumeTailorAgent:
    """
    Generates tailored resumes using:
    1. ResumeOptimizer NN (RL) → decides which sections to emphasize
    2. Qwen 2.5 → generates the actual text
    """

    def __init__(self, env, rl_trainer=None):
        self.env = env
        self.rl_trainer = rl_trainer

    def tailor(self, profile_id: str, job_id: str) -> str:
        from llm_client import llm_generate

        profile = self.env.get_profile(profile_id)
        job = self.env.get_job(job_id)
        if not profile or not job:
            return "Error: profile or job not found."

        # Get RL-optimized section emphasis
        emphasis_info = ""
        if self.rl_trainer is not None:
            try:
                emphasis = self.rl_trainer.resume_optimizer.get_emphasis(
                    profile.get("skills", []),
                    job.get("requirements", {}).get("skills", []),
                    profile.get("experience_years", 0)
                )
                top_sections = sorted(emphasis.items(), key=lambda x: x[1], reverse=True)[:3]
                emphasis_info = f"\n\nRL OPTIMIZATION: Emphasize these sections most: {', '.join([s[0] for s in top_sections])} (weights: {dict(top_sections)})"
            except Exception:
                pass

        prompt = f"""Rewrite this candidate's resume optimized for the target job posting.
Highlight relevant skills and experience. Keep it truthful but compelling.

CANDIDATE PROFILE:
Name: {profile.get('name', 'N/A')}
Skills: {', '.join(profile.get('skills', []))}
Experience: {profile.get('experience_years', 'N/A')} years
Education: {profile.get('education', 'N/A')}
Summary: {profile.get('summary', 'N/A')}

TARGET JOB:
Title: {job.get('title')} at {job.get('company')}
Description: {job.get('description')}
Required Skills: {', '.join(job.get('requirements', {}).get('skills', []))}
{emphasis_info}

Write a tailored, professional resume (max 300 words)."""

        result = llm_generate(prompt, max_tokens=500)
        self.env.publish_event("ResumeTailorAgent", "ResumeTailored", {
            "profile_id": profile_id, "job_id": job_id, "method": "RL+Qwen2.5"
        })
        return result


class CoverLetterWriterAgent:
    """Generates cover letters using Qwen 2.5."""

    def __init__(self, env):
        self.env = env

    def write(self, profile_id: str, job_id: str) -> str:
        from llm_client import llm_generate

        profile = self.env.get_profile(profile_id)
        job = self.env.get_job(job_id)
        if not profile or not job:
            return "Error: profile or job not found."

        prompt = f"""Write a compelling, professional cover letter for this candidate.

CANDIDATE:
Name: {profile.get('name', 'N/A')}
Skills: {', '.join(profile.get('skills', []))}
Experience: {profile.get('experience_years', 'N/A')} years
Summary: {profile.get('summary', 'N/A')}

JOB:
Title: {job.get('title')} at {job.get('company')}
Description: {job.get('description')}

Write a professional cover letter (max 250 words). Reference the company and role specifically."""

        result = llm_generate(prompt, max_tokens=400)
        self.env.publish_event("CoverLetterWriterAgent", "CoverLetterWritten", {
            "profile_id": profile_id, "job_id": job_id
        })
        return result


class SkillGapAnalyzerAgent:
    """Identifies skill gaps using Qwen 2.5."""

    def __init__(self, env):
        self.env = env

    def analyze(self, profile_id: str, job_id: str) -> str:
        from llm_client import llm_generate

        profile = self.env.get_profile(profile_id)
        job = self.env.get_job(job_id)
        if not profile or not job:
            return "Error: profile or job not found."

        prompt = f"""Analyze the skill gap between this candidate and job requirements.

CANDIDATE SKILLS: {', '.join(profile.get('skills', []))}
JOB REQUIRED SKILLS: {', '.join(job.get('requirements', {}).get('skills', []))}

Provide:
1. Skills the candidate already has that match
2. Skills the candidate is missing
3. For each missing skill, recommend ONE free/affordable course or resource
4. Overall match percentage

Be concise and structured."""

        result = llm_generate(prompt, max_tokens=400)
        self.env.publish_event("SkillGapAnalyzerAgent", "SkillGapAnalyzed", {
            "profile_id": profile_id, "job_id": job_id
        })
        return result


class AutoApplyAgent:
    """Submits tailored documents as an application."""

    def __init__(self, env):
        self.env = env

    def apply(self, profile_id: str, job_id: str, documents: dict):
        app_id = self.env.store_application(profile_id, job_id, "Applied", documents)
        self.env.publish_event("AutoApplyAgent", "ApplicationSubmitted", {
            "profile_id": profile_id, "job_id": job_id, "app_id": app_id
        })
        return app_id
