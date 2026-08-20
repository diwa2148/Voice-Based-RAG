import React, { useState } from 'react';
import { Layers, ChevronDown, ChevronUp, FileText, Tag, Hash, Globe, FileCode, Key } from 'lucide-react';

export default function SourceViewer({ chunks = [], requestId = '' }) {
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
          {chunks.map((chunk, idx) => {
            const metadata = chunk.metadata || {};
            const language = metadata.language || 'multilingual';
            const source = metadata.source || 'MS MARCO XI';
            const passageId = metadata.passage_id || chunk.chunk_id;
            const queryId = metadata.query_id || requestId;

            return (
              <div
                key={chunk.chunk_id || idx}
                style={{
                  background: 'rgba(0,0,0,0.25)',
                  border: '1px solid var(--bg-card-border)',
                  borderRadius: '12px',
                  padding: '16px'
                }}
              >
                {/* Header Badge Row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    <FileText size={15} color="var(--primary)" />
                    <span style={{ fontSize: '0.8rem', fontWeight: '700', color: '#e5e7eb', fontFamily: 'var(--font-mono)' }}>
                      Chunk ID: {chunk.chunk_id}
                    </span>
                  </div>

                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    <span className="badge badge-primary" style={{ fontSize: '0.7rem' }}>
                      <Tag size={10} /> Strategy: {chunk.chunking_strategy}
                    </span>
                    <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>
                      <Hash size={10} /> Score: {(chunk.score || 0).toFixed(4)}
                    </span>
                  </div>
                </div>

                {/* Chunk Text Content */}
                <p style={{ fontSize: '0.88rem', color: '#e0e7ff', lineHeight: '1.55', fontFamily: 'var(--font-sans)', background: 'rgba(0, 0, 0, 0.2)', padding: '10px 14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.04)', marginBottom: '10px' }}>
                  "{chunk.text}"
                </p>

                {/* Metadata Grid */}
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', flexWrap: 'wrap', gap: '14px', paddingTop: '4px', borderTop: '1px dashed var(--bg-card-border)' }}>
                  <span>Source: <b style={{ color: '#f3f4f6' }}>{source}</b></span>
                  <span>Lang: <b style={{ color: '#f3f4f6' }}>{language}</b></span>
                  {passageId && <span>Passage ID: <b style={{ color: '#f3f4f6' }}>{passageId}</b></span>}
                  {queryId && <span>Query ID: <code style={{ fontFamily: 'var(--font-mono)', color: '#818cf8' }}>{queryId.slice(0, 10)}...</code></span>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
