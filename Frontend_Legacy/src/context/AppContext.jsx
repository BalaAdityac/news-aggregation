import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { supabase } from '../lib/supabase';

const AppContext = createContext();

export function AppProvider({ children }) {
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true';
  });
  const [savedArticles, setSavedArticles] = useState([]);
  const [toasts, setToasts] = useState([]);
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true); // true until Supabase resolves

  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3000);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  useEffect(() => {
    // Initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user || null);
      setAuthLoading(false); // Auth resolved
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user || null);
      setAuthLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const login = useCallback(async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    addToast('Welcome back!', 'success');
  }, [addToast]);

  const signUp = useCallback(async (email, password) => {
    const { data, error } = await supabase.auth.signUp({ email, password });
    if (error) throw error;
    if (data.session) {
      addToast('Welcome! Your account is ready.', 'success');
    } else {
      addToast('Account created! Check your email to confirm.', 'info');
    }
    return data.session; // null if email confirmation required, session if auto-confirmed
  }, [addToast]);

  const logout = useCallback(async () => {
    await supabase.auth.signOut();
    addToast('Logged out successfully', 'info');
  }, [addToast]);

  useEffect(() => {
    localStorage.setItem('darkMode', darkMode);
    if (darkMode) document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
  }, [darkMode]);

  const toggleSave = useCallback((articleId) => {
    setSavedArticles(prev => {
      if (prev.includes(articleId)) {
        addToast('Removed from saved', 'info');
        return prev.filter(id => id !== articleId);
      } else {
        addToast('Article saved!', 'success');
        return [...prev, articleId];
      }
    });
  }, [addToast]);

  const isSaved = useCallback((articleId) => savedArticles.includes(articleId), [savedArticles]);

  return (
    <AppContext.Provider value={{ darkMode, setDarkMode, savedArticles, toggleSave, isSaved, toasts, addToast, removeToast, user, authLoading, login, signUp, logout }}>
      {children}
    </AppContext.Provider>
  );
}

export const useApp = () => useContext(AppContext);
