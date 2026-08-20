import React from 'react';
import { Zap, Clock, BarChart2, Flame } from 'lucide-react';

const STAGE_LABELS = {
  stt_ms: 'STT (Sarvam Saaras v3)',
  input_guardrail_ms: 'Input Guardrail',
  query_embedding_ms: 'Query Embedding (BGE-M3)',
  bm25_ms: 'BM25 Lexical Retrieval',
  dense_retrieval_ms: 'Dense Retrieval (Qdrant)',
  hybrid_fusion_ms: 'Hybrid Fusion (RRF)',
  retrieval_guardrail_ms: 'Retrieval Guardrail',
  reranking_ms: 'Reranker (BGE)',
  llm_generation_ms: 'LLM Generation (Sarvam-105B)',
  output_guardrail_ms: 'Output Guardrail'
};

export default function LatencyBreakdown({ breakdown = {}, totalMs = 0, onRunBenchmark, benchmarkLoading }) {
  const total = totalMs || Object.values(breakdown).reduce((a, b) => a + b, 0);

  // Helper to format ms into human-readable seconds or ms
  const formatTime = (ms) => {
    if (ms >= 1000) {
      return `${(ms / 1000).toFixed(2)}s`;
    }
    return `${ms.toFixed(1)}ms`;
  };

  // Find dominant bottleneck
  let maxStageKey = '';
  let maxStageVal = 0;
  Object.entries(breakdown).forEach(([key, val]) => {
    if (val > maxStageVal) {
      maxStageVal = val;
      maxStageKey = key;
    }
  });

  const dominantLabel = STAGE_LABELS[maxStageKey] || maxStageKey;
  const dominantPct = total > 0 ? ((maxStageVal / total) * 100).toFixed(1) : 0;

  return (
    <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
      
      {/* Header Banner */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Zap size={22} color="var(--warning)" />
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
              Latency Breakdown
              <span style={{ fontSize: '1.1rem', color: '#fbbf24', background: 'rgba(245, 158, 11, 0.15)', padding: '2px 10px', borderRadius: '20px', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
                ⚡ Total: {formatTime(total)}
              </span>
            </h3>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              Target: &lt;200ms (Retrieval Phase) • 9 Measured Pipeline Stages
            </p>
          </div>
        </div>

        <button
          onClick={onRunBenchmark}
          disabled={benchmarkLoading}
          className="glow-btn"
          style={{ padding: '8px 14px', fontSize: '0.8rem' }}
        >
          <BarChart2 size={14} />
          <span>{benchmarkLoading ? 'Running Benchmark...' : 'Run Benchmark'}</span>
        </button>
      </div>

      {/* Dominant Bottleneck Summary Banner */}
      {maxStageVal > 0 && (
        <div style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: '10px', padding: '10px 14px', marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Flame size={16} color="#f87171" />
            <span style={{ fontSize: '0.8rem', fontWeight: '600', color: '#fca5a5' }}>
              Dominant Bottleneck:
            </span>
            <span style={{ fontSize: '0.82rem', fontWeight: '700', color: '#fff' }}>
              {dominantLabel}
            </span>
          </div>
          <span style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', fontWeight: '700', color: '#f87171' }}>
            {formatTime(maxStageVal)} ({dominantPct}%)
          </span>
        </div>
      )}

      {/* Stage Bars */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {Object.entries(STAGE_LABELS).map(([stageKey, label]) => {
          const val = breakdown[stageKey] || 0.0;
          const pct = total > 0 ? Math.min(100, (val / total) * 100) : 0;
          const isBottleneck = stageKey === maxStageKey && val > 0;

          return (
            <div key={stageKey}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '3px' }}>
                <span style={{ color: isBottleneck ? '#fca5a5' : 'var(--text-muted)', fontWeight: isBottleneck ? '600' : '400' }}>
                  {label} {isBottleneck ? '🔥' : ''}
                </span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: '600', color: isBottleneck ? '#f87171' : val > 500 ? 'var(--warning)' : '#e5e7eb' }}>
                  {formatTime(val)} ({pct.toFixed(1)}%)
                </span>
              </div>
              <div className="latency-bar-container">
                <div
                  className="latency-bar-fill"
                  style={{
                    width: `${Math.max(1.5, pct)}%`,
                    background: isBottleneck
                      ? 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)'
                      : val > 500
                      ? 'linear-gradient(90deg, #f59e0b 0%, #ef4444 100%)'
                      : 'linear-gradient(90deg, #6366f1 0%, #10b981 100%)'
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
