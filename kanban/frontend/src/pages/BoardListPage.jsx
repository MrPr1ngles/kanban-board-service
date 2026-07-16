import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function BoardListPage() {
  const { login, logout } = useAuth()
  const navigate = useNavigate()
  const [boards, setBoards] = useState([])
  const [title, setTitle] = useState('')
  const [error, setError] = useState('')

  async function load() {
    try { setBoards(await api('/boards')) } catch (e) { setError(e.message) }
  }
  useEffect(() => { load() }, [])

  async function createBoard(e) {
    e.preventDefault()
    if (!title.trim()) return
    const board = await api('/boards', { method: 'POST', body: { title: title.trim() } })
    setTitle('')
    navigate(`/boards/${board.id}`)
  }

  return (
    <>
      <div className="topbar">
        <a href="/">Kanban</a>
        <div className="spacer" />
        <span className="muted">{login}</span>
        <button className="ghost" onClick={logout}>Выйти</button>
      </div>
      <div className="board-list">
        <form className="row" style={{ marginBottom: 16 }} onSubmit={createBoard}>
          <input placeholder="Название новой доски" value={title} onChange={e => setTitle(e.target.value)} />
          <button className="primary" style={{ flex: 'none' }} type="submit">Создать доску</button>
        </form>
        {error && <div className="error">{error}</div>}
        {boards.map(b => (
          <div key={b.id} className="board-list-item" onClick={() => navigate(`/boards/${b.id}`)}>
            <strong>{b.title}</strong>
            <span className="badge">{b.role}</span>
            <div className="spacer" style={{ flex: 1 }} />
            <span className="muted">{b.cards_total} карточек</span>
          </div>
        ))}
        {boards.length === 0 && !error && <div className="muted">Досок пока нет — создайте первую.</div>}
      </div>
    </>
  )
}
