import React, { useEffect, useRef, useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import './App.css';
import FeedbackSelector from "./components/FeedbackSelector";
import Nav from "./components/nav";
import EmotionFeedback from "./components/EmotionFeedback";
import TextFeedback from "./components/textFeedback";
import VoiceFeedback from "./components/VoiceFeedback";
import ChatbotIcon from "./components/ChatbotIcon";
import ChatForm from "./components/ChatForm";
import ChatMessage from "./components/ChatMessage";
import { companyInfo } from "./companyInfo";

function App() {
  const chatBodyRef = useRef();
  const [showChatbot, setShowChatbot] = useState(false);
  const [chatHistory, setChatHistory] = useState([
    {
      hideInChat: true,
      role: "model",
      text: companyInfo,
    },
  ]);

  const generateBotResponse = async (history) => {
    const updateHistory = (text, isError = false) => {
      setChatHistory((prev) => [
        ...prev.filter((msg) => msg.text !== "Thinking..."),
        { role: "model", text, isError },
      ]);
    };

    history = history.map(({ role, text }) => ({ role, parts: [{ text }] }));
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contents: history }),
    };

    const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=${process.env.REACT_APP_GEMINI_API_KEY}`;


    try {
      const response = await fetch(API_URL, requestOptions);
      const data = await response.json();
      if (!response.ok) throw new Error(data?.error.message || "Something went wrong!");

      const apiResponseText = data.candidates[0].content.parts[0].text.replace(/\*\*(.*?)\*\*/g, "$1").trim();
      updateHistory(apiResponseText);
    } catch (error) {
      updateHistory(error.message, true);
    }
  };

  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTo({ top: chatBodyRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [chatHistory]);

  return (
    <Router>
      <div>
        <Nav />
        <Routes>
          <Route path="/" element={<FeedbackSelector />} />
          <Route path="/emotion" element={<EmotionFeedback />} />
          <Route path="/text" element={<TextFeedback />} />
          <Route path="/voice" element={<VoiceFeedback />} />
        </Routes>

        
         <div className={`container ${showChatbot ? "show-chatbot" : ""}`}>
          <button onClick={() => setShowChatbot((prev) => !prev)} id="chatbot-toggler">
            <span className="material-symbols-rounded">AI</span>
            <span className="material-symbols-rounded">close</span>
          </button>

          <div className="chatbot-popup">
            
            <div className="chat-header">
              <div className="header-info">
                <ChatbotIcon />
                <h2 className="logo-text">Chatbot</h2>
              </div>
              <button onClick={() => setShowChatbot((prev) => !prev)} className="material-symbols-rounded">
                x
              </button>
            </div>

            <div ref={chatBodyRef} className="chat-body">
              <div className="message bot-message">
                <ChatbotIcon />
                <p className="message-text">
                  Hey there! <br /> How can I help you today?
                </p>
              </div>

              
              {chatHistory.map((chat, index) => (
                <ChatMessage key={index} chat={chat} />
              ))}
            </div>

            
            <div className="chat-footer">
              <ChatForm chatHistory={chatHistory} setChatHistory={setChatHistory} generateBotResponse={generateBotResponse} />
            </div>
          </div>
        </div>
      </div> 
    </Router>
  );
}

export default App;
