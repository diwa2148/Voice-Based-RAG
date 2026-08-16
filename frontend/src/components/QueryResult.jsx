import React from 'react';
import { MessageSquare, ShieldCheck, ShieldAlert, Sparkles, Database } from 'lucide-react';

export default function QueryResult({ result }) {
  if (!result) return null;

  const {
    query,
    transcription,
    answer,
    status,
    chunking_strategy_used,
    guardrail_decisions = {},
    request_id,
    total_latency_ms
  } = result;

  const isSuccess = status === 'success';
  const isRefused = status.includes('refused');

  return (
    <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      
      {/* Header Badges */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={20} color="var(--primary)" />
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#fff' }}>Grounded Answer</h3>
        </div>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <span className={`badge ${isSuccess ? 'badge-success' : 'badge-warning'}`}>
            {isSuccess ? <ShieldCheck size={12} /> : <ShieldAlert size={12} />}
            {status}
          </span>

          <span className="badge badge-primary">
            <Database size={12} />
            Strategy: {chunking_strategy_used}
          </span>
        </div>
      </div>

      {/* Transcription Banner if voice */}
      {transcription && transcription !== query && (
        <div style={{ background: 'rgba(99, 102, 241, 0.08)', border: '1px dashed rgba(99, 102, 241, 0.3)', borderRadius: '10px', padding: '12px 16px', marginBottom: '16px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: '600', color: '#818cf8', textTransform: 'uppercase' }}>STT Transcription (Saaras v3):</span>
          <p style={{ fontSize: '0.9rem', color: '#e0e7ff', marginTop: '2px' }}>"{transcription}"</p>
        </div>
      )}

      {/* Main Answer Box */}
      <div style={{ background: 'rgba(0, 0, 0, 0.25)', borderRadius: '12px', padding: '18px 20px', border: '1px solid var(--bg-card-border)', marginBottom: '16px' }}>
        <p style={{ fontSize: '1rem', color: isRefused ? '#fbbf24' : '#f3f4f6', lineHeight: '1.7', whiteSpace: 'pre-wrap' }}>
          {answer}
        </p>
      </div>

      {/* Footer Info */}
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
        <span>Request ID: <code style={{ fontFamily: 'var(--font-mono)' }}>{request_id?.slice(0, 12)}...</code></span>
        <span>Guardrails Passed: {Object.values(guardrail_decisions).filter(Boolean).length}/3</span>
      </div>
    </div>
  );
}
