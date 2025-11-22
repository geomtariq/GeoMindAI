'use client';

import { useState } from 'react';
import ResultsTable from './ResultsTable';
import SqlPreview from './SqlPreview';
import ConfirmationModal from './ConfirmationModal';

interface Message {
  text: string;
  sender: 'user' | 'ai';
  data?: any;
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [sqlToApprove, setSqlToApprove] = useState('');

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
      setMessages([...newMessages, { text: `Found ${data.data.results.length} results.`, sender: 'ai', data }]);
    } else if (data.response_type === 'sql_approval') {
      setSqlToApprove(data.data.sql);
    } else {
      setResults([]);
      setMessages([...newMessages, { text: data.data.message, sender: 'ai', data }]);
    }
  };

  const handleConfirm = async () => {
    // TODO: Create a new API endpoint to execute the approved SQL
    console.log("SQL Approved:", sqlToApprove);
    setSqlToApprove('');
    setMessages([...messages, { text: "Write operation successful.", sender: 'ai' }]);
  };

  const handleCancel = () => {
    setSqlToApprove('');
    setMessages([...messages, { text: "Write operation cancelled.", sender: 'ai' }]);
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
      {sqlToApprove && (
        <ConfirmationModal
          sql={sqlToApprove}
          onConfirm={handleConfirm}
          onCancel={handleCancel}
        />
      )}
      <SqlPreview sql={messages.find(m => m.data?.data?.sql)?.data.data.sql || ''} />
      <ResultsTable results={results} />
    </div>
  );
}
