import React, { useState } from 'react';
import './ChatWindow.css'; // Hier kannst du dein CSS für das Chatfenster ablegen

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    // Füge die Benutzernachricht zum Chatverlauf hinzu
    const newMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, newMessage]);
    
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/recipes/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: input })
      });
      
      const data = await response.json();
      // Füge die Antwort des Bots hinzu
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
      </div>
    </div>
  );
};

export default ChatWindow;
