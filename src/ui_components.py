
import streamlit as st
import json


# ── Color Palette ──
# #f8f9fa  #e9ecef  #dee2e6  #ced4da  #adb5bd
# #6c757d  #495057  #343a40  #212529

def inject_custom_css():
    """Inject the full custom CSS theme — professional grayscale."""
    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');


    .stApp {
        background: #212529;
        font-family: 'Poppins', sans-serif;
        color: #dee2e6;
    }


    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden !important;}
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    .glass-card {
        background: #343a40;
        border: 1px solid #495057;
        border-radius: 12px;
        padding: 28px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: #6c757d;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
    .metric-card {
        background: #343a40;
        border: 1px solid #495057;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
        border-color: #6c757d;
    }
    .metric-icon {
        font-size: 1rem;
        color: #adb5bd;
        margin-bottom: 4px;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-weight: 600;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #f8f9fa;
        margin: 8px 0;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #adb5bd;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }

    .badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .badge-applied { background: rgba(108,117,125,0.25); color: #adb5bd; border: 1px solid #6c757d; }
    .badge-reviewed { background: rgba(206,212,218,0.15); color: #ced4da; border: 1px solid #6c757d; }
    .badge-interview { background: rgba(248,249,250,0.1); color: #f8f9fa; border: 1px solid #adb5bd; }
    .badge-offered { background: rgba(248,249,250,0.15); color: #f8f9fa; border: 1px solid #dee2e6; }
    .badge-rejected { background: rgba(73,80,87,0.4); color: #adb5bd; border: 1px solid #495057; }
    .badge-active { background: rgba(248,249,250,0.1); color: #f8f9fa; border: 1px solid #adb5bd; }

    .job-card {
        background: #343a40;
        border: 1px solid #495057;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        transition: all 0.35s ease;
    }
    .job-card:hover {
        background: #3d444b;
        border-color: #6c757d;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }
    .job-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #f8f9fa;
        margin-bottom: 6px;
    }
    .job-company {
        font-size: 0.9rem;
        color: #adb5bd;
        font-weight: 600;
    }
    .job-meta {
        font-size: 0.8rem;
        color: #6c757d;
        margin-top: 8px;
    }
    .job-tags {
        margin-top: 12px;
    }
    .skill-tag {
        display: inline-block;
        background: #495057;
        color: #dee2e6;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        margin: 2px 4px 2px 0;
        border: 1px solid #6c757d;
    }

    .landing-wrapper {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px 20px;
    }

    .landing-brand {
        text-align: center;
        margin-bottom: 48px;
    }
    .landing-brand-title {
        font-size: 2.8rem;
        font-weight: 900;
        color: #f8f9fa;
        letter-spacing: -0.5px;
        line-height: 1.15;
        margin-bottom: 12px;
    }
    .landing-brand-sub {
        font-size: 1rem;
        color: #6c757d;
        font-weight: 400;
        letter-spacing: 0.3px;
    }


    .login-stack-container {
        position: relative;
        width: 420px;
        max-width: 100%;
        margin: 0 auto;
    }
    .login-stack-bg-1 {
        position: absolute;
        top: 8px;
        left: 12px;
        right: -12px;
        bottom: -8px;
        background: #e9ecef;
        border-radius: 16px;
        transform: rotate(3deg);
        z-index: 0;
    }
    .login-stack-bg-2 {
        position: absolute;
        top: 4px;
        left: 6px;
        right: -6px;
        bottom: -4px;
        background: #dee2e6;
        border-radius: 16px;
        transform: rotate(1.5deg);
        z-index: 1;
    }
    .login-card {
        position: relative;
        z-index: 2;
        background: #f8f9fa;
        border-radius: 16px;
        padding: 48px 40px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
    }
    .login-card-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #212529;
        margin-bottom: 32px;
        text-align: center;
    }

    .section-header {
        font-size: 1.6rem;
        font-weight: 800;
        color: #f8f9fa;
        margin-bottom: 8px;
    }
    .section-subheader {
        font-size: 0.9rem;
        color: #6c757d;
        margin-bottom: 28px;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #1e293b;
        border-right: 1px solid #334155;
        min-width: 18rem !important;
        max-width: 18rem !important;
        transform: translateX(0) !important;
    }
    section[data-testid="stSidebar"][aria-expanded="false"] {
        min-width: 18rem !important;
        max-width: 18rem !important;
        transform: translateX(0) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0;
    }

    /* ── Buttons (global) ── */
    .stButton > button {
        background: #343a40;
        color: #f8f9fa;
        border: 1px solid #495057;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        transition: all 0.3s ease;
        letter-spacing: 0.3px;
    }
    .stButton > button:hover {
        background: #495057;
        border-color: #6c757d;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        transform: translateY(-1px);
    }

    /* ── Primary action buttons (forms) ── */
    .stFormSubmitButton > button {
        background: #212529 !important;
        color: #f8f9fa !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-family: 'Poppins', sans-serif !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px !important;
    }
    .stFormSubmitButton > button:hover {
        background: #343a40 !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: #e9ecef !important;
        border: 1px solid #ced4da !important;
        border-radius: 8px !important;
        color: #212529 !important;
        font-family: 'Poppins', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #495057 !important;
        box-shadow: 0 0 0 2px rgba(73, 80, 87, 0.2) !important;
    }

    /* ── Inputs inside main dashboard (dark bg) ── */
    .dashboard-area .stTextInput > div > div > input,
    .dashboard-area .stTextArea > div > div > textarea,
    .dashboard-area .stSelectbox > div > div {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid #495057 !important;
        color: #f8f9fa !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: transparent;
        border-bottom: 2px solid #ced4da;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0;
        color: #6c757d;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        padding: 12px 24px;
        border-bottom: 2px solid transparent;
        margin-bottom: -2px;
    }
    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #212529 !important;
        border-bottom: 2px solid #212529 !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: #343a40 !important;
        border-radius: 8px !important;
        color: #dee2e6 !important;
        font-weight: 600 !important;
    }

    /* ── Divider ── */
    hr {
        border-color: #343a40 !important;
    }

    /* ── Nav Bar ── */
    .nav-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 0;
        border-bottom: 1px solid #343a40;
        margin-bottom: 32px;
    }
    .nav-brand {
        font-size: 1.2rem;
        font-weight: 800;
        color: #f8f9fa;
        letter-spacing: -0.3px;
    }
    .nav-user {
        font-size: 0.85rem;
        color: #6c757d;
        font-weight: 500;
    }

    /* ── Info cards / alerts ── */
    div[data-testid="stAlert"] {
        background: #343a40 !important;
        border: 1px solid #495057 !important;
        border-radius: 8px !important;
        color: #dee2e6 !important;
    }

    /* ── Score Gauge ── */
    .score-gauge {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        font-size: 2rem;
        font-weight: 800;
    }

    /* ── Spinner ── */
    .stSpinner > div {
        border-top-color: #adb5bd !important;
    }

    /* ── Label color fix for login form ── */
    .stTextInput label, .stSelectbox label, .stTextArea label {
        color: #495057 !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }

    /* ── Toast and other ── */
    .stToast {
        background: #343a40 !important;
        color: #f8f9fa !important;
    }

    /* ── Radio buttons in sidebar ── */
    section[data-testid="stSidebar"] .stRadio label {
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
    }

    </style>
    """, unsafe_allow_html=True)


def render_metric_card(label, value, icon_label=""):
    """Render a styled metric card. icon_label is plain text, no emoji."""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon_label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_job_card(job, show_apply=False):
    """Render a styled job posting card."""
    skills = job.get("requirements", {}).get("skills", [])
    skill_tags = "".join([f'<span class="skill-tag">{s}</span>' for s in skills])

    st.markdown(f"""
    <div class="job-card">
        <div class="job-title">{job.get('title', 'Untitled')}</div>
        <div class="job-company">{job.get('company', 'Unknown')}</div>
        <div class="job-meta">
            {job.get('location', 'Remote')} &middot;
            {job.get('job_type', 'Full-time')} &middot;
            {job.get('salary_range', 'Competitive')}
        </div>
        <div style="margin-top:12px; font-size:0.85rem; color:#6c757d; line-height:1.5;">
            {job.get('description', '')[:180]}...
        </div>
        <div class="job-tags">{skill_tags}</div>
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(status):
    """Return HTML for a colored status badge."""
    badge_class = f"badge-{status.lower()}"
    return f'<span class="badge {badge_class}">{status}</span>'


def render_nav_bar(user_name, role):
    """Render the top navigation bar."""
    role_map = {"seeker": "Job Seeker", "recruiter": "Recruiter", "admin": "Admin"}
    role_label = role_map.get(role, role.title())
    st.markdown(f"""
    <div class="nav-bar">
        <div class="nav-brand">AI Job Dashboard</div>
        <div class="nav-user">{user_name} &middot; {role_label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title, subtitle=""):
    """Render a styled section header."""
    st.markdown(f"""
    <div class="section-header">{title}</div>
    <div class="section-subheader">{subtitle}</div>
    """, unsafe_allow_html=True)


def render_glass_card(content_html):
    """Render content inside a glass card."""
    st.markdown(f'<div class="glass-card">{content_html}</div>', unsafe_allow_html=True)
