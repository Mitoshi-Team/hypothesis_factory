import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { App } from '@/App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      {/* Both paths render the same App instance, so switching between
          sessions only swaps the active id — no remount, no reload. */}
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/:sessionId" element={<App />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
