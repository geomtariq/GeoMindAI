'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/Tabs';
import DataTable from './visualizations/DataTable';
import ChartView from './visualizations/ChartView';
import StatsView from './visualizations/StatsView';
import { Table2, BarChart3, Activity, FileDown, RefreshCw } from 'lucide-react';
import { Button } from './ui/Button';
import { cn } from '@/lib/utils';

interface DataVisualizationPanelProps {
    data: any[];
    sql?: string;
    beforeData?: any[];
    afterData?: any[];
    onRefresh?: () => void;
    isRefreshing?: boolean;
}

export default function DataVisualizationPanel({
    data,
    sql,
    beforeData,
    afterData,
    onRefresh,
    isRefreshing = false
}: DataVisualizationPanelProps) {
    const [activeView, setActiveView] = useState('table');

    const exportToCSV = () => {
        if (!data || data.length === 0) return;

        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(h => row[h]).join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `geomind_export_${new Date().getTime()}.csv`;
        a.click();
    };

    const hasData = data && data.length > 0;

    return (
        <div className="flex flex-col h-full bg-background">
            {/* Header */}
            <div className="flex-shrink-0 border-b border-border p-4 bg-card">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="font-semibold text-lg">Data Visualization</h2>
                        <p className="text-xs text-muted-foreground mt-0.5">
                            {hasData ? `${data.length} records` : 'No data to display'}
                        </p>
                    </div>
                    <div className="flex items-center gap-2">
                        {onRefresh && (
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={onRefresh}
                                disabled={isRefreshing}
                                className="flex items-center gap-2"
                            >
                                <RefreshCw className={cn("w-4 h-4", isRefreshing && "animate-spin")} />
                                <span className="hidden sm:inline">Refresh</span>
                            </Button>
                        )}
                        {hasData && (
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={exportToCSV}
                                className="flex items-center gap-2"
                            >
                                <FileDown className="w-4 h-4" />
                                <span className="hidden sm:inline">Export CSV</span>
                            </Button>
                        )}
                    </div>
                </div>
            </div>

            {/* Content */}
            {!hasData ? (
                <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground p-8">
                    <BarChart3 className="w-16 h-16 mb-4 opacity-20" />
                    <p className="text-lg font-medium">No Data Yet</p>
                    <p className="text-sm text-center mt-2 max-w-md">
                        Start by asking a question in the chat panel. Try queries like:
                    </p>
                    <div className="mt-4 space-y-2 text-sm">
                        <div className="bg-muted/50 px-3 py-2 rounded-md font-mono">"show all wells"</div>
                        <div className="bg-muted/50 px-3 py-2 rounded-md font-mono">"count active wells"</div>
                        <div className="bg-muted/50 px-3 py-2 rounded-md font-mono">"average depth by status"</div>
                    </div>
                </div>
            ) : (
                <Tabs value={activeView} onValueChange={setActiveView} className="flex-1 flex flex-col">
                    <TabsList className="mx-4 mt-4 grid w-auto grid-cols-3 self-start">
                        <TabsTrigger value="table" className="flex items-center gap-2">
                            <Table2 className="w-4 h-4" />
                            <span className="hidden sm:inline">Table</span>
                        </TabsTrigger>
                        <TabsTrigger value="charts" className="flex items-center gap-2">
                            <BarChart3 className="w-4 h-4" />
                            <span className="hidden sm:inline">Charts</span>
                        </TabsTrigger>
                        <TabsTrigger value="stats" className="flex items-center gap-2">
                            <Activity className="w-4 h-4" />
                            <span className="hidden sm:inline">Stats</span>
                        </TabsTrigger>
                    </TabsList>

                    <div className="flex-1 overflow-hidden">
                        <TabsContent value="table" className="h-full m-0 p-4">
                            <DataTable data={data} />
                        </TabsContent>

                        <TabsContent value="charts" className="h-full m-0 p-4">
                            <ChartView data={data} />
                        </TabsContent>

                        <TabsContent value="stats" className="h-full m-0 p-4">
                            <StatsView data={data} />
                        </TabsContent>
                    </div>
                </Tabs>
            )}

            {/* SQL Query Display */}
            {sql && (
                <div className="flex-shrink-0 border-t border-border p-3 bg-muted/30">
                    <p className="text-xs text-muted-foreground mb-1">Last Query:</p>
                    <div className="bg-background px-3 py-2 rounded text-xs font-mono overflow-x-auto">
                        {sql}
                    </div>
                </div>
            )}
        </div>
    );
}
