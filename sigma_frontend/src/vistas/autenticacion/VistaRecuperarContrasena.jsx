import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { solicitarRecuperacionContrasena } from '../../servicios/servicioAutenticacion.js';
import './autenticacion.css';

/**
 * Vista para solicitar la recuperación de contraseña institucional.
 * Por seguridad, el backend siempre responde con el mismo mensaje
 * genérico exista o no una cuenta con el correo indicado.
 */
function VistaRecuperarContrasena() {
  const [correo, setCorreo] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [error, setError] = useState('');

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setError('');
    setMensaje('');
    setEnviando(true);
    try {
      const respuesta = await solicitarRecuperacionContrasena(correo);
      setMensaje(respuesta.detail);
    } catch (err) {
      setError(err.message || 'No se pudo procesar la solicitud. Intenta de nuevo.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="auth-screen-container">
      <div className="auth-card-wrapper">

        {/* Encabezado de Marca Institucional */}
        <header className="auth-card-header">
          <div className="auth-logo-badge">
            <span className="material-icons-outlined">lock_reset</span>
          </div>
          <h2 className="auth-card-title">¿Olvidaste tu contraseña?</h2>
          <p className="auth-card-subtitle">
            Ingresa tu correo institucional asignado y te enviaremos un enlace seguro para restablecer tus credenciales de acceso.
          </p>
        </header>

        {mensaje ? (
          <div className="auth-form-body">
            <p style={{ color: '#1e7d3c', textAlign: 'center' }}>{mensaje}</p>
          </div>
        ) : (
          <form onSubmit={manejarEnvio} className="auth-form-body">
            {error && (
              <p style={{ color: '#c62828', fontSize: '0.85rem', margin: '0 0 0.75rem' }}>{error}</p>
            )}
            <div className="auth-input-group">
              <label className="campo-texto__etiqueta">Correo Electrónico Institucional</label>
              <input
                type="email"
                placeholder="usuario@unicartagena.edu.co"
                className="campo-texto__input"
                value={correo}
                onChange={(e) => setCorreo(e.target.value)}
                required
              />
            </div>

            <div className="auth-action-button-container">
              <button type="submit" className="boton boton--primario boton-bloque-completo" disabled={enviando}>
                {enviando ? 'Enviando...' : 'Enviar enlace de recuperación'}
              </button>
            </div>
          </form>
        )}

        {/* Pie del Panel - Navegación Segura */}
        <footer className="auth-card-footer">
          <Link to="/iniciar-sesion" className="auth-back-link">
            <span className="material-icons-outlined">arrow_back</span>
            <span>Regresar al inicio de sesión</span>
          </Link>
        </footer>

      </div>
    </div>
  );
}

export default VistaRecuperarContrasena;