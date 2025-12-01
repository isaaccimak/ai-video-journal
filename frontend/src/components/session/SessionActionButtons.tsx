import React from 'react';
import { Save, Trash2, Loader2 } from 'lucide-react';

interface SessionActionButtonsProps {
    status: 'idle' | 'recording' | 'review' | 'saving';
    savePath: string;
    setSavePath: (path: string) => void;
    discardSession: () => void;
    saveSession: () => void;
}

const SessionActionButtons: React.FC<SessionActionButtonsProps> = ({
    status,
    savePath,
    setSavePath,
    discardSession,
    saveSession
}) => {
    if (status !== 'review' && status !== 'saving') return null;

    return (
        <div className="absolute top-6 right-6 flex items-center gap-4 animate-slide-in-right z-80 pointer-events-auto">
            <div className="glass-panel p-1 rounded-2xl backdrop-blur-md flex items-center h-12">
                <button
                    onClick={discardSession}
                    disabled={status === 'saving'}
                    className="px-4 h-full rounded-xl text-white/80 hover:bg-white/10 hover:text-red-400 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <Trash2 className="w-4 h-4" />
                    <span className="text-sm font-medium">Discard</span>
                </button>
            </div>

            <div className="glass-panel p-1 rounded-2xl flex items-center gap-2 backdrop-blur-md h-12">
                <input
                    type="text"
                    placeholder="Save File Name"
                    value={savePath}
                    onChange={(e) => setSavePath(e.target.value)}
                    disabled={status === 'saving'}
                    className="bg-transparent border-none focus:ring-0 text-white text-sm px-3 h-full w-48 placeholder-white/30 disabled:opacity-50 outline-none"
                />
                <button
                    onClick={saveSession}
                    disabled={status === 'saving'}
                    className="bg-white text-black px-4 h-full rounded-xl hover:bg-stone-200 transition-all flex items-center gap-2 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {status === 'saving' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                    Save
                </button>
            </div>
        </div>
    );
};

export default SessionActionButtons;
