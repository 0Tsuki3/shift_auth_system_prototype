import { useState, useEffect } from 'react'
import axios from 'axios'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, parseISO } from 'date-fns'
import { ja } from 'date-fns/locale'
import './SpreadsheetEditor.css'
import { EditModal } from './EditModal'

export function SpreadsheetEditor({ month }) {
  const [requests, setRequests] = useState([])
  const [staff, setStaff] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [editingCell, setEditingCell] = useState(null) // { account, date, request }
  const [clickTimer, setClickTimer] = useState(null)
  const [selectedCells, setSelectedCells] = useState(new Map()) // Map<cellKey, {account, date, request}>
  const [lastClickedCell, setLastClickedCell] = useState(null) // Shift+クリック用
  const [copiedData, setCopiedData] = useState(null)
  const [bulkActionLoading, setBulkActionLoading] = useState(false)

  useEffect(() => {
    fetchData()
  }, [month])

  // コンポーネントのクリーンアップ
  useEffect(() => {
    return () => {
      if (clickTimer) {
        clearTimeout(clickTimer)
      }
    }
  }, [clickTimer])

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const [reqRes, staffRes] = await Promise.all([
        axios.get(`/admin/api/shift-requests/${month}`),
        axios.get(`/admin/api/staff`)
      ])
      
      setRequests(reqRes.data)
      setStaff(staffRes.data)
    } catch (error) {
      console.error('データ取得エラー:', error)
      setError('データの取得に失敗しました。管理者としてログインしていることを確認してください。')
    } finally {
      setLoading(false)
    }
  }

  // セルキーを生成（account_date）
  const getCellKey = (account, date) => `${account}_${date}`

  // セルをクリック（シングルクリック：選択、ダブルクリック：編集）
  const handleCellClick = (account, date, request, event) => {
    const cellKey = getCellKey(account, date)
    
    // ダブルクリック検知
    if (clickTimer) {
      // 既にタイマーが動いている = ダブルクリック
      clearTimeout(clickTimer)
      setClickTimer(null)
      // ダブルクリック処理：編集モーダルを開く
      openEditModal(account, date, request)
    } else {
      // 新しいクリック：タイマーをセット
      const timer = setTimeout(() => {
        // タイムアウト後：シングルクリック処理（セル選択）
        handleCellSelect(account, date, request, event)
        setClickTimer(null)
      }, 250) // 250ms以内の2回目のクリックをダブルクリックと判定
      setClickTimer(timer)
    }
  }

  // セル選択（Ctrl/Shift対応）
  const handleCellSelect = (account, date, request, event) => {
    const cellKey = getCellKey(account, date)
    const cellData = { account, date, request }

    if (event && (event.ctrlKey || event.metaKey)) {
      // Ctrl+クリック：トグル
      setSelectedCells(prev => {
        const newMap = new Map(prev)
        if (newMap.has(cellKey)) {
          newMap.delete(cellKey)
        } else {
          newMap.set(cellKey, cellData)
        }
        return newMap
      })
      setLastClickedCell(cellData)
    } else if (event && event.shiftKey && lastClickedCell) {
      // Shift+クリック：範囲選択（同じスタッフの日付範囲）
      handleRangeSelect(lastClickedCell, cellData)
    } else {
      // 通常クリック：単一選択
      const newMap = new Map()
      newMap.set(cellKey, cellData)
      setSelectedCells(newMap)
      setLastClickedCell(cellData)
    }
  }

  // 範囲選択（Shift+クリック）
  const handleRangeSelect = (startCell, endCell) => {
    // 同じスタッフの場合のみ範囲選択
    if (startCell.account !== endCell.account) {
      return
    }

    const startDate = new Date(startCell.date)
    const endDate = new Date(endCell.date)
    const [minDate, maxDate] = startDate <= endDate ? [startDate, endDate] : [endDate, startDate]

    const newMap = new Map(selectedCells)
    
    // 日付範囲内のすべてのセルを選択
    const currentDate = new Date(minDate)
    while (currentDate <= maxDate) {
      const dateStr = format(currentDate, 'yyyy-MM-dd')
      const cellKey = getCellKey(startCell.account, dateStr)
      
      // requestsからリクエストを検索
      const req = requests.find(r => r.account === startCell.account && r.date === dateStr)
      
      newMap.set(cellKey, {
        account: startCell.account,
        date: dateStr,
        request: req || null
      })
      
      currentDate.setDate(currentDate.getDate() + 1)
    }

    setSelectedCells(newMap)
  }

  const openEditModal = (account, date, request) => {
    setEditingCell({ account, date, request })
  }

  const closeEditModal = () => {
    setEditingCell(null)
  }

  const handleSave = async (updatedData) => {
    try {
      if (editingCell.request) {
        // 既存のリクエストを更新
        await axios.patch(`/admin/api/shift-requests/${editingCell.request.id}`, {
          month: month,
          start: updatedData.start,
          end: updatedData.end,
          note: updatedData.note
        })
      } else {
        // 新規リクエストを作成（空セルの場合）
        await axios.post('/admin/api/shift-requests/create', {
          month: month,
          account: editingCell.account,
          date: editingCell.date,
          start: updatedData.start,
          end: updatedData.end,
          note: updatedData.note
        })
      }
      
      // データをリフレッシュ
      await fetchData()
      closeEditModal()
    } catch (error) {
      console.error('保存エラー:', error)
      throw error
    }
  }

  const handleDelete = async () => {
    if (!editingCell.request) {
      alert('削除するリクエストがありません')
      return
    }
    
    try {
      await axios.delete(`/admin/api/shift-requests/${editingCell.request.id}`, {
        data: { month: month }
      })
      
      // データをリフレッシュ
      await fetchData()
      closeEditModal()
    } catch (error) {
      console.error('削除エラー:', error)
      throw error
    }
  }

  // セルをコピー（右クリック）
  const handleCellCopy = (request, event) => {
    if (event) {
      event.preventDefault()
    }
    
    if (!request) {
      alert('コピーするデータがありません')
      return
    }
    
    setCopiedData({
      start: request.start,
      end: request.end,
      note: request.note || ''
    })
    
    // クリップボードにもコピー（テキスト形式）
    const copyText = `${request.start}-${request.end}${request.note ? ' (' + request.note + ')' : ''}`
    navigator.clipboard.writeText(copyText).catch(err => {
      console.error('クリップボードへのコピーに失敗:', err)
    })
    
    // ビジュアルフィードバック
    alert(`コピーしました: ${copyText}`)
  }

  // キーボードショートカット処理
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Ctrl+V または Cmd+V で貼り付け
      if ((event.ctrlKey || event.metaKey) && event.key === 'v') {
        if (copiedData && selectedCells.size > 0) {
          event.preventDefault()
          handleBulkPaste()
        }
      }
      
      // Ctrl+A または Cmd+A で全選択（リクエストがあるセルのみ）
      if ((event.ctrlKey || event.metaKey) && event.key === 'a') {
        event.preventDefault()
        handleSelectAll()
      }
      
      // Escape で選択解除
      if (event.key === 'Escape') {
        setSelectedCells(new Map())
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [copiedData, selectedCells, requests, staff])

  // 全選択（リクエストがあるセルのみ）
  const handleSelectAll = () => {
    const newMap = new Map()
    requests.forEach(req => {
      const cellKey = getCellKey(req.account, req.date)
      newMap.set(cellKey, {
        account: req.account,
        date: req.date,
        request: req
      })
    })
    setSelectedCells(newMap)
  }

  // 選択解除
  const handleDeselectAll = () => {
    setSelectedCells(new Map())
  }

  // 一括貼り付け（空セルへの貼り付けで新規作成も可能）
  const handleBulkPaste = async () => {
    if (!copiedData || selectedCells.size === 0) {
      alert('貼り付けるデータと貼り付け先を選択してください')
      return
    }

    if (!confirm(`選択した ${selectedCells.size} 件のセルに貼り付けますか？`)) {
      return
    }

    setBulkActionLoading(true)

    try {
      const promises = []
      
      selectedCells.forEach((cellData, cellKey) => {
        if (cellData.request) {
          // 既存のリクエストを更新
          promises.push(
            axios.patch(`/admin/api/shift-requests/${cellData.request.id}`, {
              month: month,
              start: copiedData.start,
              end: copiedData.end,
              note: copiedData.note
            })
          )
        } else {
          // 新規リクエストを作成
          promises.push(
            axios.post('/admin/api/shift-requests/create', {
              month: month,
              account: cellData.account,
              date: cellData.date,
              start: copiedData.start,
              end: copiedData.end,
              note: copiedData.note
            })
          )
        }
      })

      await Promise.all(promises)
      
      alert(`${selectedCells.size} 件のセルに貼り付けました`)
      
      // データをリフレッシュ
      await fetchData()
      
      // 選択を解除
      setSelectedCells(new Map())
    } catch (error) {
      console.error('一括貼り付けエラー:', error)
      alert('一括貼り付けに失敗しました')
    } finally {
      setBulkActionLoading(false)
    }
  }

  // 一括インポート（リクエストがあるセルのみ）
  const handleBulkImport = async () => {
    // リクエストがあるセルのみフィルター
    const requestIds = Array.from(selectedCells.values())
      .filter(cell => cell.request)
      .map(cell => cell.request.id)
    
    if (requestIds.length === 0) {
      alert('インポートするシフト希望を選択してください（空セルは対象外）')
      return
    }

    if (!confirm(`選択した ${requestIds.length} 件のシフト希望を確定シフトにインポートしますか？`)) {
      return
    }

    setBulkActionLoading(true)

    try {
      const response = await axios.post('/admin/api/shift-requests/bulk-import', {
        month: month,
        request_ids: requestIds
      })

      alert(response.data.message)
      
      // データをリフレッシュ
      await fetchData()
      
      // 選択を解除
      setSelectedCells(new Map())
    } catch (error) {
      console.error('一括インポートエラー:', error)
      alert('一括インポートに失敗しました')
    } finally {
      setBulkActionLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>読み込み中...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-container">
        <p className="error-message">⚠️ {error}</p>
        <button onClick={fetchData} className="retry-button">再試行</button>
      </div>
    )
  }

  // 日付リストを生成（月の1日〜末日）
  const monthDate = parseISO(month + '-01')
  const days = eachDayOfInterval({
    start: startOfMonth(monthDate),
    end: endOfMonth(monthDate)
  })

  // スタッフごとにリクエストをマッピング
  const requestsByStaff = {}
  staff.forEach(s => {
    requestsByStaff[s.account] = {}
  })

  requests.forEach(req => {
    if (requestsByStaff[req.account]) {
      requestsByStaff[req.account][req.date] = req
    }
  })

  // 統計情報
  const unreadCount = requests.filter(r => !r.is_read).length
  const totalCount = requests.length

  return (
    <div className="spreadsheet-container">
      {/* ヘッダー情報 */}
      <div className="spreadsheet-info">
        <div className="info-item">
          <span className="info-label">合計希望数:</span>
          <span className="info-value">{totalCount}件</span>
        </div>
        <div className="info-item">
          <span className="info-label">未読:</span>
          <span className="info-value unread">{unreadCount}件</span>
        </div>
        <div className="info-item">
          <span className="info-label">既読:</span>
          <span className="info-value read">{totalCount - unreadCount}件</span>
        </div>
        <div className="info-item">
          <span className="info-label">選択中:</span>
          <span className="info-value selected">{selectedCells.size}件</span>
        </div>
      </div>

      {/* 一括操作ツールバー */}
      {selectedCells.size > 0 && (
        <div className="bulk-action-toolbar">
          <div className="toolbar-left">
            <button 
              onClick={handleDeselectAll}
              className="btn-deselect"
              disabled={bulkActionLoading}
            >
              選択解除
            </button>
            <button 
              onClick={handleSelectAll}
              className="btn-select-all"
              disabled={bulkActionLoading}
            >
              全選択
            </button>
          </div>
          <div className="toolbar-right">
            {copiedData && (
              <button 
                onClick={handleBulkPaste}
                className="btn-paste"
                disabled={bulkActionLoading}
                title="Ctrl+V でも貼り付け可能 | 空セルにも貼り付け可能"
              >
                📋 貼り付け ({copiedData.start}-{copiedData.end})
              </button>
            )}
            <button 
              onClick={handleBulkImport}
              className="btn-bulk-import"
              disabled={bulkActionLoading}
            >
              ✅ シフトにインポート
            </button>
          </div>
        </div>
      )}

      {/* スプレッドシートテーブル */}
      <div className="spreadsheet-wrapper">
        <table className="spreadsheet-table">
          <thead>
            <tr>
              <th className="staff-header">スタッフ</th>
              {days.map(day => (
                <th key={day.toISOString()} className="date-header">
                  <div className="date-cell">
                    <div className="date-day">{format(day, 'd')}</div>
                    <div className="date-weekday">{format(day, 'E', { locale: ja })}</div>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {staff.length === 0 ? (
              <tr>
                <td colSpan={days.length + 1} style={{ textAlign: 'center', padding: '2rem', color: '#999' }}>
                  スタッフが登録されていません
                </td>
              </tr>
            ) : (
              staff.map(s => {
                return (
                  <tr key={s.account} className="staff-row">
                    <td className="staff-cell">
                      <div className="staff-name">{s.name}</div>
                      <div className="staff-position">{s.position}</div>
                    </td>
                    {days.map(day => {
                      const dayStr = format(day, 'yyyy-MM-dd')
                      const req = requestsByStaff[s.account][dayStr]
                      const cellKey = getCellKey(s.account, dayStr)
                      const isSelected = selectedCells.has(cellKey)
                      
                      return (
                        <td
                          key={dayStr}
                          className={`shift-cell ${req ? (req.is_read ? 'has-request read' : 'has-request unread') : 'empty'} ${isSelected ? 'selected' : ''}`}
                          onClick={(e) => handleCellClick(s.account, dayStr, req, e)}
                          onContextMenu={(e) => {
                            if (req) {
                              handleCellCopy(req, e)
                            } else {
                              e.preventDefault()
                            }
                          }}
                          title={req ? `クリック：選択 | ダブルクリック：編集 | 右クリック：コピー` : `クリック：選択 | ダブルクリック：新規作成`}
                        >
                          {req ? (
                            <div className="shift-content">
                              <div className="shift-time">
                                {req.start} - {req.end}
                              </div>
                              <div className="shift-meta">
                                <span className="shift-hours">
                                  {req.duration_hours}h
                                </span>
                                {req.note && (
                                  <span className="shift-note" title={req.note}>
                                    💬
                                  </span>
                                )}
                              </div>
                              <div className="shift-status">
                                {req.is_read ? '✓' : '●'}
                              </div>
                            </div>
                          ) : (
                            <div className="shift-empty">─</div>
                          )}
                        </td>
                      )
                    })}
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {/* 凡例 */}
      <div className="spreadsheet-legend">
        <div className="legend-title">操作方法:</div>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-box unread"></span>
            <span className="legend-text">未読シフト希望</span>
          </div>
          <div className="legend-item">
            <span className="legend-box read"></span>
            <span className="legend-text">既読シフト希望</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">💬</span>
            <span className="legend-text">備考あり（マウスオーバーで表示）</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">🖱️</span>
            <span className="legend-text">クリック：選択 | Ctrl+クリック：複数選択 | Shift+クリック：範囲選択</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">✏️</span>
            <span className="legend-text">ダブルクリック：編集/新規作成</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">📋</span>
            <span className="legend-text">右クリック：コピー | Ctrl+V：貼り付け（空セル可）</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">⌨️</span>
            <span className="legend-text">Ctrl+A：全選択 | Escape：選択解除</span>
          </div>
        </div>
      </div>

      {/* 編集モーダル */}
      {editingCell && (
        <EditModal
          request={editingCell.request}
          onClose={closeEditModal}
          onSave={handleSave}
          onDelete={handleDelete}
        />
      )}

      {/* データがない場合 */}
      {totalCount === 0 && (
        <div className="no-data-message">
          <p>📭 この月のシフト希望はまだ提出されていません</p>
        </div>
      )}
    </div>
  )
}
