import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


SKILL_VOCAB = [
    "python", "java", "javascript", "typescript", "react", "node.js",
    "sql", "postgresql", "mongodb", "redis", "docker", "kubernetes",
    "aws", "gcp", "azure", "terraform", "ci/cd", "linux",
    "machine learning", "deep learning", "pytorch", "tensorflow",
    "nlp", "computer vision", "data analysis", "data visualization",
    "statistics", "pandas", "numpy", "scikit-learn",
    "fastapi", "django", "flask", "spring boot",
    "git", "agile", "communication", "leadership",
    "system design", "microservices", "graphql", "rest api",
    "security", "devops", "mlops", "figma", "css",
    "research", "transformers", "cuda", "kafka",
    "excel", "product management", "accessibility",
]
SKILL_TO_IDX = {s: i for i, s in enumerate(SKILL_VOCAB)}
VOCAB_SIZE = len(SKILL_VOCAB)


SKILL_DIM = VOCAB_SIZE        # binary skill vector
EXTRA_FEATURES = 4            # experience_years, education_level, job_type_encoded, salary_encoded
STATE_DIM = SKILL_DIM * 2 + EXTRA_FEATURES  # user skills + job skills + extras


def encode_skills(skills: list[str]) -> np.ndarray:
    vec = np.zeros(VOCAB_SIZE, dtype=np.float32)
    for s in skills:
        idx = SKILL_TO_IDX.get(s.lower().strip())
        if idx is not None:
            vec[idx] = 1.0
    return vec


def encode_state(user_skills: list[str], job_skills: list[str],
                 experience_years: int = 0, extra_features: list[float] = None) -> np.ndarray:
    """Encode a (user, job) pair into a state vector for the RL networks."""
    user_vec = encode_skills(user_skills)
    job_vec = encode_skills(job_skills)
    extras = np.array(extra_features or [experience_years / 10.0, 0.5, 0.5, 0.5], dtype=np.float32)
    return np.concatenate([user_vec, job_vec, extras])


# =====================================================================
#  1. JOB MATCHER NETWORK — Actor-Critic
# =====================================================================
class JobMatcherNetwork(nn.Module):
    """
    Actor-Critic network for job recommendation.
    - Actor: outputs a preference score for each (user, job) pair
    - Critic: estimates the value of the current state
    """

    def __init__(self, state_dim: int = STATE_DIM, hidden_dim: int = 128):
        super().__init__()
        # Shared feature extractor
        self.shared = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
        )
        # Actor head — outputs score for this (user, job) pair
        self.actor = nn.Sequential(
            nn.Linear(hidden_dim // 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1),  # single score
        )
        # Critic head — estimates state value
        self.critic = nn.Sequential(
            nn.Linear(hidden_dim // 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, state: torch.Tensor):
        """
        Args:
            state: (batch, STATE_DIM) tensor
        Returns:
            score: (batch, 1) — preference score for this job
            value: (batch, 1) — estimated value
        """
        features = self.shared(state)
        score = self.actor(features)
        value = self.critic(features)
        return score, value

    def rank_jobs(self, user_skills: list[str], jobs: list[dict],
                  experience_years: int = 0) -> list[tuple]:
        """
        Rank a list of jobs for this user.
        Returns: [(job_id, score), ...] sorted by score descending.
        """
        self.eval()
        scored = []
        with torch.no_grad():
            for job in jobs:
                job_skills = job.get("requirements", {}).get("skills", [])
                state = encode_state(user_skills, job_skills, experience_years)
                state_tensor = torch.FloatTensor(state).unsqueeze(0)
                score, _ = self.forward(state_tensor)
                scored.append((job["id"], float(score.item())))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored


# =====================================================================
#  2. CANDIDATE SCORER NETWORK — DQN
# =====================================================================
class CandidateScorerNetwork(nn.Module):
    """
    Deep Q-Network for candidate scoring.
    Maps a (candidate, job) state to a quality score (0-100).
    """

    def __init__(self, state_dim: int = STATE_DIM, hidden_dim: int = 96):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid(),  # output in [0, 1], multiply by 100 for score
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.network(state) * 100.0  # Scale to 0-100

    def score_candidate(self, candidate_skills: list[str], job_skills: list[str],
                        experience_years: int = 0) -> float:
        """Score a single candidate for a job. Returns 0-100."""
        self.eval()
        with torch.no_grad():
            state = encode_state(candidate_skills, job_skills, experience_years)
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            score = self.forward(state_tensor)
            return round(float(score.item()), 1)


# =====================================================================
#  3. RESUME OPTIMIZER NETWORK — Contextual Bandit
# =====================================================================
class ResumeOptimizerNetwork(nn.Module):
    """
    Contextual bandit for resume optimization.
    Given (profile, job), outputs importance weights for different resume sections.
    Sections: [summary, skills, experience, education, projects, certifications]
    """
    NUM_SECTIONS = 6
    SECTION_NAMES = ["summary", "skills", "experience", "education", "projects", "certifications"]

    def __init__(self, state_dim: int = STATE_DIM, hidden_dim: int = 64):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, self.NUM_SECTIONS),
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """Returns softmax weights over resume sections."""
        logits = self.network(state)
        return F.softmax(logits, dim=-1)

    def get_emphasis(self, user_skills: list[str], job_skills: list[str],
                     experience_years: int = 0) -> dict:
        """Get section emphasis weights for resume generation."""
        self.eval()
        with torch.no_grad():
            state = encode_state(user_skills, job_skills, experience_years)
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            weights = self.forward(state_tensor).squeeze().numpy()

        return {name: round(float(w), 3) for name, w in zip(self.SECTION_NAMES, weights)}
