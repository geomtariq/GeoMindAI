'use client';

import { Modal } from './ui/Modal';
import { Button } from './ui/Button';

interface ConfirmationModalProps {
  sql: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmationModal({ sql, onConfirm, onCancel }: ConfirmationModalProps) {
  return (
    <Modal isOpen={true} onClose={onCancel} title="Confirm SQL Execution">
      <div className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Are you sure you want to execute the following SQL statement?
        </p>
        <div className="bg-muted p-4 rounded-md overflow-x-auto">
          <pre className="text-xs font-mono text-foreground"><code>{sql}</code></pre>
        </div>
        <div className="flex justify-end space-x-2">
          <Button variant="outline" onClick={onCancel}>Cancel</Button>
          <Button onClick={onConfirm}>Confirm</Button>
        </div>
      </div>
    </Modal>
  );
}
