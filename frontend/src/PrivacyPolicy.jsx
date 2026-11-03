import React from 'react';
import { Link } from 'react-router-dom';

const PrivacyPolicy = () => {
    return (
        <div className="relative min-h-screen w-full flex flex-col items-center overflow-x-hidden bg-[#020617] py-20 px-4">
            <div className="stars"></div>
            <div className="twinkling"></div>

            <div className="relative z-10 w-full max-w-4xl bg-white/5 backdrop-blur-xl p-8 md:p-12 rounded-3xl border border-white/10 shadow-2xl">
                <Link to="/" className="text-blue-400 hover:text-blue-300 mb-8 inline-block transition-colors font-medium">
                    ← Back to BoostSEO
                </Link>

                <h1 className="text-4xl font-extrabold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                    Privacy Policy
                </h1>
                <p className="text-gray-400 mb-8 text-sm">Last updated: June 27, 2026</p>

                <div className="space-y-8 text-gray-300 leading-relaxed">

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">1. Introduction</h2>
                        <p>
                            Welcome to <strong className="text-white">BoostSEO</strong> ("we", "our", or "us"). We are committed to protecting your privacy.
                            This Privacy Policy explains how we collect, use, and share information when you use our website at boostseo.app
                            (the "Service"). By using the Service, you agree to the terms described below.
                        </p>
                        <p className="mt-3">
                            If you have any questions about this policy, please contact us at:{' '}
                            <a href="mailto:info@jxtechstudio.com" className="text-blue-400 hover:text-blue-300 underline">
                                info@jxtechstudio.com
                            </a>
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">2. Information We Collect</h2>
                        <p className="mb-3">We collect the following types of information:</p>
                        <ul className="list-disc list-inside space-y-2 ml-2">
                            <li><strong className="text-white">URLs you submit</strong> — when you enter a website address for analysis, we process that URL to perform the SEO audit. We do not permanently store submitted URLs.</li>
                            <li><strong className="text-white">Usage data</strong> — collected automatically via Google Analytics, including your IP address, browser type, device type, pages visited, and time spent on the site.</li>
                            <li><strong className="text-white">Cookies</strong> — we and our third-party partners use cookies and similar tracking technologies. See Section 5 for full details.</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">3. How We Use Your Information</h2>
                        <ul className="list-disc list-inside space-y-2 ml-2">
                            <li>To provide the SEO analysis service you request</li>
                            <li>To generate and deliver PDF reports</li>
                            <li>To monitor and improve the performance and quality of our Service</li>
                            <li>To show relevant advertisements through Google AdSense</li>
                            <li>To analyze site traffic and usage patterns via Google Analytics</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">4. Google Analytics</h2>
                        <p>
                            We use <strong className="text-white">Google Analytics</strong> to understand how visitors use our Service.
                            Google Analytics collects information such as how often users visit the site, what pages they visit, and what
                            other sites they used prior to coming to our site. Google uses this data to compile reports and to help us improve the Service.
                        </p>
                        <p className="mt-3">
                            Google's ability to use and share information collected by Google Analytics is restricted by the{' '}
                            <a href="https://marketingplatform.google.com/about/analytics/terms/us/" className="text-blue-400 hover:text-blue-300 underline" target="_blank" rel="noreferrer">
                                Google Analytics Terms of Service
                            </a>{' '}
                            and the{' '}
                            <a href="https://policies.google.com/privacy" className="text-blue-400 hover:text-blue-300 underline" target="_blank" rel="noreferrer">
                                Google Privacy Policy
                            </a>.
                            You may opt out of Google Analytics by installing the{' '}
                            <a href="https://tools.google.com/dlpage/gaoptout" className="text-blue-400 hover:text-blue-300 underline" target="_blank" rel="noreferrer">
                                Google Analytics Opt-out Browser Add-on
                            </a>.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">5. Cookies & Third-Party Advertising (Google AdSense)</h2>
                        <p className="mb-3">
                            We use <strong className="text-white">Google AdSense</strong> to display advertisements on our Service.
                            Google AdSense uses cookies to serve ads based on your prior visits to our website or other websites.
                        </p>
                        <p className="mb-3">
                            <strong className="text-white">Third-party vendors, including Google, use cookies to serve ads based on a user's prior visits to our website or other websites.</strong>{' '}
                            Google's use of advertising cookies enables it and its partners to serve ads to you based on your visit to our site and/or other sites on the Internet.
                        </p>
                        <p className="mb-3">
                            You may opt out of personalized advertising by visiting{' '}
                            <a href="https://www.google.com/settings/ads" className="text-blue-400 hover:text-blue-300 underline" target="_blank" rel="noreferrer">
                                Google Ads Settings
                            </a>.
                            You can also opt out of a third-party vendor's use of cookies for personalized advertising by visiting{' '}
                            <a href="https://www.aboutads.info/choices/" className="text-blue-400 hover:text-blue-300 underline" target="_blank" rel="noreferrer">
                                www.aboutads.info
                            </a>.
                        </p>
                        <p>
                            For more information on how Google uses data when you use our site, please visit:{' '}
                            <a href="https://policies.google.com/technologies/partner-sites" className="text-blue-400 hover:text-blue-300 underline" target="_blank" rel="noreferrer">
                                How Google uses data when you use our partners' sites or apps
                            </a>.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">6. Information Sharing</h2>
                        <p>
                            We do not sell, trade, or rent your personal information to third parties. We may share anonymized, aggregated
                            data (such as total visitor counts) for analytical purposes. We share data with Google as described in Sections 4 and 5 above.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">7. Data Retention</h2>
                        <p>
                            We do not permanently store the URLs you submit for analysis. Google Analytics data is retained for 26 months
                            by default. You may request deletion of any data associated with your use of the Service by contacting us.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">8. Your Rights</h2>
                        <p className="mb-3">Depending on your location, you may have the following rights regarding your data:</p>
                        <ul className="list-disc list-inside space-y-2 ml-2">
                            <li>The right to access the personal data we hold about you</li>
                            <li>The right to request correction or deletion of your data</li>
                            <li>The right to object to or restrict processing of your data</li>
                            <li>The right to opt out of personalized advertising (see Section 5)</li>
                        </ul>
                        <p className="mt-3">
                            To exercise any of these rights, please contact us at{' '}
                            <a href="mailto:info@jxtechstudio.com" className="text-blue-400 hover:text-blue-300 underline">
                                info@jxtechstudio.com
                            </a>.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">9. Children's Privacy</h2>
                        <p>
                            Our Service is not directed to children under the age of 13. We do not knowingly collect personal information
                            from children under 13. If you believe a child has provided us with personal information, please contact us immediately.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">10. Data Security</h2>
                        <p>
                            We implement appropriate technical and organizational security measures to protect your information against
                            unauthorized access, alteration, disclosure, or destruction. However, no internet transmission is 100% secure,
                            and we cannot guarantee absolute security.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">11. Changes to This Policy</h2>
                        <p>
                            We may update this Privacy Policy from time to time. We will notify you of any significant changes by updating
                            the "Last updated" date at the top of this page. We encourage you to review this page periodically.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-3">12. Contact Us</h2>
                        <p>
                            If you have any questions or concerns about this Privacy Policy, please contact us:
                        </p>
                        <div className="mt-3 bg-white/5 rounded-xl p-4 border border-white/10">
                            <p className="text-white font-medium">BoostSEO</p>
                            <p>Email:{' '}
                                <a href="mailto:info@jxtechstudio.com" className="text-blue-400 hover:text-blue-300 underline">
                                    info@jxtechstudio.com
                                </a>
                            </p>
                        </div>
                    </section>

                </div>
            </div>
        </div>
    );
};

export default PrivacyPolicy;
