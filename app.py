"""One Streamlit entry point, guest-first navigation, no sidebar on auth pages."""
import streamlit as st
from utils.state import init_state, go, logout
from utils.styles import inject_styles

st.set_page_config(page_title="SAR FloodWatch · NASA Space Apps", page_icon="🛰️", layout="wide", initial_sidebar_state="expanded")
init_state()
inject_styles()

from pages import landing, auth, dashboard, flood_detection, comparison, analytics, about  # noqa: E402

APP_PAGES = [
    ("dashboard", "📊 Overview"), ("detection", "🌊 Flood Detection"),
    ("comparison", "🛰️ Before / After"), ("analytics", "📈 Analytics"),
    ("about", "ℹ️ About"),
]

page = st.session_state.get("page", "landing")
allowed = bool(st.session_state.get("guest") or st.session_state.get("auth_user"))
if page not in {"landing", "login", "signup"} and not allowed:
    page = "landing"
    go(page)

if page in {"login", "signup"}:
    auth.render(page)
elif page == "landing":
    landing.render()
else:
    with st.sidebar:
        st.markdown("## 🛰️ SAR FloodWatch")
        st.caption("Flood intelligence · NASA Space Apps 2026")
        st.divider()
        for route, label in APP_PAGES:
            if st.button(label, key=f"nav_{route}", use_container_width=True,
                         type="primary" if route == page else "secondary"):
                go(route); st.rerun()
        st.divider()
        user = st.session_state.get("auth_user")
        st.caption(f"{user['email']}" if user else "Guest demonstration")
        if st.button("Log out" if user else "Exit guest mode", use_container_width=True):
            logout(); st.rerun()
    render = {"dashboard": dashboard.render, "detection": flood_detection.render,
              "comparison": comparison.render, "analytics": analytics.render,
              "about": about.render}
    render.get(page, dashboard.render)()
