"""
Experience Replay Buffer for RL training.
Stores (state, action, reward, next_state, done) transitions.
"""
import numpy as np
import random
from collections import deque


class ReplayBuffer:
    """Fixed-size experience replay buffer with uniform sampling."""

    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state: np.ndarray, action: float, reward: float,
             next_state: np.ndarray, done: bool = False):
        """Store a transition."""
        self.buffer.append({
            "state": state.copy(),
            "action": action,
            "reward": reward,
            "next_state": next_state.copy(),
            "done": done,
        })

    def sample(self, batch_size: int) -> list[dict]:
        """Sample a random batch of transitions."""
        batch_size = min(batch_size, len(self.buffer))
        return random.sample(list(self.buffer), batch_size)

    def sample_tensors(self, batch_size: int):
        """Sample and return as numpy arrays ready for PyTorch."""
        import torch

        batch = self.sample(batch_size)
        states = np.array([t["state"] for t in batch])
        actions = np.array([t["action"] for t in batch])
        rewards = np.array([t["reward"] for t in batch])
        next_states = np.array([t["next_state"] for t in batch])
        dones = np.array([t["done"] for t in batch], dtype=np.float32)

        return (
            torch.FloatTensor(states),
            torch.FloatTensor(actions),
            torch.FloatTensor(rewards),
            torch.FloatTensor(next_states),
            torch.FloatTensor(dones),
        )

    def __len__(self):
        return len(self.buffer)

    def is_ready(self, min_size: int = 64) -> bool:
        """Check if buffer has enough samples for training."""
        return len(self.buffer) >= min_size

    def get_stats(self) -> dict:
        """Return summary statistics of the buffer."""
        if not self.buffer:
            return {"size": 0, "avg_reward": 0, "max_reward": 0, "min_reward": 0}

        rewards = [t["reward"] for t in self.buffer]
        return {
            "size": len(self.buffer),
            "avg_reward": round(np.mean(rewards), 3),
            "max_reward": round(np.max(rewards), 3),
            "min_reward": round(np.min(rewards), 3),
        }
