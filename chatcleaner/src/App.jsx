import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [comment, setComment] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!comment.trim() || isLoading) return;

    const msgText = comment;
    setComment('');
    setIsLoading(true);

    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const userMessage = {
      text: msgText,
      type: 'user',
      hidden: false,
      timestamp,
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/check/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment: msgText }),
      });
      const data = await res.json();
      const { final_flagged } = data;

      setMessages(prev =>
        prev.map((msg, idx) =>
          idx === prev.length - 1 ? { ...msg, hidden: final_flagged } : msg
        )
      );
    } catch (err) {
      console.error('API Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="chat-box">
        <header className="chat-header">
          <div className="header-icon" />
          <div>
            <h2 className="title">CleanChat AI</h2>
            <p className="subtitle">Protected by AI moderation</p>
          </div>
        </header>

        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="welcome">
              <div className="welcome-icon" />
              <p className="welcome-title">Welcome to CleanChat!</p>
              <p className="welcome-subtitle">
                Start a conversation. Toxic messages will be filtered.
              </p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`message-row ${msg.type === 'user' ? 'right' : 'left'}`}
              >
                <div className={`message-bubble ${msg.hidden ? 'hidden-msg' : ''}`}>
                  {msg.hidden ? (
                    <span className="hidden-text">🚫 Message hidden due to toxic content</span>
                  ) : (
                    <>
                      <p>{msg.text}</p>
                      <span className="timestamp">{msg.timestamp}</span>
                    </>
                  )}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input">
          <input
            type="text"
            placeholder="Type your message..."
            value={comment}
            maxLength={500}
            onChange={(e) => setComment(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            disabled={isLoading}
          />
          <button onClick={handleSend} disabled={!comment.trim() || isLoading}>
            ➤
          </button>
        </div>
        <div className="chat-footer">
          <span>🛡️ AI Protection Active</span>
          <span>{messages.filter((m) => m.hidden).length} messages filtered</span>
        </div>
      </div>
    </div>
  );
}

export default App;
