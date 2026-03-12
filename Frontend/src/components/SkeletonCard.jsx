function SkeletonCard() {
  return (
    <div className="flex-none w-72 animate-pulse">
      <div className="aspect-[3/4] rounded-xl bg-nordic-accent/10 dark:bg-slate-700 mb-4" />
      <div className="h-4 bg-nordic-accent/10 dark:bg-slate-700 rounded-full mb-2 w-3/4" />
      <div className="h-3 bg-nordic-accent/10 dark:bg-slate-700 rounded-full w-1/2" />
    </div>
  );
}

export function SkeletonGrid() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
      {Array(6).fill(0).map((_, i) => (
        <div key={i} className="animate-pulse">
          <div className="aspect-[3/2] rounded-xl bg-nordic-accent/10 dark:bg-slate-700 mb-4" />
          <div className="h-4 bg-nordic-accent/10 dark:bg-slate-700 rounded-full mb-2 w-3/4" />
          <div className="h-3 bg-nordic-accent/10 dark:bg-slate-700 rounded-full w-1/2" />
        </div>
      ))}
    </div>
  );
}

export default SkeletonCard;
