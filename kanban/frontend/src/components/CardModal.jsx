import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function CardModal({ card, members, canEdit, onClose, onChanged }) {
  const [title, setTitle] = useState(card.title)
  const [description, setDescription] = useState(card.description || '')
  const [assigneeId, setAssigneeId] = useState(card.assignee?.id || '')
  const [deadline, setDeadline] = useState(card.deadline ? card.deadline.slice(0, 16) : '')
  const [comments, setComments] = useState([])
  const [newComment, setNewComment] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api(`/cards/${card.id}/comments`).then(setComments).catch(() => {})
  }, [card.id])

  async function save() {
    setError('')
    const body = { version: card.version }
    if (title !== card.title) body.title = title
    if (description !== (card.description || '')) body.description = description
    if (String(assigneeId) !== String(card.assignee?.id || '')) {
      if (assigneeId) body.assignee_id = Number(assigneeId)
      else body.clear_assignee = true
    }
    const oldDeadline = card.deadline ? card.deadline.slice(0, 16) : ''
    if (deadline !== oldDeadline) {
      if (deadline) body.deadline = new Date(deadline).toISOString()
      else body.clear_deadline = true
    }
    try {
      await api(`/cards/${card.id}`, { method: 'PATCH', body })
      onChanged()
      onClose()
    } catch (e) {
      setError(e.status === 409 ? 'Карточку изменил другой пользователь — доска будет обновлена.' : e.message)
      if (e.status === 409) { onChanged(); setTimeout(onClose, 1200) }
    }
  }

  async function removeCard() {
    if (!confirm('Удалить карточку?')) return
    await api(`/cards/${card.id}`, { method: 'DELETE' })
    onChanged()
    onClose()
  }

  async function addComment(e) {
    e.preventDefault()
    if (!newComment.trim()) return
    const c = await api(`/cards/${card.id}/comments`, { method: 'POST', body: { body: newComment.trim() } })
    setComments(prev => [...prev, c])
    setNewComment('')
    onChanged()
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h2>Карточка #{card.id}</h2>
        <input value={title} onChange={e => setTitle(e.target.value)} disabled={!canEdit} />
        <textarea
          rows={4} placeholder="Описание"
          value={description} onChange={e => setDescription(e.target.value)} disabled={!canEdit}
        />
        <div className="row">
          <label>
            <span className="muted">Исполнитель</span>
            <select value={assigneeId} onChange={e => setAssigneeId(e.target.value)} disabled={!canEdit}>
              <option value="">— не назначен —</option>
              {members.map(m => (
                <option key={m.user.id} value={m.user.id}>{m.user.login}</option>
              ))}
            </select>
          </label>
          <label>
            <span className="muted">Дедлайн</span>
            <input type="datetime-local" value={deadline} onChange={e => setDeadline(e.target.value)} disabled={!canEdit} />
          </label>
        </div>
        {error && <div className="error">{error}</div>}
        {canEdit && (
          <div className="row">
            <button className="primary" onClick={save}>Сохранить</button>
            <button className="danger" onClick={removeCard}>Удалить карточку</button>
          </div>
        )}
        <div>
          <div className="muted" style={{ marginBottom: 4 }}>Комментарии</div>
          {comments.map(c => (
            <div className="comment" key={c.id}>
              <div className="head">
                <strong>{c.author.login}</strong>
                <span className="muted">{new Date(c.created_at).toLocaleString('ru-RU')}</span>
              </div>
              <div>{c.body}</div>
            </div>
          ))}
          {comments.length === 0 && <div className="muted">Пока нет комментариев.</div>}
          {canEdit && (
            <form className="row" style={{ marginTop: 8 }} onSubmit={addComment}>
              <input placeholder="Написать комментарий" value={newComment} onChange={e => setNewComment(e.target.value)} />
              <button style={{ flex: 'none' }} type="submit">Отправить</button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
