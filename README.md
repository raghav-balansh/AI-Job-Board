---
title: AI Job Dashboard — RL + Qwen 2.5 + OpenEnv
emoji: 🤝
colorFrom: balck -grey platte
colorTo: black
sdk: streamlit
sdk_version: 1.45.1
app_file: app.py
pinned: false
license: apache 2.0

#  AI Job Dashboard — Reinforcement Learning + Qwen 2.5 + OpenEnv

A **reinforcement learning-powered** job dashboard built with **PyTorch** policy networks, **Qwen 2.5** for text generation, and **OpenEnv** multi-agent collaboration.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                   │
│  (Job Seeker View  |  Recruiter View  |  RL Dashboard)  │
├─────────────────────────────────────────────────────────┤
│                  RL Policy Networks (PyTorch)            │
│  JobMatcherNN (Actor-Critic)  |  CandidateScorerNN (DQN)│
├─────────────────────────────────────────────────────────┤
│               Qwen 2.5 (HF Inference API)               │
│  Resume Tailoring  |  Cover Letters  |  Analysis         │
├─────────────────────────────────────────────────────────┤
│                OpenEnv (RL Environment)                  │
│  State Manager  |  Reward Calculator  |  Replay Buffer   │
├─────────────────────────────────────────────────────────┤
│                   SQLite + SQLAlchemy                    │
└─────────────────────────────────────────────────────────┘
```

## Key Features
- **RL-based Job Matching** — Policy network learns from user feedback to rank jobs better over time
- **RL-based Candidate Scoring** — DQN learns optimal scoring from recruiter interactions
- **Qwen 2.5 Text Generation** — AI-powered resume tailoring, cover letters, and skill gap analysis
- **OpenEnv Integration** — Shared environment for agent communication, state management, and reward signals
- **Live RL Training Dashboard** — Watch the policy improve in real-time

## Demo Accounts
| Role | Email | Password |
|------|-------|----------|
| Job Seeker | `seeker@demo.com` | `demo123` |
| Recruiter | `recruiter@demo.com` | `demo123` |

## Tech Stack
- **RL Engine**: PyTorch (Actor-Critic, DQN)
- **LLM**: Qwen 2.5-7B-Instruct (HF Inference API, free)
- **UI**: Streamlit + Custom Glassmorphism CSS
- **Environment**: OpenEnv (custom RL environment)
- **Database**: SQLAlchemy + SQLite
