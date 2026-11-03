import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';

const NotFound = () => {
    useEffect(() => {
        const meta = document.createElement('meta');
        meta.name = 'robots';
        meta.content = 'noindex, follow';
        document.head.appendChild(meta);
        return () => document.head.removeChild(meta);
    }, []);

    return (
        <div className="relative min-h-screen w-full flex flex-col items-center justify-center overflow-x-hidden bg-[#020617] py-20 px-4">
            <div className="stars"></div>
            <div className="twinkling"></div>

            <div className="relative z-10 w-full max-w-lg text-center">
                <div className="bg-white/5 backdrop-blur-xl p-10 rounded-3xl border border-white/10 shadow-2xl">
                    <p className="text-6xl font-black mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                        404
                    </p>
                    <h1 className="text-2xl font-bold text-white mb-3">Page not found</h1>
                    <p className="text-gray-400 mb-8">
                        The page you're looking for doesn't exist or may have moved.
                    </p>
                    <Link
                        to="/"
                        className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-3 px-8 rounded-xl transition-all hover:scale-105 active:scale-95"
                    >
                        ← Back to BoostSEO
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default NotFound;
