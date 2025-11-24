'use client';

import { useState, useEffect } from 'react';
import { Modal } from './ui/Modal';
import { Button } from './ui/Button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/Tabs';
import ResultsTable from './ResultsTable';
import { AlertCircle, Info, Code, Eye } from 'lucide-react';

interface EnhancedConfirmationModalProps {
    sql: string;
    sessionId: string;
    onConfirm: (beforeData: any[], afterData: any[]) => void;
    onCancel: () => void;
}

export default function EnhancedConfirmationModal({
    sql,
    sessionId,
    onConfirm,
    onCancel
}: EnhancedConfirmationModalProps) {
    const [loading, setLoading] = useState(true);
    const [previewData, setPreviewData] = useState<any>(null);
    const [error, setError] = useState('');

    useEffect(() => {
        // Fetch preview data
        const fetchPreview = async () => {
            try {
                const response = await fetch('/api/preview', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: sessionId, sql }),
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch preview');
                }

                const data = await response.json();
                setPreviewData(data);
            } catch (err: any) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchPreview();
    }, [sql, sessionId]);

    const handleConfirm = () => {
        if (previewData) {
            onConfirm(previewData.before_data, previewData.after_data);
        }
    };

    return (
        <Modal isOpen={true} onClose={onCancel} title="Confirm Operation">
            <div className="space-y-4">
                {loading ? (
                    <div className="flex items-center justify-center p-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                        <span className="ml-3 text-muted-foreground">Loading preview...</span>
                    </div>
                ) : error ? (
                    <div className="bg-destructive/10 border border-destructive text-destructive p-4 rounded-md">
                        <p className="font-medium">Error loading preview</p>
                        <p className="text-sm">{error}</p>
                    </div>
                ) : (
                    <>
                        {/* Warnings */}
                        {previewData?.warnings && previewData.warnings.length > 0 && (
                            <div className="bg-yellow-500/10 border border-yellow-500 text-yellow-700 dark:text-yellow-400 p-3 rounded-md flex items-start gap-2">
                                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                                <div className="flex-1">
                                    <p className="font-medium text-sm">Warnings:</p>
                                    <ul className="text-xs mt-1 space-y-1">
                                        {previewData.warnings.map((warning: string, idx: number) => (
                                            <li key={idx}>• {warning}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        )}

                        {/* Tabs */}
                        <Tabs defaultValue="explanation" className="w-full">
                            <TabsList className="grid w-full grid-cols-4">
                                <TabsTrigger value="explanation" className="flex items-center gap-1">
                                    <Info className="w-3 h-3" />
                                    <span className="hidden sm:inline">Explanation</span>
                                </TabsTrigger>
                                <TabsTrigger value="before" className="flex items-center gap-1">
                                    <Eye className="w-3 h-3" />
                                    <span className="hidden sm:inline">Before</span>
                                </TabsTrigger>
                                <TabsTrigger value="after" className="flex items-center gap-1">
                                    <Eye className="w-3 h-3" />
                                    <span className="hidden sm:inline">After</span>
                                </TabsTrigger>
                                <TabsTrigger value="sql" className="flex items-center gap-1">
                                    <Code className="w-3 h-3" />
                                    <span className="hidden sm:inline">SQL</span>
                                </TabsTrigger>
                            </TabsList>

                            <TabsContent value="explanation" className="mt-4 space-y-3">
                                <div className="bg-muted/50 p-4 rounded-md">
                                    <h4 className="font-semibold text-sm mb-2">What will happen:</h4>
                                    <p className="text-sm text-foreground">{previewData?.description}</p>
                                </div>
                                <div className="flex items-center justify-between text-sm bg-primary/5 p-3 rounded-md">
                                    <span className="text-muted-foreground">Affected rows:</span>
                                    <span className="font-semibold">{previewData?.affected_rows || 0}</span>
                                </div>
                            </TabsContent>

                            <TabsContent value="before" className="mt-4">
                                <div className="space-y-2">
                                    <h4 className="text-sm font-semibold text-muted-foreground">Current State</h4>
                                    {previewData?.before_data && previewData.before_data.length > 0 ? (
                                        <div className="max-h-60 overflow-auto border rounded-md">
                                            <ResultsTable results={previewData.before_data} />
                                        </div>
                                    ) : (
                                        <p className="text-sm text-muted-foreground italic p-4 bg-muted/30 rounded-md">
                                            No existing data (new record will be created)
                                        </p>
                                    )}
                                </div>
                            </TabsContent>

                            <TabsContent value="after" className="mt-4">
                                <div className="space-y-2">
                                    <h4 className="text-sm font-semibold text-muted-foreground">Predicted State</h4>
                                    {previewData?.after_data && previewData.after_data.length > 0 ? (
                                        <div className="max-h-60 overflow-auto border rounded-md">
                                            <ResultsTable results={previewData.after_data} highlightChanges={true} />
                                        </div>
                                    ) : (
                                        <p className="text-sm text-muted-foreground italic p-4 bg-muted/30 rounded-md">
                                            Data will be removed
                                        </p>
                                    )}
                                </div>
                            </TabsContent>

                            <TabsContent value="sql" className="mt-4">
                                <div className="bg-muted p-4 rounded-md overflow-x-auto">
                                    <pre className="text-xs font-mono text-foreground"><code>{sql}</code></pre>
                                </div>
                            </TabsContent>
                        </Tabs>

                        {/* Actions */}
                        <div className="flex justify-end space-x-2 pt-4 border-t">
                            <Button variant="outline" onClick={onCancel}>
                                Cancel
                            </Button>
                            <Button onClick={handleConfirm} className="bg-primary hover:bg-primary/90">
                                Confirm & Execute
                            </Button>
                        </div>
                    </>
                )}
            </div>
        </Modal>
    );
}
