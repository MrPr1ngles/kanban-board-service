import { useDroppable } from '@dnd-kit/core'
import { useState } from 'react'
import Card from './Card'

export default function Column({ column, canEdit, onOpenCard, onAddCard, onRenameColumn, onDeleteColumn }) {
  const { setNodeRef, isOver } = useDroppable({ id: `col-${column.id}`, data: { column } })
  const [adding, setAdding] = useState(false)
  const [title, setTitle] = useState('')

  function submit(e) {
    e.preventDefault()
    if (title.trim()) onAddCard(column.id, title.trim())
    setTitle('')
    setAdding(false)
  }

  return (
    <div ref={setNodeRef} className={`column${isOver ? ' drop-over' : ''}`}>
      <div className="column-header">
        <span
          onDoubleClick={() => {
            if (!canEdit) return
            const t = prompt('Название колонки', column.title)
            if (t && t.trim()) onRenameColumn(column.id, t.trim())
          }}
        >
          {column.title}
        </span>
        <span className="count">{column.cards.length}</span>
        <div style={{ flex: 1 }} />
        {canEdit && (
          <button className="ghost" title="Удалить колонку" onClick={() => onDeleteColumn(column.id)}>×</button>
        )}
      </div>
      {column.cards.map(card => (
        <Card key={card.id} card={card} canEdit={canEdit} onOpen={onOpenCard} />
      ))}
      {canEdit && (adding ? (
        <form onSubmit={submit}>
          <input
            autoFocus
            placeholder="Заголовок карточки"
            value={title}
            onChange={e => setTitle(e.target.value)}
            onBlur={() => { setAdding(false); setTitle('') }}
          />
        </form>
      ) : (
        <button className="add-card" onClick={() => setAdding(true)}>+ Добавить карточку</button>
      ))}
    </div>
  )
}
