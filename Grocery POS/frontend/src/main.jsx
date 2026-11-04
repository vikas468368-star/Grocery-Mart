import React, { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

class AppErrorBoundary extends React.Component {
  state = { error: null };

  static getDerivedStateFromError(error) {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: '32px', color: '#fca5a5', background: '#0b0f19', minHeight: '100vh', fontFamily: 'sans-serif' }}>
          <h2>Grocery POS could not render</h2>
          <p>{this.state.error.message || String(this.state.error)}</p>
          <button onClick={() => window.location.reload()} style={{ padding: '10px 16px' }}>Reload application</button>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AppErrorBoundary>
      <App />
    </AppErrorBoundary>
  </StrictMode>,
)
