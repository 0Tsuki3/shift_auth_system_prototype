import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [message, setMessage] = useState('React + Flask 統合テスト')

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎉 React セットアップ完了！</h1>
        <p>{message}</p>
        <div style={{ marginTop: '2rem', textAlign: 'left', maxWidth: '600px' }}>
          <h2>✅ セットアップ済み項目</h2>
          <ul>
            <li>✅ Vite + React</li>
            <li>✅ axios (HTTP通信)</li>
            <li>✅ date-fns (日付処理)</li>
            <li>✅ ビルド設定 (→ static/js/shift-editor/)</li>
            <li>✅ Flask API プロキシ設定</li>
          </ul>
          
          <h2>📝 次のステップ</h2>
          <ol>
            <li>Flask側のAPI実装 (/api/shift-requests/*, /api/staff)</li>
            <li>スプレッドシート編集画面のコンポーネント作成</li>
            <li>データフェッチとステート管理</li>
            <li>編集機能（モーダル）の実装</li>
          </ol>
          
          <p style={{ marginTop: '2rem', color: '#888' }}>
            詳細は <code>plan/REACT_INTEGRATION.md</code> を参照
          </p>
        </div>
      </header>
    </div>
  )
}

export default App
