import React from 'react';
import { Link } from 'react-router-dom';
import { Video } from 'lucide-react';

const Header: React.FC = () => {
    return (
        <header className="h-16 bg-black border-b border-white/10 flex items-center justify-between px-6 z-50 relative">
            <Link to="/" className="flex items-center gap-2 group">
                <div className="p-2 bg-white/5 rounded-lg group-hover:bg-white/10 transition-colors">
                    <Video className="w-5 h-5 text-white" />
                </div>
                <span className="text-white font-light tracking-wide text-lg">Video Journal</span>
            </Link>

            <nav>
                {/* Add navigation items here if needed */}
            </nav>
        </header>
    );
};

export default Header;
