import React, { useState } from 'react';
import { Zap, Clock, Activity, BarChart2 } from 'lucide-react';

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
  const [showBenchmark, setShowBenchmark] = useState(false);

  const total = totalMs || Object.values(breakdown).reduce((a, b) => a + b, 0);

  return (
    <div className="glass-panel" style={{ padding: '20px', marginBottom: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Zap size={20} color="var(--warning)" />
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#fff' }}>
              Latency Breakdown <span style={{ color: total < 200 ? 'var(--accent)' : 'var(--warning)', marginLeft: '8px' }}>⚡ {total.toFixed(1)} ms</span>
            </h3>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Target: &lt;200ms | 9 Pipeline Stages Measured</p>
          </div>
        </div>

        <button
          onClick={onRunBenchmark}
          disabled={benchmarkLoading}
          className="glow-btn"
          style={{ padding: '8px 14px', fontSize: '0.8rem' }}
        >
          <BarChart2 size={14} />
          <span>{benchmarkLoading ? 'Running Benchmark...' : 'Run P50/P70/P100 Benchmark'}</span>
        </button>
      </div>

      {/* Stage Bars */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {Object.entries(STAGE_LABELS).map(([stageKey, label]) => {
          const val = breakdown[stageKey] || 0.0;
          const pct = total > 0 ? Math.min(100, (val / total) * 100) : 0;
          return (
            <div key={stageKey}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '3px' }}>
                <span style={{ color: 'var(--text-muted)' }}>{label}</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: '600', color: val > 50 ? 'var(--warning)' : '#e5e7eb' }}>
                  {val.toFixed(2)} ms ({pct.toFixed(0)}%)
                </span>
              </div>
              <div className="latency-bar-container">
                <div
                  className="latency-bar-fill"
                  style={{
                    width: `${Math.max(2, pct)}%`,
                    background: val > 50 ? 'linear-gradient(90deg, #f59e0b 0%, #ef4444 100%)' : 'linear-gradient(90deg, #6366f1 0%, #10b981 100%)'
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
