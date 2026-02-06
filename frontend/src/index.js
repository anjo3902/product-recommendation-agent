import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));

// Remove initial loader when React is ready
const removeLoader = () => {
  const loader = document.getElementById('initial-loader');
  if (loader) {
    loader.classList.add('hide');
    setTimeout(() => {
      loader.style.display = 'none';
    }, 300);
  }
};

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Hide loader after render
setTimeout(removeLoader, 100);
