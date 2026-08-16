import React, { useState } from 'react';
import { Layers, ChevronDown, ChevronUp, FileText, Tag, Hash } from 'lucide-react';

export default function SourceViewer({ chunks = [] }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!chunks || chunks.length === 0) return null;

  return (
    <div className="glass-panel" style={{ padding: '18px 20px', marginBottom: '24px' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '100%',
          background: 'none',
          border: 'none',
          color: 'var(--text-main)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          padding: '0'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Layers size={20} color="var(--accent)" />
          <span style={{ fontSize: '0.95rem', fontWeight: '600' }}>
            Retrieved Context Chunks ({chunks.length})
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            {isOpen ? 'Collapse' : 'Expand Sources'}
          </span>
          {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </div>
      </button>

      {isOpen && (
        <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {chunks.map((chunk, idx) => (
            <div
              key={chunk.chunk_id || idx}
              style={{
                background: 'rgba(0,0,0,0.2)',
                border: '1px solid var(--bg-card-border)',
                borderRadius: '10px',
                padding: '14px 16px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <FileText size={14} color="var(--primary)" />
                  <span style={{ fontSize: '0.8rem', fontWeight: '600', color: '#e5e7eb', fontFamily: 'var(--font-mono)' }}>
                    {chunk.chunk_id}
                  </span>
                </div>

                <div style={{ display: 'flex', gap: '6px' }}>
                  <span className="badge badge-primary" style={{ fontSize: '0.7rem' }}>
                    <Tag size={10} /> Strategy: {chunk.chunking_strategy}
                  </span>
                  <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>
                    <Hash size={10} /> Score: {(chunk.score || 0).toFixed(4)}
                  </span>
                </div>
              </div>

              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.5', fontFamily: 'var(--font-sans)' }}>
                "{chunk.text}"
              </p>

              {chunk.metadata && Object.keys(chunk.metadata).length > 0 && (
                <div style={{ marginTop: '8px', fontSize: '0.72rem', color: 'var(--text-dim)', display: 'flex', gap: '12px' }}>
                  {chunk.metadata.language && <span>Lang: <b>{chunk.metadata.language}</b></span>}
                  {chunk.metadata.source && <span>Source: <b>{chunk.metadata.source}</b></span>}
                  {chunk.metadata.passage_id && <span>PassageID: <b>{chunk.metadata.passage_id}</b></span>}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
