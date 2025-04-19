import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./textFeedback.css";

const TextFeedback = () => {
  const [feedback, setFeedback] = useState("");
  const [category, setCategory] = useState("");
  const [product, setProduct] = useState("");
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [aiSuggestion, setAiSuggestion] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8080/get_categories");
        const data = await res.json();
        setCategories(data.categories || []);
      } catch (err) {
        console.error("Error fetching categories:", err);
      }
    };

    const fetchProducts = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8080/get_products");
        const data = await res.json();
        setProducts(data.products || []);
      } catch (err) {
        console.error("Error fetching products:", err);
      }
    };

    fetchCategories();
    fetchProducts();
  }, []);

  const handleSubmit = async () => {
    if (!feedback.trim() || !category.trim() || !product.trim()) {
      setError("⚠️ Please provide feedback, category, and product.");
      return;
    }

    try {
      // Submit the feedback
      const response = await fetch("http://127.0.0.1:8080/submit_text_feedback", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ feedback, category, product }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Submission failed");

      // Get AI suggestion
      const aiResponse = await fetch("http://127.0.0.1:8080/get_ai_suggestion", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ feedback, category, product }), // ✅ Fixed
      });

      const aiData = await aiResponse.json();
      setAiSuggestion(aiData.suggestion);
      setSubmitted(true);
      setError("");
      setFeedback("");

      setTimeout(() => {
        navigate("/");
      }, 5000);
    } catch (error) {
      console.error("❌ Error submitting feedback:", error.message);
      setError(`❌ ${error.message}`);
    }
  };

  return (
    <div className="page-container">
      <div className="feedback-page">
        <h2 className="feedback-heading">Provide Your Feedback</h2>
        <div className="text-container">
          {!submitted ? (
            <>
              {error && <p className="error-message">{error}</p>}

              <label className="message">Category</label>
              <select
                className="feedback-dropdown"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                <option value="">-- Select Category --</option>
                {categories.map((cat, index) => (
                  <option key={index} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>

              <label className="message">Product</label>
              <select
                className="feedback-dropdown"
                value={product}
                onChange={(e) => setProduct(e.target.value)}
              >
                <option value="">-- Select Product --</option>
                {products.map((prod, index) => (
                  <option key={index} value={prod}>
                    {prod}
                  </option>
                ))}
              </select>

              <label className="message">Message</label>
              <textarea
                className="feedback-input"
                value={feedback}
                onChange={(e) => {
                  setFeedback(e.target.value);
                  setError("");
                }}
                placeholder="Type your feedback here..."
              />
              <button className="submit-btn" onClick={handleSubmit}>
                Submit
              </button>
            </>
          ) : (
            <>
              <p className="success-message">✅ Thank you for your feedback!</p>
              
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TextFeedback;
