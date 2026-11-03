import React from 'react';
import { Link } from 'react-router-dom';

const MetaTagsGuide = () => {
    return (
        <div className="relative min-h-screen w-full flex flex-col items-center overflow-x-hidden bg-[#020617] py-20 px-4">
            <div className="stars"></div>
            <div className="twinkling"></div>

            <div className="relative z-10 w-full max-w-3xl">
                <Link to="/resources" className="text-blue-400 hover:text-blue-300 mb-8 inline-block transition-colors font-medium">
                    ← Back to Guides
                </Link>

                <h1 className="text-4xl font-extrabold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                    Meta Tags Guide: Title, Description &amp; Open Graph
                </h1>
                <p className="text-gray-400 leading-relaxed mb-10">
                    Meta tags don't change how a page looks to a visitor — they change how it looks
                    everywhere else: in search results, in Slack previews, in a tweet. Getting them wrong
                    doesn't just cost rankings, it costs click-throughs from people who already found you.
                </p>

                <div className="space-y-8">
                    <div className="bg-white/5 backdrop-blur-md p-6 rounded-2xl border border-white/10">
                        <h2 className="text-xl font-bold text-white mb-3">Title Tag</h2>
                        <p className="text-gray-300 text-sm leading-relaxed mb-3">
                            The title tag is the blue link text in search results and the text shown in a
                            browser tab. Keep it between roughly 10 and 60 characters — long titles get
                            truncated with an ellipsis in search results, which looks unfinished and hurts
                            click-through rate.
                        </p>
                        <p className="text-gray-300 text-sm leading-relaxed mb-2"><strong className="text-white">Weak:</strong> "Home"</p>
                        <p className="text-gray-300 text-sm leading-relaxed"><strong className="text-white">Better:</strong> "BoostSEO — Free Technical SEO Audit Tool"</p>
                    </div>

                    <div className="bg-white/5 backdrop-blur-md p-6 rounded-2xl border border-white/10">
                        <h2 className="text-xl font-bold text-white mb-3">Meta Description</h2>
                        <p className="text-gray-300 text-sm leading-relaxed mb-3">
                            The meta description doesn't directly affect rankings, but it's usually the
                            snippet shown under your title in search results, so it directly affects
                            whether someone clicks. Aim for roughly 50–160 characters and write it like ad
                            copy: what the page offers, and why it's worth the click.
                        </p>
                        <p className="text-gray-300 text-sm leading-relaxed">
                            One description per page. Copying the same description across every page is a
                            common mistake — search engines treat it as a signal the pages are
                            interchangeable, which works against you.
                        </p>
                    </div>

                    <div className="bg-white/5 backdrop-blur-md p-6 rounded-2xl border border-white/10">
                        <h2 className="text-xl font-bold text-white mb-3">Canonical Tag</h2>
                        <p className="text-gray-300 text-sm leading-relaxed">
                            If the same content is reachable at more than one URL — with and without a
                            trailing slash, with tracking parameters, over http and https — a canonical tag
                            tells search engines which version is the "real" one, so they consolidate
                            ranking signals instead of splitting them across duplicates.
                        </p>
                    </div>

                    <div className="bg-white/5 backdrop-blur-md p-6 rounded-2xl border border-white/10">
                        <h2 className="text-xl font-bold text-white mb-3">Open Graph &amp; Twitter Card Tags</h2>
                        <p className="text-gray-300 text-sm leading-relaxed">
                            These control how a link looks when it's shared — the image, title, and
                            description shown in a Slack unfurl, an iMessage preview, or a tweet. At
                            minimum, set <code className="text-blue-300">og:title</code>,{' '}
                            <code className="text-blue-300">og:description</code>, and{' '}
                            <code className="text-blue-300">og:image</code>. Without them, platforms often
                            fall back to guessing from page content, which produces inconsistent or
                            unflattering previews.
                        </p>
                    </div>
                </div>

                <div className="mt-10 bg-white/5 backdrop-blur-md p-6 rounded-2xl border border-white/10 text-center">
                    <p className="text-gray-300 mb-4">
                        BoostSEO checks all of these automatically and flags what's missing.
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

export default MetaTagsGuide;
