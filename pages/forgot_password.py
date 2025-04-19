import streamlit as st
import smtplib
import ssl
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from mongo_utils import shopkeepers_col

load_dotenv()
st.set_page_config(page_title="Forgot Password", layout="centered")
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


st.title("🔐 Forgot Password")

email_input = st.text_input("📧 Enter your registered email")

if st.button("Send Reset Link"):
    user = shopkeepers_col.find_one({"email": email_input})
    if user:
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_APP_PASSWORD")
        receiver_email = email_input

        reset_link = f"{st.secrets['app_url']}/reset_password"  # Update app_url in secrets.toml or hardcode for local
        message = EmailMessage()
        message.set_content(f"Click the link below to reset your password:\n\n{reset_link}")
        message["Subject"] = "Reset your Shopkeeper Dashboard Password"
        message["From"] = sender_email
        message["To"] = receiver_email

        try:
            context = ssl.create_default_context()

            # ✅ Try SSL first (Port 465)
            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(sender_email, sender_password)
                    server.send_message(message)
                st.success("✅ Reset link sent to your email.")
            except Exception as e:
                # ⛔ If SSL fails, try STARTTLS on port 587
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls(context=context)
                    server.login(sender_email, sender_password)
                    server.send_message(message)
                st.success("✅ Reset link sent to your email (TLS fallback).")

        except Exception as e:
            st.error("❌ Failed to send email. Please check your internet, firewall, or app password setup.")
            st.error(str(e))
    else:
        st.error("❌ This email is not registered.")