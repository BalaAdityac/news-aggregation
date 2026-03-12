import { useApp } from '../context/AppContext';

function Toast() {
  const { toasts, removeToast } = useApp();

  const icons = { success: 'check_circle', error: 'error', info: 'info' };
  const colors = {
    success: 'bg-emerald-500 text-white',
    error: 'bg-red-500 text-white',
    info: 'bg-nordic-text dark:bg-slate-700 text-white',
  };

  return (
    <div className="fixed bottom-28 right-4 z-[200] flex flex-col gap-2 pointer-events-none">
      {toasts.map(toast => (
        <div
          key={toast.id}
          onClick={() => removeToast(toast.id)}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl shadow-2xl cursor-pointer pointer-events-auto
            animate-toast-in backdrop-blur-md ${colors[toast.type] || colors.info}`}
        >
          <span className="material-symbols-outlined text-base">{icons[toast.type] || 'info'}</span>
          <span className="text-sm font-semibold">{toast.message}</span>
        </div>
      ))}
    </div>
  );
}

export default Toast;
