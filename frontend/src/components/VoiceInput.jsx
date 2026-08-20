import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Send, Sparkles, AlertCircle, Loader2 } from 'lucide-react';

export default function VoiceInput({ onSubmit, isLoading, currentQuery, onError }) {
  const [isRecording, setIsRecording] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Sync displayed text with backend's returned transcription or submitted query
  useEffect(() => {
    if (currentQuery !== undefined && currentQuery !== null) {
      setTextInput(currentQuery);
    }
  }, [currentQuery]);

  const clearAudioState = () => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioBlob(null);
    setAudioUrl(null);
  };

  const startRecording = async () => {
    if (isLoading) return;
    clearAudioState();

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const url = URL.createObjectURL(blob);
        setAudioBlob(blob);
        setAudioUrl(url);
        // Auto submit recorded audio
        onSubmit({ audioBlob: blob });
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Microphone access denied:', err);
      if (onError) {
        onError({
          title: 'Microphone Access Denied',
          message: 'Microphone access is required for voice queries. Please allow microphone permissions or type your question below.'
        });
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (textInput.trim() && !isLoading && !isRecording) {
      clearAudioState();
      onSubmit({ textQuery: textInput.trim() });
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
        
        {/* Interactive Microphone Button */}
        <div style={{ textAlign: 'center' }}>
          <button
            type="button"
            className={`glow-btn ${isRecording ? 'mic-btn-recording' : ''}`}
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isLoading}
            style={{
              width: '80px',
              height: '80px',
              borderRadius: '50%',
              padding: '0',
              justifyContent: 'center',
              fontSize: '1.5rem',
              opacity: isLoading ? 0.6 : 1,
              cursor: isLoading ? 'not-allowed' : 'pointer',
              boxShadow: isRecording ? '0 0 30px #ef4444' : '0 8px 32px var(--primary-glow)'
            }}
          >
            {isRecording ? <MicOff size={36} /> : <Mic size={36} />}
          </button>

          <p style={{ marginTop: '12px', fontSize: '0.875rem', fontWeight: '500', color: isRecording ? '#f87171' : 'var(--text-muted)' }}>
            {isRecording
              ? '🎙 Listening... Click to stop & send'
              : isLoading
              ? '⏳ Processing query & generating answer...'
              : 'Click microphone to speak your question'}
          </p>
        </div>

        <div style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '12px', margin: '4px 0' }}>
          <div style={{ flex: 1, height: '1px', background: 'var(--bg-card-border)' }} />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>OR TYPE YOUR QUERY</span>
          <div style={{ flex: 1, height: '1px', background: 'var(--bg-card-border)' }} />
        </div>

        {/* Text Input Form */}
        <form onSubmit={handleSubmit} style={{ width: '100%', display: 'flex', gap: '12px' }}>
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder={isLoading ? "Processing request..." : "Ask anything about MS MARCO XI, languages, or RAG architecture..."}
            disabled={isLoading || isRecording}
            style={{
              flex: 1,
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid var(--bg-card-border)',
              borderRadius: '12px',
              padding: '14px 18px',
              color: '#fff',
              fontSize: '0.95rem',
              fontFamily: 'var(--font-sans)',
              outline: 'none',
              transition: 'all 0.2s',
              opacity: (isLoading || isRecording) ? 0.6 : 1
            }}
          />
          <button
            type="submit"
            className="glow-btn"
            disabled={isLoading || isRecording || !textInput.trim()}
            style={{
              opacity: (isLoading || isRecording || !textInput.trim()) ? 0.5 : 1,
              cursor: (isLoading || isRecording || !textInput.trim()) ? 'not-allowed' : 'pointer'
            }}
          >
            {isLoading ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
            <span>{isLoading ? 'Processing...' : 'Ask'}</span>
          </button>
        </form>

        {audioUrl && (
          <div style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '12px', background: 'rgba(0,0,0,0.25)', padding: '10px 14px', borderRadius: '10px', border: '1px solid var(--bg-card-border)' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Recorded Audio:</span>
            <audio src={audioUrl} controls style={{ height: '32px', flex: 1 }} />
          </div>
        )}
      </div>
    </div>
  );
}
