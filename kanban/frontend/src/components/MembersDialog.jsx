import { useState } from 'react'
import { api } from '../api/client'

export default function MembersDialog({ board, onClose, onChanged }) {
  const [login, setLogin] = useState('')
  const [role, setRole] = useState('writer')
  const [error, setError] = useState('')
  const isOwner = board.my_role === 'owner'

  async function addMember(e) {
    e.preventDefault()
    setError('')
    try {
      await api(`/boards/${board.id}/members`, { method: 'POST', body: { login: login.trim(), role } })
      setLogin('')
      onChanged()
    } catch (err) { setError(err.message) }
  }

  async function changeRole(userId, newRole) {
    try {
      await api(`/boards/${board.id}/members/${userId}`, { method: 'PATCH', body: { role: newRole } })
      onChanged()
    } catch (err) { setError(err.message) }
  }

  async function remove(userId) {
    try {
      await api(`/boards/${board.id}/members/${userId}`, { method: 'DELETE' })
      onChanged()
    } catch (err) { setError(err.message) }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h2>Участники доски</h2>
        {board.members.map(m => (
          <div className="member-row" key={m.user.id}>
            <span className="avatar">{m.user.login[0]}</span>
            <span style={{ flex: 1 }}>{m.user.login}{m.user.id === board.owner_id && <span className="muted"> · владелец</span>}</span>
            {isOwner && m.user.id !== board.owner_id ? (
              <>
                <select value={m.role} onChange={e => changeRole(m.user.id, e.target.value)}>
                  <option value="reader">reader</option>
                  <option value="writer">writer</option>
                  <option value="owner">owner</option>
                </select>
                <button className="ghost danger" onClick={() => remove(m.user.id)}>×</button>
              </>
            ) : (
              <span className="badge">{m.role}</span>
            )}
          </div>
        ))}
        {isOwner && (
          <form className="row" onSubmit={addMember}>
            <input placeholder="Логин пользователя" value={login} onChange={e => setLogin(e.target.value)} />
            <select style={{ width: 110, flex: 'none' }} value={role} onChange={e => setRole(e.target.value)}>
              <option value="reader">reader</option>
              <option value="writer">writer</option>
            </select>
            <button style={{ flex: 'none' }} type="submit">Добавить</button>
          </form>
        )}
        {error && <div className="error">{error}</div>}
      </div>
    </div>
  )
}
