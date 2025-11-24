'use client';

import { useState, useMemo } from 'react';
import { Input } from '../ui/Input';
import { Search, ArrowUpDown } from 'lucide-react';

interface DataTableProps {
    data: any[];
}

export default function DataTable({ data }: DataTableProps) {
    const [searchTerm, setSearchTerm] = useState('');
    const [sortColumn, setSortColumn] = useState<string | null>(null);
    const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

    const columns = useMemo(() => {
        if (!data || data.length === 0) return [];
        return Object.keys(data[0]);
    }, [data]);

    const handleSort = (column: string) => {
        if (sortColumn === column) {
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
        } else {
            setSortColumn(column);
            setSortDirection('asc');
        }
    };

    const filteredAndSortedData = useMemo(() => {
        let result = [...data];

        // Filter
        if (searchTerm) {
            result = result.filter(row =>
                Object.values(row).some(val =>
                    String(val).toLowerCase().includes(searchTerm.toLowerCase())
                )
            );
        }

        // Sort
        if (sortColumn) {
            result.sort((a, b) => {
                const aVal = a[sortColumn];
                const bVal = b[sortColumn];

                if (typeof aVal === 'number' && typeof bVal === 'number') {
                    return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
                }

                const aStr = String(aVal).toLowerCase();
                const bStr = String(bVal).toLowerCase();
                return sortDirection === 'asc'
                    ? aStr.localeCompare(bStr)
                    : bStr.localeCompare(aStr);
            });
        }

        return result;
    }, [data, searchTerm, sortColumn, sortDirection]);

    return (
        <div className="flex flex-col h-full">
            {/* Search */}
            <div className="mb-4">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                        placeholder="Search data..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                    />
                </div>
            </div>

            {/* Table */}
            <div className="flex-1 overflow-auto border rounded-lg">
                <table className="w-full text-sm">
                    <thead className="bg-muted/50 sticky top-0 z-10">
                        <tr>
                            {columns.map((col) => (
                                <th
                                    key={col}
                                    className="text-left p-3 font-semibold cursor-pointer hover:bg-muted transition-colors"
                                    onClick={() => handleSort(col)}
                                >
                                    <div className="flex items-center gap-2">
                                        {col}
                                        <ArrowUpDown className="w-3 h-3 text-muted-foreground" />
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {filteredAndSortedData.map((row, idx) => (
                            <tr
                                key={idx}
                                className="border-t border-border hover:bg-muted/30 transition-colors"
                            >
                                {columns.map((col) => (
                                    <td key={col} className="p-3">
                                        {String(row[col])}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Footer */}
            <div className="mt-4 text-xs text-muted-foreground">
                Showing {filteredAndSortedData.length} of {data.length} records
            </div>
        </div>
    );
}
