import React from 'react';

interface TranscriptViewProps {
    transcription: string;
}

const TranscriptView: React.FC<TranscriptViewProps> = ({ transcription }) => {
    return (
        <div className="col-span-3 glass-panel rounded-2xl p-6 h-full overflow-y-auto backdrop-blur-xl animate-slide-up flex flex-col">
            <h3 className="text-xs font-medium uppercase tracking-widest text-white/50 text-center rounded-4xl mb-4 sticky top-0 bg-black/0 backdrop-blur-sm py-2">Transcript</h3>
            <p className="text-sm leading-relaxed font-light text-white/80 whitespace-pre-wrap">
                {transcription}
            </p>
        </div>
    );
};

export default TranscriptView;
