import { useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const { authorize } = useAuth()
  const [mode, setMode] = useState('login')
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function submit(e) {
    e.preventDefault()
    setError('')
    try {
      if (mode === 'register') {
        await api('/auth/register', { method: 'POST', body: { login, password } })
      }
      const data = await api('/auth/login', { method: 'POST', body: { login, password } })
      authorize(data.auth_token, login)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form className="auth-page" onSubmit={submit}>
      <h1>{mode === 'login' ? 'Вход' : 'Регистрация'}</h1>
      <input placeholder="Логин" value={login} onChange={e => setLogin(e.target.value)} required minLength={3} />
      <input placeholder="Пароль" type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={6} />
      {error && <div className="error">{error}</div>}
      <button className="primary" type="submit">{mode === 'login' ? 'Войти' : 'Создать аккаунт'}</button>
      <button type="button" className="ghost" onClick={() => setMode(m => (m === 'login' ? 'register' : 'login'))}>
        {mode === 'login' ? 'Нет аккаунта? Регистрация' : 'Уже есть аккаунт? Вход'}
      </button>
    </form>
  )
}
