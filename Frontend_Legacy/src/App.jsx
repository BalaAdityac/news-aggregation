import { Routes, Route, useNavigate, useParams } from 'react-router-dom';
import { useState, useMemo } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import JournalCard from './components/JournalCard';
import SkeletonCard, { SkeletonGrid } from './components/SkeletonCard';
import { useApp } from './context/AppContext';
import { articles, categories } from './data/articles';
import DashboardPage from './pages/DashboardPage';
import LoginPage from './pages/LoginPage';
import { Navigate, useLocation } from 'react-router-dom';

/* ── HOME PAGE ────────────────────────────────────────────────────── */
function HomePage() {
  const navigate = useNavigate();
  const featured = articles[0];
  const recent   = articles.slice(1, 5);
  const trending = articles.slice(5);

  return (
    <main className="flex-grow relative overflow-hidden bg-background-light dark:bg-black min-h-screen transition-colors duration-500">
      {/* Global Interactive Animated Background */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div
          className="absolute inset-0 bg-cover bg-center animate-cinematic-zoom opacity-80 dark:opacity-50"
          style={{ backgroundImage: `url('/hero-newspaper.png')` }}
        />
        {/* Very soft radial overlay to ensure readability without hiding the newspaper */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-transparent via-white/20 to-white/60 dark:from-transparent dark:via-black/40 dark:to-black/80 transition-colors duration-500" />
        <div className="absolute inset-0 bg-gradient-to-t from-background-light/90 via-transparent to-transparent dark:from-background-dark/80 dark:via-transparent dark:to-transparent transition-colors duration-500" />
        <div className="lens-flare hidden dark:block" />
      </div>

      <div className="relative z-10 pt-16">
        {/* Hero */}
        <section className="relative h-[60vh] w-full flex flex-col justify-end p-8 md:p-16 max-w-7xl mx-auto cursor-pointer">
          <span className="text-nordic-accent dark:text-white/80 text-sm font-semibold tracking-widest uppercase mb-2 drop-shadow-sm dark:drop-shadow-md">
            {featured.category}
          </span>
          <h2 className="text-nordic-text dark:text-white text-4xl md:text-6xl font-bold leading-tight mb-6 max-w-2xl hover:text-primary transition-colors drop-shadow-sm dark:drop-shadow-lg">
            {featured.title}
          </h2>
          <p className="text-nordic-text/80 dark:text-white/80 text-base md:text-lg mb-8 max-w-xl line-clamp-2 drop-shadow-sm dark:drop-shadow-md">{featured.excerpt}</p>
          <div className="flex flex-wrap gap-4">
            <button
              onClick={(e) => { e.stopPropagation(); navigate(`/article/${featured.id}`); }}
              className="bg-primary hover:bg-primary/90 text-white px-8 py-3 rounded-full font-medium transition-all shadow-lg shadow-primary/20 dark:shadow-xl dark:shadow-primary/30"
            >
              Read Issue
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); navigate('/explore'); }}
              className="bg-white/50 hover:bg-white/80 dark:bg-white/10 dark:hover:bg-white/20 backdrop-blur-md border border-nordic-accent/20 dark:border-white/30 text-nordic-text dark:text-white px-8 py-3 rounded-full font-medium transition-all shadow-md dark:shadow-xl"
            >
              Explore All
            </button>
          </div>
        </section>

        {/* Flash News Floating Cards */}
        <section className="py-12 overflow-hidden relative">
          <div className="flex items-center gap-4 mb-6 px-6 md:px-16 max-w-7xl mx-auto">
            <div className="flex items-center gap-2 bg-red-600/90 backdrop-blur-md text-white px-4 py-2 rounded-full text-xs font-black uppercase tracking-wider shadow-lg shadow-red-600/30 border border-red-500/50">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
              </span>
              Breaking Updates
            </div>
            <div className="h-[1px] flex-grow bg-gradient-to-r from-red-500/40 dark:from-red-500/50 to-transparent"></div>
          </div>
          
          <div className="flex-1 overflow-hidden mt-2">
            {/* Using animationDirection: 'reverse' makes it scroll from left to right */}
            <div className="flex w-max animate-marquee hover:[animation-play-state:paused] cursor-pointer" style={{ animationDirection: 'reverse', animationDuration: '60s' }}>
              {/* Array of fake news items duplicated 2 times for seamless looping (-50% translation) */}
              {[...Array(2)].map((_, i) => (
                <div key={i} className="flex gap-6 px-3 items-stretch">
                  <div className="w-80 md:w-96 bg-white/60 dark:bg-slate-900/40 backdrop-blur-xl rounded-3xl p-6 shadow-xl dark:shadow-2xl shadow-nordic-accent/10 dark:shadow-black/20 border border-white/40 dark:border-white/10 flex flex-col gap-3 group hover:bg-white/80 dark:hover:bg-white/10 hover:border-red-500/40 dark:hover:border-red-500/40 hover:-translate-y-2 transition-all duration-500">
                    <span className="text-red-600 dark:text-red-400 font-black uppercase tracking-widest text-[10px] drop-shadow-sm dark:drop-shadow-md">Markets</span>
                    <h4 className="font-bold text-lg text-nordic-text dark:text-white group-hover:text-red-600 dark:group-hover:text-red-400 transition-colors line-clamp-2 drop-shadow-sm dark:drop-shadow-md">Global Markets Surge to Record Highs in Early Trading</h4>
                    <p className="text-sm text-nordic-accent dark:text-white/80 line-clamp-4 leading-relaxed mt-2 drop-shadow-sm">
                      Tech stocks rallied an unprecedented 5% this morning as the new series of AI manufacturing chips began scaling globally. Investors are showing extreme confidence in the latest supply chain reports, pushing major indices past their previous all-time highs.
                    </p>
                    <span className="text-[10px] text-nordic-accent/60 dark:text-white/50 mt-auto pt-4 block font-bold uppercase tracking-widest">12 mins ago</span>
                  </div>

                  <div className="w-80 md:w-96 bg-white/60 dark:bg-slate-900/40 backdrop-blur-xl rounded-3xl p-6 shadow-xl dark:shadow-2xl shadow-nordic-accent/10 dark:shadow-black/20 border border-white/40 dark:border-white/10 flex flex-col gap-3 group hover:bg-white/80 dark:hover:bg-white/10 hover:border-red-500/40 dark:hover:border-red-500/40 hover:-translate-y-2 transition-all duration-500">
                    <span className="text-red-600 dark:text-red-400 font-black uppercase tracking-widest text-[10px] drop-shadow-sm dark:drop-shadow-md">Science</span>
                    <h4 className="font-bold text-lg text-nordic-text dark:text-white group-hover:text-red-600 dark:group-hover:text-red-400 transition-colors line-clamp-2 drop-shadow-sm dark:drop-shadow-md">New Breakthrough in Quantum Computing Announced</h4>
                    <p className="text-sm text-nordic-accent dark:text-white/80 line-clamp-4 leading-relaxed mt-2 drop-shadow-sm">
                      Researchers at leading institutes have successfully achieved stable qubits at room temperature for the very first time. This monumental leap eliminates the need for absolute zero cooling systems, paving the way for commercial quantum processors.
                    </p>
                    <span className="text-[10px] text-nordic-accent/60 dark:text-white/50 mt-auto pt-4 block font-bold uppercase tracking-widest">45 mins ago</span>
                  </div>

                  <div className="w-80 md:w-96 bg-white/60 dark:bg-slate-900/40 backdrop-blur-xl rounded-3xl p-6 shadow-xl dark:shadow-2xl shadow-nordic-accent/10 dark:shadow-black/20 border border-white/40 dark:border-white/10 flex flex-col gap-3 group hover:bg-white/80 dark:hover:bg-white/10 hover:border-red-500/40 dark:hover:border-red-500/40 hover:-translate-y-2 transition-all duration-500">
                    <span className="text-red-600 dark:text-red-400 font-black uppercase tracking-widest text-[10px] drop-shadow-sm dark:drop-shadow-md">Environment</span>
                    <h4 className="font-bold text-lg text-nordic-text dark:text-white group-hover:text-red-600 dark:group-hover:text-red-400 transition-colors line-clamp-2 drop-shadow-sm dark:drop-shadow-md">Exclusive: Upcoming Summit to Address Climate Goals</h4>
                    <p className="text-sm text-nordic-accent dark:text-white/80 line-clamp-4 leading-relaxed mt-2 drop-shadow-sm">
                      G7 leaders are preparing to outline a massive new $500B fund designed to completely accelerate the renewable energy grid transition over the next decade. The leaked drafted proposal shows aggressive timelines for phasing out fossil fuel subsidies.
                    </p>
                    <span className="text-[10px] text-nordic-accent/60 dark:text-white/50 mt-auto pt-4 block font-bold uppercase tracking-widest">1 hour ago</span>
                  </div>

                  <div className="w-80 md:w-96 bg-white/60 dark:bg-slate-900/40 backdrop-blur-xl rounded-3xl p-6 shadow-xl dark:shadow-2xl shadow-nordic-accent/10 dark:shadow-black/20 border border-white/40 dark:border-white/10 flex flex-col gap-3 group hover:bg-white/80 dark:hover:bg-white/10 hover:border-red-500/40 dark:hover:border-red-500/40 hover:-translate-y-2 transition-all duration-500">
                    <span className="text-red-600 dark:text-red-400 font-black uppercase tracking-widest text-[10px] drop-shadow-sm dark:drop-shadow-md">Technology</span>
                    <h4 className="font-bold text-lg text-nordic-text dark:text-white group-hover:text-red-600 dark:group-hover:text-red-400 transition-colors line-clamp-2 drop-shadow-sm dark:drop-shadow-md">REDACTED App Sees 200% User Growth Following Redesign</h4>
                    <p className="text-sm text-nordic-accent dark:text-white/80 line-clamp-4 leading-relaxed mt-2 drop-shadow-sm">
                      The premium news aggregation platform REDACTED has hit a staggering 5 million active users this week. The explosive growth comes on the heels of their massive visual overhaul and the introduction of advanced, AI-driven algorithmic curation.
                    </p>
                    <span className="text-[10px] text-nordic-accent/60 dark:text-white/50 mt-auto pt-4 block font-bold uppercase tracking-widest">2 hours ago</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Featured Journals */}
        <section className="py-12 px-6 md:px-16 max-w-7xl mx-auto w-full relative z-10">
          <div className="bg-white/60 dark:bg-black/30 backdrop-blur-2xl rounded-[3rem] p-8 md:p-12 border border-white/40 dark:border-white/10 shadow-xl dark:shadow-2xl">
            <div className="flex items-center justify-between mb-10">
              <div>
                <h3 className="text-3xl font-bold text-nordic-text dark:text-white drop-shadow-sm dark:drop-shadow-lg mb-2">Featured Journals</h3>
                <p className="text-nordic-accent dark:text-white/70 text-sm font-medium">Hand-picked stories for your afternoon</p>
              </div>
              <button
                onClick={() => navigate('/explore')}
                className="text-primary hover:text-white bg-primary/10 hover:bg-primary/50 transition-colors px-6 py-2 rounded-full font-bold text-sm flex items-center gap-2"
              >
                View All <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </button>
            </div>
            <div className="flex overflow-x-auto gap-8 no-scrollbar pb-8 -mx-4 px-4 snap-x">
              {recent.map(article => (
                <div key={article.id} className="flex-none w-72 md:w-80 snap-start transform transition-transform duration-500 hover:-translate-y-2">
                  <JournalCard article={article} />
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Trending */}
        <section className="py-12 px-6 md:px-16 max-w-7xl mx-auto w-full relative z-10">
          <div className="bg-white/60 dark:bg-black/30 backdrop-blur-2xl rounded-[3rem] p-8 md:p-12 border border-white/40 dark:border-white/10 shadow-xl dark:shadow-2xl">
            <h3 className="text-3xl font-bold text-nordic-text dark:text-white mb-10 drop-shadow-sm dark:drop-shadow-lg">Trending Now</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {trending.map(article => (
                <div key={article.id} className="bg-white/40 dark:bg-white/5 p-4 rounded-3xl border border-white/30 dark:border-white/10 hover:bg-white/60 dark:hover:bg-white/10 transition-colors shadow-md dark:shadow-lg">
                  <JournalCard article={article} variant="horizontal" />
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Newsletter */}
        <section className="py-24 px-6 relative z-10">
          <div className="bg-gradient-to-br from-white/80 via-white/60 to-white/80 dark:from-primary/20 dark:via-blue-900/20 dark:to-rose-500/20 backdrop-blur-3xl rounded-[3rem] p-12 max-w-4xl mx-auto text-center border border-white/50 dark:border-white/20 shadow-xl dark:shadow-[-10px_-10px_30px_rgba(255,255,255,0.05),_10px_10px_30px_rgba(0,0,0,0.5)]">
            <span className="material-symbols-outlined text-5xl text-primary mb-6 drop-shadow-sm dark:drop-shadow-[0_0_15px_rgba(74,144,226,0.6)]">mail</span>
            <h3 className="text-4xl font-bold mb-4 text-nordic-text dark:text-white drop-shadow-sm dark:drop-shadow-xl">Subscribe to REDACTED</h3>
            <p className="text-nordic-accent dark:text-white/80 mb-10 text-lg max-w-xl mx-auto">
              Get weekly insights into mindful living and intentional productivity delivered to your inbox.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 max-w-lg mx-auto">
              <input
                className="flex-grow rounded-full px-8 py-4 bg-white/50 dark:bg-black/40 backdrop-blur-xl border border-white/60 dark:border-white/20 focus:ring-2 focus:ring-primary outline-none text-nordic-text dark:text-white placeholder-nordic-accent/60 dark:placeholder-white/40 shadow-inner"
                placeholder="Your email address"
                type="email"
              />
              <button className="bg-primary hover:bg-primary/90 dark:hover:bg-white dark:hover:text-primary text-white px-10 py-4 rounded-full font-bold shadow-xl shadow-primary/30 transition-all duration-300 transform active:scale-95">
                Join
              </button>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

/* ── EXPLORE PAGE ─────────────────────────────────────────────────── */
function ExplorePage() {
  const [activeCategory, setActiveCategory] = useState('All');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return articles.filter(a => {
      const matchCat = activeCategory === 'All' || a.category === activeCategory;
      const q = search.trim().toLowerCase();
      const matchSearch = !q ||
        a.title.toLowerCase().includes(q) ||
        a.author.toLowerCase().includes(q) ||
        a.tags.some(t => t.includes(q));
      return matchCat && matchSearch;
    });
  }, [activeCategory, search]);

  return (
    <main className="flex-grow py-10 px-6 md:px-16 max-w-7xl mx-auto w-full">
      <div className="mb-10">
        <h2 className="text-3xl font-bold text-nordic-text dark:text-slate-100 mb-2">Explore</h2>
        <p className="text-nordic-accent text-sm">Browse all articles by topic or search</p>
      </div>

      {/* Search */}
      <div className="relative mb-8 max-w-lg">
        <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-nordic-accent">search</span>
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search articles…"
          className="w-full pl-11 pr-4 py-3 rounded-full border border-nordic-accent/20 bg-white dark:bg-slate-800 text-nordic-text dark:text-slate-100 placeholder-nordic-accent/50 outline-none focus:ring-2 focus:ring-primary transition"
        />
      </div>

      {/* Category chips */}
      <div className="flex flex-wrap gap-2 mb-10">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-5 py-2 rounded-full text-sm font-semibold transition-all border
              ${activeCategory === cat
                ? 'bg-primary text-white border-primary shadow-lg shadow-primary/20'
                : 'bg-white dark:bg-slate-800 text-nordic-accent border-nordic-accent/20 hover:border-primary/40 hover:text-primary'
              }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Grid */}
      {filtered.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {filtered.map(article => (
            <JournalCard key={article.id} article={article} />
          ))}
        </div>
      ) : (
        <div className="py-20 text-center text-nordic-accent">
          <span className="material-symbols-outlined text-5xl mb-4 block opacity-30">search_off</span>
          <p className="text-lg">No articles found</p>
          <button
            onClick={() => { setActiveCategory('All'); setSearch(''); }}
            className="mt-4 text-primary text-sm hover:underline"
          >
            Clear filters
          </button>
        </div>
      )}
    </main>
  );
}

/* ── SAVED PAGE ───────────────────────────────────────────────────── */
function SavedPage() {
  const { savedArticles, toggleSave } = useApp();
  const navigate = useNavigate();

  const saved = articles.filter(a => savedArticles.includes(a.id));

  return (
    <main className="flex-grow py-10 px-6 md:px-16 max-w-7xl mx-auto w-full">
      <div className="mb-10">
        <h2 className="text-3xl font-bold text-nordic-text dark:text-slate-100 mb-2">Saved</h2>
        <p className="text-nordic-accent text-sm">
          {saved.length} {saved.length === 1 ? 'article' : 'articles'} saved for later
        </p>
      </div>

      {saved.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {saved.map(article => (
            <JournalCard key={article.id} article={article} />
          ))}
        </div>
      ) : (
        <div className="py-24 text-center text-nordic-accent">
          <span className="material-symbols-outlined text-6xl mb-6 block opacity-20">bookmark_border</span>
          <h3 className="text-xl font-semibold text-nordic-text dark:text-slate-200 mb-2">No saved articles yet</h3>
          <p className="text-sm mb-6">Tap the bookmark icon on any article to save it here</p>
          <button
            onClick={() => navigate('/explore')}
            className="bg-primary text-white px-8 py-3 rounded-full font-semibold hover:bg-primary/90 transition-colors"
          >
            Explore Articles
          </button>
        </div>
      )}
    </main>
  );
}

/* ── ARTICLE PAGE ─────────────────────────────────────────────────── */
function ArticlePage() {
  const { id } = useParams();
  const { isSaved, toggleSave, user } = useApp();
  const navigate = useNavigate();
  const location = useLocation();

  const article = articles.find(a => a.id === id);
  const related = articles.filter(a => a.id !== id && a.category === article?.category).slice(0, 3);

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!article) {
    return (
      <main className="flex-grow py-20 text-center text-nordic-accent">
        <span className="material-symbols-outlined text-5xl mb-4 block opacity-30">article</span>
        <p className="text-lg">Article not found</p>
        <button onClick={() => navigate(-1)} className="mt-4 text-primary hover:underline text-sm">Go back</button>
      </main>
    );
  }

  const saved = isSaved(article.id);

  return (
    <main className="flex-grow">
      {/* Article Hero */}
      <div className="relative h-64 md:h-96 w-full overflow-hidden">
        <img src={article.img} alt={article.title} className="w-full h-full object-cover" />
        <div className="absolute inset-0 hero-gradient" />
        <div className="absolute inset-0 flex flex-col justify-end p-6 md:p-12">
          <span className="text-white/80 text-xs font-bold uppercase tracking-widest mb-2">{article.category}</span>
          <h1 className="text-white text-3xl md:text-5xl font-bold leading-tight max-w-3xl">{article.title}</h1>
        </div>
      </div>

      {/* Article meta + content */}
      <div className="max-w-3xl mx-auto px-6 py-10">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
              <span className="text-primary font-bold text-sm">{article.author[0]}</span>
            </div>
            <div>
              <p className="text-sm font-semibold text-nordic-text dark:text-slate-100">{article.author}</p>
              <p className="text-xs text-nordic-accent">{article.date} · {article.readTime}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => toggleSave(article.id)}
              className={`p-2 rounded-full border transition-all ${saved ? 'bg-primary text-white border-primary' : 'border-nordic-accent/20 text-nordic-accent hover:border-primary hover:text-primary'}`}
              title={saved ? 'Remove from saved' : 'Save article'}
            >
              <span className="material-symbols-outlined text-xl">{saved ? 'bookmark' : 'bookmark_border'}</span>
            </button>
            <button
              onClick={() => navigate(-1)}
              className="p-2 rounded-full border border-nordic-accent/20 text-nordic-accent hover:border-primary hover:text-primary transition-all"
              title="Go back"
            >
              <span className="material-symbols-outlined text-xl">arrow_back</span>
            </button>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-8">
          {article.tags.map(tag => (
            <span key={tag} className="px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold capitalize">
              #{tag}
            </span>
          ))}
        </div>

        {/* Content */}
        <article
          className="prose prose-slate dark:prose-invert max-w-none text-nordic-text dark:text-slate-200 leading-relaxed
            prose-h2:font-bold prose-h2:text-2xl prose-h2:mt-10 prose-h2:mb-4 prose-h2:text-nordic-text dark:prose-h2:text-slate-100
            prose-p:mb-5 prose-p:text-base"
          dangerouslySetInnerHTML={{ __html: article.content }}
        />
      </div>

      {/* Related */}
      {related.length > 0 && (
        <section className="border-t border-nordic-accent/10 py-12 px-6 md:px-16 max-w-7xl mx-auto w-full">
          <h3 className="text-2xl font-bold text-nordic-text dark:text-slate-100 mb-8">More in {article.category}</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {related.map(a => <JournalCard key={a.id} article={a} />)}
          </div>
        </section>
      )}
    </main>
  );
}

/* ── PROFILE PAGE ─────────────────────────────────────────────────── */
function ProfilePage() {
  const { savedArticles, darkMode, setDarkMode, user, logout } = useApp();
  const navigate = useNavigate();

  const stats = [
    { label: 'Saved', value: savedArticles.length, icon: 'bookmark' },
    { label: 'Categories', value: categories.length - 1, icon: 'category' },
    { label: 'Articles', value: articles.length, icon: 'article' },
  ];

  const prefs = [
    { label: 'Dark Mode', icon: darkMode ? 'light_mode' : 'dark_mode', action: () => setDarkMode(!darkMode), value: darkMode ? 'On' : 'Off' },
    { label: 'Saved Articles', icon: 'bookmark', action: () => navigate('/saved'), value: `${savedArticles.length} saved` },
    { label: 'Explore Topics', icon: 'explore', action: () => navigate('/explore'), value: 'Browse' },
  ];

  if (user) {
    prefs.push({ 
      label: 'Logout', 
      icon: 'logout', 
      action: () => { logout(); navigate('/'); }, 
      value: 'Sign Out' 
    });
  }

  return (
    <main className="flex-grow relative overflow-hidden min-h-screen">
      {/* Profile Live Background Array */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div
          className="absolute inset-0 bg-cover bg-center animate-cinematic-zoom opacity-80 dark:opacity-60"
          style={{ backgroundImage: `url('/profile-bg.png')` }}
        />
        {/* Soft morning light / warm gradient for Profile */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-amber-500/10 via-white/40 to-white/70 dark:from-transparent dark:via-black/50 dark:to-black/80 transition-colors duration-500" />
        <div className="absolute inset-0 bg-gradient-to-t from-background-light/90 via-transparent to-transparent dark:from-background-dark/90 dark:via-transparent dark:to-transparent transition-colors duration-500" />
      </div>

      <div className="relative z-10 py-10 px-6 md:px-16 max-w-4xl mx-auto w-full pt-20 pb-32">
        {/* Avatar Section Container */}
        <div className="bg-white/60 dark:bg-black/40 backdrop-blur-2xl rounded-3xl p-8 mb-10 shadow-2xl border border-white/40 dark:border-white/10 flex flex-col items-center text-center transform transition-transform duration-500 hover:-translate-y-1">
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-amber-600 to-rose-400 flex items-center justify-center mb-6 shadow-xl shadow-amber-600/30 ring-4 ring-white/50 dark:ring-white/10">
            <span className="material-symbols-outlined text-white text-5xl">person</span>
          </div>
          <h2 className="text-3xl font-black text-nordic-text dark:text-white drop-shadow-md">{user ? (user.user_metadata?.full_name || user.email?.split('@')[0] || 'Reader') : 'Guest Reader'}</h2>
          <p className="text-nordic-accent dark:text-white/70 text-sm mt-2 font-medium">{user ? user.email : 'Join to unlock full access'}</p>
          {!user && (
            <button 
              onClick={() => navigate('/login')}
              className="mt-6 px-8 py-3 bg-amber-600/90 hover:bg-amber-600 text-white rounded-full text-sm font-bold shadow-lg shadow-amber-600/30 transition-all transform hover:scale-105 active:scale-95 border border-amber-400/30"
            >
              Sign In
            </button>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-12">
          {stats.map(s => (
            <div key={s.label} className="bg-white/60 dark:bg-black/40 backdrop-blur-xl rounded-2xl p-6 text-center shadow-xl border border-white/40 dark:border-white/10 flex flex-col items-center group transition-all duration-300 hover:bg-white/80 dark:hover:bg-black/60 hover:-translate-y-1">
              <span className="material-symbols-outlined text-amber-600 dark:text-amber-400 text-3xl mb-3 drop-shadow-sm group-hover:scale-110 transition-transform">{s.icon}</span>
              <p className="text-3xl font-black text-nordic-text dark:text-white drop-shadow-sm">{s.value}</p>
              <p className="text-xs font-bold uppercase tracking-widest text-nordic-accent dark:text-white/60 mt-1">{s.label}</p>
            </div>
          ))}
        </div>

        {/* Preferences */}
        <div className="bg-white/60 dark:bg-black/40 backdrop-blur-2xl rounded-3xl p-8 border border-white/40 dark:border-white/10 shadow-2xl mb-12">
          <h3 className="text-xl font-bold text-nordic-text dark:text-white mb-6 flex items-center gap-2 drop-shadow-md">
            <span className="material-symbols-outlined text-amber-500">settings</span>
            Preferences
          </h3>
          <div className="flex flex-col gap-4">
            {prefs.map(p => (
              <button
                key={p.label}
                onClick={p.action}
                className="w-full flex items-center justify-between px-6 py-4 rounded-2xl bg-white/50 dark:bg-white/5 border border-white/50 dark:border-white/10 hover:border-amber-500/40 dark:hover:border-amber-500/40 hover:bg-white/80 dark:hover:bg-white/10 shadow-sm hover:shadow-lg transition-all text-left group"
              >
                <div className="flex items-center gap-4">
                  <span className="material-symbols-outlined text-amber-600 dark:text-amber-400 transition-transform group-hover:scale-110">{p.icon}</span>
                  <span className="text-sm font-bold text-nordic-text dark:text-white transition-colors">{p.label}</span>
                </div>
                <div className="flex items-center gap-2 text-sm font-semibold text-nordic-accent dark:text-white/70">
                  {p.value}
                  <span className="material-symbols-outlined text-xl transition-transform group-hover:translate-x-1">chevron_right</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Reading categories */}
        <div className="bg-white/60 dark:bg-black/40 backdrop-blur-2xl rounded-3xl p-8 border border-white/40 dark:border-white/10 shadow-2xl">
          <h3 className="text-xl font-bold text-nordic-text dark:text-white mb-6 flex items-center gap-2 drop-shadow-md">
            <span className="material-symbols-outlined text-amber-500">label</span>
            Browse by Category
          </h3>
          <div className="flex flex-wrap gap-3">
            {categories.filter(c => c !== 'All').map(cat => (
              <button
                key={cat}
                onClick={() => navigate(`/explore?cat=${cat}`)}
                className="px-6 py-2 rounded-full text-sm font-bold bg-white/80 text-amber-700 border border-amber-200 shadow-sm hover:shadow-md hover:bg-amber-600 hover:text-white dark:bg-white/10 dark:text-amber-400 dark:border-amber-400/30 dark:hover:bg-amber-500 dark:hover:text-white transition-all transform hover:-translate-y-0.5"
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}

/* ── APP (Router shell) ───────────────────────────────────────────── */
function App() {
  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-x-hidden font-display">
      <Header />

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/explore" element={<ExplorePage />} />
        <Route path="/saved" element={<SavedPage />} />
        <Route path="/article/:id" element={<ArticlePage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="*" element={<HomePage />} />
      </Routes>

      <Footer />

      {/* Mobile Bottom Nav */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white/95 dark:bg-background-dark/95 backdrop-blur-md border-t border-nordic-accent/10 px-4 pb-6 pt-3 md:hidden z-50 safe-area-inset-bottom">
        <div className="flex justify-around items-center max-w-md mx-auto">
          {[
            { to: '/', icon: 'home', label: 'Home' },
            { to: '/dashboard', icon: 'dashboard', label: 'Dash' },
            { to: '/explore', icon: 'explore', label: 'Explore' },
            { to: '/saved', icon: 'bookmark', label: 'Saved' },
            { to: '/profile', icon: 'person', label: 'Profile' },
          ].map(item => (
            <MobileNavItem key={item.to} {...item} />
          ))}
        </div>
      </nav>
    </div>
  );
}

function MobileNavItem({ to, icon, label }) {
  const { pathname } = window.location;
  // Use React Router's Link for navigation
  const navigate = useNavigate();
  const isActive = pathname === to || (to !== '/' && pathname.startsWith(to));

  return (
    <button
      onClick={() => navigate(to)}
      className={`flex flex-col items-center gap-1 transition-colors ${isActive ? 'text-primary' : 'text-nordic-accent hover:text-primary'}`}
    >
      <span className={`material-symbols-outlined ${isActive ? 'filled' : ''}`}>{icon}</span>
      <span className="text-[10px] font-bold uppercase tracking-wider">{label}</span>
    </button>
  );
}

export default App;
