import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const { login, signUp, addToast } = useApp();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) return;
    
    setLoading(true);
    try {
      if (isLogin) {
        await login(email, password);
        navigate(from, { replace: true });
      } else {
        const session = await signUp(email, password);
        if (session) {
          // Email confirmation is OFF — user is logged in immediately
          navigate('/dashboard', { replace: true });
        } else {
          // Email confirmation is ON — ask them to check inbox
          addToast('Check your email to confirm your account, then log in.', 'info');
          setIsLogin(true);
        }
      }
    } catch (err) {
      addToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-6">
      <div className="glass-card w-full max-w-md p-8 rounded-[2rem] border border-white/20 bg-white/10 backdrop-blur-3xl shadow-2xl relative overflow-hidden group">
        {/* Decorative background glow */}
        <div className="absolute -top-24 -left-24 w-48 h-48 bg-primary/20 rounded-full blur-[80px] group-hover:bg-primary/30 transition-all duration-700"></div>
        <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-rose-500/10 rounded-full blur-[80px] group-hover:bg-rose-500/20 transition-all duration-700"></div>

        <div className="relative z-10">
          <div className="text-center mb-10">
            <h2 className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-rose-400 to-red-600 text-3xl font-black tracking-widest mb-2 drop-shadow-[0_0_8px_rgba(220,38,38,0.5)]">
              REDACTED
            </h2>
            <p className="text-nordic-accent text-sm font-medium">
              {isLogin ? 'Please sign in to continue reading' : 'Join the Inner Circle'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-xs font-bold uppercase tracking-widest text-nordic-accent mb-2 ml-1">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-5 py-4 rounded-2xl bg-white/5 border border-white/10 text-nordic-text dark:text-white placeholder-white/20 focus:ring-2 focus:ring-primary outline-none transition-all"
                placeholder="name@example.com"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-widest text-nordic-accent mb-2 ml-1">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-5 py-4 rounded-2xl bg-white/5 border border-white/10 text-nordic-text dark:text-white placeholder-white/20 focus:ring-2 focus:ring-primary outline-none transition-all"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-red-600 to-rose-500 hover:from-red-500 hover:to-rose-400 disabled:opacity-50 text-white font-bold py-4 rounded-2xl shadow-xl shadow-red-600/20 transform transition-all active:scale-95 flex items-center justify-center gap-2 group"
            >
              {loading ? 'Processing...' : (isLogin ? 'Unlock Access' : 'Create Account')}
              {!loading && <span className="material-symbols-outlined text-xl group-hover:translate-x-1 transition-transform">arrow_forward</span>}
            </button>
          </form>

          <p className="mt-8 text-center text-xs text-nordic-accent">
             {isLogin ? "Don't have an account?" : "Already have an account?"} 
             <button 
                onClick={() => setIsLogin(!isLogin)} 
                className="text-primary font-bold hover:underline ml-1"
             >
                {isLogin ? 'Join the Inner Circle' : 'Sign in instead'}
             </button>
          </p>
        </div>
      </div>
    </div>
  );
}
