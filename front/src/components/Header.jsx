import { useState, useEffect } from 'react';
import styles from './Header.module.scss';

function Header() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // 🎯 Эффект при скролле
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // 🌙 Переключение темы
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  return (
    <header className={`${styles.header} ${isScrolled ? styles.scrolled : ''}`}>
      {/* 🎬 Logo */}
      <div className={styles.logo_section}>
        <div className={styles.logo_mark} aria-label="MAVIS Logo" />
        <div className={styles.logo_text}>
          <h1>MAVIS</h1>
          <span className={styles.tagline}>Video Analysis Platform</span>
        </div>
      </div>

      

      {/* 👤 User Section */}
      <div className={styles.user_section}>
        {/* 🌙 Theme Toggle */}
        <button 
          className={styles.theme_toggle}
          onClick={() => setIsDarkMode(!isDarkMode)}
          aria-label={isDarkMode ? 'Светлая тема' : 'Тёмная тема'}
          title={isDarkMode ? '☀️ Светлая тема' : '🌙 Тёмная тема'}
        >
          {isDarkMode ? '☀️' : '🌙'}
        </button>

        {/* 👤 Avatar + Menu */}
        <button className={styles.user_menu_btn} aria-label="Меню профиля">
          <div className={styles.user_avatar}>U</div>
          <span className={styles.chevron}>▾</span>
        </button>

        {/* 📱 Mobile Menu Toggle */}
        <button 
          className={`${styles.mobile_menu_btn} ${mobileMenuOpen ? styles.active : ''}`}
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Меню"
          aria-expanded={mobileMenuOpen}
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
    </header>
  );
}

export default Header;