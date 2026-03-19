import { Routes, Route } from 'react-router-dom'
import AppLayout from './components/Layout'
import Home from './pages/Home'
import Chat from './pages/Chat'
import Dimensions from './pages/Dimensions'
import AIEmployeeDemo from './pages/AIEmployeeDemo'

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/chat/:id" element={<Chat />} />
        <Route path="/dimensions" element={<Dimensions />} />
        <Route path="/ai-employee-demo" element={<AIEmployeeDemo />} />
      </Route>
    </Routes>
  )
}

export default App
