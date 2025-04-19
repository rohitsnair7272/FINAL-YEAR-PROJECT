import React from 'react';
import ReactDOM from 'react-dom/client';  // Import the new root API
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));  // Create a root element
root.render(<App />);  // Use render with the root
