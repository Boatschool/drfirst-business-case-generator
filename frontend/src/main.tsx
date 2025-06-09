import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';

// Register service worker for production performance
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('[SW] Service worker registered successfully:', registration.scope);
        
        // Check for updates every 30 minutes
        setInterval(() => {
          registration.update();
        }, 30 * 60 * 1000);
      })
      .catch((error) => {
        console.warn('[SW] Service worker registration failed:', error);
      });
  });
}

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Root element not found');
}
ReactDOM.createRoot(rootElement).render(<App />);
