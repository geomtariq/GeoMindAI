'use client';

import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';

interface ResultsTableProps {
  results: any[];
}

export default function ResultsTable({ results }: ResultsTableProps) {
  if (!results || results.length === 0) {
    return null;
  }

  const headers = Object.keys(results[0]);

  return (
    <Card className="mt-4 border-primary/20 bg-card/50 backdrop-blur-sm overflow-hidden">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-medium text-primary">Query Results</CardTitle>
      </CardHeader>
      <CardContent className="p-0 overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-xs uppercase bg-muted/50 text-muted-foreground">
            <tr>
              {headers.map((header) => (
                <th key={header} className="px-6 py-3 font-medium tracking-wider">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            {results.map((row, index) => (
              <tr key={index} className="bg-card hover:bg-muted/50 transition-colors">
                {headers.map((header) => (
                  <td key={header} className="px-6 py-4 whitespace-nowrap text-foreground/90">
                    {row[header]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}
