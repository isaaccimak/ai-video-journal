import React from 'react';
import { Square, Save, Trash2, Loader2, AlertCircle } from 'lucide-react';

interface SessionControlsProps {
    status: 'idle' | 'recording' | 'review' | 'saving';
    error: string;
    savePath: string;
    setSavePath: (path: string) => void;
    startSession: () => void;
    stopSession: () => void;
    discardSession: () => void;
    saveSession: () => void;
}

const SessionControls: React.FC<SessionControlsProps> = ({
    status,
    error,
    savePath,
    setSavePath,
    startSession,
    stopSession,
    discardSession,
    saveSession
}) => {
    return (
        <div className="pointer-events-auto flex flex-col items-center gap-4 animate-slide-up">

            {error && (
                <div className="bg-red-500/90 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm mb-2">
                    <AlertCircle className="w-4 h-4" /> {error}
                </div>
            )}

            {status === 'idle' && (
                <button
                    onClick={startSession}
                    className="group relative flex items-center justify-center w-16 h-16 rounded-full bg-white hover:bg-stone-200 transition-all shadow-lg hover:scale-105 active:scale-95"
                >
                    <div className="absolute inset-0 rounded-full border border-white/20 opacity-20 group-hover:opacity-40" />
                    <div className="w-4 h-4 bg-red-500 rounded-xl transition-all duration-300" />
                </button>
            )}

            {status === 'recording' && (
                <button
                    onClick={stopSession}
                    // recording button
                    className="flex items-center cursor-pointer justify-center w-16 h-16 rounded-full bg-red-500 hover:bg-red-600 text-white transition-all shadow-lg hover:scale-105 active:scale-95"
                >
                    <Square className="w-6 h-6 fill-current" />
                </button>
            )}


        </div>
    );
};

export default SessionControls;
