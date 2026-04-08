"""
RL Trainer — handles pre-training and online learning for policy networks.
Uses Experience Replay and gradient descent with PyTorch.
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os

from rl.policy_networks import JobMatcherNetwork, CandidateScorerNetwork, ResumeOptimizerNetwork, STATE_DIM
from rl.replay_buffer import ReplayBuffer


class RLTrainer:
    """
    Manages training of all RL policy networks.
    - Pre-trains with simulated episodes on startup
    - Online-trains from live user feedback
    """

    MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")

    def __init__(self):
        # Initialize networks
        self.job_matcher = JobMatcherNetwork(state_dim=STATE_DIM)
        self.candidate_scorer = CandidateScorerNetwork(state_dim=STATE_DIM)
        self.resume_optimizer = ResumeOptimizerNetwork(state_dim=STATE_DIM)

        # Optimizers
        self.jm_optimizer = optim.Adam(self.job_matcher.parameters(), lr=1e-3)
        self.cs_optimizer = optim.Adam(self.candidate_scorer.parameters(), lr=1e-3)
        self.ro_optimizer = optim.Adam(self.resume_optimizer.parameters(), lr=1e-3)

        # Replay buffers
        self.jm_buffer = ReplayBuffer(capacity=5000)
        self.cs_buffer = ReplayBuffer(capacity=5000)

        # Training stats
        self.training_history = {
            "jm_losses": [],
            "cs_losses": [],
            "episodes_trained": 0,
        }

        # Try to load pre-trained weights
        self._load_models()

    def pretrain(self, rl_env, num_episodes: int = 200):
        """
        Pre-train policy networks using simulated episodes.
        Called once on startup.
        """
        print(f"[RLTrainer] Pre-training with {num_episodes} simulated episodes...")

        # Get data from environment
        all_jobs = rl_env.openenv.get_all_jobs()
        if not all_jobs:
            print("[RLTrainer] No jobs available for pre-training.")
            return

        # Create diverse simulated user profiles
        sim_profiles = [
            {"skills": ["Python", "Machine Learning", "Docker", "SQL", "FastAPI"], "experience_years": 3},
            {"skills": ["React", "JavaScript", "TypeScript", "CSS", "Node.js"], "experience_years": 2},
            {"skills": ["Python", "TensorFlow", "Statistics", "Data Visualization", "Pandas"], "experience_years": 4},
            {"skills": ["Java", "Spring Boot", "Kafka", "PostgreSQL", "Microservices"], "experience_years": 5},
            {"skills": ["AWS", "Terraform", "Docker", "Kubernetes", "CI/CD", "Linux"], "experience_years": 4},
            {"skills": ["Python", "PyTorch", "NLP", "Transformers", "Research"], "experience_years": 3},
            {"skills": ["SQL", "Excel", "Python", "Data Visualization", "Communication"], "experience_years": 1},
            {"skills": ["React", "Figma", "CSS", "JavaScript", "Accessibility"], "experience_years": 2},
            {"skills": ["Python", "Computer Vision", "CUDA", "MLOps", "PyTorch"], "experience_years": 4},
            {"skills": ["Product Management", "Agile", "Data Analysis", "Communication"], "experience_years": 5},
        ]

        for ep in range(num_episodes):
            profile = sim_profiles[ep % len(sim_profiles)]
            transitions = rl_env.simulate_episode(profile, all_jobs, self.job_matcher)

            for state, action, reward, next_state, done in transitions:
                self.jm_buffer.push(state, action, reward, next_state, done)
                self.cs_buffer.push(state, action, reward, next_state, done)

            # Train every 10 episodes
            if (ep + 1) % 10 == 0 and self.jm_buffer.is_ready(32):
                jm_loss = self._train_job_matcher(batch_size=32)
                cs_loss = self._train_candidate_scorer(batch_size=32)
                self.training_history["jm_losses"].append(jm_loss)
                self.training_history["cs_losses"].append(cs_loss)

        self.training_history["episodes_trained"] += num_episodes
        self._save_models()
        print(f"[RLTrainer] Pre-training complete. Buffer size: {len(self.jm_buffer)}")

    def train_step_from_feedback(self, state: np.ndarray, action: float,
                                 reward: float, next_state: np.ndarray,
                                 network_type: str = "job_matcher"):
        """
        Online learning: train from a single user feedback interaction.
        """
        if network_type == "job_matcher":
            self.jm_buffer.push(state, action, reward, next_state)
            if self.jm_buffer.is_ready(16):
                loss = self._train_job_matcher(batch_size=16)
                self.training_history["jm_losses"].append(loss)
                return loss
        elif network_type == "candidate_scorer":
            self.cs_buffer.push(state, action, reward, next_state)
            if self.cs_buffer.is_ready(16):
                loss = self._train_candidate_scorer(batch_size=16)
                self.training_history["cs_losses"].append(loss)
                return loss
        return None

    def _train_job_matcher(self, batch_size: int = 32) -> float:
        """Train the job matcher network using Actor-Critic loss."""
        self.job_matcher.train()
        states, actions, rewards, next_states, dones = self.jm_buffer.sample_tensors(batch_size)

        # Forward pass
        scores, values = self.job_matcher(states)
        _, next_values = self.job_matcher(next_states)

        # Advantage = reward + gamma * next_value - current_value
        gamma = 0.95
        targets = rewards.unsqueeze(1) + gamma * next_values * (1 - dones.unsqueeze(1))
        advantages = targets - values

        # Actor loss: encourage actions that lead to positive advantage
        actor_loss = -(scores * advantages.detach()).mean()

        # Critic loss: MSE between predicted value and target
        critic_loss = nn.MSELoss()(values, targets.detach())

        # Combined loss
        loss = actor_loss + 0.5 * critic_loss

        self.jm_optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.job_matcher.parameters(), 1.0)
        self.jm_optimizer.step()

        return round(float(loss.item()), 4)

    def _train_candidate_scorer(self, batch_size: int = 32) -> float:
        """Train the candidate scorer using DQN loss."""
        self.candidate_scorer.train()
        states, actions, rewards, next_states, dones = self.cs_buffer.sample_tensors(batch_size)

        # Current Q-values
        current_q = self.candidate_scorer(states)

        # Target Q-values (simple DQN, no target network for simplicity)
        gamma = 0.95
        with torch.no_grad():
            next_q = self.candidate_scorer(next_states)
            target_q = rewards.unsqueeze(1) + gamma * next_q * (1 - dones.unsqueeze(1))

        # Normalize target to [0, 100]
        target_q = torch.clamp(target_q, 0, 100)

        loss = nn.SmoothL1Loss()(current_q, target_q)

        self.cs_optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.candidate_scorer.parameters(), 1.0)
        self.cs_optimizer.step()

        return round(float(loss.item()), 4)

    def _save_models(self):
        """Save trained model weights."""
        os.makedirs(self.MODEL_DIR, exist_ok=True)
        try:
            torch.save(self.job_matcher.state_dict(), os.path.join(self.MODEL_DIR, "job_matcher.pt"))
            torch.save(self.candidate_scorer.state_dict(), os.path.join(self.MODEL_DIR, "candidate_scorer.pt"))
            torch.save(self.resume_optimizer.state_dict(), os.path.join(self.MODEL_DIR, "resume_optimizer.pt"))
            print("[RLTrainer] Models saved.")
        except Exception as e:
            print(f"[RLTrainer] Could not save models: {e}")

    def _load_models(self):
        """Load pre-trained weights if they exist."""
        try:
            jm_path = os.path.join(self.MODEL_DIR, "job_matcher.pt")
            cs_path = os.path.join(self.MODEL_DIR, "candidate_scorer.pt")
            ro_path = os.path.join(self.MODEL_DIR, "resume_optimizer.pt")

            if os.path.exists(jm_path):
                self.job_matcher.load_state_dict(torch.load(jm_path, map_location="cpu", weights_only=True))
                print("[RLTrainer] Loaded job_matcher weights.")
            if os.path.exists(cs_path):
                self.candidate_scorer.load_state_dict(torch.load(cs_path, map_location="cpu", weights_only=True))
                print("[RLTrainer] Loaded candidate_scorer weights.")
            if os.path.exists(ro_path):
                self.resume_optimizer.load_state_dict(torch.load(ro_path, map_location="cpu", weights_only=True))
                print("[RLTrainer] Loaded resume_optimizer weights.")
        except Exception as e:
            print(f"[RLTrainer] Could not load models (starting fresh): {e}")

    def get_stats(self) -> dict:
        """Return training stats for the dashboard."""
        return {
            "episodes_trained": self.training_history["episodes_trained"],
            "jm_losses": self.training_history["jm_losses"][-50:],
            "cs_losses": self.training_history["cs_losses"][-50:],
            "jm_buffer_size": len(self.jm_buffer),
            "cs_buffer_size": len(self.cs_buffer),
            "jm_buffer_stats": self.jm_buffer.get_stats(),
            "cs_buffer_stats": self.cs_buffer.get_stats(),
            "jm_params": sum(p.numel() for p in self.job_matcher.parameters()),
            "cs_params": sum(p.numel() for p in self.candidate_scorer.parameters()),
            "ro_params": sum(p.numel() for p in self.resume_optimizer.parameters()),
        }
