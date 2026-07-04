import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { App } from '@/App'
import { AuthProvider } from '@/lib/auth'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        {/* All paths render the same App instance: switching between sessions
            or opening /auth only swaps state — no remount, no reload. */}
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/auth" element={<App />} />
          <Route path="/:sessionId" element={<App />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
