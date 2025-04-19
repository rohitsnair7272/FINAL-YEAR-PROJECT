import streamlit as st
import hashlib
from mongo_utils import shopkeepers_col
import re

st.set_page_config(page_title="Reset Password", layout="centered")
st.title("🔁 Reset Your Password")
# Completely hide the sidebar and its space
hide_sidebar_style = """
    <style>
        /* Hide sidebar and collapse its space */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        .css-1d391kg {  /* hamburger menu */
            display: none !important;
        }
        .block-container {
            padding-left: 1rem !important;
        }
        header[data-testid="stHeader"] {
            padding-left: 1rem !important;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

email = st.text_input("📧 Enter your registered email")
new_password = st.text_input("🔐 New Password", type="password")
confirm_password = st.text_input("🔐 Confirm Password", type="password")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

if st.button("Reset Password"):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        st.warning("Please enter a valid email.")
    elif new_password != confirm_password:
        st.error("Passwords do not match.")
    else:
        user = shopkeepers_col.find_one({"email": email})
        if user:
            shopkeepers_col.update_one(
                {"email": email},
                {"$set": {"password": hash_password(new_password)}}
            )
            st.success("✅ Password reset successfully! You can now login.")
        else:
            st.error("❌ Email not found in our records.")
        st.switch_page("login.py")
