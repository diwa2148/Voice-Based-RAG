import React, { useState, useRef } from 'react';
import { Mic, MicOff, Send, Sparkles, AlertCircle } from 'lucide-react';

export default function VoiceInput({ onSubmit, isLoading }) {
  const [isRecording, setIsRecording] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
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
      alert('Microphone access is required for voice input. You can also type your query below.');
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
    if (textInput.trim() && !isLoading) {
      onSubmit({ textQuery: textInput.trim() });
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
        
        {/* Big Interactive Microphone Button */}
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
              boxShadow: isRecording ? '0 0 30px #ef4444' : '0 8px 32px var(--primary-glow)'
            }}
          >
            {isRecording ? <MicOff size={36} /> : <Mic size={36} />}
          </button>
          <p style={{ marginTop: '12px', fontSize: '0.875rem', color: isRecording ? '#f87171' : 'var(--text-muted)' }}>
            {isRecording ? '● Listening... Click to stop & send' : 'Click microphone to speak your question'}
          </p>
        </div>

        <div style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '12px', margin: '8px 0' }}>
          <div style={{ flex: 1, height: '1px', background: 'var(--bg-card-border)' }} />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>OR TYPE YOUR QUERY</span>
          <div style={{ flex: 1, height: '1px', background: 'var(--bg-card-border)' }} />
        </div>

        {/* Text Input Form */}
        <form onSubmit={handleSubmit} style={{ width: '100%', display: 'flex', gap: '12px' }}>
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Ask anything about MS MARCO XI, languages, or RAG architecture..."
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
              transition: 'all 0.2s'
            }}
          />
          <button
            type="submit"
            className="glow-btn"
            disabled={isLoading || isRecording || !textInput.trim()}
          >
            {isLoading ? <Sparkles className="spin" size={18} /> : <Send size={18} />}
            <span>Ask</span>
          </button>
        </form>

        {audioUrl && (
          <div style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '12px', background: 'rgba(0,0,0,0.2)', padding: '10px 14px', borderRadius: '10px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Recorded Audio:</span>
            <audio src={audioUrl} controls style={{ height: '32px', flex: 1 }} />
          </div>
        )}
      </div>
    </div>
  );
}
