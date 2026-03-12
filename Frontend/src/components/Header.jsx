import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import SearchModal from './SearchModal';
import MobileMenuDrawer from './MobileMenuDrawer';

const navLinks = [
  { to: '/', label: 'Home' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/explore', label: 'Explore' },
  { to: '/saved', label: 'Saved' },
  { to: '/profile', label: 'Profile' },
];

function Header() {
  const { darkMode, setDarkMode } = useApp();
  const [searchOpen, setSearchOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();

  return (
    <>
      <header className="sticky top-0 z-50 flex items-center bg-white/70 dark:bg-background-dark/70 backdrop-blur-xl px-4 md:px-6 py-4 justify-between border-b border-primary/10">
        {/* Left: hamburger (mobile) + desktop nav */}
        <div className="flex items-center gap-6">
          <button onClick={() => setMenuOpen(true)} className="text-nordic-text dark:text-slate-100 md:hidden hover:text-primary transition-colors">
            <span className="material-symbols-outlined">menu</span>
          </button>
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map(l => (
              <Link
                key={l.to}
                to={l.to}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                  ${location.pathname === l.to
                    ? 'text-primary bg-primary/10'
                    : 'text-nordic-text dark:text-slate-100 hover:text-primary hover:bg-primary/5'}`}
              >
                {l.label}
              </Link>
            ))}
          </nav>
        </div>

        {/* Center: Logo */}
        <Link to="/" className="absolute left-1/2 -translate-x-1/2 group">
          <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-rose-400 to-red-600 text-2xl font-black tracking-[0.2em] transform transition-all duration-300 group-hover:scale-105 group-hover:drop-shadow-[0_0_8px_rgba(220,38,38,0.5)]">
            REDACTED
          </h1>
        </Link>

        {/* Right: actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSearchOpen(true)}
            className="p-2 rounded-lg text-nordic-text dark:text-slate-100 hover:text-primary hover:bg-primary/5 transition-all"
          >
            <span className="material-symbols-outlined">search</span>
          </button>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-lg text-nordic-text dark:text-slate-100 hover:text-primary hover:bg-primary/5 transition-all"
            title={darkMode ? 'Light mode' : 'Dark mode'}
          >
            <span className="material-symbols-outlined">{darkMode ? 'light_mode' : 'dark_mode'}</span>
          </button>
          <Link to="/profile" className="p-2 rounded-lg text-nordic-text dark:text-slate-100 hover:text-primary hover:bg-primary/5 transition-all">
            <span className="material-symbols-outlined">account_circle</span>
          </Link>
        </div>
      </header>

      {searchOpen && <SearchModal onClose={() => setSearchOpen(false)} />}
      <MobileMenuDrawer isOpen={menuOpen} onClose={() => setMenuOpen(false)} />
    </>
  );
}

export default Header;
