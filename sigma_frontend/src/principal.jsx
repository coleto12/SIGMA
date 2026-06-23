import React from 'react';
import ReactDOM from 'react-dom/client';
import AplicacionPrincipal from './AplicacionPrincipal.jsx';
import './activos/estilos/global.css';

ReactDOM.createRoot(document.getElementById('raiz')).render(
  <React.StrictMode>
    <AplicacionPrincipal />
  </React.StrictMode>
);
