import { useState, useEffect } from 'react';

const useDarkMode = (): [boolean, (enabled: boolean) => void] => {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    if (saved !== null) return saved === 'true';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle('dark-mode', darkMode);
    localStorage.setItem('darkMode', darkMode.toString());
  }, [darkMode]);

  // Sync across components when localStorage changes (e.g. other tab or component)
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === 'darkMode' && e.newValue !== null) {
        setDarkMode(e.newValue === 'true');
      }
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  return [darkMode, setDarkMode];
};

export default useDarkMode;
