import React from 'react';
import { AlertTriangle, XCircle, RefreshCw } from 'lucide-react';

export default function ErrorBanner({ error, onDismiss, onRetry }) {
  if (!error) return null;

  const title = typeof error === 'object' ? error.title || 'Something went wrong' : 'Something went wrong';
  const message = typeof error === 'object' ? error.message || String(error) : String(error);

  return (
    <div
      className="glass-panel"
      style={{
        padding: '16px 20px',
        marginBottom: '24px',
        background: 'rgba(239, 68, 68, 0.1)',
        border: '1px solid rgba(239, 68, 68, 0.35)',
        borderRadius: '14px',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        gap: '16px',
        boxShadow: '0 4px 20px rgba(239, 68, 68, 0.15)'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', flex: 1 }}>
        <AlertTriangle size={22} color="#f87171" style={{ marginTop: '2px', flexShrink: 0 }} />
        <div style={{ flex: 1 }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: '700', color: '#fca5a5', marginBottom: '4px' }}>
            ⚠️ {title}
          </h4>
          <p style={{ fontSize: '0.875rem', color: '#f3f4f6', lineHeight: '1.5' }}>
            {message}
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
        {onRetry && (
          <button
            onClick={onRetry}
            style={{
              background: 'rgba(239, 68, 68, 0.2)',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              color: '#fff',
              padding: '6px 12px',
              borderRadius: '8px',
              fontSize: '0.78rem',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <RefreshCw size={12} />
            <span>Retry</span>
          </button>
        )}
        {onDismiss && (
          <button
            onClick={onDismiss}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '4px',
              display: 'flex',
              alignItems: 'center'
            }}
            title="Dismiss error"
          >
            <XCircle size={18} />
          </button>
        )}
      </div>
    </div>
  );
}
