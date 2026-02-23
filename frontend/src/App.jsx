import { useState, useEffect } from 'react'
import { SpreadsheetEditor } from './components/SpreadsheetEditor'
import './App.css'

function App() {
  const [month, setMonth] = useState('')

  useEffect(() => {
    // HTML要素のdata-month属性から月を取得
    const rootElement = document.getElementById('root')
    const monthData = rootElement?.getAttribute('data-month')
    
    if (monthData) {
      setMonth(monthData)
    } else {
      // デフォルトは今月
      const now = new Date()
      const defaultMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
      setMonth(defaultMonth)
    }
  }, [])

  if (!month) {
    return (
      <div className="App">
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <p>読み込み中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="App">
      <SpreadsheetEditor month={month} />
    </div>
  )
}

export default App
