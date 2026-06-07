import React from 'react';

interface TestSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

export const TestSection: React.FC<TestSectionProps> = ({ title, description, children }) => {
  return (
    <div className="card" style={{
      marginBottom: '24px',
      padding: '24px',
    }}>
      <h3 style={{
        fontSize: '16px',
        fontWeight: 700,
        margin: '0 0 8px 0',
      }}>
        {title}
      </h3>
      {description && (
        <p style={{
          fontSize: '13px',
          color: 'var(--text-muted)',
          margin: '8px 0 16px 0',
          lineHeight: 1.6,
        }}>
          {description}
        </p>
      )}
      {children}
    </div>
  );
};
