import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import styles from './Layout.module.css'

export default function AppLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const isChat = location.pathname.startsWith('/chat/')
  const isDimensions = location.pathname === '/dimensions'

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <div className={styles.brand} onClick={() => navigate('/')} role="button" tabIndex={0}>
            <div className={styles.logo}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
            </div>
            <div>
              <h1 className={styles.title}>提示词工程 · AI设计师</h1>
              {!isChat && !isDimensions && <p className={styles.slogan}>信息对称 · 相信 AI —— 让每次设计对话都达到专业级别</p>}
            </div>
          </div>
          <nav className={styles.nav}>
            <button
              className={`${styles.navBtn} ${isDimensions ? styles.navBtnActive : ''}`}
              onClick={() => navigate('/dimensions')}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
                <rect x="3" y="14" width="7" height="7" /><rect x="14" y="14" width="7" height="7" />
              </svg>
              维度管理
            </button>
          </nav>
        </div>
      </header>
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  )
}
