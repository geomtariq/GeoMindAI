'use client';

import { useState } from 'react';
import ResultsTable from './ResultsTable';
import SqlPreview from './SqlPreview';

interface Message {
  text: string;
  sender: 'user' | 'ai';
  data?: any;
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [sql, setSql] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessages: Message[] = [...messages, { text: input, sender: 'user' }];
    setMessages(newMessages);
    setInput('');

    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input, session_id: '123' }), // Placeholder session_id
    });
    const data = await response.json();

    if (data.response_type === 'data') {
      setResults(data.data.results);
      setSql(data.data.sql);
    } else {
      setResults([]);
      setSql('');
    }

    setMessages([...newMessages, { text: data.response_type === 'data' ? `Found ${data.data.results.length} results.` : data.data.message, sender: 'ai', data }]);
  };

  return (
    <div>
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
      <SqlPreview sql={sql} />
      <ResultsTable results={results} />
    </div>
  );
}
