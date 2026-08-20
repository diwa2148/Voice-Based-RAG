import React from 'react';
import { MessageSquare, ShieldCheck, ShieldAlert, Sparkles, Database, HelpCircle, AlertTriangle, ShieldX, Mic } from 'lucide-react';

export default function QueryResult({ result }) {
  if (!result) return null;

  const {
    query,
    transcription,
    answer,
    status = 'success',
    chunking_strategy_used,
    guardrail_decisions = {},
    request_id,
    total_latency_ms
  } = result;

  const isSuccess = status === 'success';
  const isInsufficientContext = status === 'refused_insufficient_context' || guardrail_decisions.retrieval === false;
  const isInputRefused = status === 'refused_input_guardrail' || guardrail_decisions.input === false;
  const isOutputRefused = status === 'hallucination_refused' || guardrail_decisions.output === false;
  const isRefused = isInsufficientContext || isInputRefused || isOutputRefused || status.includes('refused');

  const isVoiceQuery = Boolean(transcription && transcription.trim());

  // Count passed guardrails
  const totalGuardrailsChecked = Object.keys(guardrail_decisions).length || 3;
  const passedGuardrailsCount = Object.values(guardrail_decisions).filter(val => val === true).length;

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

      {/* Prominently Displayed Submitted Query */}
      <div style={{ background: 'rgba(99, 102, 241, 0.08)', border: '1px solid rgba(99, 102, 241, 0.25)', borderRadius: '12px', padding: '14px 18px', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#818cf8', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <HelpCircle size={14} /> Submitted Query
          </span>
          {isVoiceQuery && (
            <span style={{ fontSize: '0.7rem', color: '#a5b4fc', background: 'rgba(99, 102, 241, 0.2)', padding: '2px 8px', borderRadius: '12px', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <Mic size={10} /> Voice STT (Saaras v3)
            </span>
          )}
        </div>
        <p style={{ fontSize: '1.05rem', fontWeight: '600', color: '#f3f4f6', lineHeight: '1.4' }}>
          "{transcription || query}"
        </p>
      </div>

      {/* Insufficient Context / Guardrail Warning Banners */}
      {isInsufficientContext && (
        <div style={{ background: 'rgba(245, 158, 11, 0.12)', border: '1px solid rgba(245, 158, 11, 0.35)', borderRadius: '10px', padding: '12px 16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <AlertTriangle size={20} color="#fbbf24" style={{ flexShrink: 0 }} />
          <span style={{ fontSize: '0.9rem', fontWeight: '700', color: '#fbbf24' }}>
            ⚠️ Insufficient knowledge-base context
          </span>
        </div>
      )}

      {isInputRefused && (
        <div style={{ background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.35)', borderRadius: '10px', padding: '12px 16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ShieldX size={20} color="#f87171" style={{ flexShrink: 0 }} />
          <span style={{ fontSize: '0.9rem', fontWeight: '700', color: '#fca5a5' }}>
            🛡️ Input Guardrail Triggered
          </span>
        </div>
      )}

      {isOutputRefused && (
        <div style={{ background: 'rgba(245, 158, 11, 0.12)', border: '1px solid rgba(245, 158, 11, 0.35)', borderRadius: '10px', padding: '12px 16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ShieldAlert size={20} color="#fbbf24" style={{ flexShrink: 0 }} />
          <span style={{ fontSize: '0.9rem', fontWeight: '700', color: '#fbbf24' }}>
            ⚠️ Grounding / Hallucination Guardrail Triggered
          </span>
        </div>
      )}

      {/* Main Answer Box */}
      <div style={{ background: 'rgba(0, 0, 0, 0.25)', borderRadius: '12px', padding: '18px 20px', border: '1px solid var(--bg-card-border)', marginBottom: '16px' }}>
        <p style={{ fontSize: '0.98rem', color: isRefused ? '#fbbf24' : '#f3f4f6', lineHeight: '1.7', whiteSpace: 'pre-wrap' }}>
          {answer}
        </p>
      </div>

      {/* Footer Info */}
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-dim)', flexWrap: 'wrap', gap: '8px' }}>
        <span>Request ID: <code style={{ fontFamily: 'var(--font-mono)' }}>{request_id?.slice(0, 12)}...</code></span>
        <span>Guardrails Passed: {passedGuardrailsCount}/{totalGuardrailsChecked}</span>
      </div>
    </div>
  );
}
