import React from 'react';
import { Link } from 'react-router-dom';

const STEPS = [
    {
        title: '1. Compress and resize images first',
        desc: 'Images are almost always the biggest contributor to page weight. Resize them to the dimensions they\'re actually displayed at (not the camera-original resolution) and run them through compression before upload. This one change often has the biggest speed impact for the least effort.',
    },
    {
        title: '2. Defer or async non-critical JavaScript',
        desc: 'Scripts that aren\'t needed to render the initial view (analytics, chat widgets, ad scripts) should load with async or defer so they don\'t block the page from becoming visible and interactive.',
    },
    {
        title: '3. Load fonts without blocking render',
        desc: 'Use font-display: swap so text renders in a fallback font immediately instead of staying invisible while a custom web font downloads.',
    },
    {
        title: '4. Set caching headers for static assets',
        desc: 'CSS, JS, and image files that don\'t change often should be served with long cache lifetimes, so repeat visits don\'t re-download assets that haven\'t changed.',
    },
    {
        title: '5. Cut what you don\'t need',
        desc: 'Every third-party embed, tracking pixel, and unused CSS/JS library adds weight and a network request. Before optimizing what\'s there, it\'s worth checking whether it needs to be there at all.',
    },
];

const PageSpeedGuide = () => {
    return (
        <div className="relative min-h-screen w-full flex flex-col items-center overflow-x-hidden bg-[#020617] py-20 px-4">
            <div className="stars"></div>
            <div className="twinkling"></div>

            <div className="relative z-10 w-full max-w-3xl">
                <Link to="/resources" className="text-blue-400 hover:text-blue-300 mb-8 inline-block transition-colors font-medium">
                    ← Back to Guides
                </Link>

                <h1 className="text-4xl font-extrabold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                    How to Improve Page Speed (Without a Rebuild)
                </h1>
                <p className="text-gray-400 leading-relaxed mb-10">
                    Page speed matters for two reasons: it's a confirmed ranking factor, and slower pages
                    lose visitors before they ever see your content. Most sites don't need a rebuild to get
                    meaningfully faster — they need the five fixes below, roughly in this order of
                    impact-to-effort ratio.
                </p>

                <div className="space-y-6">
                    {STEPS.map((step) => (
                        <div key={step.title} className="bg-white/5 backdrop-blur-md p-6 rounded-2xl border border-white/10">
                            <h2 className="text-lg font-bold text-white mb-2">{step.title}</h2>
                            <p className="text-gray-300 text-sm leading-relaxed">{step.desc}</p>
                        </div>
                    ))}
                </div>

                <div className="mt-8 bg-white/5 backdrop-blur-md p-6 rounded-2xl border border-white/10">
                    <h2 className="text-lg font-bold text-white mb-2">What "fast enough" looks like</h2>
                    <p className="text-gray-300 text-sm leading-relaxed">
                        There's no single magic number, but a page that loads in around two seconds or
                        less is a reasonable general target before speed starts noticeably costing you
                        rankings and conversions. Beyond that, focus on the metrics that reflect what users
                        actually feel: how soon content appears, and how soon the page responds to input —
                        rather than chasing a single lab score.
                    </p>
                </div>

                <div className="mt-10 bg-white/5 backdrop-blur-md p-6 rounded-2xl border border-white/10 text-center">
                    <p className="text-gray-300 mb-4">
                        BoostSEO measures your page load time against this benchmark automatically.
                    </p>
                    <Link
                        to="/"
                        className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-3 px-8 rounded-xl transition-all hover:scale-105"
                    >
                        Run a Free Audit
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default PageSpeedGuide;
