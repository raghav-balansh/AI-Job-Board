import re
from typing import Dict, Any, List


class ResumeLinkExtractorAgent:
    
    def __init__(self, env):
        self.env = env

    def extract(self, resume_text: str) -> List[str]:
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        links = re.findall(url_pattern, resume_text)
        unique_links = list(set(links))

        self.env.publish_event("ResumeLinkExtractorAgent", "LinksExtracted", {
            "count": len(unique_links)
        })
        return unique_links if unique_links else [
            "https://github.com/candidate",
            "https://linkedin.com/in/candidate"
        ]


class LinkContentAnalyzerAgent:
    
    def __init__(self, env):
        self.env = env

    def analyze(self, links: List[str]) -> Dict[str, str]:
        from llm_client import llm_generate

        summaries = {}
        for link in links[:5]:
            prompt = f"""Given this URL from a candidate's resume: {link}
Describe what type of content this likely contains and what it reveals about the candidate's skills and experience.
Be concise  in 2-3 sentences only."""

            summary = llm_generate(prompt, max_tokens=150)
            summaries[link] = summary

        self.env.publish_event("LinkContentAnalyzerAgent", "LinksAnalyzed", {
            "count": len(summaries)
        })
        return summaries


class ConsistencyCheckerAgent:
    """Cross-validates resume claims against link content using Qwen 2.5."""

    def __init__(self, env):
        self.env = env

    def check(self, profile_id: str, resume_text: str, link_summaries: Dict[str, str]) -> Dict[str, Any]:
        from llm_client import llm_generate

        profile = self.env.get_profile(profile_id)
        links_context = "\n".join([f"- {url}: {summary}" for url, summary in link_summaries.items()])

        prompt = f"""Cross-validate this candidate's resume claims against their online presence.

RESUME CLAIMS:
{resume_text[:1000]}

PROFILE DATA:
Skills: {', '.join(profile.get('skills', [])) if profile else 'N/A'}
Experience: {profile.get('experience_years', 'N/A') if profile else 'N/A'} years

ONLINE PRESENCE:
{links_context}

Provide:
1. Consistency score (0-100)
2. What matches well
3. Any discrepancies or red flags
4. Overall assessment

Be structured and concise."""

        report = llm_generate(prompt, max_tokens=400)

        score_match = re.search(r'(\d{1,3})(?:/100|%)', report)
        score = int(score_match.group(1)) if score_match else 85

        self.env.publish_event("ConsistencyCheckerAgent", "ConsistencyChecked", {
            "profile_id": profile_id, "score": score
        })

        return {"score": min(score, 100), "report": report}


class EnhancedATSScorerAgent:
   

    def __init__(self, env, rl_trainer=None):
        self.env = env
        self.rl_trainer = rl_trainer

    def score(self, profile_id: str, job_id: str, consistency_data: Dict[str, Any]) -> Dict[str, Any]:
        from llm_client import llm_generate

        profile = self.env.get_profile(profile_id)
        job = self.env.get_job(job_id)

        if not profile or not job:
            return {"score": 0, "breakdown": "Missing data", "recommendation": "N/A", "method": "error"}

        user_skills = set(s.lower() for s in profile.get("skills", []))
        job_skills = set(s.lower() for s in job.get("requirements", {}).get("skills", []))
        keyword_score = int(100 * len(user_skills & job_skills) / max(len(job_skills), 1))
        consistency_score = consistency_data.get("score", 80)

        # ── RL-based scoring ──
        rl_score = None
        method = "Heuristic"
        if self.rl_trainer is not None:
            try:
                rl_score = self.rl_trainer.candidate_scorer.score_candidate(
                    list(profile.get("skills", [])),
                    list(job.get("requirements", {}).get("skills", [])),
                    profile.get("experience_years", 0)
                )
                method = "DQN RL Policy"
            except Exception as e:
                print(f"[EnhancedATSScorerAgent] RL fallback: {e}")

        # Compute final score
        if rl_score is not None:
            final_score = int(0.35 * rl_score + 0.30 * keyword_score + 0.20 * consistency_score + 0.15 * 80)
        else:
            final_score = int(0.40 * keyword_score + 0.30 * consistency_score + 0.30 * 80)

        # LLM analysis
        prompt = f"""Score this candidate holistically for the job position.

CANDIDATE: {profile.get('name', 'N/A')}
Skills: {', '.join(profile.get('skills', []))}
Experience: {profile.get('experience_years', 'N/A')} years

JOB: {job.get('title')} at {job.get('company')}
Required Skills: {', '.join(job.get('requirements', {}).get('skills', []))}

COMPUTED SCORES:
- Keyword Match: {keyword_score}%
- Consistency Score: {consistency_score}/100
{f'- RL Policy Score: {rl_score:.1f}/100' if rl_score else ''}

Provide a brief analysis with strengths, weaknesses, and a recommendation (STRONG CANDIDATE / GOOD FIT / NEEDS REVIEW / NOT RECOMMENDED)."""

        analysis = llm_generate(prompt, max_tokens=300)

        self.env.publish_event("EnhancedATSScorerAgent", "CandidateScored", {
            "profile_id": profile_id, "job_id": job_id,
            "score": final_score, "method": method
        })

        return {
            "score": final_score,
            "keyword_score": keyword_score,
            "consistency_score": consistency_score,
            "rl_score": rl_score,
            "analysis": analysis,
            "method": method,
        }
