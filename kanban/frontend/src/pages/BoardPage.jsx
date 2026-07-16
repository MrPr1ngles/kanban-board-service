import { DndContext, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/client'
import CardModal from '../components/CardModal'
import Column from '../components/Column'
import MembersDialog from '../components/MembersDialog'
import { useAuth } from '../context/AuthContext'

const STEP = 1024

export default function BoardPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { login, logout } = useAuth()
  const [board, setBoard] = useState(null)
  const [openCard, setOpenCard] = useState(null)
  const [showMembers, setShowMembers] = useState(false)
  const [notice, setNotice] = useState('')
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 6 } }))

  const load = useCallback(async () => {
    try {
      setBoard(await api(`/boards/${id}`))
    } catch (e) {
      if (e.status === 404) navigate('/')
    }
  }, [id, navigate])

  useEffect(() => { load() }, [load])

  const canEdit = board && (board.my_role === 'writer' || board.my_role === 'owner')

  // fractional indexing: позиция при вставке в конец колонки
  function endPosition(column) {
    const last = column.cards[column.cards.length - 1]
    return last ? Number(last.position) + STEP : STEP
  }

  async function handleDragEnd({ active, over }) {
    if (!over || !board) return
    const card = active.data.current.card
    let targetColumn, position

    if (String(over.id).startsWith('col-')) {
      targetColumn = over.data.current.column
      if (targetColumn.id === card.column_id) return
      position = endPosition(targetColumn)
    } else {
      // бросили на карточку -> вставка перед ней
      const overCard = over.data.current.card
      if (overCard.id === card.id) return
      targetColumn = board.columns.find(c => c.id === overCard.column_id)
      const cards = targetColumn.cards.filter(c => c.id !== card.id)
      const idx = cards.findIndex(c => c.id === overCard.id)
      const before = idx > 0 ? Number(cards[idx - 1].position) : null
      const after = Number(overCard.position)
      position = before !== null ? (before + after) / 2 : after / 2
    }

    // оптимистичное обновление UI, при 409 — перечитываем доску
    setBoard(prev => {
      const columns = prev.columns.map(col => ({
        ...col,
        cards: col.cards.filter(c => c.id !== card.id),
      }))
      const target = columns.find(c => c.id === targetColumn.id)
      target.cards = [...target.cards, { ...card, column_id: target.id, position }]
        .sort((a, b) => Number(a.position) - Number(b.position))
      return { ...prev, columns }
    })
    try {
      await api(`/cards/${card.id}/move`, {
        method: 'POST',
        body: { target_column_id: targetColumn.id, position, version: card.version },
      })
      load()
    } catch (e) {
      if (e.status === 409) setNotice('Доску изменил другой пользователь — данные обновлены.')
      load()
      setTimeout(() => setNotice(''), 3000)
    }
  }

  async function addCard(columnId, title) {
    await api(`/boards/${board.id}/cards`, { method: 'POST', body: { column_id: columnId, title } })
    load()
  }
  async function addColumn() {
    const title = prompt('Название колонки')
    if (!title || !title.trim()) return
    await api(`/boards/${board.id}/columns`, { method: 'POST', body: { title: title.trim() } })
    load()
  }
  async function renameColumn(columnId, title) {
    await api(`/columns/${columnId}`, { method: 'PATCH', body: { title } })
    load()
  }
  async function deleteColumn(columnId) {
    if (!confirm('Удалить колонку вместе с карточками?')) return
    await api(`/columns/${columnId}`, { method: 'DELETE' })
    load()
  }
  async function renameBoard() {
    const title = prompt('Название доски', board.title)
    if (!title || !title.trim()) return
    try {
      await api(`/boards/${board.id}`, { method: 'PATCH', body: { title: title.trim(), version: board.version } })
      load()
    } catch (e) {
      if (e.status === 409) { setNotice('Доску переименовал другой пользователь.'); load() }
    }
  }
  async function deleteBoard() {
    if (!confirm('Удалить доску безвозвратно?')) return
    await api(`/boards/${board.id}`, { method: 'DELETE' })
    navigate('/')
  }

  if (!board) return null

  return (
    <>
      <div className="topbar">
        <Link to="/">← Доски</Link>
        <strong onDoubleClick={canEdit ? renameBoard : undefined}>{board.title}</strong>
        <span className="badge">{board.my_role}</span>
        {notice && <span className="muted">{notice}</span>}
        <div className="spacer" />
        <button onClick={() => setShowMembers(true)}>Участники</button>
        {canEdit && <button onClick={addColumn}>+ Колонка</button>}
        {board.my_role === 'owner' && <button className="danger" onClick={deleteBoard}>Удалить доску</button>}
        <span className="muted">{login}</span>
        <button className="ghost" onClick={logout}>Выйти</button>
      </div>
      <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
        <div className="board">
          {board.columns.map(col => (
            <Column
              key={col.id}
              column={col}
              canEdit={canEdit}
              onOpenCard={setOpenCard}
              onAddCard={addCard}
              onRenameColumn={renameColumn}
              onDeleteColumn={deleteColumn}
            />
          ))}
        </div>
      </DndContext>
      {openCard && (
        <CardModal
          card={openCard}
          members={board.members}
          canEdit={canEdit}
          onClose={() => setOpenCard(null)}
          onChanged={load}
        />
      )}
      {showMembers && (
        <MembersDialog board={board} onClose={() => setShowMembers(false)} onChanged={load} />
      )}
    </>
  )
}
