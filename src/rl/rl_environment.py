"""
RL Environment wrapper over OpenEnv.
Implements a Gymnasium-like interface: reset(), step(), observe().
Provides state vectors and reward signals for the RL policy networks.
"""
import numpy as np
from rl.policy_networks import encode_skills, encode_state, STATE_DIM


class RLEnvironment:
    """
    Wraps the OpenEnv Environment as an RL environment.

    The RL loop:
      1. Agent observes state (user profile + available jobs)
      2. Agent takes action (recommend a job / score a candidate)
      3. Environment returns reward based on user feedback
      4. Transition stored in replay buffer for training
    """

    def __init__(self, openenv):
        self.openenv = openenv
        self.state_dim = STATE_DIM
        self.current_user = None
        self.current_job = None
        self._episode_rewards = []
        self._total_episodes = 0
        self._reward_history = []  # tracks avg reward per episode

    def reset(self, user_email: str = None):
        """Reset the environment for a new episode."""
        self.current_user = user_email
        self.current_job = None
        self._episode_rewards = []
        self._total_episodes += 1
        return self.observe()

    def observe(self) -> np.ndarray:
        """Return the current state vector."""
        if self.current_user:
            profile = self.openenv.get_profile(self.current_user)
            if profile:
                return encode_skills(profile.get("skills", []))
        return np.zeros(len(encode_skills([])), dtype=np.float32)

    def get_state_for_job(self, user_email: str, job_id: str) -> np.ndarray:
        """Get a full state vector for a (user, job) pair."""
        profile = self.openenv.get_profile(user_email) or {}
        job = self.openenv.get_job(job_id) or {}

        user_skills = profile.get("skills", [])
        job_skills = job.get("requirements", {}).get("skills", [])
        experience = profile.get("experience_years", 0)

        return encode_state(user_skills, job_skills, experience)

    def step(self, action: str, feedback_type: str = "click") -> tuple:
        """
        Take an action and return (next_state, reward, done, info).

        Actions:
            - For job matching: action = job_id recommended
            - For candidate scoring: action = score given

        Feedback types and rewards:
            - "click"     → +1.0  (user clicked on recommended job)
            - "apply"     → +5.0  (user applied)
            - "interview" → +8.0  (got interview)
            - "hire"      → +10.0 (got hired)
            - "skip"      → -0.5  (user skipped)
            - "reject"    → -1.0  (recruiter rejected)
            - "star"      → +3.0  (recruiter starred candidate)
        """
        reward_map = {
            "click": 1.0,
            "apply": 5.0,
            "interview": 8.0,
            "hire": 10.0,
            "skip": -0.5,
            "reject": -1.0,
            "star": 3.0,
            "view": 0.5,
            "save": 2.0,
        }
        reward = reward_map.get(feedback_type, 0.0)
        self._episode_rewards.append(reward)

        # Store feedback in OpenEnv
        self.openenv.record_feedback(
            user_id=self.current_user or "unknown",
            action=str(action),
            feedback_type=feedback_type,
            reward=reward
        )

        next_state = self.observe()
        done = False
        info = {"feedback": feedback_type, "reward": reward}

        return next_state, reward, done, info

    def end_episode(self):
        """End the current episode and log stats."""
        if self._episode_rewards:
            avg = np.mean(self._episode_rewards)
            self._reward_history.append(avg)

    def get_stats(self) -> dict:
        """Return RL training statistics."""
        return {
            "total_episodes": self._total_episodes,
            "reward_history": self._reward_history[-100:],  # last 100 episodes
            "avg_reward": round(np.mean(self._reward_history[-50:]), 3) if self._reward_history else 0,
            "total_interactions": sum(len(r) for r in [self._episode_rewards]),
        }

    def simulate_episode(self, user_profile: dict, jobs: list, policy_network) -> list:
        """
        Simulate an episode for pre-training.
        Uses rule-based rewards to generate training data.

        Returns: list of (state, action_score, reward) transitions
        """
        transitions = []
        user_skills = set(s.lower() for s in user_profile.get("skills", []))

        for job in jobs:
            job_skills = set(s.lower() for s in job.get("requirements", {}).get("skills", []))
            overlap = len(user_skills & job_skills)
            total = max(len(job_skills), 1)

            # State
            state = encode_state(
                list(user_profile.get("skills", [])),
                list(job.get("requirements", {}).get("skills", [])),
                user_profile.get("experience_years", 0)
            )

            # Simulated reward based on skill overlap
            match_ratio = overlap / total
            if match_ratio >= 0.6:
                reward = np.random.choice([5.0, 8.0, 10.0], p=[0.5, 0.3, 0.2])  # likely apply/interview/hire
            elif match_ratio >= 0.3:
                reward = np.random.choice([1.0, 5.0, -0.5], p=[0.4, 0.3, 0.3])  # click/apply/skip
            else:
                reward = np.random.choice([-0.5, -1.0, 1.0], p=[0.5, 0.3, 0.2])  # mostly skip/reject

            transitions.append((state, match_ratio, reward, state, False))

        return transitions
