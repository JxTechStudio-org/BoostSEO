import React from 'react';
import { Link } from 'react-router-dom';

const About = () => {
    return (
        <div className="relative min-h-screen w-full flex flex-col items-center overflow-x-hidden bg-[#020617] py-20 px-4">
            <div className="stars"></div>
            <div className="twinkling"></div>

            <div className="relative z-10 w-full max-w-4xl">
                <Link to="/" className="text-blue-400 hover:text-blue-300 mb-8 inline-block transition-colors font-medium">
                    ← Back to BoostSEO
                </Link>

                <div className="bg-white/5 backdrop-blur-xl p-8 md:p-12 rounded-3xl border border-white/10 shadow-2xl mb-8">
                    <h1 className="text-4xl font-extrabold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                        About BoostSEO
                    </h1>
                    <p className="text-gray-300 leading-relaxed text-lg mb-6">
                        BoostSEO is a free, fast, and easy-to-use technical SEO audit tool designed for website owners,
                        bloggers, developers, and digital marketers who want to improve their search engine visibility.
                    </p>
                    <p className="text-gray-400 leading-relaxed">
                        We believe that good SEO should be accessible to everyone — not just large enterprises with expensive agencies.
                        With BoostSEO, you get instant, actionable insights about your website's technical SEO health in seconds,
                        completely free of charge.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    {[
                        {
                            title: 'What We Check',
                            items: [
                                'Title tag presence and optimal length (10–60 characters)',
                                'Meta description tag',
                                'H1 heading structure',
                                'Image alt text coverage',
                                'Page load speed',
                                'Internal and external link count',
                            ],
                        },
                        {
                            title: 'Why It Matters',
                            items: [
                                'Search engines use title tags to rank and display pages',
                                'Meta descriptions influence click-through rates',
                                'H1 tags signal your page topic to crawlers',
                                'Alt text improves accessibility and image indexing',
                                'Page speed is a confirmed Google ranking factor',
                                'Links help search engines discover and evaluate content',
                            ],
                        },
                    ].map((card) => (
                        <div key={card.title} className="bg-white/5 backdrop-blur-md p-6 rounded-2xl border border-white/10">
                            <h2 className="text-xl font-bold text-white mb-4">{card.title}</h2>
                            <ul className="space-y-2">
                                {card.items.map((item) => (
                                    <li key={item} className="flex items-start gap-2 text-gray-300 text-sm">
                                        <span className="text-blue-400 mt-0.5 flex-shrink-0">✓</span>
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                <div className="bg-white/5 backdrop-blur-xl p-8 rounded-3xl border border-white/10 shadow-2xl">
                    <h2 className="text-2xl font-bold text-white mb-4">How It Works</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {[
                            { step: '1', title: 'Enter Your URL', desc: 'Paste any public website URL into the input field on our homepage.' },
                            { step: '2', title: 'Run the Audit', desc: 'Click "Start Audit" and our engine fetches and analyzes your page in real time.' },
                            { step: '3', title: 'Get Your Report', desc: 'View your SEO score, check-by-check breakdown, and download a full PDF report.' },
                        ].map((item) => (
                            <div key={item.step} className="text-center">
                                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center text-white font-bold text-xl mx-auto mb-3">
                                    {item.step}
                                </div>
                                <h3 className="text-white font-semibold mb-2">{item.title}</h3>
                                <p className="text-gray-400 text-sm">{item.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default About;
