import { useState } from 'react';

const statusStyle = (status) => {
    if (status === 'Passed') return 'text-green-400 border-green-400/20 bg-green-400/10';
    if (status === 'Warning') return 'text-yellow-400 border-yellow-400/20 bg-yellow-400/10';
    return 'text-red-400 border-red-400/20 bg-red-400/10';
};

const scoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 50) return 'text-yellow-400';
    return 'text-red-400';
};

const CategoryCard = ({ category }) => {
    const [expanded, setExpanded] = useState(true);

    const failed = category.checks.filter(c => c.status === 'Failed').length;
    const warned = category.checks.filter(c => c.status === 'Warning').length;

    return (
        <div className="bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 overflow-hidden">
            <button
                onClick={() => setExpanded((v) => !v)}
                className="w-full flex justify-between items-center px-5 py-4 hover:bg-white/5 transition-colors text-left"
            >
                <div className="flex items-center gap-3 flex-wrap">
                    <span className="text-white font-bold">{category.name}</span>
                    <span className={`text-sm font-bold ${scoreColor(category.score)}`}>
                        {category.score}%
                    </span>
                    {(failed > 0 || warned > 0) && (
                        <span className="text-gray-500 text-xs">
                            {failed > 0 && <span className="text-red-400">{failed} failed</span>}
                            {failed > 0 && warned > 0 && <span className="text-gray-600"> · </span>}
                            {warned > 0 && <span className="text-yellow-400">{warned} warnings</span>}
                        </span>
                    )}
                </div>
                <span className="text-gray-400 text-xs flex-shrink-0 ml-2">{expanded ? '▲' : '▼'}</span>
            </button>

            {expanded && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 px-4 pb-4">
                    {category.checks.map((check, i) => (
                        <div
                            key={i}
                            className="bg-white/5 p-4 rounded-xl border border-white/10 text-left hover:border-white/30 transition-colors"
                        >
                            <div className="flex justify-between items-start mb-2">
                                <span className="text-blue-400 text-xs uppercase tracking-widest font-bold leading-tight">
                                    {check.name}
                                </span>
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border flex-shrink-0 ml-2 ${statusStyle(check.status)}`}>
                                    {check.status}
                                </span>
                            </div>
                            <p className="text-white font-medium text-sm mb-1">{check.message}</p>
                            {check.value && (
                                <p className="text-gray-500 text-xs truncate italic">Value: {check.value}</p>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default CategoryCard;
