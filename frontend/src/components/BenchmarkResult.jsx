import React from 'react';
import { Award, CheckCircle2, Zap, XCircle } from 'lucide-react';

export default function BenchmarkResult({ report, onDismiss }) {
  if (!report) return null;

  const {
    total_queries_tested,
    bottleneck_stage,
    bottleneck_p50_ms,
    percentiles = {},
    timestamp
  } = report;

  const totalP50 = percentiles.total_latency_ms?.p50;
  const totalP70 = percentiles.total_latency_ms?.p70;
  const totalP100 = percentiles.total_latency_ms?.p100;

  const formatMs = (ms) => {
    if (ms === undefined || ms === null) return 'N/A';
    if (ms >= 1000) return `${(ms / 1000).toFixed(2)}s`;
    return `${ms.toFixed(1)}ms`;
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <CheckCircle2 size={22} color="var(--accent)" />
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#fff' }}>
              Benchmark Suite Results
            </h3>
            {timestamp && (
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Executed: {new Date(timestamp).toLocaleString()}
              </p>
            )}
          </div>
        </div>

        <button
          onClick={onDismiss}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: '4px'
          }}
          title="Dismiss Benchmark Report"
        >
          <XCircle size={20} />
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '16px' }}>
        <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '14px', borderRadius: '10px', border: '1px solid var(--bg-card-border)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Queries Tested</span>
          <span style={{ fontSize: '1.3rem', fontWeight: '800', color: '#fff' }}>{total_queries_tested}</span>
        </div>

        <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '14px', borderRadius: '10px', border: '1px solid var(--bg-card-border)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Dominant Bottleneck</span>
          <span style={{ fontSize: '0.95rem', fontWeight: '700', color: '#fbbf24', display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {bottleneck_stage}
          </span>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>({formatMs(bottleneck_p50_ms)})</span>
        </div>

        <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '14px', borderRadius: '10px', border: '1px solid var(--bg-card-border)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>P50 Latency</span>
          <span style={{ fontSize: '1.3rem', fontWeight: '800', color: 'var(--accent)' }}>{formatMs(totalP50)}</span>
        </div>

        <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '14px', borderRadius: '10px', border: '1px solid var(--bg-card-border)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>P70 / P100 Latency</span>
          <span style={{ fontSize: '1rem', fontWeight: '700', color: '#e5e7eb' }}>
            {formatMs(totalP70)} / {formatMs(totalP100)}
          </span>
        </div>
      </div>
    </div>
  );
}
