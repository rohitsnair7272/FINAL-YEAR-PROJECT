import streamlit as st
import smtplib
import ssl
from email.message import EmailMessage
import os
import secrets
from datetime import datetime, timedelta
from dotenv import load_dotenv
from mongo_utils import shopkeepers_col

load_dotenv()
st.set_page_config(page_title="Forgot Password", layout="centered")

# Hide sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], .css-1d391kg {
            display: none !important;
        }
        .block-container, header[data-testid="stHeader"] {
            padding-left: 1rem !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🔐 Forgot Password")

email_input = st.text_input("📧 Enter your registered email")

if st.button("Send Reset Link"):
    user = shopkeepers_col.find_one({"email": email_input})
    if user:
        # Generate secure token
        token = secrets.token_urlsafe(32)
        expiry_time = datetime.utcnow() + timedelta(minutes=30)

        shopkeepers_col.update_one(
            {"email": email_input},
            {"$set": {
                "reset_token": token,
                "reset_token_expiry": expiry_time
            }}
        )

        # Send email
        sender_email = st.secrets["SENDER_EMAIL"]
        sender_password = st.secrets["SENDER_APP_PASSWORD"]
        reset_link = f"{st.secrets['app_url']}/reset_password?token={token}"

        message = EmailMessage()
        message.set_content(f"Click the link to reset your password (valid for 30 mins):\n\n{reset_link}")
        message["Subject"] = "Reset your Shopkeeper Dashboard Password"
        message["From"] = sender_email
        message["To"] = email_input

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, sender_password)
                server.send_message(message)
            st.success("✅ Reset link sent to your email.")
        except Exception as e:
            st.error("❌ Failed to send email.")
            st.error(str(e))
    else:
        st.error("❌ This email is not registered.")
