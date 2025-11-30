import React from 'react';
import { useLocation } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';

interface LayoutProps {
    children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    const location = useLocation();
    const isLandingPage = location.pathname === '/';

    return (
        <div className="min-h-screen flex flex-col bg-black">
            {!isLandingPage && <Header />}

            <main className="flex-1 relative overflow-hidden flex flex-col">
                {children}
            </main>

            {!isLandingPage && <Footer />}
        </div>
    );
};

export default Layout;
