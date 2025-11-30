import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Activity } from 'lucide-react';

interface AudioStreamerProps {
    onTranscription: (text: string) => void;
    onQuestion: (text: string) => void;
}

interface WebSocketMessage {
    type: 'transcription' | 'question';
    text: string;
    vad?: boolean;
}

const AudioStreamer: React.FC<AudioStreamerProps> = ({ onTranscription, onQuestion }) => {
    const [isStreaming, setIsStreaming] = useState<boolean>(false);
    const [vadActive, setVadActive] = useState<boolean>(false);
    const [status, setStatus] = useState<string>('Disconnected');

    const wsRef = useRef<WebSocket | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const processorRef = useRef<ScriptProcessorNode | null>(null);
    const inputRef = useRef<MediaStreamAudioSourceNode | null>(null);

    useEffect(() => {
        return () => {
            stopStreaming();
        };
    }, []);

    const startStreaming = async () => {
        try {
            wsRef.current = new WebSocket('ws://localhost:8000/api/ws/audio');

            wsRef.current.onopen = () => {
                setStatus('Connected');
                setIsStreaming(true);
                startAudioProcessing();
            };

            wsRef.current.onmessage = (event: MessageEvent) => {
                const data: WebSocketMessage = JSON.parse(event.data);
                if (data.type === 'transcription') {
                    onTranscription(data.text);
                } else if (data.type === 'question') {
                    onQuestion(data.text);
                } else if (data.vad !== undefined) {
                    // Optional: Backend VAD status if sent
                }
            };

            wsRef.current.onclose = () => {
                setStatus('Disconnected');
                setIsStreaming(false);
                stopAudioProcessing();
            };

            wsRef.current.onerror = (error: Event) => {
                console.error("WebSocket error:", error);
                setStatus('Error');
            };

        } catch (error) {
            console.error("Error starting stream:", error);
            setStatus('Error starting stream');
        }
    };

    const startAudioProcessing = async () => {
        try {
            const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
            audioContextRef.current = new AudioContextClass({ sampleRate: 16000 });

            if (!audioContextRef.current) return;

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            inputRef.current = audioContextRef.current.createMediaStreamSource(stream);

            // Buffer size 512 for low latency (~32ms at 16kHz)
            processorRef.current = audioContextRef.current.createScriptProcessor(512, 1, 1);

            processorRef.current.onaudioprocess = (e: AudioProcessingEvent) => {
                if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                    const inputData = e.inputBuffer.getChannelData(0);
                    // Simple client-side VAD visualization check (energy based)
                    const energy = inputData.reduce((acc, val) => acc + Math.abs(val), 0) / inputData.length;
                    setVadActive(energy > 0.01);

                    // Convert float32 to int16 PCM
                    const buffer = new ArrayBuffer(inputData.length * 2);
                    const view = new DataView(buffer);
                    for (let i = 0; i < inputData.length; i++) {
                        let s = Math.max(-1, Math.min(1, inputData[i]));
                        view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
                    }
                    wsRef.current.send(buffer);
                }
            };

            inputRef.current.connect(processorRef.current);
            processorRef.current.connect(audioContextRef.current.destination);
        } catch (e) {
            console.error("Audio processing error:", e);
        }
    };

    const stopAudioProcessing = () => {
        if (inputRef.current) inputRef.current.disconnect();
        if (processorRef.current) processorRef.current.disconnect();
        if (audioContextRef.current) audioContextRef.current.close();
    };

    const stopStreaming = () => {
        if (wsRef.current) wsRef.current.close();
        stopAudioProcessing();
        setIsStreaming(false);
        setVadActive(false);
    };

    return (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 flex flex-col gap-4">
            <h2 className="text-xl font-semibold text-stone-800 flex items-center gap-2">
                <Activity className="w-5 h-5" /> Audio Stream
            </h2>

            <div className="flex items-center justify-between bg-stone-50 p-3 rounded-lg">
                <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${status === 'Connected' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-sm text-stone-600">{status}</span>
                </div>
                <div className={`w-4 h-4 rounded-full transition-colors ${vadActive ? 'bg-green-500' : 'bg-stone-300'}`} title="Voice Activity"></div>
            </div>

            {!isStreaming ? (
                <button
                    onClick={startStreaming}
                    className="w-full bg-stone-800 text-white py-2 px-4 rounded-lg hover:bg-stone-700 transition-colors flex items-center justify-center gap-2"
                >
                    <Mic className="w-4 h-4" /> Start Streaming
                </button>
            ) : (
                <button
                    onClick={stopStreaming}
                    className="w-full bg-red-500 text-white py-2 px-4 rounded-lg hover:bg-red-600 transition-colors flex items-center justify-center gap-2"
                >
                    <MicOff className="w-4 h-4" /> Stop Streaming
                </button>
            )}
        </div>
    );
};

export default AudioStreamer;
