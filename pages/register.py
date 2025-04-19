import streamlit as st
import hashlib
import re
from mongo_utils import shopkeepers_col

# ---------------- Streamlit Page Config ----------------
st.set_page_config(page_title="Register", layout="centered")

# Completely hide the sidebar and its space
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        .css-1d391kg {
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

# ---------------- Helper Function ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- Registration Form ----------------
st.title("📝 Register Shopkeeper")

email = st.text_input("📧 Email")
phone_number = st.text_input("📱 Phone Number")
password = st.text_input("🔐 Password", type="password")
confirm_password = st.text_input("🔐 Confirm Password", type="password")

if st.button("Register"):
    if not email or not phone_number or not password or not confirm_password:
        st.warning("⚠️ Please fill in all fields.")
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        st.warning("⚠️ Please enter a valid email.")
    elif password != confirm_password:
        st.warning("⚠️ Passwords do not match.")
    else:
        # ✅ Allow only one user in the database
        if shopkeepers_col.count_documents({}) >= 1:
            st.error("🚫 Only one shopkeeper is allowed to register.")
        else:
            hashed_password = hash_password(password)
            shopkeepers_col.insert_one({
                "email": email,
                "password": hashed_password,
                "Phone_number": phone_number
            })
            st.success("✅ Registered successfully! Please login.")
            st.switch_page("login.py")

# Optional: Add link to login
st.page_link("login.py", label="🔐 Already registered? Go to Login")
