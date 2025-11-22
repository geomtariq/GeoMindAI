'use client';

interface SqlPreviewProps {
  sql: string;
}

export default function SqlPreview({ sql }: SqlPreviewProps) {
  if (!sql) {
    return null;
  }

  return (
    <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#eee', border: '1px solid #ccc' }}>
      <h4>Generated SQL:</h4>
      <pre><code>{sql}</code></pre>
    </div>
  );
}
