import React from 'react';
import { Routes, Route } from 'react-router-dom';
import SessionController from './pages/SessionController';
import LandingPage from './pages/LandingPage';
import Layout from './components/Layout';

const RouterConfig: React.FC = () => {
    return (
        <Layout>
            <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/session" element={<SessionController />} />
            </Routes>
        </Layout>
    );
};

export default RouterConfig;
