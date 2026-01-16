import { useState } from 'react';
import axios from 'axios';
import { Routes, Route, Link } from 'react-router-dom';
import PrivacyPolicy from './PrivacyPolicy';
import './App.css';

const Home = () => {
  const [url, setUrl] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!url) return;
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const response = await axios.get(
        `/api/analyze?url=${encodeURIComponent(url)}`
      );

      setData(response.data);
    } catch (err) {
      setError("Unable to reach the backend. Make sure it's running on port 8000!");
    }
    setLoading(false);
  };

  const getStatusColor = (status) => {
    if (status === "Passed") return "text-green-400 border-green-400/20 bg-green-400/10";
    if (status === "Warning") return "text-yellow-400 border-yellow-400/20 bg-yellow-400/10";
    return "text-red-400 border-red-400/20 bg-red-400/10";
  };

  return (
    <div className="relative min-h-screen w-full flex flex-col items-center justify-center overflow-x-hidden bg-[#020617] py-10">
      <div className="stars"></div>
      <div className="twinkling"></div>

<<<<<<< HEAD:frontend/src/App.jsx
      <div className="relative z-10 w-full max-w-3xl px-4 mx-auto text-center">
        <h1 className="text-4xl md:text-6xl font-extrabold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 animate-pulse">
          BoostSEO
        </h1>
        <p className="text-gray-400 mb-8 text-sm md:text-lg">Detailed Technical Audit & Action Plan</p>
        
        {/* Input Section */}
        <div className="flex flex-col md:flex-row gap-3 mb-8 shadow-2xl p-2 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10">
          <input 
            type="text" 
            placeholder="https://example.com" 
            className="flex-1 p-4 bg-transparent text-white outline-none placeholder-gray-500 text-lg"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <button 
            onClick={handleAnalyze}
            disabled={loading}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-3 px-8 rounded-xl transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Start Audit'}
          </button>
        </div>

        {error && <p className="text-red-400 mb-4 bg-red-400/10 p-3 rounded-lg border border-red-400/20">{error}</p>}

        {/* Results Section */}
        {data && (
          <div className="animate-fadeIn space-y-6">
            {/* Score Card */}
            <div className="bg-white/10 backdrop-blur-xl p-8 rounded-3xl border border-white/20 flex flex-col md:flex-row items-center justify-between gap-6 shadow-2xl">
              <div className="text-left">
                <h2 className="text-3xl font-bold text-white">Overall Score</h2>
                <p className="text-gray-400">Based on technical SEO standards</p>
              </div>
              <div className={`text-5xl font-black p-6 rounded-full border-4 ${data.score > 70 ? 'border-green-500 text-green-500' : 'border-yellow-500 text-yellow-500'}`}>
                {data.score}
              </div>
            </div>

            {/* Checks Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.checks.map((check, index) => (
                <div key={index} className="bg-white/5 backdrop-blur-md p-5 rounded-2xl border border-white/10 text-left hover:border-white/30 transition-colors">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-blue-400 text-xs uppercase tracking-widest font-bold">{check.name}</span>
                    <span className={`px-2 py-1 rounded text-[10px] font-bold border ${getStatusColor(check.status)}`}>
                      {check.status}
                    </span>
                  </div>
                  <p className="text-white font-medium mb-1">{check.message}</p>
                  <p className="text-gray-500 text-xs truncate italic">Value: {check.value}</p>
                </div>
              ))}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
              <a 
                href={`/api/download-pdf?url=${encodeURIComponent(url)}`}
                target="_blank"
                rel="noreferrer"
                className="bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-xl border border-white/20 transition-all flex items-center justify-center gap-2"
              >
                📥 Download PDF Report
              </a>
            </div>
=======
      <div className="relative z-10 w-full max-w-3xl px-4 mx-auto text-center flex-grow flex flex-col justify-center">
        <div>
          <h1 className="text-4xl md:text-6xl font-extrabold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 animate-pulse">
            SEO Checker Pro
          </h1>
          <p className="text-gray-400 mb-8 text-sm md:text-lg">Detailed Technical Audit & Action Plan</p>

          {/* Input Section */}
          <div className="flex flex-col md:flex-row gap-3 mb-8 shadow-2xl p-2 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10">
            <input
              type="text"
              placeholder="https://example.com"
              className="flex-1 p-4 bg-transparent text-white outline-none placeholder-gray-500 text-lg"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-3 px-8 rounded-xl transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
            >
              {loading ? 'Analyzing...' : 'Start Audit'}
            </button>
>>>>>>> 0b4bbd50bda3df0a196cbf8a0afb94f21e845219:frontend/frontend/src/App.jsx
          </div>

          {error && <p className="text-red-400 mb-4 bg-red-400/10 p-3 rounded-lg border border-red-400/20">{error}</p>}

          {/* Results Section */}
          {data && (
            <div className="animate-fadeIn space-y-6">
              {/* Score Card */}
              <div className="bg-white/10 backdrop-blur-xl p-8 rounded-3xl border border-white/20 flex flex-col md:flex-row items-center justify-between gap-6 shadow-2xl">
                <div className="text-left">
                  <h2 className="text-3xl font-bold text-white">Overall Score</h2>
                  <p className="text-gray-400">Based on technical SEO standards</p>
                </div>
                <div className={`text-5xl font-black p-6 rounded-full border-4 ${data.score > 70 ? 'border-green-500 text-green-500' : 'border-yellow-500 text-yellow-500'}`}>
                  {data.score}
                </div>
              </div>

              {/* Checks Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.checks.map((check, index) => (
                  <div key={index} className="bg-white/5 backdrop-blur-md p-5 rounded-2xl border border-white/10 text-left hover:border-white/30 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-blue-400 text-xs uppercase tracking-widest font-bold">{check.name}</span>
                      <span className={`px-2 py-1 rounded text-[10px] font-bold border ${getStatusColor(check.status)}`}>
                        {check.status}
                      </span>
                    </div>
                    <p className="text-white font-medium mb-1">{check.message}</p>
                    <p className="text-gray-500 text-xs truncate italic">Value: {check.value}</p>
                  </div>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
                <a
                  href={`http://127.0.0.1:8000/download-pdf?url=${url}`}
                  target="_blank"
                  rel="noreferrer"
                  className="bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-xl border border-white/20 transition-all flex items-center justify-center gap-2"
                >
                  📥 Download PDF Report
                </a>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 w-full py-6 text-center border-t border-white/5 bg-[#020617]/50 backdrop-blur-sm">
        <div className="flex justify-center gap-6 text-sm">
          <Link to="/" className="text-gray-500 hover:text-blue-400 transition-colors">Home</Link>
          <Link to="/privacy-policy" className="text-gray-500 hover:text-blue-400 transition-colors">Privacy Policy</Link>
        </div>
        <p className="mt-2 text-gray-600 text-xs">© 2026 SEO Checker Pro. All rights reserved.</p>
      </footer>
    </div>
  );
};

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/privacy-policy" element={<PrivacyPolicy />} />
    </Routes>
  );
}

export default App;
