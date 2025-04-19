import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
import os
import requests
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
GEMINI_API_KEY = os.getenv("REACT_APP_GEMINI_API_KEY")

# ✅ Streamlit Page Config
st.set_page_config(page_title="Customer Feedback Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 🔐 Login protection
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("You must log in to access the dashboard.")
    if st.button("Go to Login"):
        st.switch_page("login.py")
    st.stop()

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

st.markdown("<br><br>", unsafe_allow_html=True)
st.title("Welcome to the Dashboard!")

if st.button("Logout"):
    st.session_state.logged_in = False
    st.switch_page("login.py")

# ✅ MongoDB Setup
client = MongoClient(MONGO_URI)
db = client["FeedbackDB"]
feedback_collection = db["feedbacks"]
product_collection = db["Products"]

# ✅ Fetch Feedback Data
feedback_data = list(feedback_collection.find({}, {"_id": 0}))
df = pd.DataFrame(feedback_data) if feedback_data else pd.DataFrame()

# ✅ Custom CSS
st.markdown("""
    <style>
        div[data-testid="stDataFrame"] { overflow: hidden !important; width: 100%; height: auto !important; }
        .st-emotion-cache-1r6slb0, .st-emotion-cache-16idsys { white-space: normal !important; word-wrap: break-word !important; }
        section.main { padding-top: 0rem; padding-bottom: 0rem; }
        .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; font-size: 62px; padding-top: 40px;'>📊 Customer Feedback Dashboard</h2>", unsafe_allow_html=True)

if not df.empty:
    # ✅ Key Metrics
    st.markdown("### 📌 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Feedbacks", value=len(df))
    col2.metric(label="Text Feedbacks", value=len(df[df["type"] == "text"]))
    col3.metric(label="Voice Feedbacks", value=len(df[df["type"] == "voice"]))
    col4.metric(label="Emotion Feedbacks", value=len(df[df["type"] == "emotion"]))

    # ✅ Emotion Trend
    st.markdown("<h2 style='font-size: 32px; font-style: italic'>📈 Emotion Trend Over Time</h2>", unsafe_allow_html=True)
    if "timestamp" in df.columns and "emotion" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = df["timestamp"].dt.date
        trend_df = df[df["type"] == "emotion"].groupby(["date", "emotion"]).size().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(10, 4))
        trend_df.plot(ax=ax, marker="o")
        ax.set_title("Daily Emotion Trends", fontsize=10)
        ax.set_xlabel("Date", fontsize=8)
        ax.set_ylabel("Count", fontsize=8)
        ax.tick_params(axis='x', rotation=45, labelsize=6)
        ax.tick_params(axis='y', labelsize=6)
        st.pyplot(fig)
    else:
        st.info("Timestamp or emotion data not available for trend analysis.")

    # ✅ Emotion Chart + Pie Chart
    st.markdown("<h2 style='font-size: 32px; font-style: italic'>😊 Emotion Feedback Analysis</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])

    if "emotion" in df.columns:
        emotion_order = ["happy", "sad", "surprise", "neutral", "angry"]
        df["emotion"] = df["emotion"].fillna("Not Available")
        emotion_counts = df["emotion"].value_counts().reindex(emotion_order, fill_value=0)
        fig, ax = plt.subplots(figsize=(1.5, 0.5))
        sns.barplot(x=emotion_counts.index, y=emotion_counts.values, hue=emotion_counts.index, ax=ax, palette="coolwarm", legend=False)
        ax.tick_params(axis="x", labelsize=3)
        ax.tick_params(axis="y", labelsize=3)
        ax.set_xlabel("-----> Emotion", fontsize=2)
        ax.set_ylabel("-----> Count", fontsize=2)
        ax.set_title("Emotion Distribution", fontsize=4)
        col1.pyplot(fig)

    feedback_counts = df["type"].value_counts()
    fig, ax = plt.subplots(figsize=(1, 1))
    ax.pie(feedback_counts, labels=feedback_counts.index, autopct="%1.1f%%", colors=sns.color_palette("pastel"), textprops={"fontsize": 3})
    col2.pyplot(fig)

    # ✅ Feedback Table    
    

    # Feedback type filter
    feedback_types = ["All"] + df["type"].unique().tolist()
    selected_feedback_type = st.selectbox("Select Feedback Type:", feedback_types, key="feedback_type")
    
    sort_options = ["Newest First", "Oldest First", "Most Priority First (Negative Sentiment)", "Least Priority First (Positive Sentiment)"]
    selected_sort = st.selectbox("Sort Feedbacks By:", sort_options, key="sort_option")

    filtered_feedback = df if selected_feedback_type == "All" else df[df["type"] == selected_feedback_type]

    feedback_table = filtered_feedback.copy()
    feedback_table["timestamp"] = pd.to_datetime(feedback_table["timestamp"])
    feedback_table["rating"] = feedback_table["rating"].apply(lambda x: "⭐" * int(x) if pd.notna(x) else "N/A")
    feedback_table["emotion"] = feedback_table.apply(lambda row: row["emotion"] if row["type"] == "emotion" else "N/A", axis=1)
    feedback_table["category"] = feedback_table.get("category", "N/A")
    feedback_table["product"] = feedback_table.get("product", "N/A")
    feedback_table["sentiment"] = feedback_table.get("sentiment", "N/A").fillna("unknown").astype(str).str.strip().str.lower()

    if selected_sort == "Newest First":
        feedback_table = feedback_table.sort_values(by="timestamp", ascending=False)
    elif selected_sort == "Oldest First":
        feedback_table = feedback_table.sort_values(by="timestamp", ascending=True)
    elif selected_sort == "Most Priority First (Negative Sentiment)":
        sentiment_priority = {"negative": 0, "neutral": 1, "positive": 2}
        feedback_table["priority"] = feedback_table["sentiment"].map(sentiment_priority).fillna(3)
        feedback_table = feedback_table.sort_values(by="priority")
    elif selected_sort == "Least Priority First (Positive Sentiment)":
        sentiment_priority = {"positive": 0, "neutral": 1, "negative": 2}
        feedback_table["priority"] = feedback_table["sentiment"].map(sentiment_priority).fillna(3)
        feedback_table = feedback_table.sort_values(by="priority")

    feedback_table = feedback_table.rename(columns={
        "content": "Feedback", "type": "Type", "rating": "Rating", "emotion": "Emotion",
        "category": "Category", "product": "Product", "sentiment": "Sentiment"
    })

    display_cols = ["Type", "Feedback", "Emotion", "Rating", "Category", "Product", "Sentiment"]
    st.dataframe(feedback_table[display_cols], use_container_width=True)

    
    # ✅ AI Suggestions
    st.markdown("<h2 style='font-size: 32px; font-style: italic'>🤖 AI Suggestions</h2>", unsafe_allow_html=True)
    suggestion_types = ["All"] + df[df["type"].isin(["text", "voice"])]["type"].unique().tolist()
    selected_suggestion_type = st.selectbox("Select AI Suggestion Type:", suggestion_types, key="ai_type")

    ai_filtered = df[(df["type"].isin(["text", "voice"])) & df["suggestion"].notna()]
    if selected_suggestion_type != "All":
        ai_filtered = ai_filtered[ai_filtered["type"] == selected_suggestion_type]

    ai_table = ai_filtered.rename(columns={"content": "Feedback", "type": "Type", "suggestion": "AI Suggestion"})
    ai_table = ai_table[["Type", "Feedback", "AI Suggestion"]]

    for idx, row in ai_table.iterrows():
        with st.expander(f"**{idx+1}. Type:** {row['Type'].capitalize()} - 💬 {row['Feedback']}"):
            st.success(f"🤖 {row['AI Suggestion']}")

    # ✅ Ask RAL
    st.markdown("---")
    st.markdown("<h2 style='font-size: 32px; font-style: italic;'>💬 Ask RAL - Your AI Business Advisor</h2>", unsafe_allow_html=True)
    question = st.text_input("Type your question below 👇", placeholder="e.g. What are my customers complaining about the most?")

    if question:
        with st.spinner("RAL is analyzing your data..."):
            df_copy = df.copy()
            df_copy["suggestion"] = df_copy["suggestion"].fillna("No suggestion")
            feedback_context = "\n".join(
                f"Type: {row['type']}, Feedback: {row['content']}, Suggestion: {row['suggestion']}"
                for _, row in df_copy.iterrows()
            )
            full_prompt = f"""
            You are 'RAL' – an expert AI advisor for shopkeepers. Your job is to help the shopkeeper by answering their questions using only the customer feedback and existing AI suggestions provided below. 
            {feedback_context}
            Based on this, answer the shopkeeper's question:
            {question}
            """
            def get_ai_insight_from_feedback(user_prompt):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                headers = {"Content-Type": "application/json"}
                data = {"contents": [{"parts": [{"text": user_prompt}]}]}
                try:
                    response = requests.post(url, json=data, headers=headers)
                    result = response.json()
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                except Exception as e:
                    return f"Error from Gemini: {e}"

            ai_response = get_ai_insight_from_feedback(full_prompt)
            st.success(ai_response)
else:
    st.warning("No feedback data found.")











# 📂 Category Management Section
st.markdown("---")
st.markdown("<h2 style='font-size: 32px; font-style: italic;'>📂 Category Management</h2>", unsafe_allow_html=True)

API_BASE_URL = "http://127.0.0.1:8080"

def fetch_categories():
    try:
        response = requests.get(f"{API_BASE_URL}/get_categories")
        if response.status_code == 200:
            return response.json().get("categories", [])
        else:
            st.error("Error fetching categories from server.")
            return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []

st.subheader("➕ Add New Category")
with st.form("add_category_form"):
    new_category = st.text_input("Enter Category Name:")
    add_btn = st.form_submit_button("Add Category")
    if add_btn and new_category.strip():
        try:
            res = requests.post(f"{API_BASE_URL}/add_category", data={"name": new_category.strip()})
            if res.status_code == 200:
                st.success(f"✅ Category '{new_category.strip()}' added!")
            else:
                st.warning(f"⚠️ {res.json().get('detail', 'Failed to add category.')}")
        except Exception as e:
            st.error(f"Error: {e}")

st.subheader("❌ Delete Existing Category")
categories = fetch_categories()
if categories:
    selected_category = st.selectbox("Select Category to Delete:", categories)
    if st.button("Delete Selected Category"):
        try:
            res = requests.post(f"{API_BASE_URL}/delete_category", data={"name": selected_category})
            if res.status_code == 200:
                st.success(f"✅ Category '{selected_category}' deleted!")
            else:
                st.warning(f"⚠️ {res.json().get('detail', 'Failed to delete category.')}")
        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.info("No categories available to display.")

# 🛍️ Product Management Section
st.markdown("---")
st.markdown("<h2 style='font-size: 32px; font-style: italic;'>🛍️ Product Management</h2>", unsafe_allow_html=True)

def get_products():
    try:
        return list(product_collection.find({}, {"_id": 0}))
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        return []

st.subheader("📋 Available Products")
products = get_products()
if products:
    st.dataframe(pd.DataFrame(products), use_container_width=True)
else:
    st.info("No products found.")

st.subheader("➕ Add New Product")
with st.form("add_product_form"):
    p_name = st.text_input("Enter Product Name:")
    add_product_btn = st.form_submit_button("Add Product")
    if add_product_btn:
        if not p_name.strip():
            st.warning("Please enter a valid product name.")
        else:
            try:
                if product_collection.find_one({"name": p_name.strip()}):
                    st.warning("Product already exists.")
                else:
                    product_collection.insert_one({"name": p_name.strip()})
                    st.success(f"✅ Product '{p_name}' added successfully!")
            except Exception as e:
                st.error(f"Failed to add product: {e}")

st.subheader("❌ Delete Product")
product_names = [p["name"] for p in get_products()]
if product_names:
    selected_product = st.selectbox("Select Product to Delete:", product_names)
    if st.button("Delete Selected Product"):
        try:
            result = product_collection.delete_one({"name": selected_product})
            if result.deleted_count > 0:
                st.success(f"✅ Product '{selected_product}' deleted successfully!")
            else:
                st.warning("⚠️ Product not found.")
        except Exception as e:
            st.error(f"Failed to delete product: {e}")
else:
    st.info("No products available to delete.")
