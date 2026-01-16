import React from 'react';
import { Link } from 'react-router-dom';

const PrivacyPolicy = () => {
    return (
        <div className="relative min-h-screen w-full flex flex-col items-center overflow-x-hidden bg-[#020617] py-20 px-4">
            <div className="stars"></div>
            <div className="twinkling"></div>

            <div className="relative z-10 w-full max-w-4xl bg-white/5 backdrop-blur-xl p-8 md:p-12 rounded-3xl border border-white/10 shadow-2xl">
                <Link to="/" className="text-blue-400 hover:text-blue-300 mb-8 inline-block transition-colors font-medium">
                    ← Back to SEO Checker
                </Link>
                
                <h1 className="text-4xl font-extrabold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                    Privacy Policy
                </h1>

                <div className="space-y-6 text-gray-300 leading-relaxed">
                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">1. Introduction</h2>
                        <p>Welcome to SEO Checker Pro. We are committed to protecting your personal information and your right to privacy. If you have any questions or concerns about our policy, or our practices with regards to your personal information, please contact us.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">2. Information We Collect</h2>
                        <p>We collect information that you provide to us such as URLs you submit for analysis. We also collect certain information automatically when you visit, use or navigate the SEO Checker Pro, such as IP address and browser characteristics.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">3. How We Use Your Information</h2>
                        <p>We use the information we collect or receive to provide the technical SEO analysis services you request, to improve our tool, and for other internal business purposes.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">4. Google Analytics & Advertising</h2>
                        <p>We use Google Analytics to monitor and analyze the use of our Service. We also use Google AdSense to serve ads. Google may use cookies to serve ads based on a user's prior visits to our website or other websites.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">5. Data Security</h2>
                        <p>We use appropriate technical and organizational security measures designed to protect the security of any personal information we process.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">6. Changes to This Policy</h2>
                        <p>We may update this privacy policy from time to time. The updated version will be indicated by an updated "Revised" date and the updated version will be effective as soon as it is accessible.</p>
                    </section>
                </div>

                <div className="mt-12 pt-8 border-t border-white/10 text-sm text-gray-500">
                    Last updated: January 16, 2026
                </div>
            </div>
        </div>
    );
};

export default PrivacyPolicy;
