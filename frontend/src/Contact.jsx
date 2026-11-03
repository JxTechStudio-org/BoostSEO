import React from 'react';
import { Link } from 'react-router-dom';

const Contact = () => {
    return (
        <div className="relative min-h-screen w-full flex flex-col items-center overflow-x-hidden bg-[#020617] py-20 px-4">
            <div className="stars"></div>
            <div className="twinkling"></div>

            <div className="relative z-10 w-full max-w-2xl">
                <Link to="/" className="text-blue-400 hover:text-blue-300 mb-8 inline-block transition-colors font-medium">
                    ← Back to BoostSEO
                </Link>

                <div className="bg-white/5 backdrop-blur-xl p-8 md:p-12 rounded-3xl border border-white/10 shadow-2xl">
                    <h1 className="text-4xl font-extrabold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                        Contact Us
                    </h1>
                    <p className="text-gray-400 leading-relaxed mb-8">
                        Have a question, feedback, or a bug to report? We'd love to hear from you.
                        Reach out and we'll get back to you as soon as possible.
                    </p>

                    <div className="space-y-4">
                        <div className="bg-white/5 rounded-2xl p-6 border border-white/10">
                            <h2 className="text-white font-semibold mb-1">Email</h2>
                            <a
                                href="mailto:info@jxtechstudio.com"
                                className="text-blue-400 hover:text-blue-300 underline transition-colors"
                            >
                                info@jxtechstudio.com
                            </a>
                        </div>

                        <div className="bg-white/5 rounded-2xl p-6 border border-white/10">
                            <h2 className="text-white font-semibold mb-2">Common Questions</h2>
                            <div className="space-y-4 text-sm text-gray-300">
                                <div>
                                    <p className="font-medium text-white">Why can't my URL be analyzed?</p>
                                    <p className="text-gray-400 mt-1">Some sites block automated requests. Make sure the URL is publicly accessible and starts with https://.</p>
                                </div>
                                <div>
                                    <p className="font-medium text-white">Is my data stored?</p>
                                    <p className="text-gray-400 mt-1">No. URLs submitted for analysis are not permanently stored. See our <Link to="/privacy-policy" className="text-blue-400 hover:text-blue-300 underline">Privacy Policy</Link> for details.</p>
                                </div>
                                <div>
                                    <p className="font-medium text-white">Is BoostSEO free?</p>
                                    <p className="text-gray-400 mt-1">Yes, BoostSEO is completely free to use. We are supported by advertising.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Contact;
