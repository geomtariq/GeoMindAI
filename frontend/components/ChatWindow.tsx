'use client';

import { useState, useRef, useEffect } from 'react';
import ResultsTable from './ResultsTable';
import SqlPreview from './SqlPreview';
import EnhancedConfirmationModal from './EnhancedConfirmationModal';
import UndoRedoControls from './UndoRedoControls';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from './ui/Card';
import { Input } from './ui/Input';
import { Button } from './ui/Button';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
  text: string;
  sender: 'user' | 'ai';
  data?: any;
}

interface ChatWindowProps {
  isEnabled: boolean;
  sessionId: string;
}

export default function ChatWindow({ isEnabled, sessionId }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [sqlToApprove, setSqlToApprove] = useState('');
  const [beforeData, setBeforeData] = useState<any[]>([]);
  const [afterData, setAfterData] = useState<any[]>([]);
  const [showComparison, setShowComparison] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !isEnabled) return;

    const newMessages: Message[] = [...messages, { text: input, sender: 'user' }];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, session_id: sessionId }),
      });
      const data = await response.json();

      if (data.response_type === 'data') {
        setResults(data.data.results);
        const warningsText = data.data.warnings?.length > 0
          ? ` (${data.data.warnings.length} warnings)`
          : '';
        setMessages(prev => [...prev, {
          text: `Found ${data.data.results.length} results${warningsText}.`,
          sender: 'ai',
          data
        }]);
      } else if (data.response_type === 'sql_approval') {
        setSqlToApprove(data.data.sql);
      } else {
        setResults([]);
        setMessages(prev => [...prev, { text: data.data.message || 'An error occurred.', sender: 'ai', data }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { text: "Failed to send message.", sender: 'ai' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = async (before: any[], after: any[]) => {
    try {
      const response = await fetch('/api/execute_approved', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, sql: sqlToApprove }),
      });
      const data = await response.json();

      if (response.ok) {
        // Show before/after comparison
        setBeforeData(data.before_data || before);
        setAfterData(data.after_data || after);
        setShowComparison(true);

        setMessages(prev => [...prev, {
          text: `✅ ${data.description || 'Operation executed successfully'}`,
          sender: 'ai'
        }]);
      } else {
        setMessages(prev => [...prev, { text: `Execution failed: ${data.detail || 'Unknown error'}`, sender: 'ai' }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { text: "Failed to execute operation.", sender: 'ai' }]);
    } finally {
      setSqlToApprove('');
    }
  };

  const handleCancel = () => {
    setSqlToApprove('');
    setMessages(prev => [...prev, { text: "Write operation cancelled.", sender: 'ai' }]);
  };

  const handleOperationChange = () => {
    // Refresh results or show notification
    setMessages(prev => [...prev, { text: "Operation history updated.", sender: 'ai' }]);
  };

  return (
    <Card className={cn("flex flex-col h-[600px] w-full border-primary/20 shadow-2xl bg-card/80 backdrop-blur-xl transition-opacity duration-500", !isEnabled && "opacity-50 pointer-events-none")}>
      <CardHeader className="border-b border-border/50 p-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Bot className="w-5 h-5 text-primary" />
            AI Assistant
          </CardTitle>
          {isEnabled && <UndoRedoControls sessionId={sessionId} onOperationChange={handleOperationChange} />}
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-primary/20 scrollbar-track-transparent">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground opacity-50">
            <Bot className="w-12 h-12 mb-2" />
            <p>Start a conversation with the AI...</p>
            <p className="text-xs mt-1">Try: "show all wells" or "create well named test"</p>
          </div>
        )}
        {messages.map((msg, index) => (
          <div
            key={index}
            className={cn(
              "flex w-full gap-2",
              msg.sender === 'user' ? "justify-end" : "justify-start"
            )}
          >
            {msg.sender === 'ai' && (
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 border border-primary/20">
                <Bot className="w-4 h-4 text-primary" />
              </div>
            )}
            <div
              className={cn(
                "max-w-[80%] rounded-lg p-3 text-sm",
                msg.sender === 'user'
                  ? "bg-primary text-primary-foreground ml-12"
                  : "bg-muted text-foreground mr-12"
              )}
            >
              <p className="whitespace-pre-wrap">{msg.text}</p>
              {msg.data?.data?.sql && <SqlPreview sql={msg.data.data.sql} />}
            </div>
            {msg.sender === 'user' && (
              <div className="w-8 h-8 rounded-full bg-secondary/10 flex items-center justify-center flex-shrink-0 border border-secondary/20">
                <User className="w-4 h-4 text-secondary" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start gap-2">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 border border-primary/20">
              <Bot className="w-4 h-4 text-primary" />
            </div>
            <div className="bg-muted rounded-lg p-3 flex items-center">
              <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </CardContent>
      <CardFooter className="p-4 border-t border-border/50">
        <div className="flex w-full gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={!isEnabled || isLoading}
            placeholder={isEnabled ? "Ask a question about your data..." : "Please connect to a database first."}
            className="flex-1 bg-background/50"
          />
          <Button
            onClick={handleSend}
            disabled={!isEnabled || isLoading || !input.trim()}
            size="icon"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </Button>
        </div>
      </CardFooter>

      {/* Enhanced Confirmation Modal */}
      {sqlToApprove && (
        <EnhancedConfirmationModal
          sql={sqlToApprove}
          sessionId={sessionId}
          onConfirm={handleConfirm}
          onCancel={handleCancel}
        />
      )}

      {/* Results Display */}
      {results.length > 0 && !showComparison && (
        <div className="fixed inset-x-0 bottom-0 z-40 p-4 bg-background/95 backdrop-blur-lg border-t border-border shadow-2xl max-h-[40vh] overflow-y-auto animate-in slide-in-from-bottom duration-300">
          <div className="container mx-auto max-w-4xl">
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-semibold text-lg">Query Results</h3>
              <Button variant="ghost" size="sm" onClick={() => setResults([])}>Close</Button>
            </div>
            <ResultsTable results={results} />
          </div>
        </div>
      )}

      {/* Before/After Comparison */}
      {showComparison && (
        <div className="fixed inset-x-0 bottom-0 z-40 p-4 bg-background/95 backdrop-blur-lg border-t border-border shadow-2xl max-h-[50vh] overflow-y-auto animate-in slide-in-from-bottom duration-300">
          <div className="container mx-auto max-w-6xl">
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-semibold text-lg">Operation Results</h3>
              <Button variant="ghost" size="sm" onClick={() => setShowComparison(false)}>Close</Button>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h4 className="text-sm font-semibold text-muted-foreground mb-2">Before</h4>
                <div className="border rounded-md overflow-hidden">
                  {beforeData.length > 0 ? (
                    <ResultsTable results={beforeData} />
                  ) : (
                    <p className="text-sm text-muted-foreground p-4 italic">No data</p>
                  )}
                </div>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-muted-foreground mb-2">After</h4>
                <div className="border rounded-md overflow-hidden">
                  {afterData.length > 0 ? (
                    <ResultsTable results={afterData} highlightChanges={true} />
                  ) : (
                    <p className="text-sm text-muted-foreground p-4 italic">No data</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
