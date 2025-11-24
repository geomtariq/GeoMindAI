'use client';

import { useState, useRef, useEffect } from 'react';
import EnhancedConfirmationModal from './EnhancedConfirmationModal';
import UndoRedoControls from './UndoRedoControls';
import { Input } from './ui/Input';
import { Button } from './ui/Button';
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
    text: string;
    sender: 'user' | 'ai';
    data?: any;
}

interface ChatPanelProps {
    isEnabled: boolean;
    sessionId: string;
    onDataReceived: (data: any[], sql: string, message?: string) => void;
    onOperationExecuted: (beforeData: any[], afterData: any[]) => void;
}

export default function ChatPanel({
    isEnabled,
    sessionId,
    onDataReceived,
    onOperationExecuted
}: ChatPanelProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [sqlToApprove, setSqlToApprove] = useState('');
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
        const currentInput = input; // Capture input for closure
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: currentInput, session_id: sessionId }),
            });
            const data = await response.json();

            if (data.response_type === 'data') {
                onDataReceived(data.data.results, data.data.sql, currentInput);
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
                onOperationExecuted(data.before_data || before, data.after_data || after);
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
        setMessages(prev => [...prev, { text: "Operation history updated.", sender: 'ai' }]);
    };

    return (
        <div className="flex flex-col h-full bg-card border-r border-border">
            {/* Header */}
            <div className="flex-shrink-0 border-b border-border p-3 bg-muted/30">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                            <Sparkles className="w-4 h-4 text-primary" />
                        </div>
                        <div>
                            <h2 className="font-semibold text-sm">AI Assistant</h2>
                            <p className="text-xs text-muted-foreground">Powered by Gemini</p>
                        </div>
                    </div>
                    {isEnabled && <UndoRedoControls sessionId={sessionId} onOperationChange={handleOperationChange} />}
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-3 space-y-3 scrollbar-thin scrollbar-thumb-primary/20 scrollbar-track-transparent">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-muted-foreground opacity-50 text-center px-4">
                        <Bot className="w-10 h-10 mb-2" />
                        <p className="text-sm font-medium">Ask me anything about your data</p>
                        <p className="text-xs mt-1">Try: "show all wells" or "create well named test"</p>
                    </div>
                )}
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={cn(
                            "flex gap-2",
                            msg.sender === 'user' ? "justify-end" : "justify-start"
                        )}
                    >
                        {msg.sender === 'ai' && (
                            <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 border border-primary/20">
                                <Bot className="w-3.5 h-3.5 text-primary" />
                            </div>
                        )}
                        <div
                            className={cn(
                                "max-w-[85%] rounded-lg px-3 py-2 text-sm",
                                msg.sender === 'user'
                                    ? "bg-primary text-primary-foreground"
                                    : "bg-muted text-foreground"
                            )}
                        >
                            <p className="whitespace-pre-wrap">{msg.text}</p>
                            {msg.data?.data?.sql && (
                                <div className="mt-2 p-2 bg-background/50 rounded text-xs font-mono overflow-x-auto">
                                    {msg.data.data.sql}
                                </div>
                            )}
                        </div>
                        {msg.sender === 'user' && (
                            <div className="w-7 h-7 rounded-full bg-secondary/10 flex items-center justify-center flex-shrink-0 border border-secondary/20">
                                <User className="w-3.5 h-3.5 text-secondary" />
                            </div>
                        )}
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start gap-2">
                        <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 border border-primary/20">
                            <Bot className="w-3.5 h-3.5 text-primary" />
                        </div>
                        <div className="bg-muted rounded-lg px-3 py-2 flex items-center">
                            <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="flex-shrink-0 p-3 border-t border-border bg-background">
                <div className="flex gap-2">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        disabled={!isEnabled || isLoading}
                        placeholder={isEnabled ? "Ask a question..." : "Connect to database first"}
                        className="flex-1 text-sm"
                    />
                    <Button
                        onClick={handleSend}
                        disabled={!isEnabled || isLoading || !input.trim()}
                        size="icon"
                        className="flex-shrink-0"
                    >
                        {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                    </Button>
                </div>
            </div>

            {/* Enhanced Confirmation Modal */}
            {sqlToApprove && (
                <EnhancedConfirmationModal
                    sql={sqlToApprove}
                    sessionId={sessionId}
                    onConfirm={handleConfirm}
                    onCancel={handleCancel}
                />
            )}
        </div>
    );
}
