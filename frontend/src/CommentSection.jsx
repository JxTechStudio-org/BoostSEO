import { useEffect, useState } from 'react';
import axios from 'axios';

const isValidEmail = (value) => /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value);

const CommentSection = () => {
    const [comments, setComments] = useState([]);
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [body, setBody] = useState('');
    const [website, setWebsite] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        axios.get('/api/comments')
            .then((res) => setComments(res.data))
            .catch(() => {});
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        const trimmedName = name.trim();
        const trimmedEmail = email.trim();
        const trimmedBody = body.trim();

        if (!trimmedName || !trimmedEmail || !trimmedBody) {
            setError('Please fill in your name, email, and comment.');
            return;
        }
        if (!isValidEmail(trimmedEmail)) {
            setError('Please enter a valid email address.');
            return;
        }

        setSubmitting(true);
        try {
            const response = await axios.post('/api/comments', {
                name: trimmedName,
                email: trimmedEmail,
                body: trimmedBody,
                website: website.trim(),
            });
            setComments((prev) => [response.data, ...prev]);
            setName('');
            setEmail('');
            setBody('');
            setWebsite('');
        } catch (err) {
            if (err.response?.status === 429) {
                setError('Please wait a bit before submitting another comment.');
            } else {
                setError('Unable to submit your comment. Please try again.');
            }
        }
        setSubmitting(false);
    };

    return (
        <div className="mt-12 text-left">
            <h2 className="text-2xl font-bold text-white mb-4">What people think</h2>

            <form
                onSubmit={handleSubmit}
                className="bg-white/5 backdrop-blur-md p-5 rounded-xl border border-white/10 mb-6 space-y-3"
            >
                <div className="flex flex-col md:flex-row gap-3">
                    <input
                        type="text"
                        placeholder="Your name"
                        className="flex-1 p-3 bg-white/5 text-white rounded-lg border border-white/10 outline-none placeholder-gray-500"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        maxLength={100}
                    />
                    <input
                        type="email"
                        placeholder="Your email (kept private)"
                        className="flex-1 p-3 bg-white/5 text-white rounded-lg border border-white/10 outline-none placeholder-gray-500"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        maxLength={200}
                    />
                </div>
                <input
                    type="text"
                    name="website"
                    value={website}
                    onChange={(e) => setWebsite(e.target.value)}
                    style={{ position: 'absolute', left: '-9999px', width: '1px', height: '1px', overflow: 'hidden' }}
                    tabIndex={-1}
                    autoComplete="off"
                    aria-hidden="true"
                />
                <textarea
                    placeholder="What do you think of BoostSEO?"
                    className="w-full p-3 bg-white/5 text-white rounded-lg border border-white/10 outline-none placeholder-gray-500 min-h-24"
                    value={body}
                    onChange={(e) => setBody(e.target.value)}
                    maxLength={2000}
                />
                {error && (
                    <p className="text-red-400 bg-red-400/10 p-3 rounded-lg border border-red-400/20 text-sm">
                        {error}
                    </p>
                )}
                <button
                    type="submit"
                    disabled={submitting}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-2 px-6 rounded-xl transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
                >
                    {submitting ? 'Submitting…' : 'Submit Comment'}
                </button>
            </form>

            <div className="space-y-3">
                {comments.map((c) => (
                    <div key={c.id} className="bg-white/5 p-4 rounded-xl border border-white/10">
                        <div className="flex justify-between items-baseline mb-1">
                            <span className="text-white font-semibold text-sm">{c.name}</span>
                            <span className="text-gray-500 text-xs">
                                {new Date(c.created_at).toLocaleDateString()}
                            </span>
                        </div>
                        <p className="text-gray-300 text-sm">{c.body}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CommentSection;
