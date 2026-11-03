import React from 'react';
import { Link } from 'react-router-dom';

const SECTIONS = [
    {
        title: '1. Meta & Social Tags',
        items: [
            ['Title tag on every page', 'Unique, 10–60 characters, describes the page rather than repeating the site name.'],
            ['Meta description', 'One per page, roughly 50–160 characters, written to earn the click — not just stuffed with keywords.'],
            ['Canonical tag', 'Points to the preferred URL when the same content is reachable at more than one address (with/without trailing slash, query params, etc.).'],
            ['Open Graph & Twitter Card tags', 'og:title, og:description, og:image so links look right when shared on social platforms.'],
        ],
    },
    {
        title: '2. Content Structure',
        items: [
            ['One H1 per page', 'A single, clear H1 that states the page topic; H2/H3 used to structure sections underneath it.'],
            ['Reasonable word count', 'Thin pages (under ~150–200 words of real content) struggle to rank and, per Google\'s publisher policies, can also block ad monetization.'],
            ['Image alt text', 'Every meaningful image has descriptive alt text — helps accessibility and image search.'],
        ],
    },
    {
        title: '3. Technical Basics',
        items: [
            ['HTTPS everywhere', 'No mixed content, no pages still served over plain HTTP.'],
            ['Viewport meta tag', 'width=device-width, initial-scale=1.0 so mobile rendering isn\'t left to guesswork.'],
            ['Favicon', 'A favicon set so the site doesn\'t look broken in browser tabs and bookmarks.'],
            ['Declared language', 'lang attribute on the <html> tag matching the page\'s actual language.'],
            ['Structured data where relevant', 'JSON-LD schema (Article, Product, SoftwareApplication, etc.) so search engines can understand the content type.'],
        ],
    },
    {
        title: '4. Performance',
        items: [
            ['Page load under ~2 seconds', 'The general benchmark before load time starts costing you rankings and conversions.'],
            ['Compressed images', 'Serve appropriately sized, compressed images instead of full-resolution originals.'],
            ['Minimal render-blocking resources', 'Defer or async non-critical scripts; inline critical CSS where practical.'],
        ],
    },
    {
        title: '5. Crawlability',
        items: [
            ['robots.txt present and correct', 'Not accidentally blocking pages you want indexed.'],
            ['sitemap.xml present and submitted', 'Listed in robots.txt and submitted in Search Console.'],
            ['No broken internal links', 'Internal 404s waste crawl budget and hurt user experience.'],
        ],
    },
];

const TechnicalSeoChecklist = () => {
    return (
        <div className="relative min-h-screen w-full flex flex-col items-center overflow-x-hidden bg-[#020617] py-20 px-4">
            <div className="stars"></div>
            <div className="twinkling"></div>

            <div className="relative z-10 w-full max-w-3xl">
                <Link to="/resources" className="text-blue-400 hover:text-blue-300 mb-8 inline-block transition-colors font-medium">
                    ← Back to Guides
                </Link>

                <h1 className="text-4xl font-extrabold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                    The Complete Technical SEO Checklist
                </h1>
                <p className="text-gray-400 leading-relaxed mb-10">
                    Most technical SEO problems fall into a small number of recurring categories. This
                    checklist covers the checks that matter most, grouped the same way{' '}
                    <Link to="/" className="text-blue-400 hover:text-blue-300 underline">BoostSEO</Link>{' '}
                    groups them when it audits a site — so you can fix issues in the same order the tool
                    reports them.
                </p>

                <div className="space-y-8">
                    {SECTIONS.map((section) => (
                        <div key={section.title} className="bg-white/5 backdrop-blur-md p-6 rounded-2xl border border-white/10">
                            <h2 className="text-xl font-bold text-white mb-4">{section.title}</h2>
                            <ul className="space-y-3">
                                {section.items.map(([label, desc]) => (
                                    <li key={label} className="flex items-start gap-3">
                                        <span className="text-blue-400 mt-1 flex-shrink-0">✓</span>
                                        <span className="text-gray-300 text-sm">
                                            <strong className="text-white">{label}</strong> — {desc}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                <div className="mt-10 bg-white/5 backdrop-blur-md p-6 rounded-2xl border border-white/10 text-center">
                    <p className="text-gray-300 mb-4">
                        Want to check where your own site stands against this list?
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

export default TechnicalSeoChecklist;
