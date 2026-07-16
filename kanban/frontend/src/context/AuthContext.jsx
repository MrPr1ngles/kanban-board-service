import { createContext, useContext, useEffect, useState } from 'react'
import { setUnauthorizedHandler } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [login, setLoginName] = useState(() => localStorage.getItem('login'))

  useEffect(() => {
    setUnauthorizedHandler(() => logout())
  }, [])

  function authorize(newToken, loginName) {
    localStorage.setItem('token', newToken)
    localStorage.setItem('login', loginName)
    setToken(newToken)
    setLoginName(loginName)
  }
  function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('login')
    setToken(null)
    setLoginName(null)
  }
  return (
    <AuthContext.Provider value={{ token, login, authorize, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
