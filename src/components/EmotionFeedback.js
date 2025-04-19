import React, { useRef, useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./EmotionFeedback.css";

const EmotionFeedback = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const navigate = useNavigate();

  const [emotion, setEmotion] = useState(null);
  const [captured, setCaptured] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [countdown, setCountdown] = useState(null);
  const [userFeedback, setUserFeedback] = useState("");
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [feedbackMode, setFeedbackMode] = useState(null);
  const [isRecording, setIsRecording] = useState(false);

  const [category, setCategory] = useState("");
  const [product, setProduct] = useState("");
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);

  useEffect(() => {
    startWebcam();
    fetchCategories();
    fetchProducts();
  }, []);

  const startWebcam = () => {
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      })
      .catch((err) => console.error("Webcam error:", err));
  };

  const startCaptureCountdown = () => {
    setCountdown(3);
    let timeLeft = 3;
    const interval = setInterval(() => {
      timeLeft -= 1;
      setCountdown(timeLeft);
      if (timeLeft === 0) {
        clearInterval(interval);
        captureImage();
      }
    }, 1000);
  };

  const captureImage = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext("2d");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageURL = canvas.toDataURL("image/jpeg");
    setCapturedImage(imageURL);
    setCaptured(true);
    setCountdown(null);

    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }

    sendToBackend(canvas);
  };

  const sendToBackend = (canvas) => {
    canvas.toBlob(async (blob) => {
      const formData = new FormData();
      formData.append("image", blob, "captured.jpg");

      try {
        const res = await axios.post("http://127.0.0.1:5000/detect_emotion", formData);
        const detectedEmotion = res.data.emotion;
        setEmotion(detectedEmotion);

        const isNegative = detectedEmotion === "angry" || detectedEmotion === "sad";

        if (!isNegative) {
          await sendEmotionFeedbackToDB(detectedEmotion); // submit immediately for non-negatives
          setTimeout(() => navigate("/"), 2000);
        }

      } catch (err) {
        console.error("Detection error:", err);
        setEmotion("Error detecting emotion");
      }
    }, "image/jpeg");
  };

  const getStarRating = (emotion) => {
    const ratings = { angry: 1, sad: 2, neutral: 3, surprise: 4, happy: 5 };
    return ratings[emotion] || 0;
  };

  const fetchCategories = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8080/get_categories");
      setCategories(res.data.categories || []);
    } catch (err) {
      console.error("Category fetch error:", err);
    }
  };

  const fetchProducts = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8080/get_products");
      setProducts(res.data.products || []);
    } catch (err) {
      console.error("Product fetch error:", err);
    }
  };

  const handleMicClick = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return alert("Speech recognition not supported.");

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.onstart = () => setIsRecording(true);
    recognition.onresult = (event) => {
      setUserFeedback(event.results[0][0].transcript);
      setIsRecording(false);
    };
    recognition.onerror = () => setIsRecording(false);
    recognition.onend = () => setIsRecording(false);
    recognition.start();
  };

  const sendEmotionFeedbackToDB = async (detectedEmotion, reason = null, reasonType = null) => {
    const rating = getStarRating(detectedEmotion);
    const formData = new URLSearchParams();
    formData.append("emotion", detectedEmotion);
    formData.append("rating", rating.toString());

    if (reason && reasonType) {
      formData.append(reasonType === "text" ? "reason_text" : "reason_voice", reason);
      formData.append("category", category);
      formData.append("product", product);
    }

    try {
      await axios.post("http://127.0.0.1:8080/submit_emotion_feedback", formData);
      setFeedbackSubmitted(true);
      setTimeout(() => navigate("/"), 2000);
    } catch (error) {
      console.error("Submit error:", error.message);
    }
  };

  return (
    <div className="emotion-container">
      <h2>Emotion Feedback</h2>

      {capturedImage ? (
        <img src={capturedImage} alt="Captured" className="captured-image" />
      ) : (
        <video ref={videoRef} autoPlay />
      )}
      <canvas ref={canvasRef} style={{ display: "none" }}></canvas>

      {countdown !== null ? (
        <h3 className="countdown">{countdown}</h3>
      ) : !captured ? (
        <button onClick={startCaptureCountdown}>Capture</button>
      ) : (
        <>
          <h3>Detected Emotion: {emotion || "Detecting..."}</h3>
          <div className="stars">
            {Array.from({ length: getStarRating(emotion) }, (_, i) => (
              <span key={i} className="star">⭐</span>
            ))}
          </div>

          {(emotion === "angry" || emotion === "sad") && !feedbackSubmitted && !feedbackMode && (
            <div className="feedback-options">
              <p>Would you like to give feedback?</p>
              <button onClick={() => setFeedbackMode("text")}>Text</button>
              <button onClick={() => setFeedbackMode("voice")}>Voice</button>
            </div>
          )}

          {(feedbackMode === "text" || feedbackMode === "voice") && !feedbackSubmitted && (
            <>
              <div className="dropdowns">
                <select value={category} onChange={(e) => setCategory(e.target.value)}>
                  <option value="">Select Category</option>
                  {categories.map((cat, i) => <option key={i} value={cat}>{cat}</option>)}
                </select>

                <select value={product} onChange={(e) => setProduct(e.target.value)}>
                  <option value="">Select Product</option>
                  {products.map((prod, i) => <option key={i} value={prod}>{prod}</option>)}
                </select>
              </div>

              <div className="feedback-box">
                <textarea
                  placeholder={
                    feedbackMode === "voice"
                      ? "Your transcribed feedback will appear here..."
                      : "Tell us why you felt this way..."
                  }
                  value={userFeedback}
                  onChange={(e) => setUserFeedback(e.target.value)}
                  className="text-feedback"
                ></textarea>

                {feedbackMode === "voice" && (
                  <button onClick={handleMicClick} className="mic-button">🎤</button>
                )}
              </div>

              {isRecording && <p>Recording... Speak now 🎙️</p>}
              <button onClick={() =>
                sendEmotionFeedbackToDB(emotion, userFeedback, feedbackMode)
              }>
                Submit Feedback
              </button>
            </>
          )}

          {feedbackSubmitted && <p>✅ Thank you for your feedback! Redirecting...</p>}
        </>
      )}
    </div>
  );
};

export default EmotionFeedback;
