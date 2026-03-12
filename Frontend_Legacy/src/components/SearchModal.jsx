import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { articles } from '../data/articles';

function SearchModal({ onClose }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const inputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    inputRef.current?.focus();
    const onKey = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  useEffect(() => {
    const q = query.trim().toLowerCase();
    if (!q) { setResults([]); return; }
    const filtered = articles.filter(a =>
      a.title.toLowerCase().includes(q) ||
      a.category.toLowerCase().includes(q) ||
      a.author.toLowerCase().includes(q) ||
      a.tags.some(t => t.includes(q))
    );
    setResults(filtered.slice(0, 6));
  }, [query]);

  const go = (article) => { navigate(`/article/${article.id}`); onClose(); };

  return (
    <div
      className="fixed inset-0 bg-black/70 backdrop-blur-md z-[300] flex items-start justify-center pt-16 px-4 animate-fade-in"
      onClick={onClose}
    >
      <div
        className="w-full max-w-2xl bg-white dark:bg-background-dark rounded-2xl shadow-2xl overflow-hidden animate-slide-down"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 px-5 py-4 border-b border-nordic-accent/10">
          <span className="material-symbols-outlined text-nordic-accent">search</span>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search articles, topics, authors…"
            className="flex-1 bg-transparent text-nordic-text dark:text-slate-100 placeholder-nordic-accent/60 text-base outline-none"
          />
          <button onClick={onClose} className="text-nordic-accent hover:text-nordic-text dark:hover:text-slate-100 transition-colors">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {results.length > 0 ? (
          <ul className="divide-y divide-nordic-accent/10 max-h-96 overflow-y-auto">
            {results.map(article => (
              <li key={article.id}>
                <button
                  onClick={() => go(article)}
                  className="w-full flex items-center gap-4 px-5 py-3 hover:bg-nordic-accent/5 text-left transition-colors group"
                >
                  <img src={article.img} alt="" className="w-12 h-12 rounded-lg object-cover flex-none" />
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-nordic-text dark:text-slate-100 group-hover:text-primary transition-colors truncate">{article.title}</p>
                    <p className="text-xs text-nordic-accent mt-0.5">{article.category} · {article.author}</p>
                  </div>
                  <span className="material-symbols-outlined text-nordic-accent/40 ml-auto flex-none">arrow_forward</span>
                </button>
              </li>
            ))}
          </ul>
        ) : query ? (
          <div className="py-12 text-center text-nordic-accent">
            <span className="material-symbols-outlined text-4xl mb-3 block">search_off</span>
            <p className="text-sm">No articles found for "{query}"</p>
          </div>
        ) : (
          <div className="py-12 text-center text-nordic-accent">
            <span className="material-symbols-outlined text-4xl mb-3 block opacity-30">search</span>
            <p className="text-sm opacity-60">Start typing to search articles…</p>
          </div>
        )}

        <div className="px-5 py-3 border-t border-nordic-accent/10 flex items-center gap-4 text-xs text-nordic-accent/60">
          <span><kbd className="bg-nordic-accent/10 px-1.5 py-0.5 rounded">↵</kbd> to select</span>
          <span><kbd className="bg-nordic-accent/10 px-1.5 py-0.5 rounded">Esc</kbd> to close</span>
        </div>
      </div>
    </div>
  );
}

export default SearchModal;
