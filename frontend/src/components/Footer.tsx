import React from 'react';

const Footer: React.FC = () => {
    return (
        <footer className="h-12 bg-black border-t border-white/10 flex items-center justify-center px-6 z-50 relative">
            <p className="text-white/30 text-xs font-light">
                &copy; {new Date().getFullYear()} AI Video Journal. All rights reserved.
            </p>
        </footer>
    );
};

export default Footer;
