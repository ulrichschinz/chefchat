import { useState } from 'react'
import ChatWindow from './ChatWindow'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div className="App">
        <ChatWindow />
      </div>
    </>
  )
}

export default App
