import { useState, useEffect } from 'react';
import ChatWindow from '../components/ChatWindow';
import DbConnection from '../components/DbConnection';
import Head from 'next/head';

export default function Home() {
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    // Generate a unique session ID when the component mounts
    setSessionId(Math.random().toString(36).substring(7));
  }, []);

  const handleConnect = async (details: any) => {
    setError('');
    try {
      const response = await fetch('/api/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...details, session_id: sessionId }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to connect');
      }

      setIsConnected(true);
    } catch (err: any) {
      setError(err.message);
      throw err; // Re-throw to be caught by the component
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-primary selection:text-primary-foreground">
      <Head>
        <title>GeoMind AI | Intelligent Database Assistant</title>
        <meta name="description" content="AI-powered database analysis tool" />
      </Head>

      <main className="container mx-auto p-4 md:p-8 max-w-5xl space-y-8">
        <header className="text-center space-y-2 mb-12">
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent animate-pulse">
            GeoMind AI
          </h1>
          <p className="text-muted-foreground text-lg md:text-xl max-w-2xl mx-auto">
            Your intelligent assistant for Oracle database analysis and visualization.
          </p>
        </header>

        <div className="grid gap-8 animate-in slide-in-from-bottom-10 duration-700 fade-in">
          {!isConnected ? (
            <DbConnection onConnect={handleConnect} isConnected={isConnected} />
          ) : (
            <div className="space-y-4">
              <div className="flex justify-between items-center bg-card/50 p-4 rounded-lg border border-border">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
                  <span className="font-medium">Connected to Database</span>
                </div>
                <button
                  onClick={() => setIsConnected(false)}
                  className="text-sm text-muted-foreground hover:text-destructive transition-colors"
                >
                  Disconnect
                </button>
              </div>
              <ChatWindow isEnabled={isConnected} sessionId={sessionId} />
            </div>
          )}
        </div>

        {error && (
          <div className="fixed bottom-4 right-4 p-4 bg-destructive/10 border border-destructive text-destructive rounded-md shadow-lg animate-in slide-in-from-right">
            <p className="font-medium">Connection Error</p>
            <p className="text-sm opacity-90">{error}</p>
          </div>
        )}
      </main>
    </div>
  );
}
