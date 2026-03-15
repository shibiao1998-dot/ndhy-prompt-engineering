import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { HomeOutlined, DatabaseOutlined } from '@ant-design/icons'
import styles from './Layout.module.css'

export default function AppLayout() {
  const location = useLocation()
  const navigate = useNavigate()

  const tabs = [
    { key: '/', label: '设计工作台', icon: <HomeOutlined /> },
    { key: '/dimensions', label: '维度管理', icon: <DatabaseOutlined /> },
  ]

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <h1 className={styles.title}>华渔提示词工程 · AI设计师</h1>
          <p className={styles.slogan}>信息对称 · 相信 AI —— 让每次设计对话都达到专业级别</p>
        </div>
      </header>
      <main className={styles.main}>
        <Outlet />
      </main>
      <nav className={styles.nav}>
        {tabs.map((tab) => (
          <button
            key={tab.key}
            className={`${styles.navBtn} ${location.pathname === tab.key ? styles.navBtnActive : ''}`}
            onClick={() => navigate(tab.key)}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>
    </div>
  )
}
