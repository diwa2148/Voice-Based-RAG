const API_BASE = 'https://voice-based-rag.onrender.com/api';

export async function sendQuery({ audioBlob, textQuery, strategyOverride = 'auto', languageFilter = '' }) {
  const formData = new FormData();
  
  if (audioBlob) {
    formData.append('audio_file', audioBlob, 'voice_query.wav');
  }
  if (textQuery) {
    formData.append('text_query', textQuery);
  }
  if (strategyOverride) {
    formData.append('strategy_override', strategyOverride);
  }
  if (languageFilter) {
    formData.append('language_filter', languageFilter);
  }

  const response = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Query processing failed');
  }

  return response.json();
}

export async function runBenchmark() {
  const response = await fetch(`${API_BASE}/benchmark`, {
    method: 'POST'
  });

  if (!response.ok) {
    throw new Error('Benchmark suite failed');
  }

  return response.json();
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}
