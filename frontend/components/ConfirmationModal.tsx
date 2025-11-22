'use client';

interface ConfirmationModalProps {
  sql: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmationModal({ sql, onConfirm, onCancel }: ConfirmationModalProps) {
  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex',
      justifyContent: 'center', alignItems: 'center'
    }}>
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '5px' }}>
        <h3>Confirm SQL Execution</h3>
        <p>Are you sure you want to execute the following SQL statement?</p>
        <pre><code>{sql}</code></pre>
        <div style={{ marginTop: '10px' }}>
          <button onClick={onConfirm} style={{ marginRight: '10px' }}>Confirm</button>
          <button onClick={onCancel}>Cancel</button>
        </div>
      </div>
    </div>
  );
}
