from fastapi import FastAPI, Form
import os
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv
from gemini import get_ai_suggestion
from sentiment import get_sentiment  # ✅ Import sentiment analysis

# ✅ Load environment variables
load_dotenv()
app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Twilio Setup
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")  # e.g., 'whatsapp:+14155238886'
        

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# ✅ MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI")
print("Mongo URI:", MONGO_URI)  # Debugging line to check the Mongo URI
mongo_client = MongoClient(MONGO_URI)
feedback_db = mongo_client["FeedbackDB"]
feedback_collection = feedback_db["feedbacks"]
category_collection = feedback_db["feedback_categories"]
product_collection = feedback_db["Products"]

# ✅ Shopkeeper DB
shopkeeper_db = mongo_client["ShopkeepersDB"]
shopkeeper_collection = shopkeeper_db["shopkeepers"]

# ✅ Send WhatsApp Notification
def send_whatsapp_message(message: str):
    try:
        # Fetch the latest registered shopkeeper's phone number
        shopkeeper = shopkeeper_collection.find_one(sort=[('_id', -1)])
        if shopkeeper and "Phone_number" in shopkeeper:
            to_number = f"whatsapp:{shopkeeper['Phone_number']}"
        
        else:
            print("❌ No shopkeeper number found.")
            return

        msg = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_number
        )
        print(f"✅ WhatsApp message sent to {to_number} with SID: {msg.sid}")
    except Exception as e:
        print(f"❌ WhatsApp message failed: {str(e)}")

# ✅ Route: AI Suggestion Only
@app.post("/get_ai_suggestion")
async def get_ai_response(
    feedback: str = Form(...),
    category: str = Form(...),
    product: str = Form(...)
):
    ai_suggestion = get_ai_suggestion(feedback, category, product)
    return {"suggestion": ai_suggestion}

# ✅ Route: Submit Text Feedback
@app.post("/submit_text_feedback")
async def submit_text_feedback(
    feedback: str = Form(...),
    category: str = Form(...),
    product: str = Form(...)
):
    ai_suggestion = get_ai_suggestion(feedback, category, product)
    sentiment = get_sentiment(feedback)

    feedback_data = {
        "type": "text",
        "category": category,
        "product": product,
        "content": feedback,
        "sentiment": sentiment,
        "suggestion": ai_suggestion,
        "timestamp": datetime.utcnow()
    }

    result = feedback_collection.insert_one(feedback_data)
    print(f"✅ Text feedback stored with ID: {result.inserted_id}")

    message = f"📝 New feedback:\nType: Text\nCategory: {category}\nProduct: {product}\nFeedback: {feedback}"
    send_whatsapp_message(message)

    return {
        "message": "Text feedback saved successfully",
        "category": category,
        "product": product,
        "ai_suggestion": ai_suggestion,
        "sentiment": sentiment
    }

# ✅ Route: Submit Voice Feedback
@app.post("/submit_voice_feedback")
async def submit_voice_feedback(
    text: str = Form(...),
    category: str = Form(...),
    product: str = Form(...)
):
    ai_suggestion = get_ai_suggestion(text, category, product)
    sentiment = get_sentiment(text)

    feedback_data = {
        "type": "voice",
        "category": category,
        "product": product,
        "content": text,
        "sentiment": sentiment,
        "suggestion": ai_suggestion,
        "timestamp": datetime.utcnow()
    }

    result = feedback_collection.insert_one(feedback_data)
    print(f"✅ Voice feedback stored with ID: {result.inserted_id}")

    message = f"🎤 New voice feedback:\nCategory: {category}\nProduct: {product}\nFeedback: {text}"
    send_whatsapp_message(message)

    return {
        "message": "Voice feedback saved successfully",
        "category": category,
        "product": product,
        "ai_suggestion": ai_suggestion,
        "sentiment": sentiment
    }

# ✅ Route: Submit Emotion Feedback
@app.post("/submit_emotion_feedback")
async def submit_emotion_feedback(
    emotion: str = Form(...),
    rating: int = Form(...),
    reason_text: str = Form(None),
    reason_voice: str = Form(None),
    category: str = Form(None),
    product: str = Form(None)
):
    feedback_data = {
        "type": "emotion",
        "emotion": emotion,
        "rating": rating,
        "timestamp": datetime.utcnow()
    }

    # Store category and product only if available
    if category:
        feedback_data["category"] = category
    if product:
        feedback_data["product"] = product

    # If negative emotion and reason is provided
    if emotion.lower() in ["angry", "sad"]:
        reason = reason_text or reason_voice
        if reason:
            feedback_data["content"] = reason
            feedback_data["sentiment"] = get_sentiment(reason)
            feedback_data["suggestion"] = get_ai_suggestion(reason, category or "General", product or "General")

    # ✅ Always store the emotion feedback
    result = feedback_collection.insert_one(feedback_data)
    print(f"✅ Emotion feedback stored with ID: {result.inserted_id}")
    print("📄 Stored Document:", feedback_data)

    

    # 📲 Construct WhatsApp message for all emotion feedback
    message = f"😊 New emotion feedback:\nEmotion: {emotion}\nRating: {rating}"

    if category:
        message += f"\nCategory: {category}"
    if product:
        message += f"\nProduct: {product}"
    if "content" in feedback_data:
        message += f"\nReason: {feedback_data['content']}"

    send_whatsapp_message(message)


    return {
        "message": "Emotion feedback saved successfully",
        "emotion": emotion,
        "rating": rating,
        "stored": True,
        "ai_suggestion": feedback_data.get("suggestion"),
        "sentiment": feedback_data.get("sentiment")
    }

# ✅ Route: Get All Categories
@app.get("/get_categories")
async def get_categories():
    categories = list(category_collection.find({}, {"_id": 0, "name": 1}))
    return {"categories": [cat["name"] for cat in categories]}

# ✅ Route: Add Category
@app.post("/add_category")
async def add_category(name: str = Form(...)):
    if not name.strip():
        return {"error": "Category name cannot be empty"}
    exists = category_collection.find_one({"name": name})
    if exists:
        return {"error": "Category already exists"}
    category_collection.insert_one({"name": name})
    return {"message": f"Category '{name}' added"}

# ✅ Route: Delete Category
@app.post("/delete_category")
async def delete_category(name: str = Form(...)):
    result = category_collection.delete_one({"name": name})
    if result.deleted_count == 0:
        return {"error": "Category not found"}
    return {"message": f"Category '{name}' deleted"}

# ✅ Route: Get All Products
@app.get("/get_products")
async def get_products():
    products = list(product_collection.find({}, {"_id": 0, "name": 1, "price": 1}))
    return {"products": products}

# ✅ Route: Add Product
@app.post("/add_product")
async def add_product(name: str = Form(...)):
    if not name.strip():
        return {"error": "Product name cannot be empty"}
    exists = product_collection.find_one({"name": name})
    if exists:
        return {"error": "Product already exists"}
    product_collection.insert_one({"name": name})
    return {"message": f"Product '{name}' added"}

# ✅ Route: Delete Product
@app.post("/delete_product")
async def delete_product(name: str = Form(...)):
    result = product_collection.delete_one({"name": name})
    if result.deleted_count == 0:
        return {"error": "Product not found"}
    return {"message": f"Product '{name}' deleted"}

# ✅ Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)