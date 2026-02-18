import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import HotTakeGenerator from './components/HotTakeGenerator'
import HistoryPage from './pages/HistoryPage'
import AgentsPage from './pages/AgentsPage'
import SourcesPage from './pages/SourcesPage'
import SettingsPage from './pages/SettingsPage'
import AboutPage from './pages/AboutPage'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/generate" replace />} />
          <Route path="generate" element={<HotTakeGenerator />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="agents" element={<AgentsPage />} />
          <Route path="sources" element={<SourcesPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="about" element={<AboutPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
