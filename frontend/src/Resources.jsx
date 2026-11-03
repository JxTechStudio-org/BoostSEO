import React from 'react';
import { Link } from 'react-router-dom';

const GUIDES = [
    {
        path: '/resources/technical-seo-checklist',
        title: 'The Complete Technical SEO Checklist',
        desc: 'A practical, no-fluff checklist covering the 21 technical checks that most commonly break a site\'s search visibility — and how to fix each one.',
    },
    {
        path: '/resources/meta-tags-guide',
        title: 'Meta Tags Guide: Title, Description & Open Graph',
        desc: 'What each meta tag actually does, the length limits that matter, and real examples of good vs. bad tags.',
    },
    {
        path: '/resources/page-speed-guide',
        title: 'How to Improve Page Speed (Without a Rebuild)',
        desc: 'The highest-impact, lowest-effort fixes for slow-loading pages, in the order you should actually do them.',
    },
];

const Resources = () => {
    return (
        <div className="relative min-h-screen w-full flex flex-col items-center overflow-x-hidden bg-[#020617] py-20 px-4">
            <div className="stars"></div>
            <div className="twinkling"></div>

            <div className="relative z-10 w-full max-w-4xl">
                <Link to="/" className="text-blue-400 hover:text-blue-300 mb-8 inline-block transition-colors font-medium">
                    ← Back to BoostSEO
                </Link>

                <h1 className="text-4xl font-extrabold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                    SEO Guides
                </h1>
                <p className="text-gray-400 leading-relaxed mb-10 max-w-2xl">
                    Free, practical guides based on the same checks BoostSEO runs when it audits a site.
                    No sign-up, no gated content — just the fixes, explained.
                </p>

                <div className="space-y-4">
                    {GUIDES.map((g) => (
                        <Link
                            key={g.path}
                            to={g.path}
                            className="block bg-white/5 backdrop-blur-md p-6 rounded-2xl border border-white/10 hover:border-blue-400/40 transition-all"
                        >
                            <h2 className="text-xl font-bold text-white mb-2">{g.title}</h2>
                            <p className="text-gray-400 text-sm">{g.desc}</p>
                        </Link>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Resources;
