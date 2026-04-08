import hashlib
import streamlit as st


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def init_auth_state():
    """Initialize authentication session state."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "page" not in st.session_state:
        st.session_state.page = "landing"


def signup(env, email, password, name, role):
    """Register a new user."""
    existing = env.get_user(email)
    if existing:
        return False, "An account with this email already exists."

    pw_hash = hash_password(password)
    success = env.create_user(email, pw_hash, name, role)
    if success:
        return True, "Account created successfully! Please log in."
    return False, "Failed to create account. Try again."


def login(env, email, password):
    """Authenticate a user."""
    user = env.get_user(email)
    if not user:
        return False, "No account found with this email."

    if not check_password(password, user["password_hash"]):
        return False, "Incorrect password."

    st.session_state.authenticated = True
    st.session_state.user = user
    st.session_state.page = "dashboard"
    return True, f"Welcome back, {user['name']}!"


def logout():
    """Log out the current user — clear ALL session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.page = "landing"


def require_auth():
    """Check if user is authenticated. Returns True if authenticated."""
    return st.session_state.get("authenticated", False)


def get_current_user():
    """Get the currently logged-in user dict."""
    return st.session_state.get("user", None)


def get_user_role():
    """Get the role of the currently logged-in user."""
    user = get_current_user()
    return user.get("role", "") if user else ""
