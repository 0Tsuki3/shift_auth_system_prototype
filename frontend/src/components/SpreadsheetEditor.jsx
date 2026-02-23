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
  const [editingRequest, setEditingRequest] = useState(null)
  const [clickTimer, setClickTimer] = useState(null)
  const [selectedRequestIds, setSelectedRequestIds] = useState(new Set())
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

  const toggleRead = async (requestId) => {
    try {
      const response = await axios.patch(`/admin/api/shift-requests/${requestId}/read`, {
        month: month
      })
      
      // フルリロードせず、ローカルステートのみ更新（スクロール位置を保持）
      setRequests(prevRequests => 
        prevRequests.map(req => 
          req.id === requestId 
            ? { ...req, is_read: response.data.is_read, read_status: response.data.read_status }
            : req
        )
      )
    } catch (error) {
      console.error('更新エラー:', error)
      alert('更新に失敗しました')
    }
  }

  const handleCellClick = (request) => {
    // ダブルクリック検知のため、シングルクリックを遅延実行
    if (clickTimer) {
      // 既にタイマーが動いている = ダブルクリック
      clearTimeout(clickTimer)
      setClickTimer(null)
      // ダブルクリック処理：編集モーダルを開く
      openEditModal(request)
    } else {
      // 新しいクリック：タイマーをセット
      const timer = setTimeout(() => {
        // タイムアウト後：シングルクリック処理
        toggleRead(request.id)
        setClickTimer(null)
      }, 250) // 250ms以内の2回目のクリックをダブルクリックと判定
      setClickTimer(timer)
    }
  }

  const openEditModal = (request) => {
    setEditingRequest(request)
  }

  const closeEditModal = () => {
    setEditingRequest(null)
  }

  const handleSave = async (updatedData) => {
    try {
      await axios.patch(`/admin/api/shift-requests/${editingRequest.id}`, {
        month: month,
        start: updatedData.start,
        end: updatedData.end,
        note: updatedData.note
      })
      
      // データをリフレッシュ
      await fetchData()
    } catch (error) {
      console.error('保存エラー:', error)
      throw error
    }
  }

  const handleDelete = async () => {
    try {
      await axios.delete(`/admin/api/shift-requests/${editingRequest.id}`, {
        data: { month: month }
      })
      
      // データをリフレッシュ
      await fetchData()
    } catch (error) {
      console.error('削除エラー:', error)
      throw error
    }
  }

  // セルをコピー（右クリックまたはCtrl+C）
  const handleCellCopy = (request, event) => {
    if (event) {
      event.preventDefault()
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
        if (copiedData && selectedRequestIds.size > 0) {
          event.preventDefault()
          handleBulkPaste()
        }
      }
      
      // Ctrl+A または Cmd+A で全選択
      if ((event.ctrlKey || event.metaKey) && event.key === 'a') {
        event.preventDefault()
        handleSelectAll()
      }
      
      // Escape で選択解除
      if (event.key === 'Escape') {
        setSelectedRequestIds(new Set())
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [copiedData, selectedRequestIds, requests])

  // 全選択
  const handleSelectAll = () => {
    const allIds = new Set(requests.map(r => r.id))
    setSelectedRequestIds(allIds)
  }

  // 選択解除
  const handleDeselectAll = () => {
    setSelectedRequestIds(new Set())
  }

  // チェックボックスのトグル
  const handleToggleSelect = (requestId) => {
    setSelectedRequestIds(prev => {
      const newSet = new Set(prev)
      if (newSet.has(requestId)) {
        newSet.delete(requestId)
      } else {
        newSet.add(requestId)
      }
      return newSet
    })
  }

  // 一括貼り付け
  const handleBulkPaste = async () => {
    if (!copiedData || selectedRequestIds.size === 0) {
      alert('貼り付けるデータと貼り付け先を選択してください')
      return
    }

    if (!confirm(`選択した ${selectedRequestIds.size} 件のシフト希望に貼り付けますか？`)) {
      return
    }

    setBulkActionLoading(true)

    try {
      // 選択された各リクエストを更新
      const promises = Array.from(selectedRequestIds).map(requestId =>
        axios.patch(`/admin/api/shift-requests/${requestId}`, {
          month: month,
          start: copiedData.start,
          end: copiedData.end,
          note: copiedData.note
        })
      )

      await Promise.all(promises)
      
      alert(`${selectedRequestIds.size} 件のシフト希望を更新しました`)
      
      // データをリフレッシュ
      await fetchData()
      
      // 選択を解除
      setSelectedRequestIds(new Set())
    } catch (error) {
      console.error('一括貼り付けエラー:', error)
      alert('一括貼り付けに失敗しました')
    } finally {
      setBulkActionLoading(false)
    }
  }

  // 一括インポート
  const handleBulkImport = async () => {
    if (selectedRequestIds.size === 0) {
      alert('インポートするシフト希望を選択してください')
      return
    }

    if (!confirm(`選択した ${selectedRequestIds.size} 件のシフト希望を確定シフトにインポートしますか？`)) {
      return
    }

    setBulkActionLoading(true)

    try {
      const response = await axios.post('/admin/api/shift-requests/bulk-import', {
        month: month,
        request_ids: Array.from(selectedRequestIds)
      })

      alert(response.data.message)
      
      // データをリフレッシュ
      await fetchData()
      
      // 選択を解除
      setSelectedRequestIds(new Set())
    } catch (error) {
      console.error('一括インポートエラー:', error)
      alert('一括インポートに失敗しました')
    } finally {
      setBulkActionLoading(false)
    }
  }

  // 一括既読/未読切り替え
  const handleBulkToggleRead = async (readStatus) => {
    if (selectedRequestIds.size === 0) {
      alert('操作するシフト希望を選択してください')
      return
    }

    const statusText = readStatus === 'read' ? '既読' : '未読'
    
    if (!confirm(`選択した ${selectedRequestIds.size} 件を${statusText}にしますか？`)) {
      return
    }

    setBulkActionLoading(true)

    try {
      const response = await axios.post('/admin/api/shift-requests/bulk-toggle-read', {
        month: month,
        request_ids: Array.from(selectedRequestIds),
        read_status: readStatus
      })

      alert(response.data.message)
      
      // データをリフレッシュ
      await fetchData()
      
      // 選択を解除
      setSelectedRequestIds(new Set())
    } catch (error) {
      console.error('一括既読/未読切り替えエラー:', error)
      alert('一括既読/未読切り替えに失敗しました')
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
          <span className="info-value selected">{selectedRequestIds.size}件</span>
        </div>
      </div>

      {/* 一括操作ツールバー */}
      {selectedRequestIds.size > 0 && (
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
                title="Ctrl+V でも貼り付け可能"
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
            <button 
              onClick={() => handleBulkToggleRead('read')}
              className="btn-mark-read"
              disabled={bulkActionLoading}
            >
              既読にする
            </button>
            <button 
              onClick={() => handleBulkToggleRead('unread')}
              className="btn-mark-unread"
              disabled={bulkActionLoading}
            >
              未読にする
            </button>
          </div>
        </div>
      )}

      {/* スプレッドシートテーブル */}
      <div className="spreadsheet-wrapper">
        <table className="spreadsheet-table">
          <thead>
            <tr>
              <th className="checkbox-header">
                <input
                  type="checkbox"
                  checked={selectedRequestIds.size > 0 && selectedRequestIds.size === requests.length}
                  onChange={(e) => e.target.checked ? handleSelectAll() : handleDeselectAll()}
                  title="全選択/解除"
                />
              </th>
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
                <td colSpan={days.length + 2} style={{ textAlign: 'center', padding: '2rem', color: '#999' }}>
                  スタッフが登録されていません
                </td>
              </tr>
            ) : (
              staff.map(s => {
                // このスタッフの全リクエストを取得
                const staffRequests = Object.values(requestsByStaff[s.account]).filter(r => r)
                const allSelected = staffRequests.length > 0 && staffRequests.every(r => selectedRequestIds.has(r.id))
                
                return (
                  <tr key={s.account} className="staff-row">
                    <td className="checkbox-cell">
                      <input
                        type="checkbox"
                        checked={allSelected}
                        onChange={(e) => {
                          e.stopPropagation()
                          if (e.target.checked) {
                            // このスタッフの全リクエストを選択
                            setSelectedRequestIds(prev => {
                              const newSet = new Set(prev)
                              staffRequests.forEach(r => newSet.add(r.id))
                              return newSet
                            })
                          } else {
                            // このスタッフの全リクエストを解除
                            setSelectedRequestIds(prev => {
                              const newSet = new Set(prev)
                              staffRequests.forEach(r => newSet.delete(r.id))
                              return newSet
                            })
                          }
                        }}
                        title="このスタッフの全希望を選択"
                      />
                    </td>
                    <td className="staff-cell">
                      <div className="staff-name">{s.name}</div>
                      <div className="staff-position">{s.position}</div>
                    </td>
                    {days.map(day => {
                      const dayStr = format(day, 'yyyy-MM-dd')
                      const req = requestsByStaff[s.account][dayStr]
                      
                      return (
                        <td
                          key={dayStr}
                          className={`shift-cell ${req ? (req.is_read ? 'has-request read' : 'has-request unread') : 'empty'} ${req && selectedRequestIds.has(req.id) ? 'selected' : ''}`}
                          onClick={() => req && handleCellClick(req)}
                          onContextMenu={(e) => {
                            if (req) {
                              handleCellCopy(req, e)
                            }
                          }}
                          title={req ? `左クリック：既読/未読切替 | ダブルクリック：編集 | 右クリック：コピー` : ''}
                        >
                          {req ? (
                            <div className="shift-content">
                              <div className="shift-checkbox">
                                <input
                                  type="checkbox"
                                  checked={selectedRequestIds.has(req.id)}
                                  onChange={(e) => {
                                    e.stopPropagation()
                                    handleToggleSelect(req.id)
                                  }}
                                  onClick={(e) => e.stopPropagation()}
                                />
                              </div>
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
            <span className="legend-text">未読（左クリックで既読に）</span>
          </div>
          <div className="legend-item">
            <span className="legend-box read"></span>
            <span className="legend-text">既読（左クリックで未読に）</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">💬</span>
            <span className="legend-text">備考あり（マウスオーバーで表示）</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">✏️</span>
            <span className="legend-text">ダブルクリック：編集</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">🖱️</span>
            <span className="legend-text">右クリック：コピー</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">⌨️</span>
            <span className="legend-text">Ctrl+V：貼り付け / Ctrl+A：全選択</span>
          </div>
        </div>
      </div>

      {/* 編集モーダル */}
      {editingRequest && (
        <EditModal
          request={editingRequest}
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
