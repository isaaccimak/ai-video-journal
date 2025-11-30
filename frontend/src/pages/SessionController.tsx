import React, { useState, useRef, useEffect } from 'react';
import SessionHeader from '../components/session/SessionHeader';
import SessionControls from '../components/session/SessionControls';
import TranscriptView from '../components/TranscriptView';
import QuestionDisplay from '../components/QuestionDisplay';
import HistoryView from '../components/HistoryView';
import CustomVideoPlayer from '../components/CustomVideoPlayer';
import SessionActionButtons from '../components/session/SessionActionButtons';

type SessionStatus = 'idle' | 'recording' | 'review' | 'saving';

interface WebSocketMessage {
    type: 'transcription' | 'question' | 'vad';
    text?: string;
    active?: boolean;
}

const SessionController: React.FC = () => {
    // State
    const [status, setStatus] = useState<SessionStatus>('idle');
    const [recordingTime, setRecordingTime] = useState<number>(0);
    const [transcription, setTranscription] = useState<string>('');
    const [questions, setQuestions] = useState<string[]>([]);
    const [vadActive, setVadActive] = useState<boolean>(false);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [savePath, setSavePath] = useState<string>('');
    const [error, setError] = useState<string>('');

    // Refs
    const videoRef = useRef<HTMLVideoElement>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const recordedChunksRef = useRef<Blob[]>([]);
    const wsRef = useRef<WebSocket | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const processorRef = useRef<ScriptProcessorNode | null>(null);
    const streamRef = useRef<MediaStream | null>(null);

    useEffect(() => {
        console.log("Session Status:", status);
    }, [status]);

    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (status === 'recording') {
            interval = setInterval(() => {
                setRecordingTime(prev => prev + 1);
            }, 1000);
        } else {
            setRecordingTime(0);
        }
        return () => clearInterval(interval);
    }, [status]);



    // Initialize camera on mount
    useEffect(() => {
        let isMounted = true;

        const init = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });

                if (!isMounted) {
                    // Component unmounted while waiting for permission/stream
                    // Stop the stream immediately
                    stream.getTracks().forEach(track => track.stop());
                    return;
                }

                streamRef.current = stream;
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
            } catch (err) {
                if (isMounted) {
                    console.error("Failed to init camera:", err);
                    setError('Could not access camera. Please check permissions.');
                }
            }
        };

        init();

        return () => {
            isMounted = false;
            cleanupResources();
        };
    }, []);

    // Helper function (kept for reference if needed, but logic is now inside useEffect)
    // const initCamera = async () => { ... }

    const cleanupResources = () => {
        // Stop all tracks on unmount
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        if (wsRef.current) {
            wsRef.current.close();
        }
        if (audioContextRef.current) {
            audioContextRef.current.close();
        }
        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
        }
    };

    const startSession = async () => {
        try {
            setError('');
            setTranscription('');
            setQuestions([]);
            recordedChunksRef.current = [];
            setRecordingTime(0); // Reset timer

            // 1. Ensure Stream (reuse or get new)
            let stream = streamRef.current;
            if (!stream || !stream.active) {
                stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                streamRef.current = stream;
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
            }

            // 2. Start Video Recording
            mediaRecorderRef.current = new MediaRecorder(stream!);
            mediaRecorderRef.current.ondataavailable = (event: BlobEvent) => {
                if (event.data.size > 0) {
                    recordedChunksRef.current.push(event.data);
                }
            };
            mediaRecorderRef.current.start();

            // 3. Start Audio Streaming (WebSocket)
            wsRef.current = new WebSocket('ws://localhost:8000/api/ws/audio');

            wsRef.current.onopen = () => {
                setupAudioProcessing(stream!);
            };

            wsRef.current.onmessage = (event: MessageEvent) => {
                const data: WebSocketMessage = JSON.parse(event.data);
                if (data.type === 'transcription' && data.text) {
                    setTranscription(prev => prev + data.text + " ");
                } else if (data.type === 'question' && data.text) {
                    setQuestions(prev => [...prev, data.text!]);
                } else if (data.type === 'vad' && data.active !== undefined) {
                    setVadActive(data.active);
                }
            };

            setStatus('recording');

        } catch (err) {
            console.error("Failed to start session:", err);
            setError('Could not access camera/microphone. Please check permissions.');
        }
    };

    const setupAudioProcessing = (stream: MediaStream) => {
        try {
            const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
            audioContextRef.current = new AudioContextClass({ sampleRate: 16000 });

            if (!audioContextRef.current) return;

            const source = audioContextRef.current.createMediaStreamSource(stream);
            processorRef.current = audioContextRef.current.createScriptProcessor(512, 1, 1);

            processorRef.current.onaudioprocess = (e: AudioProcessingEvent) => {
                if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                    const inputData = e.inputBuffer.getChannelData(0);

                    // Convert float32 to int16
                    const buffer = new ArrayBuffer(inputData.length * 2);
                    const view = new DataView(buffer);
                    for (let i = 0; i < inputData.length; i++) {
                        let s = Math.max(-1, Math.min(1, inputData[i]));
                        view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
                    }
                    wsRef.current.send(buffer);
                }
            };

            source.connect(processorRef.current);
            processorRef.current.connect(audioContextRef.current.destination);
        } catch (e) {
            console.error("Audio processing setup failed:", e);
        }
    };

    const stopSession = () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
            mediaRecorderRef.current.stop();
        }

        // Close WebSocket and AudioContext
        if (wsRef.current) wsRef.current.close();
        if (audioContextRef.current) audioContextRef.current.close();

        // Create preview
        setTimeout(() => {
            const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
            const url = URL.createObjectURL(blob);
            setPreviewUrl(url);
            setStatus('review');
        }, 100); // Small delay to ensure chunks are gathered
    };

    const discardSession = () => {
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        setPreviewUrl(null);
        setTranscription('');
        setQuestions([]);
        recordedChunksRef.current = [];
        setStatus('idle');

        // Re-attach stream to video element if needed (it might have been hidden)
        if (videoRef.current && streamRef.current) {
            videoRef.current.srcObject = streamRef.current;
        }
    };

    const saveSession = async () => {
        if (!savePath) {
            setError('Please enter a folder path to save.');
            return;
        }

        setStatus('saving');
        const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
        const formData = new FormData();
        formData.append('file', blob, `journal_${Date.now()}.mp4`);
        formData.append('save_path', savePath);

        try {
            const response = await fetch('http://localhost:8000/api/save-video', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                discardSession(); // Reset after save
                // Maybe show success toast?
            } else {
                const data = await response.json();
                setError(data.detail || 'Failed to save video');
                setStatus('review');
            }
        } catch (err) {
            console.error("Save error:", err);
            setError('Network error while saving.');
            setStatus('review');
        }
    };

    return (
        <div className="relative w-full flex-1 flex flex-col items-center justify-center overflow-hidden bg-black px-4 py-4">

            {/* Background / Video Preview */}
            <div className="absolute inset-4 w-[calc(100%-2rem)] h-[calc(100%-2rem)] rounded-3xl overflow-hidden ring-1 ring-white/10">

                {/* Live Video (Visible in Idle and Recording) */}
                <video
                    ref={videoRef}
                    autoPlay
                    muted
                    className={`w-full h-full object-cover transform scale-x-[-1] transition-opacity duration-500 ${status === 'review' || status === 'saving' ? 'opacity-0' : 'opacity-100'}`}
                />

                {/* Idle Overlay Text */}
                {/* {status === 'idle' && (
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <div className="text-center animate-fade-in bg-black/30 backdrop-blur-sm p-6 rounded-3xl border border-white/10">
                            <Sparkles className="w-12 h-12 mx-auto mb-4 text-white/50" />
                            <p className="text-2xl font-light tracking-wide text-white/90">Ready to reflect?</p>
                        </div>
                    </div>
                )} */}

                {/* Recorded Video Preview (Visible in Review) */}
                {status === 'review' && previewUrl && (
                    <div className="absolute inset-0 z-[60]">
                        <CustomVideoPlayer
                            src={previewUrl}
                            className="w-full h-full shadow-2xl ring-1 ring-white/10"
                        />
                    </div>
                )}
            </div>

            {/* Overlays */}
            <div className="absolute inset-0 pointer-events-none flex flex-col justify-between p-8 z-[70]">

                {/* Header */}
                <SessionHeader status={status} recordingTime={recordingTime} vadActive={vadActive} />

                {/* Content Area (3-Column Grid) */}
                {/* {(transcription || questions.length > 0) && ( */}
                {status === 'recording' && (
                    <div className="w-full h-full max-h-[70vh] grid grid-cols-12 gap-6 px-8 pointer-events-auto items-start mt-20">
                        <TranscriptView transcription={transcription} />
                        <QuestionDisplay question={questions[questions.length - 1]} />
                        {/* <HistoryView questions={questions} /> */}
                    </div>
                )}

                {/* Footer Controls */}
                <SessionControls
                    status={status}
                    error={error}
                    savePath={savePath}
                    setSavePath={setSavePath}
                    startSession={startSession}
                    stopSession={stopSession}
                    discardSession={discardSession}
                    saveSession={saveSession}
                />

                {/* Top Right Action Buttons */}
                <SessionActionButtons
                    status={status}
                    savePath={savePath}
                    setSavePath={setSavePath}
                    discardSession={discardSession}
                    saveSession={saveSession}
                />
            </div>
        </div>
    );
};

export default SessionController;
