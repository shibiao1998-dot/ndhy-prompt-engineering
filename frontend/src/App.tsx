import { Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/Layout'
import Chat from './pages/Chat'
import Dimensions from './pages/Dimensions'

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Navigate to="/dimensions" replace />} />
        <Route path="/chat/:id" element={<Chat />} />
        <Route path="/dimensions" element={<Dimensions />} />
      </Route>
    </Routes>
  )
}

export default App
