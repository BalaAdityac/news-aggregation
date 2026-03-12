import React, { useEffect, useRef, useMemo } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { articles } from '../data/articles';

export default function DashboardPage() {
  const containerRef = useRef(null);
  const particleContainerRef = useRef(null);
  const navigate = useNavigate();
  const { user, authLoading } = useApp();

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!containerRef.current) return;
      const x = (window.innerWidth / 2 - e.pageX) / 25;
      const y = (window.innerHeight / 2 - e.pageY) / 25;
      containerRef.current.style.transform = `translate(calc(-5% + ${x}px), calc(-5% + ${y}px))`;
    };

    const handleDeviceOrientation = (e) => {
      if (!containerRef.current) return;
      const x = (e.gamma || 0) / 2;
      const y = (e.beta || 0) / 2;
      containerRef.current.style.transform = `translate(calc(-5% + ${x}px), calc(-5% + ${y}px))`;
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('deviceorientation', handleDeviceOrientation);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('deviceorientation', handleDeviceOrientation);
    };
  }, []);

  useEffect(() => {
    if (!particleContainerRef.current) return;
    const container = particleContainerRef.current;
    const particleCount = 40; // Increased particle count
    
    // clear just in case
    container.innerHTML = '';

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        // Added glow effect to particles via box-shadow
        particle.className = 'absolute pointer-events-none -z-10 bg-pulse-green/60 rounded-full shadow-[0_0_10px_rgba(74,222,128,0.5)]';
        
        const size = Math.random() * 6 + 2; // Slightly larger particles
        const posX = Math.random() * 100;
        const posY = Math.random() * 100;
        const delay = Math.random() * 5;
        const duration = Math.random() * 10 + 10;

        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${posX}%`;
        particle.style.top = `${posY}%`;
        particle.style.opacity = (0.2 + Math.random() * 0.5).toString(); // Higher minimum opacity
        
        particle.animate([
            { transform: 'translate(0, 0)', opacity: 0 },
            { transform: 'translate(30px, -80px)', opacity: 0.8 },
            { transform: 'translate(-30px, -150px)', opacity: 0 }
        ], {
            duration: duration * 1000,
            iterations: Infinity,
            delay: delay * 1000,
            easing: 'ease-in-out'
        });

        container.appendChild(particle);
    }
  }, []);

  // Wait for Supabase session to resolve before redirecting
  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-pulse-bg">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-pulse-green/30 border-t-pulse-green rounded-full animate-spin" />
          <p className="text-pulse-green font-medium">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="relative text-slate-100 overflow-x-hidden font-sans bg-pulse-bg w-full flex-grow">
      <style>{`
        .glass-card {
          background: rgba(255, 255, 255, 0.12);
          backdrop-filter: blur(24px);
          -webkit-backdrop-filter: blur(24px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          box-shadow: inset 0 0 20px rgba(74, 222, 128, 0.08);
        }
        .progress-ring-circle {
          transition: stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1);
          transform: rotate(-90deg);
          transform-origin: 50% 50%;
        }
        .chart-path {
          stroke-dasharray: 1000;
          stroke-dashoffset: 1000;
          animation: drawLine 2.5s forwards ease-in-out;
        }
        @keyframes drawLine {
          to { stroke-dashoffset: 0; }
        }
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
      `}</style>
      
      {/* Background Layer */}
      <div 
        ref={containerRef}
        className="absolute top-0 left-0 w-[110%] h-[110%] z-0 transition-transform duration-100 ease-out"
        style={{ transform: 'translate(-5%, -5%)' }}
      >
        <img 
          alt="Background" 
          src="https://lh3.googleusercontent.com/aida-public/AB6AXuBKnTKGbPhr01D1k7c8ehYYHo8QmNkqUH89M2dSxhRgy8x2RhWZXVRfiauGFGJDCaTfVKfC7IvSIT_-cT4rmioEeri97Iidxzu3Mqhx1ktJ2D3O_9DSe_-r3aQX6JLSXBMT-TuSxpIB_AmnD467hiF539wErFtp3wdKhbxcwPPbWq3_rTZQEpSsANlBKsmp71IkcQfp-tOItcpIhGAqb_tqIjH4Rf0rTfXvFh1NHQswssdzCLue1W7rro_pW0U2Y8RrxkEYaiKGafvp" 
          className="w-full h-full object-cover opacity-80 saturate-75 contrast-125"
        />
        <div className="fixed inset-0 pointer-events-none" style={{ background: 'linear-gradient(to bottom, rgba(10, 18, 11, 0.45) 0%, rgba(10, 18, 11, 0.75) 100%)' }}></div>
      </div>
      
      <div ref={particleContainerRef} className="absolute inset-0 z-0 pointer-events-none overflow-hidden" />
      
      <main className="relative z-10 p-5 pt-8 md:pt-12 max-w-lg mx-auto pb-28">
        {/* Header Section */}
        <header className="flex justify-between items-start mb-10 pt-4">
          <div>
            <h2 className="tracking-widest uppercase text-3xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-rose-400 to-red-600 drop-shadow-[0_0_8px_rgba(220,38,38,0.5)] mb-2">THE PULSE</h2>
            <h1 className="text-3xl font-bold tracking-tight text-white mb-2 leading-tight">
              {(() => { const h = new Date().getHours(); return h < 12 ? 'Good Morning.' : h < 17 ? 'Good Afternoon.' : 'Good Evening.'; })()}
            </h1>
            <p className="text-pulse-green">{user?.email ? `Logged in as ${user.email.split('@')[0]}` : 'System Synchronized'}</p>
          </div>
          <div className="w-14 h-14 rounded-full border-2 border-pulse-green/30 overflow-hidden glass-card flex items-center justify-center shadow-lg shadow-pulse-green/20 bg-gradient-to-br from-emerald-800 to-teal-900">
            <span className="text-pulse-green font-black text-xl">
              {user?.email ? user.email[0].toUpperCase() : '?'}
            </span>
          </div>
        </header>

        {/* Stats Grid */}
        <section className="grid grid-cols-2 gap-4 mb-8">
          <div className="glass-card rounded-3xl p-5 flex flex-col items-center text-center" style={{ background: 'rgba(13, 148, 136, 0.25)', borderColor: 'rgba(20, 184, 166, 0.4)' }}>
            <div className="relative mb-3">
              <svg className="w-20 h-20">
                <defs>
                  <linearGradient id="progressGradient" x1="0%" x2="100%" y1="0%" y2="100%">
                    <stop offset="0%" stopColor="#4ADE80" />
                    <stop offset="100%" stopColor="#22D3EE" />
                  </linearGradient>
                </defs>
                <circle className="text-white/5" cx="40" cy="40" fill="transparent" r="34" stroke="currentColor" strokeWidth="6" />
                <circle className="progress-ring-circle" cx="40" cy="40" fill="transparent" r="34" stroke="url(#progressGradient)" strokeDasharray="213.6" strokeDashoffset="64" strokeLinecap="round" strokeWidth="7" style={{ filter: 'drop-shadow(0 0 5px rgba(74, 222, 128, 0.8))' }} />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center font-bold text-lg text-pulse-green">70%</div>
            </div>
            <p className="text-xs text-white/60 uppercase tracking-widest font-medium">Daily Goal</p>
            <p className="text-lg font-bold">42m / 60m</p>
          </div>

          <div className="glass-card rounded-3xl p-5 flex flex-col justify-between" style={{ background: 'rgba(21, 128, 61, 0.25)', borderColor: 'rgba(34, 197, 94, 0.4)' }}>
            <div className="flex justify-between items-start">
              <div className="p-2 bg-pulse-green/20 rounded-xl">
                <svg className="h-6 w-6 text-pulse-green" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                </svg>
              </div>
              <span className="text-xs font-bold text-pulse-green">+12%</span>
            </div>
            <div>
              <p className="text-xs text-white/60 uppercase tracking-widest font-medium">Streak</p>
              <p className="text-2xl font-bold">14 Days</p>
            </div>
          </div>
        </section>

        {/* Reading Insights */}
        <section className="glass-card rounded-3xl p-6 mb-8" style={{ background: 'rgba(30, 58, 138, 0.25)', borderColor: 'rgba(59, 130, 246, 0.4)' }}>
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-bold text-lg">Reading Insights</h3>
            <select className="bg-transparent border-none text-xs text-pulse-green font-bold outline-none cursor-pointer">
              <option className="bg-slate-900">This Week</option>
              <option className="bg-slate-900">This Month</option>
            </select>
          </div>
          <div className="h-32 w-full relative">
            <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 300 100">
              <line stroke="rgba(255,255,255,0.05)" strokeWidth="1" x1="0" x2="300" y1="20" y2="20" />
              <line stroke="rgba(255,255,255,0.05)" strokeWidth="1" x1="0" x2="300" y1="50" y2="50" />
              <line stroke="rgba(255,255,255,0.05)" strokeWidth="1" x1="0" x2="300" y1="80" y2="80" />
              <path className="chart-path drop-shadow-[0_0_8px_rgba(74,222,128,0.5)]" d="M0,80 Q30,70 60,85 T120,50 T180,30 T240,60 T300,10" fill="none" stroke="url(#lineGradient)" strokeLinecap="round" strokeWidth="5" style={{ filter: 'drop-shadow(0 0 10px rgba(74, 222, 128, 0.6))' }} />
              <path d="M0,80 Q30,70 60,85 T120,50 T180,30 T240,60 T300,10 V100 H0 Z" fill="url(#chartGradient)" opacity="0.1" />
              <defs>
                <linearGradient id="chartGradient" x1="0%" x2="0%" y1="0%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#4ADE80', stopOpacity: 0.4 }} />
                  <stop offset="100%" style={{ stopColor: '#22D3EE', stopOpacity: 0 }} />
                </linearGradient>
                <linearGradient id="lineGradient" x1="0%" x2="100%" y1="0%" y2="0%">
                  <stop offset="0%" stopColor="#4ADE80" />
                  <stop offset="50%" stopColor="#A8FF78" />
                  <stop offset="100%" stopColor="#22D3EE" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div className="flex justify-between mt-4 text-[10px] text-white/40 font-bold uppercase tracking-widest">
            <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
          </div>
        </section>

        {/* Trending */}
        <section className="mb-0">
          <div className="flex justify-between items-center mb-4 px-1">
            <h3 className="font-bold text-lg text-white">Trending Now</h3>
            <button className="text-xs text-pulse-green font-bold uppercase tracking-wider">See All</button>
          </div>
          <div className="flex overflow-x-auto hide-scrollbar gap-4 pb-4 snap-x">
            {articles.slice(0, 4).map((article) => (
              <div
                key={article.id}
                className="glass-card flex-shrink-0 w-64 rounded-3xl p-5 relative overflow-hidden group hover:border-pulse-green/50 transition-colors cursor-pointer snap-start"
                onClick={() => navigate(`/article/${article.id}`)}
              >
                <div className="absolute top-0 right-0 p-3">
                  <span className="bg-pulse-green text-pulse-bg text-[10px] font-bold px-2 py-1 rounded-full uppercase">{article.category}</span>
                </div>
                <p className="text-xs text-pulse-green mb-3">{article.readTime}</p>
                <h4 className="font-bold text-md leading-snug mb-4 group-hover:text-pulse-green transition-colors line-clamp-2 text-white">{article.title}</h4>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-pulse-green/20 flex items-center justify-center text-[10px] font-bold text-pulse-green">
                    {article.author[0]}
                  </div>
                  <span className="text-[11px] font-medium text-white/70">{article.author}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* NEW SECTION: Category Distribution */}
        <section className="mt-8">
          <h3 className="font-bold text-lg mb-4 px-1 text-white">Reading Distribution</h3>
          <div className="glass-card rounded-3xl p-6 grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-3">
              {[
                { label: 'Science', pct: 45, color: '#4ADE80' },
                { label: 'Technology', pct: 30, color: '#22D3EE' },
                { label: 'Politics', pct: 15, color: '#F43F5E' },
                { label: 'Arts', pct: 10, color: '#A855F7' }
              ].map(cat => (
                <div key={cat.label} className="flex flex-col gap-1">
                  <div className="flex justify-between text-[10px] uppercase font-bold text-white/60">
                    <span>{cat.label}</span>
                    <span>{cat.pct}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                    <div 
                      className="h-full rounded-full transition-all duration-1000 ease-out" 
                      style={{ width: `${cat.pct}%`, backgroundColor: cat.color, boxShadow: `0 0 8px ${cat.color}66` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            <div className="flex items-center justify-center relative">
              <div className="w-24 h-24 rounded-full border-4 border-white/5 flex items-center justify-center relative">
                <div className="text-center">
                  <span className="block text-2xl font-black text-white">124</span>
                  <span className="text-[8px] uppercase font-bold text-white/40">Total Reads</span>
                </div>
                {/* Decorative rings */}
                <div className="absolute inset-0 rounded-full border border-pulse-green/20 animate-ripple"></div>
              </div>
            </div>
          </div>
        </section>

        {/* NEW SECTION: Focus Mode & Reading Streaks */}
        <section className="mt-8 grid grid-cols-2 gap-4">
           <div className="glass-card rounded-3xl p-5 flex flex-col items-center justify-center bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border-indigo-500/30 group hover:scale-105 transition-all">
              <span className="material-symbols-outlined text-indigo-400 text-4xl mb-3 animate-pulse">timer</span>
              <h4 className="font-bold text-white text-sm">Focus Mode</h4>
              <p className="text-[10px] text-indigo-300 uppercase font-black tracking-tighter">Ready to Sprint</p>
           </div>
           <div className="glass-card rounded-3xl p-5 flex flex-col items-center justify-center bg-gradient-to-br from-amber-500/20 to-orange-500/20 border-amber-500/30 group hover:scale-105 transition-all">
              <span className="material-symbols-outlined text-amber-400 text-4xl mb-3">auto_awesome</span>
              <h4 className="font-bold text-white text-sm">Curation Mix</h4>
              <p className="text-[10px] text-amber-300 uppercase font-black tracking-tighter">AI Optimized</p>
           </div>
        </section>

        {/* NEW SECTION: Future Reading List / Events */}
        <section className="mt-8 mb-4">
          <h3 className="font-bold text-lg mb-4 px-1 text-white">Locked Content</h3>
          <div className="space-y-3">
             {[
               { title: "The Future of AI Architecture", release: "In 2 Hours", type: "Webinar" },
               { title: "Deep Dive: Nordic Economics", release: "Tomorrow", type: "Special Issue" }
             ].map((item, i) => (
               <div key={i} className="glass-card flex items-center justify-between p-4 rounded-2xl group cursor-help">
                 <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center group-hover:bg-pulse-green/20 transition-colors">
                       <span className="material-symbols-outlined text-white/40 group-hover:text-pulse-green">lock</span>
                    </div>
                    <div>
                       <h5 className="text-sm font-bold text-white">{item.title}</h5>
                       <p className="text-[10px] text-white/40 font-medium">{item.type}</p>
                    </div>
                 </div>
                 <span className="text-[10px] font-black py-1 px-3 bg-white/5 rounded-full text-white/60 group-hover:text-pulse-green">{item.release}</span>
               </div>
             ))}
          </div>
        </section>
      </main>
    </div>
  );
}
