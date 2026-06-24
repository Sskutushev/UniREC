import { useState } from 'react';

interface CopyButtonProps {
  label: string;
  value: string;
}

export function CopyButton({ label, value }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  };

  return (
    <button className="ghost-button" type="button" onClick={handleCopy}>
      {copied ? `${label} copied` : label}
    </button>
  );
}
