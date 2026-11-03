import { useState } from 'react';
import axios from 'axios';
import { Routes, Route, Link } from 'react-router-dom';
import CategoryCard from './CategoryCard';
import CommentSection from './CommentSection';
import PrivacyPolicy from './PrivacyPolicy';
import About from './About';
import Contact from './Contact';
import NotFound from './NotFound';
import Resources from './Resources';
import TechnicalSeoChecklist from './resources/TechnicalSeoChecklist';
import MetaTagsGuide from './resources/MetaTagsGuide';
import PageSpeedGuide from './resources/PageSpeedGuide';
import './App.css';

// ── SVG icons ────────────────────────────────────────────────────────────────
const IconTag = (p) => (
    <svg {...p} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>
        <line x1="7" y1="7" x2="7.01" y2="7"/>
    </svg>
);
const IconFileText = (p) => (
    <svg {...p} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
        <polyline points="10 9 9 9 8 9"/>
    </svg>
);
const IconShield = (p) => (
    <svg {...p} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    </svg>
);
const IconZap = (p) => (
    <svg {...p} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
    </svg>
);
const IconSearch = (p) => (
    <svg {...p} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="8"/>
        <line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
);
const IconDownload = (p) => (
    <svg {...p} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="7 10 12 15 17 10"/>
        <line x1="12" y1="15" x2="12" y2="3"/>
    </svg>
);

const FEATURE_CARDS = [
    { Icon: IconTag,      label: 'Meta & Social',  desc: 'Title, description, canonical, Open Graph, Twitter Card' },
    { Icon: IconFileText, label: 'Content',         desc: 'H1/H2/H3 structure, word count, image alt text' },
    { Icon: IconShield,   label: 'Technical',       desc: 'HTTPS, viewport, favicon, language, structured data' },
    { Icon: IconZap,      label: 'Performance',     desc: 'Page load speed vs 2-second benchmark' },
    { Icon: IconSearch,   label: 'Crawlability',    desc: 'robots.txt, sitemap.xml, broken links' },
    { Icon: IconDownload, label: 'PDF Report',      desc: 'Download a full audit report for any URL' },
];

const AdBanner = () => (
    <ins
        className="adsbygoogle"
        style={{ display: 'block' }}
        data-ad-client="ca-pub-2280336108138157"
        data-ad-slot="8237171876"
        data-ad-format="auto"
        data-full-width-responsive="true"
        ref={(el) => {
            if (el) {
                try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (_) {}
            }
        }}
    />
);

const scoreRing = (score) => {
    if (score >= 70) return 'border-green-500 text-green-500';
    if (score >= 50) return 'border-yellow-500 text-yellow-500';
    return 'border-red-500 text-red-500';
};

const miniScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 50) return 'text-yellow-400';
    return 'text-red-400';
};

const Home = () => {
    const [url, setUrl] = useState('');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleAnalyze = async () => {
        if (!url.trim()) return;
        setLoading(true);
        setError(null);
        setData(null);
        try {
            const response = await axios.get(`/api/analyze?url=${encodeURIComponent(url.trim())}`);
            setData(response.data);
        } catch (err) {
            setError('Unable to analyze the URL. Make sure it is publicly accessible and starts with https://');
        }
        setLoading(false);
    };

    return (
        <div className="relative min-h-screen w-full flex flex-col items-center overflow-x-hidden bg-[#020617]">
            <div className="stars"></div>
            <div className="twinkling"></div>

            {/* Hero / Tool */}
            <div className="relative z-10 w-full max-w-3xl px-4 mx-auto text-center pt-20 pb-10">
                <h1 className="text-4xl md:text-6xl font-extrabold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                    BoostSEO
                </h1>
                <p className="text-gray-400 mb-2 text-sm md:text-lg">Free Technical SEO Audit — 21 Checks</p>
                <p className="text-gray-500 mb-8 text-xs md:text-sm max-w-xl mx-auto">
                    Enter any public URL to get an instant SEO health score, grouped check results, and a downloadable PDF report.
                </p>

                {/* Input */}
                <div className="flex flex-col md:flex-row gap-3 mb-8 shadow-2xl p-2 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10">
                    <input
                        type="text"
                        placeholder="https://example.com"
                        className="flex-1 p-4 bg-transparent text-white outline-none placeholder-gray-500 text-lg"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                    />
                    <button
                        onClick={handleAnalyze}
                        disabled={loading}
                        className="bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-3 px-8 rounded-xl transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
                    >
                        {loading ? 'Analyzing…' : 'Start Audit'}
                    </button>
                </div>

                {error && (
                    <p className="text-red-400 mb-6 bg-red-400/10 p-3 rounded-lg border border-red-400/20">{error}</p>
                )}

                {/* Results */}
                {data && (
                    <div className="space-y-6 text-left">
                        {/* Overall score card */}
                        <div className="bg-white/10 backdrop-blur-xl p-8 rounded-3xl border border-white/20 shadow-2xl">
                            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                                <div>
                                    <h2 className="text-3xl font-bold text-white">Overall SEO Score</h2>
                                    <p className="text-gray-400 text-sm mt-1">Based on {data.meta.checks_total} checks</p>
                                    {data.summary && <p className="text-gray-300 text-sm mt-2">{data.summary}</p>}
                                    <div className="flex gap-5 mt-3 text-sm">
                                        <span className="text-green-400 font-medium">{data.meta.checks_passed} Passed</span>
                                        <span className="text-yellow-400 font-medium">{data.meta.checks_warned} Warnings</span>
                                        <span className="text-red-400 font-medium">{data.meta.checks_failed} Failed</span>
                                    </div>
                                </div>
                                <div className={`text-5xl font-black p-6 rounded-full border-4 flex-shrink-0 ${scoreRing(data.score)}`}>
                                    {data.score}
                                </div>
                            </div>

                            {/* Category mini-scores */}
                            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 border-t border-white/10 mt-6 pt-5">
                                {data.categories.map((cat) => (
                                    <div key={cat.name} className="text-center">
                                        <div className={`text-xl font-bold ${miniScoreColor(cat.score)}`}>{cat.score}%</div>
                                        <div className="text-gray-500 text-xs mt-1 leading-tight">{cat.name}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Category cards */}
                        {data.categories.map((cat) => (
                            <CategoryCard key={cat.name} category={cat} />
                        ))}

                        {/* Ad banner */}
                        <div className="rounded-2xl overflow-hidden">
                            <AdBanner />
                        </div>

                        {/* PDF download */}
                        <div className="flex justify-center pb-4">
                            <a
                                href={`/api/download-pdf?url=${encodeURIComponent(url)}`}
                                target="_blank"
                                rel="noreferrer"
                                className="bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-xl border border-white/20 transition-all flex items-center gap-2"
                            >
                                <IconDownload className="w-4 h-4" /> Download PDF Report
                            </a>
                        </div>
                    </div>
                )}

                {/* Feature grid — shown before first audit */}
                {!data && (
                    <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
                        {FEATURE_CARDS.map((item) => (
                            <div key={item.label} className="bg-white/5 backdrop-blur-md p-5 rounded-xl border border-white/10">
                                <div className="w-9 h-9 rounded-lg bg-blue-500/15 flex items-center justify-center mb-3">
                                    <item.Icon className="w-5 h-5 text-blue-400" />
                                </div>
                                <p className="text-white font-semibold text-sm mb-1">{item.label}</p>
                                <p className="text-gray-400 text-xs leading-relaxed">{item.desc}</p>
                            </div>
                        ))}
                    </div>
                )}

                {/* Comment section — shown before first audit */}
                {!data && <CommentSection />}
            </div>

            {/* Footer */}
            <footer className="relative z-10 w-full py-6 text-center border-t border-white/5 bg-[#020617]/50 backdrop-blur-sm mt-auto">
                <div className="flex justify-center flex-wrap gap-6 text-sm">
                    <Link to="/" className="text-gray-500 hover:text-blue-400 transition-colors">Home</Link>
                    <Link to="/resources" className="text-gray-500 hover:text-blue-400 transition-colors">Guides</Link>
                    <Link to="/about" className="text-gray-500 hover:text-blue-400 transition-colors">About</Link>
                    <Link to="/contact" className="text-gray-500 hover:text-blue-400 transition-colors">Contact</Link>
                    <Link to="/privacy-policy" className="text-gray-500 hover:text-blue-400 transition-colors">Privacy Policy</Link>
                </div>
                <p className="mt-2 text-gray-600 text-xs">© 2026 BoostSEO. All rights reserved.</p>
            </footer>
        </div>
    );
};

function App() {
    return (
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            <Route path="/resources" element={<Resources />} />
            <Route path="/resources/technical-seo-checklist" element={<TechnicalSeoChecklist />} />
            <Route path="/resources/meta-tags-guide" element={<MetaTagsGuide />} />
            <Route path="/resources/page-speed-guide" element={<PageSpeedGuide />} />
            <Route path="*" element={<NotFound />} />
        </Routes>
    );
}

export default App;
