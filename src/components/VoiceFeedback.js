import "./VoiceFeedback.css";
import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const VoiceFeedback = () => {
  const [recording, setRecording] = useState(false);
  const [text, setText] = useState("");
  const [originalSpeech, setOriginalSpeech] = useState("");
  const [aiSuggestion, setAiSuggestion] = useState("");
  const [audioUrl, setAudioUrl] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [category, setCategory] = useState("");
  const [product, setProduct] = useState("");
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);

  const navigate = useNavigate();
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recognitionRef = useRef(null);

  // Fetch categories and products from backend
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const res = await fetch("https://server-backend-nry1.onrender.com/get_categories");
        const data = await res.json();
        setCategories(data.categories || []);
      } catch (err) {
        console.error("Error fetching categories:", err);
      }
    };

    const fetchProducts = async () => {
      try {
        const res = await fetch("https://server-backend-nry1.onrender.com/get_products");
        const data = await res.json();
        setProducts(data.products || []);
      } catch (err) {
        console.error("Error fetching products:", err);
      }
    };

    fetchCategories();
    fetchProducts();
  }, []);

  

  const startSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser does not support speech recognition. Try Chrome.");
      return;
    }

    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.lang = "en-US";
    recognitionRef.current.continuous = true;
    recognitionRef.current.interimResults = true;

    recognitionRef.current.onresult = (event) => {
      let speechText = "";
      for (let i = 0; i < event.results.length; i++) {
        speechText += event.results[i][0].transcript + " ";
      }
      setText(speechText.trim());
    };

    recognitionRef.current.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
    };

    recognitionRef.current.start();
  };

  const startRecording = () => {
    setRecording(true);
    setText("");
    setOriginalSpeech("");
    startSpeechRecognition();

    navigator.mediaDevices.getUserMedia({ audio: true })
      .then((stream) => {
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = [];

        mediaRecorderRef.current.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
        };

        mediaRecorderRef.current.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
          const url = URL.createObjectURL(audioBlob);
          setAudioUrl(url);
        };

        mediaRecorderRef.current.start();
      })
      .catch((error) => console.error("Mic access error:", error));
  };

  const stopRecording = () => {
    setRecording(false);
    setOriginalSpeech(text);
    if (mediaRecorderRef.current) mediaRecorderRef.current.stop();
    if (recognitionRef.current) recognitionRef.current.stop();
  };

  const handleSubmit = async () => {
    if (!text.trim() || !category || !product) {
      alert("Please complete all fields (speech, category, product).");
      return;
    }

    try {
      const response = await fetch("https://server-backend-nry1.onrender.com/submit_voice_feedback", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ text, category, product }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Submission failed");

      setAiSuggestion(data.ai_suggestion);
      
      setSubmitted(true);

      setTimeout(() => navigate("/"), 2000);

    } catch (error) {
      console.error("Voice feedback error:", error.message);
    }
  };

  return (
    <div className="page-container">
      {submitted ? (
        <div className="thank-you-wrapper">
          <div className="thank-you-card">
            <h3 className="thank-you-title">✅ Thank you for your feedback!</h3>
            <p className="redirect-text">You'll be redirected shortly...</p>
          </div>
        </div>
      ) : (
        <div className="voice-feedback">
          <h1 className="voice-heading">Voice Feedback</h1>
  
          <div className="dropdowns">
            <select value={category} onChange={(e) => setCategory(e.target.value)} className="dropdown">
              <option value="">Select Category</option>
              {categories.map((cat, index) => (
                <option key={index} value={cat}>{cat}</option>
              ))}
            </select>
  
            <select value={product} onChange={(e) => setProduct(e.target.value)} className="dropdown">
              <option value="">Select Product</option>
              {products.map((prod, index) => (
                <option key={index} value={prod.name}>
                {prod.name} - ₹{prod.price}
              </option>
              ))}
            </select>
          </div>

          
  
          <div className={`mic-button ${recording ? "recording" : ""}`} onClick={recording ? stopRecording : startRecording}>
            🎤
          </div>
  
          {recording && (
            <div className="waveform">
              <span></span><span></span><span></span><span></span><span></span>
            </div>
          )}
  
          {audioUrl && (
            <audio controls>
              <source src={audioUrl} type="audio/wav" />
              Your browser does not support the audio element.
            </audio>
          )}
  
          <textarea
            className="text-box"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Your speech will appear here..."
          />
  
          <button onClick={handleSubmit}>Submit Feedback</button>
        </div>
      )}
    </div>
  );
  
};

export default VoiceFeedback;