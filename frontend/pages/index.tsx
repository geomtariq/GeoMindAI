'use client';

import { useState, useEffect } from 'react';
import DbConnection from '../components/DbConnection';
import ChatPanel from '../components/ChatPanel';
import DataVisualizationPanel from '../components/DataVisualizationPanel';
import ResizablePanels from '../components/ui/ResizablePanels';
import { v4 as uuidv4 } from 'uuid';

export default function Home() {
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [connectionError, setConnectionError] = useState('');
  const [currentData, setCurrentData] = useState<any[]>([]);
  const [currentSql, setCurrentSql] = useState('');
  const [beforeData, setBeforeData] = useState<any[]>([]);
  const [afterData, setAfterData] = useState<any[]>([]);
  const [lastReadMessage, setLastReadMessage] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    setSessionId(uuidv4());
  }, []);

  const handleConnect = async (config: any) => {
    try {
      const response = await fetch('/api/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...config, session_id: sessionId }),
      });

      if (response.ok) {
        setIsConnected(true);
        setConnectionError('');
      } else {
        const data = await response.json();
        setConnectionError(data.detail || 'Connection failed');
      }
    } catch (error) {
      setConnectionError('Failed to connect to the server');
    }
  };

  const handleDataReceived = (data: any[], sql: string, message?: string) => {
    setCurrentData(data);
    setCurrentSql(sql);
    setBeforeData([]);
    setAfterData([]);
    if (message) {
      setLastReadMessage(message);
    }
  };

  const handleOperationExecuted = (before: any[], after: any[], sql?: string) => {
    setBeforeData(before);
    setAfterData(after);
    if (sql) {
      setCurrentSql(sql);
    }
    // Optionally refresh current data
    if (after && after.length > 0) {
      setCurrentData(after);
    }
  };

  const handleRefresh = async () => {
    if (!lastReadMessage) return;

    setIsRefreshing(true);
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: lastReadMessage, session_id: sessionId }),
      });
      const data = await response.json();

      if (data.response_type === 'data') {
        setCurrentData(data.data.results);
        setCurrentSql(data.data.sql);
        setBeforeData([]);
        setAfterData([]);
      }
    } catch (error) {
      console.error("Refresh failed:", error);
    } finally {
      setIsRefreshing(false);
    }
  };

  if (!isConnected) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
              GeoMind AI
            </h1>
            <p className="text-muted-foreground">
              AI-Powered Geoscience Data Platform
            </p>
          </div>
          <DbConnection onConnect={handleConnect} sessionId={sessionId} />
          {connectionError && (
            <div className="mt-4 p-3 bg-destructive/10 border border-destructive text-destructive rounded-md text-sm">
              {connectionError}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen overflow-hidden bg-background">
      {/* Header */}
      <header className="h-14 border-b border-border bg-card flex items-center px-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center">
            <span className="text-white font-bold text-sm">GM</span>
          </div>
          <div>
            <h1 className="font-bold text-lg">GeoMind AI</h1>
            <p className="text-xs text-muted-foreground">Geoscience Data Platform</p>
          </div>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span>Connected</span>
          </div>
        </div>
      </header>

      {/* Main Content - Two Panel Layout */}
      <div className="h-[calc(100vh-3.5rem)]">
        <ResizablePanels
          leftPanel={
            <ChatPanel
              isEnabled={isConnected}
              sessionId={sessionId}
              onDataReceived={handleDataReceived}
              onOperationExecuted={handleOperationExecuted}
            />
          }
          rightPanel={
            <DataVisualizationPanel
              data={currentData}
              sql={currentSql}
              beforeData={beforeData}
              afterData={afterData}
              onRefresh={lastReadMessage ? handleRefresh : undefined}
              isRefreshing={isRefreshing}
            />
          }
          defaultLeftSize={35}
        />
      </div>
    </div>
  );
}
