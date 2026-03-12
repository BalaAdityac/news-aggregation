import { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';

const navLinks = [
  { to: '/', label: 'Home', icon: 'home' },
  { to: '/explore', label: 'Explore', icon: 'explore' },
  { to: '/saved', label: 'Saved', icon: 'bookmark' },
  { to: '/profile', label: 'Profile', icon: 'person' },
];

function MobileMenuDrawer({ isOpen, onClose }) {
  const location = useLocation();
  const { darkMode, setDarkMode } = useApp();

  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  useEffect(() => { onClose(); }, [location.pathname, onClose]);

  return (
    <>
      {/* Backdrop */}
      <div
        className={`fixed inset-0 bg-black/60 backdrop-blur-sm z-[150] transition-opacity duration-300 ${isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
        onClick={onClose}
      />
      {/* Drawer */}
      <aside
        className={`fixed left-0 top-0 h-full w-72 bg-white dark:bg-background-dark z-[160] shadow-2xl flex flex-col transition-transform duration-300 ease-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="flex items-center justify-between px-6 py-5 border-b border-nordic-accent/10">
          <span className="text-xl font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-rose-400 to-red-600 drop-shadow-[0_0_8px_rgba(220,38,38,0.5)]">REDACTED</span>
          <button onClick={onClose} className="text-nordic-accent hover:text-nordic-text dark:hover:text-slate-100 transition-colors">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <nav className="flex-1 py-6 px-4 space-y-1">
          {navLinks.map(l => {
            const active = location.pathname === l.to;
            return (
              <Link
                key={l.to}
                to={l.to}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all text-sm
                  ${active ? 'bg-primary/10 text-primary' : 'text-nordic-text dark:text-slate-100 hover:bg-nordic-accent/10'}`}
              >
                <span className={`material-symbols-outlined text-xl ${active ? 'filled' : ''}`}>{l.icon}</span>
                {l.label}
              </Link>
            );
          })}
        </nav>

        <div className="p-6 border-t border-nordic-accent/10">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-nordic-text dark:text-slate-100 hover:bg-nordic-accent/10 transition-colors text-sm font-medium"
          >
            <span className="material-symbols-outlined">{darkMode ? 'light_mode' : 'dark_mode'}</span>
            {darkMode ? 'Light Mode' : 'Dark Mode'}
          </button>
          <p className="text-center text-xs text-nordic-accent/50 mt-4">© 2026 REDACTED Magazine</p>
        </div>
      </aside>
    </>
  );
}

export default MobileMenuDrawer;
