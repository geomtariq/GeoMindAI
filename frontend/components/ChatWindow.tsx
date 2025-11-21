'use client';

import { useState } from 'react';

interface Message {
  text: string;
  sender: 'user' | 'ai';
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessages: Message[] = [...messages, { text: input, sender: 'user' }];
    setMessages(newMessages);
    setInput('');

    // TODO: Replace with actual API call to the backend service
    // For now, we'll mock a response. In a real scenario, this would
    // be a call to a Next.js API route that proxies to the Python backend.
    const mockResponse = {
        response_type: 'data',
        data: {
            results: [
                { 'well_name': 'Poseidon-1', 'status': 'completed' },
                { 'well_name': 'Poseidon-2', 'status': 'drilling' },
            ],
            sql: "SELECT well_name, status FROM wells WHERE field = 'Poseidon'"
        },
        session_id: '123'
    };

    setMessages([...newMessages, { text: JSON.stringify(mockResponse, null, 2), sender: 'ai' }]);
  };

  return (
    <div style={{ border: '1px solid black', padding: '10px', height: '500px', overflowY: 'scroll' }}>
      <div>
        {messages.map((msg, index) => (
          <div key={index} style={{ textAlign: msg.sender === 'user' ? 'right' : 'left', margin: '5px' }}>
            <p style={{ display: 'inline-block', padding: '5px', borderRadius: '5px', backgroundColor: msg.sender === 'user' ? '#dcf8c6' : '#f1f0f0' }}>
                <strong>{msg.sender}:</strong>
                <pre>{msg.text}</pre>
            </p>
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', marginTop: '10px' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          style={{ flex: 1, padding: '5px' }}
        />
        <button onClick={handleSend} style={{ marginLeft: '5px' }}>Send</button>
      </div>
    </div>
  );
}
