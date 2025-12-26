import { useState } from 'react';
import axios from 'axios';
import './App.css'; 

function App() {
  const [url, setUrl] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`http://127.0.0.1:8000/analyze?url=${url}`);
      setData(response.data);
    } catch (err) {
      setError("Unable to reach the backend. Make sure it's running!");
    }
    setLoading(false);
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center overflow-hidden bg-[#020617]">
      {/* خلفية النجوم المتحركة */}
      <div className="stars"></div>
      <div className="twinkling"></div>

      <div className="relative z-10 w-full max-w-2xl px-4 py-8 mx-auto text-center">
        <h1 className="text-4xl md:text-6xl font-extrabold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 animate-pulse">
          SEO Checker Pro
        </h1>
        <p className="text-gray-400 mb-8 text-sm md:text-lg">Analyze any website's SEO instantly</p>
        
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
            {loading ? 'Scanning...' : 'Analyze'}
          </button>
        </div>

        {error && <p className="text-red-400 mb-4 bg-red-400/10 p-2 rounded-lg border border-red-400/20">{error}</p>}

        {data && (
          <div className="animate-fadeIn bg-white/10 backdrop-blur-xl p-6 rounded-3xl border border-white/20 text-left shadow-2xl">
            <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-2">Analysis Results</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1">
                <span className="text-blue-400 text-xs uppercase tracking-wider font-bold">Page Title</span>
                <p className="text-gray-200 text-lg">{data.title}</p>
              </div>
              <div className="space-y-1">
                <span className="text-purple-400 text-xs uppercase tracking-wider font-bold">Title Length</span>
                <p className="text-gray-200 text-lg font-mono">{data.title_length} chars</p>
              </div>
              <div className="md:col-span-2 space-y-1">
                <span className="text-green-400 text-xs uppercase tracking-wider font-bold">Meta Description</span>
                <p className="text-gray-200 leading-relaxed">{data.description}</p>
              </div>
            </div>
            <div className="mt-8 flex items-center justify-between bg-green-500/10 p-4 rounded-xl border border-green-500/30">
              <span className="text-green-400 font-bold uppercase tracking-tighter">Status</span>
              <span className="text-green-400 font-mono">OK - HTTP 200</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;