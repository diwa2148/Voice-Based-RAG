import React from 'react';
import { Cpu, CheckCircle2 } from 'lucide-react';

const STRATEGIES = [
  { id: 'auto', label: 'Auto Select (Optimal)' },
  { id: 'fixed_size', label: 'Fixed Size' },
  { id: 'fixed_overlap', label: 'Fixed + Overlap' },
  { id: 'sentence', label: 'Sentence' },
  { id: 'paragraph', label: 'Paragraph' },
  { id: 'recursive', label: 'Recursive' },
  { id: 'semantic', label: 'Semantic' },
  { id: 'metadata_aware', label: 'Metadata-Aware' },
];

export default function StrategySelector({ selectedStrategy, onSelectStrategy, activeStrategyUsed }) {
  return (
    <div className="glass-panel" style={{ padding: '16px 20px', marginBottom: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <Cpu size={20} color="var(--primary)" />
        <div>
          <h4 style={{ fontSize: '0.9rem', fontWeight: '600', color: 'var(--text-main)' }}>Chunking Strategy</h4>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Active: <span style={{ color: 'var(--accent)', fontWeight: '600' }}>{activeStrategyUsed || 'auto'}</span>
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
        {STRATEGIES.map((s) => {
          const isSelected = selectedStrategy === s.id;
          return (
            <button
              key={s.id}
              onClick={() => onSelectStrategy(s.id)}
              style={{
                background: isSelected ? 'var(--primary)' : 'rgba(255,255,255,0.04)',
                color: isSelected ? '#fff' : 'var(--text-muted)',
                border: isSelected ? '1px solid var(--primary)' : '1px solid var(--bg-card-border)',
                borderRadius: '8px',
                padding: '6px 12px',
                fontSize: '0.78rem',
                fontWeight: isSelected ? '600' : '400',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              {s.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
