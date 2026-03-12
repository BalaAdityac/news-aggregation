import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';

function JournalCard({ article, variant = 'vertical' }) {
  const { isSaved, toggleSave } = useApp();
  const navigate = useNavigate();
  const saved = isSaved(article.id);

  if (variant === 'horizontal') {
    return (
      <div
        className="flex gap-4 cursor-pointer group"
        onClick={() => navigate(`/article/${article.id}`)}
      >
        <div className="relative flex-none w-32 h-24 rounded-xl overflow-hidden">
          <img src={article.img} alt={article.title} className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
        </div>
        <div className="flex-1 min-w-0">
          <span className="text-[10px] font-bold uppercase tracking-wider text-primary">{article.category}</span>
          <h4 className="text-sm font-bold text-nordic-text dark:text-slate-100 group-hover:text-primary transition-colors line-clamp-2 mt-0.5">{article.title}</h4>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-nordic-accent text-xs">{article.readTime}</span>
            <span className="w-1 h-1 rounded-full bg-nordic-accent/40" />
            <span className="text-nordic-accent text-xs">{article.author}</span>
          </div>
        </div>
        <button
          onClick={(e) => { e.stopPropagation(); toggleSave(article.id); }}
          className={`flex-none self-start p-1 rounded-full transition-colors ${saved ? 'text-primary' : 'text-nordic-accent hover:text-primary'}`}
        >
          <span className="material-symbols-outlined text-lg">{saved ? 'bookmark' : 'bookmark_border'}</span>
        </button>
      </div>
    );
  }

  return (
    <div className="group cursor-pointer" onClick={() => navigate(`/article/${article.id}`)}>
      <div className="relative aspect-[3/4] rounded-xl overflow-hidden mb-4 shadow-xl shadow-nordic-accent/10 transition-transform duration-500 group-hover:scale-[1.02]">
        <img src={article.img} alt={article.title} className="object-cover w-full h-full transition-transform duration-700 group-hover:scale-110" />
        <div className="absolute top-4 left-4 bg-white/90 dark:bg-background-dark/90 backdrop-blur-sm px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider text-nordic-text dark:text-slate-100">
          {article.category}
        </div>
        <button
          onClick={(e) => { e.stopPropagation(); toggleSave(article.id); }}
          className={`absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full backdrop-blur-sm transition-all
            ${saved ? 'bg-primary text-white' : 'bg-white/90 dark:bg-background-dark/90 text-nordic-text dark:text-slate-100 hover:bg-primary hover:text-white'}`}
        >
          <span className="material-symbols-outlined text-base">{saved ? 'bookmark' : 'bookmark_border'}</span>
        </button>
        <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      </div>
      <h4 className="text-lg font-bold text-nordic-text dark:text-slate-100 group-hover:text-primary transition-colors">{article.title}</h4>
      <div className="flex items-center gap-2 mt-1">
        <span className="text-nordic-accent text-xs font-medium">{article.readTime}</span>
        <span className="w-1 h-1 rounded-full bg-nordic-accent/30" />
        <span className="text-nordic-accent text-xs font-medium">{article.author}</span>
      </div>
    </div>
  );
}

export default JournalCard;
