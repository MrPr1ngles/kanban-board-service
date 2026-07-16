import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import BoardListPage from './pages/BoardListPage'
import BoardPage from './pages/BoardPage'
import LoginPage from './pages/LoginPage'

export default function App() {
  const { token } = useAuth()
  if (!token) return <LoginPage />
  return (
    <Routes>
      <Route path="/" element={<BoardListPage />} />
      <Route path="/boards/:id" element={<BoardPage />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}
