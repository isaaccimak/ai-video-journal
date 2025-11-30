import React from 'react';
import { Mic } from 'lucide-react';

interface SessionHeaderProps {
    status: 'idle' | 'recording' | 'review' | 'saving';
    recordingTime: number;
    vadActive: boolean;
}

const SessionHeader: React.FC<SessionHeaderProps> = ({ status, recordingTime, vadActive }) => {
    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="flex justify-between items-start animate-slide-up px-5">
            <div className="glass-panel px-4 py-2 rounded-full flex items-center gap-2 text-white/80">
                <div className={`w-2 h-2 rounded-full ${status === 'recording' ? 'bg-red-500 animate-pulse' : 'bg-stone-500'}`} />
                <span className="text-xs font-medium tracking-wider uppercase">
                    {status === 'recording' ? 'Recording' : status === 'review' ? 'Review' : 'Idle'}
                </span>
            </div>

            <div className="flex items-center gap-3">
                {status === 'recording' && (
                    <div className={`glass-panel px-3 py-1 rounded-full transition-all duration-300 ${vadActive ? 'bg-green-500/20 border-green-500/50' : ''}`}>
                        <Mic className={`w-4 h-4 ${vadActive ? 'text-green-400' : 'text-white/40'}`} />
                    </div>
                )}

                {status === 'recording' && (
                    <div className="glass-panel px-4 py-1 rounded-full text-white/90 font-mono text-sm tracking-widest">
                        {formatTime(recordingTime)}
                    </div>
                )}
            </div>
        </div>
    );
};

export default SessionHeader;
