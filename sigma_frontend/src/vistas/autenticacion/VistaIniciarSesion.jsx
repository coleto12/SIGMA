import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAutenticacion } from '../../contexto/ContextoAutenticacion.jsx';
import './autenticacion.css';

function VistaIniciarSesion() {
  const navegar = useNavigate();
  const { iniciarSesion } = useAutenticacion();

  const [correo, setCorreo] = useState('');
  const [password, setPassword] = useState('');
  const [mostrarPassword, setMostrarPassword] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState('');

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setError('');
    setEnviando(true);
    try {
      await iniciarSesion(correo, password);
      navegar('/');
    } catch (err) {
      setError(err.message || 'No se pudo iniciar sesión. Intenta de nuevo.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="auth-container">
      
      {/* PANEL IZQUIERDO: SECCIÓN INFORMATIVA */}
      <div className="auth-left-panel">
        
        {/* PARTE SUPERIOR AZUL CON LA CURVA */}
        <div className="auth-blue-section">
          <div className="auth-header-uni">
            {/* Logo de la universidad desde la carpeta public */}
            <img src="/escudo.jpg" alt="Escudo Universidad de Cartagena" className="auth-uni-logo" />
            <div className="auth-uni-text">
              <h1>Universidad de Cartagena</h1>
              <span>Fundada en 1827</span>
            </div>
          </div>
          
          <div className="auth-welcome-box">
            <p className="auth-welcome-text">Bienvenido a</p>
            <h2 className="auth-sigma-title">SIGMA</h2>
            <p className="auth-sigma-desc">
              Sistema Integrado de Gestión de Matrícula Académica
            </p>
          </div>
          
          {/* Este elemento genera la curva perfecta con el borde dorado sin cortar el texto */}
          <div className="auth-wave-decorator"></div>
        </div>

        {/* PARTE INFERIOR BLANCA CON LOS BENEFICIOS */}
        <div className="auth-white-section">
          <div className="auth-benefit-list">
            
            <div className="auth-benefit-item">
              <div className="auth-icon-wrapper shield-icon"></div>
              <div className="auth-benefit-content">
                <h3>Seguro</h3>
                <p>Tus datos están protegidos con los más altos estándares.</p>
              </div>
            </div>

            <div className="auth-benefit-item">
              <div className="auth-icon-wrapper people-icon"></div>
              <div className="auth-benefit-content">
                <h3>Confiable</h3>
                <p>Información académica actualizada y en tiempo real.</p>
              </div>
            </div>

            <div className="auth-benefit-item">
              <div className="auth-icon-wrapper academic-icon"></div>
              <div className="auth-benefit-content">
                <h3>Académico</h3>
                <p>Gestión integral de tu proceso de matrícula.</p>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* PANEL DERECHO: FORMULARIO DE ACCESO */}
      <div className="auth-right-panel">

        {/* TARJETA BLANCA FLOTANTE */}
        <div className="auth-card">
          <div className="auth-user-avatar">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#db9d24" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>

          <h2>Iniciar sesión</h2>
          <p className="auth-card-subtitle">
            Ingresa tus credenciales institucionales para acceder al sistema
          </p>

          {error && (
            <div className="auth-error-message" role="alert">
              {error}
            </div>
          )}

          <form className="auth-form" onSubmit={manejarEnvio}>
            
            <div className="auth-input-group">
              <label>Correo institucional</label>
              <div className="auth-input-wrapper">
                <span className="auth-input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                </span>
                <input
                  type="email"
                  placeholder="usuario@unicartagena.edu.co"
                  value={correo}
                  onChange={(e) => setCorreo(e.target.value)}
                  required
                  autoComplete="username"
                />
              </div>
            </div>

            <div className="auth-input-group">
              <label>Contraseña</label>
              <div className="auth-input-wrapper">
                <span className="auth-input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                </span>
                <input
                  type={mostrarPassword ? 'text' : 'password'}
                  placeholder="Ingresa tu contraseña"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                />
                <span
                  className="auth-toggle-password"
                  onClick={() => setMostrarPassword((v) => !v)}
                  role="button"
                  tabIndex={0}
                  aria-label={mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                </span>
              </div>
            </div>

            <div className="auth-form-options">
              <label className="auth-remember">
                <input type="checkbox" defaultChecked />
                <span>Recordar sesión</span>
              </label>
              <Link to="/recuperar-contrasena" className="auth-forgot-link">¿Olvidaste tu contraseña?</Link>
            </div>

            <button type="submit" className="auth-btn-primary" disabled={enviando}>
              {enviando ? 'Iniciando sesión...' : <>Iniciar sesión &rarr;</>}
            </button>
          </form>

          <div className="auth-footer-note">
            <span>Solo cuentas institucionales <strong style={{color: '#db9d24'}}>@unicartagena.edu.co</strong></span>
          </div>
        </div>

        {/* PIE DE PÁGINA GENERAL */}
        <div className="auth-main-footer">
          <span>© 2026 Universidad de Cartagena. Todos los derechos reservados.</span>
        </div>
      </div>

    </div>
  );
}

export default VistaIniciarSesion;