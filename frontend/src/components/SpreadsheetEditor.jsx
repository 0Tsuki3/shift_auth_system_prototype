import { useState, useEffect } from 'react'
import axios from 'axios'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, parseISO } from 'date-fns'
import { ja } from 'date-fns/locale'
import './SpreadsheetEditor.css'

export function SpreadsheetEditor({ month }) {
  const [requests, setRequests] = useState([])
  const [staff, setStaff] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchData()
  }, [month])

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
      await axios.patch(`/admin/api/shift-requests/${requestId}/read`, {
        month: month
      })
      
      // データをリフレッシュ
      fetchData()
    } catch (error) {
      console.error('更新エラー:', error)
      alert('更新に失敗しました')
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
      </div>

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
              staff.map(s => (
                <tr key={s.account} className="staff-row">
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
                        className={`shift-cell ${req ? (req.is_read ? 'has-request read' : 'has-request unread') : 'empty'}`}
                        onClick={() => req && toggleRead(req.id)}
                        title={req ? `クリックで${req.is_read ? '未読' : '既読'}に変更` : ''}
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
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* 凡例 */}
      <div className="spreadsheet-legend">
        <div className="legend-title">凡例:</div>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-box unread"></span>
            <span className="legend-text">未読（クリックで既読に）</span>
          </div>
          <div className="legend-item">
            <span className="legend-box read"></span>
            <span className="legend-text">既読（クリックで未読に）</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">💬</span>
            <span className="legend-text">備考あり（マウスオーバーで表示）</span>
          </div>
        </div>
      </div>

      {/* データがない場合 */}
      {totalCount === 0 && (
        <div className="no-data-message">
          <p>📭 この月のシフト希望はまだ提出されていません</p>
        </div>
      )}
    </div>
  )
}
