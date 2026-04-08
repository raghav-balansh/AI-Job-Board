"""
AI-Powered Job Dashboard
Reinforcement Learning + Qwen 2.5 + OpenEnv
Main Streamlit Application
"""
import streamlit as st
import sys
import os
import uuid
import numpy as np

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from dotenv import load_dotenv
load_dotenv()

from openenv import Environment
from auth import init_auth_state, signup, login, logout, require_auth, get_current_user, get_user_role
from ui_components import (
    inject_custom_css, render_metric_card, render_job_card,
    render_status_badge, render_nav_bar, render_section_header, render_glass_card
)
from seed_data import seed_demo_data

st.set_page_config(
    page_title="AI Job Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()
init_auth_state()


@st.cache_resource
def init_system():
    """Initialize OpenEnv, RL Trainer, and RL Environment."""
    env = Environment()
    seed_demo_data(env)

    from rl.trainer import RLTrainer
    from rl.rl_environment import RLEnvironment

    trainer = RLTrainer()
    rl_env = RLEnvironment(env)

    if not trainer.jm_buffer.is_ready(32):
        trainer.pretrain(rl_env, num_episodes=200)

    return env, trainer, rl_env

env, rl_trainer, rl_env = init_system()


# =====================================================================
#  LANDING PAGE — Professional stacked-card login
# =====================================================================
def render_landing_page():
    # Use columns to center content
    _, center_col, _ = st.columns([1, 2, 1])

    with center_col:
        # Brand header
        st.markdown("""
        <div style="text-align:center; padding:60px 0 40px;">
            <div style="font-size:2.6rem; font-weight:900; color:#f8f9fa; letter-spacing:-0.5px; line-height:1.15; margin-bottom:12px;">
                AI-Powered Job Dashboard
            </div>
            <div style="font-size:0.95rem; color:#6c757d; font-weight:400; letter-spacing:0.3px; max-width:460px; margin:0 auto; line-height:1.6;">
                Reinforcement learning meets intelligent job matching.
                Smart ranking, AI-tailored resumes, and holistic candidate scoring.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Stacked card visual and Landing Page specific CSS
        st.markdown("""
        <style>
        /* Landing Page specific styles */
        div[data-testid="stTabs"] {
            position: relative;
            z-index: 2;
            background: #f8f9fa;
            border-radius: 16px;
            padding: 32px 36px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
            margin: 0 auto;
            max-width: 440px;
        }
        div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            border-bottom: 2px solid #e9ecef;
            margin-bottom: 16px;
        }
        div[data-testid="stTabs"] [data-baseweb="tab"] {
            color: #6c757d;
            font-size: 1.1rem;
            padding: 8px 16px;
        }
        div[data-testid="stTabs"] [aria-selected="true"] {
            color: #212529 !important;
            border-bottom: 2px solid #212529 !important;
            font-weight: 800;
        }
        div[data-testid="stForm"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            box-shadow: none !important;
        }
        .landing-stack-wrapper {
            position: relative;
            width: 100%;
            max-width: 440px;
            margin: 0 auto -20px;
        }
        .landing-stack-bg1 {
            position: absolute; top: 18px; left: 16px; right: -16px; bottom: -18px;
            background: #dee2e6; border-radius: 16px; transform: rotate(3deg); height: 440px;
        }
        .landing-stack-bg2 {
            position: absolute; top: 10px; left: 8px; right: -8px; bottom: -10px;
            background: #e9ecef; border-radius: 16px; transform: rotate(1.5deg); height: 440px;
        }
        /* Specific input label color for landing page */
        div[data-testid="stTabs"] .stTextInput label, div[data-testid="stTabs"] .stSelectbox label {
            color: #495057 !important;
            font-weight: 600 !important;
        }
        </style>
        
        <div class="landing-stack-wrapper">
            <div class="landing-stack-bg1"></div>
            <div class="landing-stack-bg2"></div>
        </div>
        """, unsafe_allow_html=True)

        # Streamlit tabs for Login / Sign Up
        tab_login, tab_signup = st.tabs(["Sign In", "Sign Up"])

        with tab_login:
            st.markdown("""<div style="font-size:1.4rem; font-weight:800; color:#212529; margin-bottom:16px; text-align:center;">
                Welcome Back
            </div>""", unsafe_allow_html=True)
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                if submitted and email and password:
                    success, msg = login(env, email, password)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("""<div style="text-align:center; margin-top:20px; font-size:0.8rem; color:#6c757d;">
                Demo accounts:<br><strong>seeker@demo.com</strong> / <strong>recruiter@demo.com</strong><br>password: <strong>demo123</strong>
            </div>""", unsafe_allow_html=True)

        with tab_signup:
            st.markdown("""<div style="font-size:1.4rem; font-weight:800; color:#212529; margin-bottom:16px; text-align:center;">
                Create Account
            </div>""", unsafe_allow_html=True)
            with st.form("signup_form"):
                new_name = st.text_input("Full Name", placeholder="John Doe")
                new_email = st.text_input("Email", placeholder="you@example.com", key="signup_email")
                new_password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="signup_pw")
                new_role = st.selectbox("Role", ["seeker", "recruiter"], format_func=lambda x: "Job Seeker" if x == "seeker" else "Recruiter")
                submitted = st.form_submit_button("Sign Up", use_container_width=True)
                if submitted and new_name and new_email and new_password:
                    if len(new_password) < 6:
                        st.warning("Password must be at least 6 characters.")
                    else:
                        success, msg = signup(env, new_email, new_password, new_name, new_role)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)


# =====================================================================
#  JOB SEEKER DASHBOARD
# =====================================================================
def render_seeker_dashboard():
    user = get_current_user()
    render_nav_bar(user["name"], "seeker")

    with st.sidebar:
        st.markdown(f"""<div style="text-align:center; padding:20px 0;">
            <div style="font-size:1.1rem; font-weight:700; color:#f8f9fa; margin-top:8px;">{user['name']}</div>
            <div style="font-size:0.82rem; color:#6c757d;">{user['email']}</div>
            <div style="margin-top:8px;"><span class="badge badge-active">RL-Powered</span></div>
        </div>""", unsafe_allow_html=True)
        st.divider()
        nav = st.radio("Navigation", [
            "Overview", "Job Board", "AI Resume Studio",
            "My Applications", "RL Training"
        ], label_visibility="collapsed")
        st.divider()
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

    # ── Overview ──
    if "Overview" in nav:
        render_section_header("Dashboard Overview", "Your RL-powered job search at a glance")
        apps = env.get_applications_by_user(user["email"])
        total = len(apps)
        interviews = sum(1 for a in apps if a["status"] == "Interview")
        offers = sum(1 for a in apps if a["status"] == "Offered")
        pending = sum(1 for a in apps if a["status"] in ("Applied", "Reviewed"))

        c1, c2, c3, c4 = st.columns(4)
        with c1: render_metric_card("Applications", total, "TOTAL")
        with c2: render_metric_card("Interviews", interviews, "ACTIVE")
        with c3: render_metric_card("Offers", offers, "WON")
        with c4: render_metric_card("Pending", pending, "QUEUE")

        st.markdown("<br>", unsafe_allow_html=True)

        stats = rl_trainer.get_stats()
        render_section_header("RL Engine Status", "")
        c1, c2, c3 = st.columns(3)
        with c1: render_metric_card("Episodes Trained", stats["episodes_trained"], "TRAINING")
        with c2: render_metric_card("Replay Buffer", stats["jm_buffer_size"], "MEMORY")
        with c3:
            total_params = stats["jm_params"] + stats["cs_params"] + stats["ro_params"]
            render_metric_card("Total NN Params", f"{total_params:,}", "NETWORK")

        st.markdown("<br>", unsafe_allow_html=True)
        render_section_header("Recent Applications", "")
        if apps:
            for app in apps[:5]:
                job = env.get_job(app["job_id"])
                if job:
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1: st.markdown(f"**{job['title']}** at *{job['company']}*")
                    with c2: st.markdown(f"Applied: {app['applied_date'][:10]}")
                    with c3: st.markdown(render_status_badge(app["status"]), unsafe_allow_html=True)
                    st.divider()
        else:
            st.info("No applications yet. Head to the Job Board.")

    # ── Job Board ──
    elif "Job Board" in nav:
        render_section_header("Job Board", "Jobs ranked by RL Actor-Critic policy network")

        c_s, c_t, c_l = st.columns([3, 1, 1])
        with c_s:
            search = st.text_input("Search", placeholder="Python, ML, Remote...", label_visibility="collapsed")
        with c_t:
            type_f = st.selectbox("Type", ["All", "Full-time", "Part-time", "Contract"], label_visibility="collapsed")
        with c_l:
            loc_f = st.selectbox("Location", ["All", "Remote", "San Francisco", "New York", "Seattle"], label_visibility="collapsed")

        profile = env.get_profile(user["email"])
        all_jobs = env.get_all_jobs(status_filter="Active")

        if profile and rl_trainer:
            try:
                ranked = rl_trainer.job_matcher.rank_jobs(
                    profile.get("skills", []), all_jobs, profile.get("experience_years", 0)
                )
                ranked_ids = [jid for jid, _ in ranked]
                job_map = {j["id"]: j for j in all_jobs}
                sorted_jobs = [job_map[jid] for jid in ranked_ids if jid in job_map]
                st.markdown('<div style="color:#adb5bd; font-size:0.78rem; margin-bottom:12px;">Ranked by RL Actor-Critic Policy Network</div>', unsafe_allow_html=True)
            except Exception:
                sorted_jobs = all_jobs
        else:
            sorted_jobs = all_jobs

        filtered = sorted_jobs
        if search:
            sl = search.lower()
            filtered = [j for j in filtered if sl in j["title"].lower() or sl in j["description"].lower() or
                        sl in j.get("company", "").lower() or
                        any(sl in s.lower() for s in j.get("requirements", {}).get("skills", []))]
        if type_f != "All":
            filtered = [j for j in filtered if j.get("job_type") == type_f]
        if loc_f != "All":
            filtered = [j for j in filtered if loc_f.lower() in j.get("location", "").lower()]

        st.markdown(f"<div style='color:#6c757d; font-size:0.82rem; margin-bottom:16px;'>Showing {len(filtered)} jobs</div>", unsafe_allow_html=True)

        user_apps = env.get_applications_by_user(user["email"])
        applied_jobs = [a["job_id"] for a in user_apps]

        for job in filtered:
            render_job_card(job)
            c1, c2, c3 = st.columns([1, 1, 3])
            with c1:
                if job["id"] in applied_jobs:
                    st.markdown(render_status_badge("Applied"), unsafe_allow_html=True)
                else:
                    if st.button("Apply", key=f"apply_{job['id']}"):
                        p = env.get_profile(user["email"])
                        if not p:
                            st.warning("Parse your resume in AI Studio first.")
                        else:
                            with st.spinner("RL agents tailoring your application..."):
                                from seeker_agents import ResumeTailorAgent, CoverLetterWriterAgent, AutoApplyAgent
                                tailor = ResumeTailorAgent(env, rl_trainer)
                                resume = tailor.tailor(user["email"], job["id"])
                                writer = CoverLetterWriterAgent(env)
                                cl = writer.write(user["email"], job["id"])
                                applier = AutoApplyAgent(env)
                                applier.apply(user["email"], job["id"], {"resume": resume, "cover_letter": cl})
                            st.success("Applied successfully.")
                            state = rl_env.get_state_for_job(user["email"], job["id"])
                            rl_trainer.train_step_from_feedback(state, 1.0, 5.0, state, "job_matcher")
                            st.rerun()
            with c2:
                col_up, col_down = st.columns(2)
                with col_up:
                    if st.button("Relevant", key=f"like_{job['id']}"):
                        state = rl_env.get_state_for_job(user["email"], job["id"])
                        rl_trainer.train_step_from_feedback(state, 1.0, 1.0, state, "job_matcher")
                        env.record_feedback(user["email"], job["id"], "click", 1.0)
                        st.toast("Feedback recorded. RL policy updated.")
                with col_down:
                    if st.button("Skip", key=f"skip_{job['id']}"):
                        state = rl_env.get_state_for_job(user["email"], job["id"])
                        rl_trainer.train_step_from_feedback(state, 0.0, -0.5, state, "job_matcher")
                        env.record_feedback(user["email"], job["id"], "skip", -0.5)
                        st.toast("Feedback recorded. RL policy updated.")

    # ── AI Resume Studio ──
    elif "AI Resume" in nav:
        render_section_header("AI Resume Studio", "RL-optimized section emphasis + Qwen 2.5 text generation")

        render_glass_card("""
            <div style="font-size:1rem; font-weight:700; color:#f8f9fa; margin-bottom:4px;">Step 1: Parse Your Resume</div>
            <div style="font-size:0.82rem; color:#6c757d;">ProfileParser agent + Qwen 2.5 extracts structured data from your resume text.</div>
        """)

        raw_resume = st.text_area("Paste resume text", height=160,
            placeholder="Paste your full resume text here...", label_visibility="collapsed")

        if st.button("Parse Resume", use_container_width=True):
            if raw_resume.strip():
                with st.spinner("Qwen 2.5 ProfileParser Agent analyzing..."):
                    from seeker_agents import ProfileParserAgent
                    parser = ProfileParserAgent(env)
                    parser.parse(raw_resume, user["email"])
                st.success("Profile parsed successfully.")
                st.rerun()
            else:
                st.warning("Paste your resume text first.")

        profile = env.get_profile(user["email"])
        if profile:
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                render_glass_card(f"""
                    <div style="font-size:1rem; font-weight:700; color:#f8f9fa; margin-bottom:12px;">Parsed Profile</div>
                    <div style="color:#adb5bd; font-size:0.88rem; line-height:1.8;">
                        <b>Name:</b> {profile.get('name', 'N/A')}<br>
                        <b>Experience:</b> {profile.get('experience_years', 'N/A')} years<br>
                        <b>Education:</b> {profile.get('education', 'N/A')}<br>
                        <b>Summary:</b> {profile.get('summary', 'N/A')[:200]}
                    </div>
                """)
            with c2:
                skills = profile.get("skills", [])
                skill_tags = "".join([f'<span class="skill-tag">{s}</span>' for s in skills])
                render_glass_card(f"""
                    <div style="font-size:1rem; font-weight:700; color:#f8f9fa; margin-bottom:12px;">Skills Detected</div>
                    <div class="job-tags">{skill_tags}</div>
                """)

            st.markdown("<br>", unsafe_allow_html=True)
            render_glass_card("""
                <div style="font-size:1rem; font-weight:700; color:#f8f9fa; margin-bottom:4px;">Step 2: RL-Powered Job Tools</div>
                <div style="font-size:0.82rem; color:#6c757d;">ResumeOptimizer NN decides emphasis weights, then Qwen 2.5 generates text.</div>
            """)

            jobs = env.get_all_jobs(status_filter="Active")
            job_opts = {f"{j['title']} -- {j['company']}": j["id"] for j in jobs}
            sel_label = st.selectbox("Target job", list(job_opts.keys()))
            sel_id = job_opts.get(sel_label, "")

            if rl_trainer and sel_id:
                job = env.get_job(sel_id)
                if job:
                    emphasis = rl_trainer.resume_optimizer.get_emphasis(
                        profile.get("skills", []),
                        job.get("requirements", {}).get("skills", []),
                        profile.get("experience_years", 0)
                    )
                    top = sorted(emphasis.items(), key=lambda x: x[1], reverse=True)
                    bars = " ".join([f"`{n}: {int(w*100)}%`" for n, w in top])
                    st.markdown(f"**RL Section Emphasis:** {bars}")

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("Tailor Resume", use_container_width=True):
                    with st.spinner("ResumeOptimizer NN + Qwen 2.5..."):
                        from seeker_agents import ResumeTailorAgent
                        t = ResumeTailorAgent(env, rl_trainer)
                        result = t.tailor(user["email"], sel_id)
                    st.markdown("### Tailored Resume")
                    st.code(result, language=None)
            with c2:
                if st.button("Cover Letter", use_container_width=True):
                    with st.spinner("Qwen 2.5 composing..."):
                        from seeker_agents import CoverLetterWriterAgent
                        w = CoverLetterWriterAgent(env)
                        result = w.write(user["email"], sel_id)
                    st.markdown("### Cover Letter")
                    st.code(result, language=None)
            with c3:
                if st.button("Skill Gap Analysis", use_container_width=True):
                    with st.spinner("Qwen 2.5 analyzing..."):
                        from seeker_agents import SkillGapAnalyzerAgent
                        a = SkillGapAnalyzerAgent(env)
                        result = a.analyze(user["email"], sel_id)
                    st.markdown("### Skill Gap Analysis")
                    st.code(result, language=None)

    # ── My Applications ──
    elif "Applications" in nav:
        render_section_header("My Applications", "Track your application status")
        apps = env.get_applications_by_user(user["email"])
        if not apps:
            st.info("No applications yet. Apply from the Job Board.")
            return

        statuses = {}
        for a in apps:
            statuses[a["status"]] = statuses.get(a["status"], 0) + 1
        cols = st.columns(min(len(statuses), 5))
        label_map = {"Applied": "SUBMITTED", "Reviewed": "IN REVIEW", "Interview": "INTERVIEW", "Offered": "OFFERED", "Rejected": "CLOSED"}
        for i, (s, c) in enumerate(statuses.items()):
            with cols[i]:
                render_metric_card(s, c, label_map.get(s, "STATUS"))

        st.markdown("<br>", unsafe_allow_html=True)
        for app in apps:
            job = env.get_job(app["job_id"])
            if job:
                with st.expander(f"**{job['title']}** -- {job['company']}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Status:** {app['status']}")
                        st.write(f"**Location:** {job.get('location')}")
                        st.write(f"**Salary:** {job.get('salary_range')}")
                        st.write(f"**Applied:** {app['applied_date'][:10]}")
                    with c2:
                        docs = app.get("documents", {})
                        if docs.get("resume"):
                            st.write("**Tailored Resume:**")
                            st.code(str(docs["resume"])[:400], language=None)

    # ── RL Training Dashboard ──
    elif "RL Training" in nav:
        render_rl_dashboard()


# =====================================================================
#  RECRUITER DASHBOARD
# =====================================================================
def render_recruiter_dashboard():
    user = get_current_user()
    render_nav_bar(user["name"], "recruiter")

    with st.sidebar:
        st.markdown(f"""<div style="text-align:center; padding:20px 0;">
            <div style="font-size:1.1rem; font-weight:700; color:#f8f9fa; margin-top:8px;">{user['name']}</div>
            <div style="font-size:0.82rem; color:#6c757d;">{user['email']}</div>
            <div style="margin-top:8px;"><span class="badge badge-active">RL-Powered</span></div>
        </div>""", unsafe_allow_html=True)
        st.divider()
        nav = st.radio("Navigation", [
            "Overview", "Post a Job", "Candidate Pipeline",
            "AI Analyzer", "RL Training"
        ], label_visibility="collapsed")
        st.divider()
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

    if "Overview" in nav:
        render_section_header("Recruiter Dashboard", "RL-powered candidate management")
        my_jobs = env.get_jobs_by_recruiter(user["email"])
        all_apps = env.get_all_applications()
        my_job_ids = {j["id"] for j in my_jobs}
        my_apps = [a for a in all_apps if a["job_id"] in my_job_ids]

        c1, c2, c3, c4 = st.columns(4)
        with c1: render_metric_card("Active Jobs", len(my_jobs), "POSTINGS")
        with c2: render_metric_card("Applications", len(my_apps), "RECEIVED")
        with c3: render_metric_card("Interviews", sum(1 for a in my_apps if a["status"] == "Interview"), "SCHEDULED")
        with c4: render_metric_card("Candidates", len(set(a["profile_id"] for a in my_apps)), "UNIQUE")

        st.markdown("<br>", unsafe_allow_html=True)
        stats = rl_trainer.get_stats()
        render_section_header("DQN Scorer Status", "")
        c1, c2, c3 = st.columns(3)
        with c1: render_metric_card("Episodes Trained", stats["episodes_trained"], "TRAINING")
        with c2: render_metric_card("Scorer Buffer", stats["cs_buffer_size"], "MEMORY")
        with c3: render_metric_card("DQN Params", f"{stats['cs_params']:,}", "NETWORK")

        st.markdown("<br>", unsafe_allow_html=True)
        render_section_header("Your Job Postings", "")
        for job in my_jobs:
            app_count = len([a for a in my_apps if a["job_id"] == job["id"]])
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1: st.markdown(f"**{job['title']}** -- *{job['company']}*")
            with c2: st.markdown(f"{app_count} applicants")
            with c3: st.markdown(render_status_badge(job.get("status", "Active")), unsafe_allow_html=True)
            st.divider()

    elif "Post a Job" in nav:
        render_section_header("Post a New Job", "Create a new listing")
        with st.form("post_job"):
            title = st.text_input("Job Title", placeholder="Senior ML Engineer")
            company = st.text_input("Company", placeholder="TechFlow AI")
            c1, c2 = st.columns(2)
            with c1:
                location = st.text_input("Location", placeholder="Remote")
                job_type = st.selectbox("Type", ["Full-time", "Part-time", "Contract", "Internship"])
            with c2:
                salary = st.text_input("Salary Range", placeholder="$120K - $160K")
                skills_in = st.text_input("Required Skills (comma-separated)", placeholder="Python, ML, Docker")
            desc = st.text_area("Description", height=150)
            if st.form_submit_button("Post Job", use_container_width=True):
                if title and desc:
                    jid = f"job_{uuid.uuid4().hex[:8]}"
                    skills = [s.strip() for s in skills_in.split(",") if s.strip()]
                    env.store_job(jid, title, desc, {"skills": skills}, company=company,
                                 location=location, job_type=job_type, salary_range=salary, posted_by=user["email"])
                    st.success(f"Job \"{title}\" posted successfully.")

    elif "Pipeline" in nav:
        render_section_header("Candidate Pipeline", "Review applicants with RL-powered scoring")
        my_jobs = env.get_jobs_by_recruiter(user["email"])
        if not my_jobs:
            st.info("Post a job first.")
            return
        job_opts = {f"{j['title']} -- {j['company']}": j["id"] for j in my_jobs}
        sel = st.selectbox("Select job", list(job_opts.keys()))
        sel_id = job_opts.get(sel, "")

        apps = env.get_applications_by_job(sel_id)
        if not apps:
            st.info("No applicants yet.")
            return

        st.markdown(f"<div style='color:#6c757d; font-size:0.85rem; margin:12px 0 20px;'>{len(apps)} applicants</div>", unsafe_allow_html=True)

        for app in apps:
            profile = env.get_profile(app["profile_id"])
            name = profile.get("name", app["profile_id"]) if profile else app["profile_id"]
            skills = profile.get("skills", []) if profile else []

            rl_score = None
            if profile and rl_trainer:
                job = env.get_job(sel_id)
                if job:
                    rl_score = rl_trainer.candidate_scorer.score_candidate(
                        skills, job.get("requirements", {}).get("skills", []),
                        profile.get("experience_years", 0)
                    )

            score_text = f"  |  RL Score: {rl_score}" if rl_score else ""
            with st.expander(f"{name}  |  {app['status']}{score_text}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.write(f"**Email:** {app['profile_id']}")
                    st.write(f"**Skills:** {' / '.join(skills[:5])}")
                    st.write(f"**Applied:** {app['applied_date'][:10]}")
                    if rl_score:
                        color = "#f8f9fa" if rl_score >= 70 else "#adb5bd" if rl_score >= 50 else "#6c757d"
                        st.markdown(f"**DQN Score:** <span style='color:{color}; font-weight:800;'>{rl_score}/100</span>", unsafe_allow_html=True)
                with c2:
                    new_status = st.selectbox("Status", ["Applied", "Reviewed", "Interview", "Offered", "Rejected"],
                        index=["Applied", "Reviewed", "Interview", "Offered", "Rejected"].index(app["status"]),
                        key=f"st_{app['id']}")
                    if st.button("Update", key=f"up_{app['id']}"):
                        env.update_application_status(app["id"], new_status)
                        reward_map = {"Interview": 8.0, "Offered": 10.0, "Rejected": -1.0, "Reviewed": 0.5}
                        if new_status in reward_map and profile:
                            state = rl_env.get_state_for_job(app["profile_id"], sel_id)
                            rl_trainer.train_step_from_feedback(state, 1.0, reward_map[new_status], state, "candidate_scorer")
                        st.success(f"Updated to {new_status}")
                        st.rerun()

                    if st.button("Star", key=f"star_{app['id']}"):
                        if profile:
                            state = rl_env.get_state_for_job(app["profile_id"], sel_id)
                            rl_trainer.train_step_from_feedback(state, 1.0, 3.0, state, "candidate_scorer")
                            env.record_feedback(user["email"], app["profile_id"], "star", 3.0)
                            st.toast("Starred. DQN policy updated.")

    elif "Analyzer" in nav:
        render_section_header("AI Candidate Analyzer", "Full RL + Qwen 2.5 multi-agent pipeline")

        render_glass_card("""<div style="font-size:0.88rem; color:#adb5bd; line-height:1.6;">
            <b>Pipeline:</b> ProfileParser > LinkExtractor > LinkAnalyzer > ConsistencyChecker (Qwen 2.5) > DQN Scorer (RL)
        </div>""")

        resume = st.text_area("Paste candidate resume", height=160, label_visibility="collapsed",
            placeholder="Paste candidate's resume text here...")

        all_jobs = env.get_all_jobs(status_filter="Active")
        job_opts = {f"{j['title']} -- {j['company']}": j["id"] for j in all_jobs}
        sel = st.selectbox("Target Job", list(job_opts.keys()))
        sel_id = job_opts.get(sel, "")

        if st.button("Run Full RL + AI Analysis", use_container_width=True):
            if resume.strip():
                temp_id = f"cand_{uuid.uuid4().hex[:8]}"

                with st.spinner("Step 1/4: Qwen 2.5 parsing profile..."):
                    from seeker_agents import ProfileParserAgent
                    parser = ProfileParserAgent(env)
                    parsed = parser.parse(resume, temp_id)

                with st.spinner("Step 2/4: Extracting links..."):
                    from recruiter_agents import ResumeLinkExtractorAgent
                    ext = ResumeLinkExtractorAgent(env)
                    links = ext.extract(resume)

                with st.spinner("Step 3/4: Qwen 2.5 consistency check..."):
                    from recruiter_agents import LinkContentAnalyzerAgent, ConsistencyCheckerAgent
                    la = LinkContentAnalyzerAgent(env)
                    lc = la.analyze(links)
                    cc = ConsistencyCheckerAgent(env)
                    consistency = cc.check(temp_id, resume, lc)

                with st.spinner("Step 4/4: DQN scoring..."):
                    from recruiter_agents import EnhancedATSScorerAgent
                    scorer = EnhancedATSScorerAgent(env, rl_trainer)
                    score_result = scorer.score(temp_id, sel_id, consistency)

                st.success("Analysis complete.")
                st.markdown("<br>", unsafe_allow_html=True)

                fs = score_result.get("score", 0)
                sc = "#f8f9fa" if fs >= 80 else "#adb5bd" if fs >= 60 else "#6c757d"
                st.markdown(f"""<div style="text-align:center; margin-bottom:24px;">
                    <div style="display:inline-flex; width:140px; height:140px; border-radius:50%;
                         background: conic-gradient({sc} 0%, {sc} {fs}%, #343a40 {fs}%);
                         align-items:center; justify-content:center;">
                        <div style="width:110px; height:110px; border-radius:50%; background:#212529;
                             display:flex; align-items:center; justify-content:center;
                             font-size:2.2rem; font-weight:800; color:{sc};">{fs}</div>
                    </div>
                    <div style="color:#6c757d; margin-top:8px; font-size:0.82rem;">Holistic Score / 100</div>
                    <div style="color:#adb5bd; font-size:0.72rem; margin-top:4px;">Method: {score_result.get('method', 'Heuristic')}</div>
                </div>""", unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1: render_metric_card("Keyword", f"{score_result.get('keyword_score', 0)}%", "MATCH")
                with c2: render_metric_card("Consistency", f"{score_result.get('consistency_score', 0)}%", "VERIFIED")
                with c3:
                    rl_s = score_result.get("rl_score")
                    render_metric_card("RL DQN", f"{rl_s:.1f}%" if rl_s else "N/A", "NEURAL")

                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("### Parsed Profile")
                    sk = "".join([f'<span class="skill-tag">{s}</span>' for s in parsed.get("skills", [])])
                    render_glass_card(f"<b>Name:</b> {parsed.get('name')}<br><b>Exp:</b> {parsed.get('experience_years')} yrs<br><div class='job-tags' style='margin-top:8px;'>{sk}</div>")
                with c2:
                    st.markdown("### Links")
                    for link, summary in lc.items():
                        render_glass_card(f"<b>{link}</b><br><span style='color:#6c757d;font-size:0.82rem;'>{summary}</span>")

                st.markdown("### Consistency Report")
                st.code(consistency.get("report", ""), language=None)
                st.markdown("### Holistic Analysis")
                st.code(score_result.get("analysis", ""), language=None)

    elif "RL Training" in nav:
        render_rl_dashboard()


# =====================================================================
#  RL TRAINING DASHBOARD (shared between seeker and recruiter)
# =====================================================================
def render_rl_dashboard():
    render_section_header("RL Training Dashboard", "Monitor reinforcement learning policy networks in real-time")

    stats = rl_trainer.get_stats()

    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric_card("Episodes Trained", stats["episodes_trained"], "TRAINING")
    with c2: render_metric_card("JM Buffer", stats["jm_buffer_size"], "MEMORY")
    with c3: render_metric_card("CS Buffer", stats["cs_buffer_size"], "MEMORY")
    total_params = stats["jm_params"] + stats["cs_params"] + stats["ro_params"]
    with c4: render_metric_card("Total Params", f"{total_params:,}", "NETWORK")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        render_glass_card(f"""
            <div style="font-size:1rem; font-weight:700; color:#f8f9fa; margin-bottom:8px;">Job Matcher NN</div>
            <div style="color:#adb5bd; font-size:0.82rem; line-height:1.8;">
                <b>Architecture:</b> Actor-Critic<br>
                <b>Parameters:</b> {stats['jm_params']:,}<br>
                <b>Buffer:</b> {stats['jm_buffer_size']} experiences<br>
                <b>Avg Reward:</b> {stats['jm_buffer_stats'].get('avg_reward', 0)}
            </div>
        """)
    with c2:
        render_glass_card(f"""
            <div style="font-size:1rem; font-weight:700; color:#f8f9fa; margin-bottom:8px;">Candidate Scorer NN</div>
            <div style="color:#adb5bd; font-size:0.82rem; line-height:1.8;">
                <b>Architecture:</b> DQN<br>
                <b>Parameters:</b> {stats['cs_params']:,}<br>
                <b>Buffer:</b> {stats['cs_buffer_size']} experiences<br>
                <b>Avg Reward:</b> {stats['cs_buffer_stats'].get('avg_reward', 0)}
            </div>
        """)
    with c3:
        render_glass_card(f"""
            <div style="font-size:1rem; font-weight:700; color:#f8f9fa; margin-bottom:8px;">Resume Optimizer NN</div>
            <div style="color:#adb5bd; font-size:0.82rem; line-height:1.8;">
                <b>Architecture:</b> Contextual Bandit<br>
                <b>Parameters:</b> {stats['ro_params']:,}<br>
                <b>Output:</b> 6 section weights<br>
                <b>Sections:</b> summary, skills, experience, education, projects, certs
            </div>
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    render_section_header("Training Loss History", "")
    c1, c2 = st.columns(2)
    with c1:
        jm_losses = stats.get("jm_losses", [])
        if jm_losses:
            st.markdown("**Job Matcher (Actor-Critic) Loss**")
            st.line_chart(jm_losses, use_container_width=True)
        else:
            st.info("No training steps yet for Job Matcher.")
    with c2:
        cs_losses = stats.get("cs_losses", [])
        if cs_losses:
            st.markdown("**Candidate Scorer (DQN) Loss**")
            st.line_chart(cs_losses, use_container_width=True)
        else:
            st.info("No training steps yet for Candidate Scorer.")

    st.markdown("<br>", unsafe_allow_html=True)

    render_section_header("Feedback and Reward Statistics", "")
    reward_stats = env.get_reward_stats()
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric_card("Total Feedback", reward_stats["total"], "ALL")
    with c2: render_metric_card("Avg Reward", reward_stats["avg_reward"], "MEAN")
    with c3: render_metric_card("Positive", reward_stats["positive"], "GOOD")
    with c4: render_metric_card("Negative", reward_stats["negative"], "BAD")

    st.markdown("<br>", unsafe_allow_html=True)

    render_section_header("Manual Controls", "")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Run 50 More Training Episodes", use_container_width=True):
            with st.spinner("Training RL policies..."):
                rl_trainer.pretrain(rl_env, num_episodes=50)
            st.success("50 episodes trained.")
            st.rerun()
    with c2:
        if st.button("Save Model Weights", use_container_width=True):
            rl_trainer._save_models()
            st.success("Models saved to disk.")


# =====================================================================
#  ROUTER
# =====================================================================
if require_auth():
    role = get_user_role()
    if role == "seeker":
        render_seeker_dashboard()
    elif role == "recruiter":
        render_recruiter_dashboard()
    else:
        st.error("Unknown role.")
else:
    render_landing_page()
