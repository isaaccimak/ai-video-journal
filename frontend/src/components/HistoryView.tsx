import React from 'react';

interface HistoryViewProps {
    questions: string[];
}

const HistoryView: React.FC<HistoryViewProps> = ({ questions }) => {
    return (
        <div className="col-span-3 glass-panel rounded-2xl p-6 h-full overflow-y-auto backdrop-blur-xl animate-slide-up flex flex-col">
            <h3 className="text-xs font-medium uppercase tracking-widest text-white/50 text-center rounded-4xl mb-4 sticky top-0 bg-black/0 backdrop-blur-sm py-2">Reflections</h3>
            <div className="space-y-4">
                {questions.slice(0, -1).reverse().map((q, i) => (
                    <div key={i} className="p-3 rounded-xl bg-white/5 border border-white/5 text-sm text-white/60 italic">
                        {q}
                    </div>
                ))}
                {questions.length === 0 && (
                    <p className="text-white/30 text-sm italic">No questions yet...</p>
                )}
            </div>
        </div>
    );
};

export default HistoryView;
