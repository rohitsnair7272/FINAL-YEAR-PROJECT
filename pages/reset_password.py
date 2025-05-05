import streamlit as st
import hashlib
from mongo_utils import shopkeepers_col
from datetime import datetime

st.set_page_config(page_title="Reset Password", layout="centered")
st.title("🔁 Reset Your Password")

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

# Extract token from URL using st.query_params
token = st.query_params.get("token", None)

if not token:
    st.error("❌ Invalid or missing token.")
else:
    user = shopkeepers_col.find_one({"reset_token": token})
    if not user:
        st.error("❌ Invalid token.")
    elif datetime.utcnow() > user.get("reset_token_expiry", datetime.min):
        st.error("❌ Token has expired.")
    else:
        st.success("✅ Token verified! You can now reset your password.")
        new_password = st.text_input("🔐 New Password", type="password")
        confirm_password = st.text_input("🔐 Confirm Password", type="password")

        def hash_password(password):
            return hashlib.sha256(password.encode()).hexdigest()

        if st.button("Reset Password"):
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                shopkeepers_col.update_one(
                    {"email": user["email"]},
                    {"$set": {"password": hash_password(new_password)},
                     "$unset": {"reset_token": "", "reset_token_expiry": ""}}
                )
                st.success("✅ Password reset successfully! You can now login.")
                # Link that opens in the same tab
                st.markdown(
                    '<a href="https://shopkeeper-dashboard.streamlit.app/" '
                    'style="text-decoration: underline; color: blue;" target="_self">'
                    'Go to Login Page</a>',
                    unsafe_allow_html=True
                )
                # Auto redirect after 3 seconds
                st.markdown("""
                    <script type="text/javascript">
                        setTimeout(function() {
                            window.location.href = 'https://shopkeeper-dashboard.streamlit.app/';
                        }, 3000);
                    </script>
                """, unsafe_allow_html=True)
