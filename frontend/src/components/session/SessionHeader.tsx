import React, { useState } from 'react';
import { Mic, Settings, ChevronDown, Check } from 'lucide-react';

interface SessionHeaderProps {
    status: 'idle' | 'recording' | 'review' | 'saving';
    recordingTime: number;
    vadActive: boolean;
    audioDevices: MediaDeviceInfo[];
    selectedDeviceId: string;
    onDeviceChange: (deviceId: string) => void;
}

const SessionHeader: React.FC<SessionHeaderProps> = ({
    status,
    recordingTime,
    vadActive,
    audioDevices,
    selectedDeviceId,
    onDeviceChange
}) => {
    const [isDeviceMenuOpen, setIsDeviceMenuOpen] = useState(false);

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="flex justify-between items-start animate-slide-up w-full">
            <div className="flex items-center gap-4">
                <div className="glass-panel px-4 py-2 rounded-full flex items-center gap-2 text-white/80">
                    <div className={`w-2 h-2 rounded-full ${status === 'recording' ? 'bg-red-500 animate-pulse' : 'bg-stone-500'}`} />
                    <span className="text-xs font-medium tracking-wider uppercase">
                        {status === 'recording' ? 'Recording' : status === 'review' ? 'Review' : 'Idle'}
                    </span>
                </div>

                {/* Audio Device Selector */}
                {status === 'idle' && audioDevices.length > 0 && (
                    <div className="relative pointer-events-auto z-50">
                        <button
                            onClick={() => setIsDeviceMenuOpen(!isDeviceMenuOpen)}
                            className="glass-panel px-3 py-2 rounded-full flex items-center gap-2 text-white/80 hover:bg-white/10 transition-colors cursor-pointer"
                        >
                            <Settings className="w-3 h-3 text-white/50" />
                            <span className="text-xs font-medium max-w-[120px] truncate">
                                {audioDevices.find(d => d.deviceId === selectedDeviceId)?.label || 'Select Mic'}
                            </span>
                            <ChevronDown className="w-3 h-3 text-white/50" />
                        </button>

                        {isDeviceMenuOpen && (
                            <>
                                <div
                                    className="fixed inset-0 z-40"
                                    onClick={() => setIsDeviceMenuOpen(false)}
                                />
                                <div className="absolute top-full left-0 mt-2 w-64 glass-panel rounded-xl overflow-hidden z-50 flex flex-col py-1 animate-fade-in backdrop-blur-xl bg-black/60 border border-white/10 shadow-2xl">
                                    <div className="px-3 py-2 text-[10px] uppercase tracking-wider text-white/40 font-semibold border-b border-white/5 mb-1">
                                        Select Microphone
                                    </div>
                                    {audioDevices.map(device => (
                                        <button
                                            key={device.deviceId}
                                            onClick={() => {
                                                onDeviceChange(device.deviceId);
                                                setIsDeviceMenuOpen(false);
                                            }}
                                            className={`px-3 py-2.5 text-left text-xs flex items-center justify-between hover:bg-white/10 transition-colors cursor-pointer ${selectedDeviceId === device.deviceId ? 'text-white bg-white/5' : 'text-white/70'}`}
                                        >
                                            <span className="truncate flex-1 pr-2">
                                                {device.label || `Microphone ${device.deviceId.slice(0, 5)}...`}
                                            </span>
                                            {selectedDeviceId === device.deviceId && <Check className="w-3 h-3 text-green-400" />}
                                        </button>
                                    ))}
                                </div>
                            </>
                        )}
                    </div>
                )}
            </div>

            <div className="flex items-center gap-3">
                {status === 'recording' && (
                    <div className="glass-panel px-4 py-1 rounded-full text-white/90 font-mono text-sm tracking-widest">
                        {formatTime(recordingTime)}
                    </div>
                )}

                {(status === 'recording' || status === 'idle') && (
                    <div className={`glass-panel px-3 py-1 rounded-full transition-all duration-300 ${vadActive ? 'bg-green-500/20 border-green-500/50' : ''}`}>
                        <Mic className={`w-4 h-4 ${vadActive ? 'text-green-400' : 'text-white/40'}`} />
                    </div>
                )}
            </div>
        </div>
    );
};

export default SessionHeader;
