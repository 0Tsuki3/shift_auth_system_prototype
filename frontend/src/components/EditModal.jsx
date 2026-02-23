import { useState, useEffect } from 'react'
import './EditModal.css'

export function EditModal({ request, onClose, onSave, onDelete }) {
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')
  const [note, setNote] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    if (request) {
      setStart(request.start || '')
      setEnd(request.end || '')
      setNote(request.note || '')
    }
  }, [request])

  const handleSave = async () => {
    setIsSaving(true)
    try {
      await onSave({
        start,
        end,
        note
      })
      onClose()
    } catch (error) {
      console.error('保存エラー:', error)
      alert('保存に失敗しました')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('このシフト希望を削除してもよろしいですか？')) {
      return
    }

    setIsDeleting(true)
    try {
      await onDelete()
      onClose()
    } catch (error) {
      console.error('削除エラー:', error)
      alert('削除に失敗しました')
    } finally {
      setIsDeleting(false)
    }
  }

  if (!request) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>シフト希望を編集</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <div className="modal-info">
            <div className="info-row">
              <span className="info-label">スタッフ:</span>
              <span className="info-value">{request.staff_name}</span>
            </div>
            <div className="info-row">
              <span className="info-label">日付:</span>
              <span className="info-value">{request.date}</span>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="start-time">開始時刻</label>
            <input
              id="start-time"
              type="time"
              value={start}
              onChange={(e) => setStart(e.target.value)}
              className="time-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="end-time">終了時刻</label>
            <input
              id="end-time"
              type="time"
              value={end}
              onChange={(e) => setEnd(e.target.value)}
              className="time-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="note">備考</label>
            <textarea
              id="note"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="備考を入力..."
              className="note-textarea"
              rows="3"
            />
          </div>
        </div>

        <div className="modal-footer">
          <button
            className="btn-delete"
            onClick={handleDelete}
            disabled={isDeleting || isSaving}
          >
            {isDeleting ? '削除中...' : '削除'}
          </button>
          <div className="modal-actions">
            <button
              className="btn-cancel"
              onClick={onClose}
              disabled={isSaving || isDeleting}
            >
              キャンセル
            </button>
            <button
              className="btn-save"
              onClick={handleSave}
              disabled={isSaving || isDeleting}
            >
              {isSaving ? '保存中...' : '保存'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
