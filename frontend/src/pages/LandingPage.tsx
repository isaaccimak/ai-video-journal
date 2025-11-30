import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight } from 'lucide-react';

const LandingPage: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-black flex flex-col items-center justify-center p-8 relative overflow-hidden">

            {/* Subtle Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-amber-500/10 rounded-full blur-3xl animate-pulse" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
            </div>

            <div className="z-10 text-center max-w-2xl animate-fade-in">

                <h1 className="text-5xl md:text-7xl font-light tracking-tight text-white mb-6">
                    Video Journal
                </h1>

                <p className="text-xl text-white/60 font-light mb-12 leading-relaxed">
                    A space to reflect, speak your mind, and discover insights about yourself through conversation.
                </p>

                <button
                    onClick={() => navigate('/session')}
                    className="group relative inline-flex items-center gap-3 px-8 py-4 bg-white text-black rounded-full text-lg font-medium transition-all hover:scale-105 hover:shadow-xl active:scale-95 hover:bg-stone-200"
                >
                    Let's reflect
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
            </div>

            <div className="absolute bottom-8 text-white/20 text-sm font-light">
                AI-Powered Self Reflection
            </div>
        </div>
    );
};

export default LandingPage;
