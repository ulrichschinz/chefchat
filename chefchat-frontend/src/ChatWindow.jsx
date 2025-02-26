import React, { useState, useContext } from 'react';
import './ChatWindow.css';
import { sendAuthenticatedRequest } from './api';
import { AuthContext } from './AuthContext';

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const { authTokens } = useContext(AuthContext);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, newMessage]);

    setLoading(true);
    try {
      const data = await sendAuthenticatedRequest('http://127.0.0.1:8000/recipes/chat/', 'POST', { message: input }, authTokens?.token);
      const botMessage = { sender: 'bot', text: data.response };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    }
    setLoading(false);
    setInput('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  const { setAuthTokens } = useContext(AuthContext);

  const handleLogout = () => {
    setAuthTokens(null);
    try {
      const data = sendAuthenticatedRequest('http://127.0.0.1:8000/logout/', 'POST', { message: 'logout' }, authTokens?.token);
    } catch (error) {
      console.error('Error sending message:', error);
    }
    document.cookie = 'authTokens=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  };

  return (
    <div className="chat-window">
      <div className="chat-history">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.sender}`}>
            <div className="message-text">{msg.text}</div>
          </div>
        ))}
        {loading && <div className="chat-message bot">Lädt...</div>}
      </div>
      <div className="chat-input">
        <input 
          type="text" 
          placeholder="Deine Nachricht..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button onClick={sendMessage}>Senden</button>
        <button onClick={handleLogout}>Logout</button>
      </div>
    </div>
  );
};

export default ChatWindow;
