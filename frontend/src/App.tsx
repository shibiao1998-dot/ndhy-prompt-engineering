import { Routes, Route } from 'react-router-dom'
import AppLayout from './components/Layout'
import Workbench from './pages/Workbench'
import DimensionManager from './pages/DimensionManager'

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Workbench />} />
        <Route path="/dimensions" element={<DimensionManager />} />
      </Route>
    </Routes>
  )
}

export default App
