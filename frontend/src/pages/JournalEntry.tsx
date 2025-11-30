import React from 'react';
import { BookOpen, MessageCircle } from 'lucide-react';

interface JournalEntryProps {
    transcription: string;
    questions: string[];
}

const JournalEntry: React.FC<JournalEntryProps> = ({ transcription, questions }) => {
    return (
        <div className="flex flex-col gap-6 w-full">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 flex flex-col gap-4 min-h-[200px]">
                <h2 className="text-xl font-semibold text-stone-800 flex items-center gap-2">
                    <BookOpen className="w-5 h-5" /> Live Transcription
                </h2>
                <div className="text-stone-700 leading-relaxed whitespace-pre-wrap">
                    {transcription || <span className="text-stone-400 italic">Start speaking to see transcription...</span>}
                </div>
            </div>

            <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100 flex flex-col gap-4">
                <h2 className="text-xl font-semibold text-blue-900 flex items-center gap-2">
                    <MessageCircle className="w-5 h-5" /> Follow-up Questions
                </h2>
                <div className="flex flex-col gap-3">
                    {questions.length > 0 ? (
                        questions.map((q, i) => (
                            <div key={i} className="bg-white p-3 rounded-lg text-blue-800 shadow-sm border border-blue-100">
                                {q}
                            </div>
                        ))
                    ) : (
                        <span className="text-blue-400 italic">Questions will appear here when you pause...</span>
                    )}
                </div>
            </div>
        </div>
    );
};

export default JournalEntry;
