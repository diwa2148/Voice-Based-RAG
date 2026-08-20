import React, { useState, useEffect } from 'react';
import { Award } from 'lucide-react';
import VoiceInput from './components/VoiceInput';
import StrategySelector from './components/StrategySelector';
import LatencyBreakdown from './components/LatencyBreakdown';
import QueryResult from './components/QueryResult';
import SourceViewer from './components/SourceViewer';
import ErrorBanner from './components/ErrorBanner';
import BenchmarkResult from './components/BenchmarkResult';
import { sendQuery, runBenchmark, checkHealth } from './services/api';

export default function App() {
  const [selectedStrategy, setSelectedStrategy] = useState('auto');
  const [queryResult, setQueryResult] = useState(null);
  const [currentQuery, setCurrentQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [benchmarkLoading, setBenchmarkLoading] = useState(false);
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    checkHealth()
      .then(setHealthStatus)
      .catch(err => console.error('Health check failed:', err));
  }, []);

  const handleQuerySubmit = async ({ audioBlob, textQuery }) => {
    if (isLoading) return; // Prevent duplicate requests

    setIsLoading(true);
    // Clear stale state for clean lifecycle
    setQueryResult(null);
    setErrorMessage(null);
    setBenchmarkData(null);

    try {
      const res = await sendQuery({
        audioBlob,
        textQuery,
        strategyOverride: selectedStrategy
      });
      setQueryResult(res);
      // Synchronize text state with backend returned STT transcription/query
      setCurrentQuery(res.transcription || res.query || textQuery || '');
    } catch (err) {
      setErrorMessage({
        title: 'Query Processing Error',
        message: err.message || 'Unable to process query. Please check your network connection or backend server status.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunBenchmark = async () => {
    if (benchmarkLoading) return;

    setBenchmarkLoading(true);
    setErrorMessage(null);

    try {
      const report = await runBenchmark();
      setBenchmarkData(report);
    } catch (err) {
      setErrorMessage({
        title: 'Benchmark Suite Failed',
        message: err.message || 'Failed to execute performance benchmark suite.'
      });
    } finally {
      setBenchmarkLoading(false);
    }
  };

  const handleVoiceError = (errObj) => {
    setErrorMessage(errObj);
  };

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto', padding: '32px 16px' }}>
      
      {/* Header Banner */}
      <header style={{ textAlign: 'center', marginBottom: '32px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'rgba(99, 102, 241, 0.12)', border: '1px solid rgba(99, 102, 241, 0.25)', borderRadius: '30px', padding: '6px 16px', marginBottom: '12px' }}>
          <Award size={16} color="var(--primary)" />
          <span style={{ fontSize: '0.8rem', fontWeight: '600', color: '#818cf8' }}>HH Goa 2026 Shortlisting Task 2</span>
        </div>
        <h1 style={{ fontSize: '2.25rem', fontWeight: '800', background: 'linear-gradient(135deg, #fff 0%, #a5b4fc 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '8px' }}>
          Voice-Enabled RAG System
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: '640px', margin: '0 auto' }}>
          Multilingual RAG pipeline powered by Sarvam Saaras v3 STT, BAAI BGE-M3, Qdrant Hybrid Retrieval, BGE Reranker & Sarvam-105B LLM over MS MARCO XI.
        </p>
      </header>

      {/* In-Page Error Banner */}
      <ErrorBanner
        error={errorMessage}
        onDismiss={() => setErrorMessage(null)}
      />

      {/* In-Page Benchmark Results Card */}
      <BenchmarkResult
        report={benchmarkData}
        onDismiss={() => setBenchmarkData(null)}
      />

      {/* Chunking Strategy Selector */}
      <StrategySelector
        selectedStrategy={selectedStrategy}
        onSelectStrategy={setSelectedStrategy}
        activeStrategyUsed={queryResult?.chunking_strategy_used}
      />

      {/* Voice & Text Input Component */}
      <VoiceInput
        onSubmit={handleQuerySubmit}
        isLoading={isLoading}
        currentQuery={currentQuery}
        onError={handleVoiceError}
      />

      {/* Latency Breakdown Bar Chart */}
      {queryResult && (
        <LatencyBreakdown
          breakdown={queryResult.latency_breakdown_ms}
          totalMs={queryResult.total_latency_ms}
          onRunBenchmark={handleRunBenchmark}
          benchmarkLoading={benchmarkLoading}
        />
      )}

      {/* Grounded Answer Display */}
      {queryResult && <QueryResult result={queryResult} />}

      {/* Context Source Viewer */}
      {queryResult && (
        <SourceViewer
          chunks={queryResult.retrieved_chunks}
          requestId={queryResult.request_id}
        />
      )}

      {/* Footer */}
      <footer style={{ marginTop: '48px', textAlign: 'center', fontSize: '0.78rem', color: 'var(--text-dim)', borderTop: '1px solid var(--bg-card-border)', paddingTop: '20px' }}>
        <p>Built with FastAPI • React • Qdrant • BM25 • Sarvam Saaras v3 & Sarvam-105B</p>
      </footer>
    </div>
  );
}
