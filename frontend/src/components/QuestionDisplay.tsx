import React from 'react';

interface QuestionDisplayProps {
    question?: string;
}

const QuestionDisplay: React.FC<QuestionDisplayProps> = ({ question }) => {
    return (
        <div className="col-span-6 flex items-start justify-center h-full pt-0">
            {question && (
                <div className="glass-panel opacity-65 rounded-3xl py-12 px-8 text-center backdrop-blur-xl animate-scale-in border-amber-500/20 bg-amber-500/5">
                    <h2 className="text-2xl md:text-3xl font-light text-white italic leading-relaxed">
                        {question}
                    </h2>
                </div>
            )}
        </div>
    );
};

export default QuestionDisplay;
