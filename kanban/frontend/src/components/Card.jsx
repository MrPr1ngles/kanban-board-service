import { useDraggable } from '@dnd-kit/core'

function formatDeadline(iso) {
  const d = new Date(iso)
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

export default function Card({ card, canEdit, onOpen }) {
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({
    id: `card-${card.id}`,
    data: { card },
    disabled: !canEdit,
  })
  const overdue = card.deadline && new Date(card.deadline) < new Date()
  return (
    <div
      ref={setNodeRef}
      className={`card${isDragging ? ' dragging' : ''}`}
      onClick={() => onOpen(card)}
      {...listeners}
      {...attributes}
    >
      <div>{card.title}</div>
      {(card.assignee || card.deadline || card.comments_count > 0) && (
        <div className="card-meta">
          {card.assignee && <span className="avatar" title={card.assignee.login}>{card.assignee.login[0]}</span>}
          {card.deadline && (
            <span className={`deadline${overdue ? ' overdue' : ''}`}>{formatDeadline(card.deadline)}</span>
          )}
          {card.comments_count > 0 && <span className="muted">💬 {card.comments_count}</span>}
        </div>
      )}
    </div>
  )
}
