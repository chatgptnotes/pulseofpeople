import React from 'react';

interface VersionFooterProps {
  className?: string;
}

export function VersionFooter({ className = '' }: VersionFooterProps) {
  // Version will be auto-incremented with each git push
  const version = '1.2';
  const lastUpdated = '2025-10-29';

  return (
    <footer className={`text-xs text-gray-400 text-center py-2 ${className}`}>
      <div className="container mx-auto">
        <p>
          Pulse of People v{version} | Last Updated: {lastUpdated}
        </p>
      </div>
    </footer>
  );
}

export default VersionFooter;
