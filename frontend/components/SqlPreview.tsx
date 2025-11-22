'use client';

import { Code } from 'lucide-react';

interface SqlPreviewProps {
  sql: string;
}

export default function SqlPreview({ sql }: SqlPreviewProps) {
  if (!sql) {
    return null;
  }

  return (
    <div className="mt-4 rounded-md border border-border bg-muted/50 p-4">
      <div className="flex items-center gap-2 mb-2 text-sm font-medium text-muted-foreground">
        <Code className="w-4 h-4" />
        Generated SQL
      </div>
      <pre className="overflow-x-auto rounded bg-black/50 p-3 text-xs font-mono text-primary">
        <code>{sql}</code>
      </pre>
    </div>
  );
}
