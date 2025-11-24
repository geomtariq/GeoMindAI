'use client';

import { useMemo } from 'react';
import { TrendingUp, TrendingDown, Activity, Database } from 'lucide-react';

interface StatsViewProps {
    data: any[];
}

export default function StatsView({ data }: StatsViewProps) {
    const stats = useMemo(() => {
        if (!data || data.length === 0) return null;

        const firstRow = data[0];
        const keys = Object.keys(firstRow);

        // Wells-specific stats
        if (keys.includes('STATUS') && keys.includes('DEPTH')) {
            const totalWells = data.length;
            const activeWells = data.filter(w => w.STATUS === 'ACTIVE').length;
            const inactiveWells = data.filter(w => w.STATUS === 'INACTIVE').length;
            const avgDepth = Math.round(data.reduce((sum, w) => sum + (w.DEPTH || 0), 0) / totalWells);
            const maxDepth = Math.max(...data.map(w => w.DEPTH || 0));
            const minDepth = Math.min(...data.map(w => w.DEPTH || 0));

            return {
                type: 'wells',
                cards: [
                    {
                        title: 'Total Wells',
                        value: totalWells,
                        icon: Database,
                        color: 'text-blue-500',
                        bgColor: 'bg-blue-500/10'
                    },
                    {
                        title: 'Active Wells',
                        value: activeWells,
                        subtitle: `${((activeWells / totalWells) * 100).toFixed(0)}% of total`,
                        icon: TrendingUp,
                        color: 'text-green-500',
                        bgColor: 'bg-green-500/10'
                    },
                    {
                        title: 'Inactive Wells',
                        value: inactiveWells,
                        subtitle: `${((inactiveWells / totalWells) * 100).toFixed(0)}% of total`,
                        icon: TrendingDown,
                        color: 'text-orange-500',
                        bgColor: 'bg-orange-500/10'
                    },
                    {
                        title: 'Average Depth',
                        value: `${avgDepth}m`,
                        subtitle: `Range: ${minDepth}m - ${maxDepth}m`,
                        icon: Activity,
                        color: 'text-purple-500',
                        bgColor: 'bg-purple-500/10'
                    }
                ]
            };
        }

        // Production-specific stats
        if (keys.includes('OIL_VOLUME') || keys.includes('GAS_VOLUME')) {
            const totalOil = data.reduce((sum, p) => sum + (p.OIL_VOLUME || 0), 0);
            const totalGas = data.reduce((sum, p) => sum + (p.GAS_VOLUME || 0), 0);
            const totalWater = data.reduce((sum, p) => sum + (p.WATER_VOLUME || 0), 0);
            const avgOil = Math.round(totalOil / data.length);

            return {
                type: 'production',
                cards: [
                    {
                        title: 'Total Oil Production',
                        value: `${totalOil.toLocaleString()} bbl`,
                        subtitle: `Avg: ${avgOil} bbl/day`,
                        icon: TrendingUp,
                        color: 'text-green-500',
                        bgColor: 'bg-green-500/10'
                    },
                    {
                        title: 'Total Gas Production',
                        value: `${totalGas.toLocaleString()} MCF`,
                        icon: Activity,
                        color: 'text-blue-500',
                        bgColor: 'bg-blue-500/10'
                    },
                    {
                        title: 'Total Water Production',
                        value: `${totalWater.toLocaleString()} bbl`,
                        icon: Database,
                        color: 'text-cyan-500',
                        bgColor: 'bg-cyan-500/10'
                    },
                    {
                        title: 'Production Records',
                        value: data.length,
                        icon: Database,
                        color: 'text-purple-500',
                        bgColor: 'bg-purple-500/10'
                    }
                ]
            };
        }

        // Generic stats
        return {
            type: 'generic',
            cards: [
                {
                    title: 'Total Records',
                    value: data.length,
                    icon: Database,
                    color: 'text-blue-500',
                    bgColor: 'bg-blue-500/10'
                },
                {
                    title: 'Columns',
                    value: keys.length,
                    icon: Activity,
                    color: 'text-green-500',
                    bgColor: 'bg-green-500/10'
                }
            ]
        };
    }, [data]);

    if (!stats) {
        return (
            <div className="flex items-center justify-center h-full text-muted-foreground">
                <p>No data available</p>
            </div>
        );
    }

    return (
        <div className="h-full overflow-y-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4 gap-4">
                {stats.cards.map((card, idx) => {
                    const Icon = card.icon;
                    return (
                        <div
                            key={idx}
                            className="bg-card border border-border rounded-lg p-6 hover:shadow-lg transition-shadow"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className={`w-12 h-12 rounded-lg ${card.bgColor} flex items-center justify-center`}>
                                    <Icon className={`w-6 h-6 ${card.color}`} />
                                </div>
                            </div>
                            <h3 className="text-sm font-medium text-muted-foreground mb-1">
                                {card.title}
                            </h3>
                            <p className="text-2xl font-bold mb-1">
                                {card.value}
                            </p>
                            {card.subtitle && (
                                <p className="text-xs text-muted-foreground">
                                    {card.subtitle}
                                </p>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
