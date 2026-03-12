import { Link } from 'react-router-dom';

function Footer() {
  return (
    <footer className="bg-white/60 dark:bg-background-dark/80 backdrop-blur-xl border-t border-primary/20 px-6 py-16 pb-32 md:pb-16 text-nordic-text dark:text-slate-100 relative z-10">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12">
        <div className="col-span-1 md:col-span-2">
          <h2 className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-rose-400 to-red-600 text-3xl font-black tracking-widest mb-6 drop-shadow-[0_0_8px_rgba(220,38,38,0.5)]">REDACTED</h2>
          <p className="text-nordic-text/90 dark:text-white/90 max-w-sm text-base leading-relaxed font-medium">
            A digital magazine dedicated to the pursuit of clarity, intention, and mindful existence in a chaotic world.
          </p>
          <div className="flex gap-3 mt-6">
            {['instagram','twitter','podcast','newsletter'].map(s => (
              <a key={s} href="#" className="w-10 h-10 rounded-full border border-nordic-accent/30 dark:border-white/30 flex items-center justify-center text-nordic-text dark:text-white hover:text-primary hover:border-primary/60 hover:bg-white/50 dark:hover:bg-white/10 transition-all capitalize text-sm font-bold shadow-sm">
                {s[0].toUpperCase()}
              </a>
            ))}
          </div>
        </div>
        <div>
          <h4 className="font-bold mb-6 uppercase text-sm tracking-widest text-nordic-text dark:text-white">Magazine</h4>
          <ul className="space-y-4 text-nordic-text/80 dark:text-slate-300 text-base font-medium">
            <li><Link to="/" className="hover:text-primary transition-colors">Featured</Link></li>
            <li><Link to="/explore" className="hover:text-primary transition-colors">Explore</Link></li>
            <li><Link to="/saved" className="hover:text-primary transition-colors">Saved Articles</Link></li>
            <li><Link to="/explore" className="hover:text-primary transition-colors">Categories</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold mb-6 uppercase text-sm tracking-widest text-nordic-text dark:text-white">Connect</h4>
          <ul className="space-y-4 text-nordic-text/80 dark:text-slate-300 text-base font-medium">
            <li><a href="#" className="hover:text-primary transition-colors">Instagram</a></li>
            <li><a href="#" className="hover:text-primary transition-colors">Twitter</a></li>
            <li><a href="#" className="hover:text-primary transition-colors">Podcast</a></li>
            <li><a href="#" className="hover:text-primary transition-colors">Newsletter</a></li>
          </ul>
        </div>
      </div>
      <div className="max-w-7xl mx-auto border-t border-nordic-accent/20 dark:border-white/20 mt-16 pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-nordic-text/70 dark:text-slate-400 text-sm font-medium">
        <p>© 2026 REDACTED MAGAZINE. All rights reserved.</p>
        <div className="flex gap-6">
          <a href="#" className="hover:text-primary transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-primary transition-colors">Terms of Service</a>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
