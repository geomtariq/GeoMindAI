'use client';

import { useMemo } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ChartViewProps {
    data: any[];
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function ChartView({ data }: ChartViewProps) {
    const chartData = useMemo(() => {
        if (!data || data.length === 0) return null;

        const firstRow = data[0];
        const keys = Object.keys(firstRow);

        // Try to find suitable columns for charting
        const numericColumns = keys.filter(key =>
            typeof firstRow[key] === 'number'
        );
        const textColumns = keys.filter(key =>
            typeof firstRow[key] === 'string'
        );

        // If we have STATUS and DEPTH (wells data)
        if (keys.includes('STATUS') && keys.includes('DEPTH')) {
            const statusCounts = data.reduce((acc: any, row) => {
                const status = row.STATUS;
                acc[status] = (acc[status] || 0) + 1;
                return acc;
            }, {});

            const avgDepthByStatus = data.reduce((acc: any, row) => {
                const status = row.STATUS;
                if (!acc[status]) {
                    acc[status] = { total: 0, count: 0 };
                }
                acc[status].total += row.DEPTH || 0;
                acc[status].count += 1;
                return acc;
            }, {});

            return {
                statusDistribution: Object.entries(statusCounts).map(([name, value]) => ({
                    name,
                    value
                })),
                avgDepthByStatus: Object.entries(avgDepthByStatus).map(([name, data]: [string, any]) => ({
                    status: name,
                    avgDepth: Math.round(data.total / data.count)
                }))
            };
        }

        // Generic aggregation
        if (textColumns.length > 0 && numericColumns.length > 0) {
            const groupBy = textColumns[0];
            const measureBy = numericColumns[0];

            const aggregated = data.reduce((acc: any, row) => {
                const key = row[groupBy];
                if (!acc[key]) {
                    acc[key] = { total: 0, count: 0 };
                }
                acc[key].total += row[measureBy] || 0;
                acc[key].count += 1;
                return acc;
            }, {});

            return {
                generic: Object.entries(aggregated).map(([name, data]: [string, any]) => ({
                    name,
                    value: Math.round(data.total / data.count)
                }))
            };
        }

        return null;
    }, [data]);

    if (!chartData) {
        return (
            <div className="flex items-center justify-center h-full text-muted-foreground">
                <p>No suitable data for charting</p>
            </div>
        );
    }

    return (
        <div className="h-full overflow-y-auto space-y-8 pr-4">
            {/* Status Distribution Pie Chart */}
            {chartData.statusDistribution && (
                <div className="bg-card border border-border rounded-lg p-6">
                    <h3 className="font-semibold mb-4">Status Distribution</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={chartData.statusDistribution}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                                outerRadius={100}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {chartData.statusDistribution.map((entry: any, index: number) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            )}

            {/* Average Depth by Status Bar Chart */}
            {chartData.avgDepthByStatus && (
                <div className="bg-card border border-border rounded-lg p-6">
                    <h3 className="font-semibold mb-4">Average Depth by Status</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={chartData.avgDepthByStatus}>
                            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                            <XAxis dataKey="status" className="text-xs" />
                            <YAxis className="text-xs" />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'hsl(var(--card))',
                                    border: '1px solid hsl(var(--border))'
                                }}
                            />
                            <Legend />
                            <Bar dataKey="avgDepth" fill="#3b82f6" name="Avg Depth (m)" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            )}

            {/* Generic Chart */}
            {chartData.generic && (
                <div className="bg-card border border-border rounded-lg p-6">
                    <h3 className="font-semibold mb-4">Data Overview</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={chartData.generic}>
                            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                            <XAxis dataKey="name" className="text-xs" />
                            <YAxis className="text-xs" />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'hsl(var(--card))',
                                    border: '1px solid hsl(var(--border))'
                                }}
                            />
                            <Bar dataKey="value" fill="#10b981" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            )}
        </div>
    );
}
