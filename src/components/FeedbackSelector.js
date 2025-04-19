import React, { useState } from 'react';
import './FeedbackSelector.css'; // Import the CSS file
import { useNavigate } from 'react-router-dom';

const FeedbackInterface = () => {
  const navigate = useNavigate()
  const [feedbackType, setFeedbackType] = useState(null); // State to store the selected feedback type

  // Function to handle feedback type selection
  const handleFeedbackSelection = (type) => {
    setFeedbackType(type);
  };

  return (
    <div className="feedback-container">
      <h2 className="centered-text">Build better products with<br />Customer Feedback!</h2>
      <p className="slogan">Share Your Thoughts, Feelings, and Voice<br /> Together We Improve!</p>
      <div className="feedback-type-container">
        <button className="feedback-button" onClick={() => navigate("/emotion")}>
        😊 Emotion Feedback
          </button>
        <button className="feedback-button" onClick={() => navigate("/text")}>
        📝 Text Feedback
          </button>
        <button className="feedback-button" onClick={() => navigate("/voice")}>
        🎤 Voice Feedback
          </button>
      </div>
    </div>
  );
};

export default FeedbackInterface;
