'use client';

import { useState, useEffect } from 'react';
import { Button } from './ui/Button';
import { Undo2, Redo2, History, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface UndoRedoControlsProps {
    sessionId: string;
    onOperationChange?: () => void;
}

export default function UndoRedoControls({ sessionId, onOperationChange }: UndoRedoControlsProps) {
    const [canUndo, setCanUndo] = useState(false);
    const [canRedo, setCanRedo] = useState(false);
    const [history, setHistory] = useState<any[]>([]);
    const [showHistory, setShowHistory] = useState(false);
    const [loading, setLoading] = useState(false);

    // Fetch history
    const fetchHistory = async () => {
        try {
            const response = await fetch(`/api/history?session_id=${sessionId}&limit=50`);
            const data = await response.json();

            if (data.status === 'success') {
                setHistory(data.operations);
                setCanUndo(data.operations.length > 0);
            }
        } catch (error) {
            console.error('Failed to fetch history:', error);
        }
    };

    useEffect(() => {
        fetchHistory();
        // Poll for history updates every 5 seconds
        const interval = setInterval(fetchHistory, 5000);
        return () => clearInterval(interval);
    }, [sessionId]);

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.ctrlKey && e.key === 'z' && !e.shiftKey) {
                e.preventDefault();
                handleUndo();
            } else if (e.ctrlKey && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
                e.preventDefault();
                handleRedo();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [canUndo, canRedo]);

    const handleUndo = async () => {
        if (!canUndo || loading) return;

        setLoading(true);
        try {
            const response = await fetch('/api/undo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId }),
            });

            const data = await response.json();

            if (data.status === 'success') {
                // Show notification
                showNotification(`Undone: ${data.message}`, 'success');
                setCanRedo(true);
                await fetchHistory();
                onOperationChange?.();
            } else {
                showNotification(data.message, 'error');
            }
        } catch (error) {
            showNotification('Failed to undo operation', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleRedo = async () => {
        if (!canRedo || loading) return;

        setLoading(true);
        try {
            const response = await fetch('/api/redo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId }),
            });

            const data = await response.json();

            if (data.status === 'success') {
                showNotification(`Redone: ${data.message}`, 'success');
                setCanUndo(true);
                await fetchHistory();
                onOperationChange?.();
            } else {
                showNotification(data.message, 'error');
                setCanRedo(false);
            }
        } catch (error) {
            showNotification('Failed to redo operation', 'error');
        } finally {
            setLoading(false);
        }
    };

    const showNotification = (message: string, type: 'success' | 'error') => {
        // Simple notification - could be enhanced with a toast library
        const notification = document.createElement('div');
        notification.className = `fixed bottom-4 right-4 p-4 rounded-md shadow-lg z-50 ${type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
            }`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    };

    const formatTimestamp = (timestamp: string) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);

        if (seconds < 60) return 'just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        return date.toLocaleDateString();
    };

    return (
        <div className="flex items-center gap-2">
            {/* Undo/Redo Buttons */}
            <div className="flex items-center gap-1 bg-muted/50 rounded-md p-1">
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleUndo}
                    disabled={!canUndo || loading}
                    title="Undo (Ctrl+Z)"
                    className="h-8 w-8 p-0"
                >
                    <Undo2 className="w-4 h-4" />
                </Button>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleRedo}
                    disabled={!canRedo || loading}
                    title="Redo (Ctrl+Y)"
                    className="h-8 w-8 p-0"
                >
                    <Redo2 className="w-4 h-4" />
                </Button>
            </div>

            {/* History Toggle */}
            <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowHistory(!showHistory)}
                className="h-8 px-2 flex items-center gap-1"
            >
                <History className="w-4 h-4" />
                <span className="text-xs hidden sm:inline">History</span>
                <ChevronRight className={cn("w-3 h-3 transition-transform", showHistory && "rotate-90")} />
            </Button>

            {/* History Panel */}
            {showHistory && (
                <div className="fixed right-4 top-20 w-80 max-h-96 bg-card border border-border rounded-lg shadow-2xl z-50 overflow-hidden flex flex-col">
                    <div className="p-3 border-b border-border bg-muted/50">
                        <h3 className="font-semibold text-sm">Operation History</h3>
                        <p className="text-xs text-muted-foreground">{history.length} operations</p>
                    </div>
                    <div className="flex-1 overflow-y-auto p-2 space-y-1">
                        {history.length === 0 ? (
                            <p className="text-sm text-muted-foreground text-center py-8">No operations yet</p>
                        ) : (
                            history.slice().reverse().map((op, idx) => (
                                <div
                                    key={op.id}
                                    className="p-2 rounded-md hover:bg-muted/50 transition-colors cursor-pointer text-sm"
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="flex-1 min-w-0">
                                            <p className="font-medium text-xs truncate">{op.description}</p>
                                            <p className="text-xs text-muted-foreground">{formatTimestamp(op.timestamp)}</p>
                                        </div>
                                        <span className={cn(
                                            "text-xs px-1.5 py-0.5 rounded",
                                            op.operation_type === 'INSERT' && "bg-green-500/20 text-green-700 dark:text-green-400",
                                            op.operation_type === 'UPDATE' && "bg-blue-500/20 text-blue-700 dark:text-blue-400",
                                            op.operation_type === 'DELETE' && "bg-red-500/20 text-red-700 dark:text-red-400"
                                        )}>
                                            {op.operation_type}
                                        </span>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
