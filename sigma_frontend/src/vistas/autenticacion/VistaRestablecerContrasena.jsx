import React, { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { restablecerContrasena } from '../../servicios/servicioAutenticacion.js';
import './autenticacion.css';

/**
 * Vista a la que llega el usuario al hacer clic en el enlace del
 * correo de recuperación. Lee uid/token de la URL y permite definir
 * una nueva contraseña.
 */
function VistaRestablecerContrasena() {
  const { uid, token } = useParams();
  const navegar = useNavigate();

  const [nuevaContrasena, setNuevaContrasena] = useState('');
  const [confirmarContrasena, setConfirmarContrasena] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [error, setError] = useState('');

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setError('');
    setMensaje('');

    if (nuevaContrasena.length < 8) {
      setError('La nueva contraseña debe tener al menos 8 caracteres.');
      return;
    }
    if (nuevaContrasena !== confirmarContrasena) {
      setError('Las contraseñas no coinciden.');
      return;
    }

    setEnviando(true);
    try {
      const respuesta = await restablecerContrasena({ uid, token, nuevaContrasena });
      setMensaje(respuesta.detail);
      setTimeout(() => navegar('/iniciar-sesion'), 2500);
    } catch (err) {
      setError(err.message || 'No se pudo restablecer la contraseña. Intenta solicitando un nuevo enlace.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="auth-screen-container">
      <div className="auth-card-wrapper">

        <header className="auth-card-header">
          <div className="auth-logo-badge">
            <span className="material-icons-outlined">lock_reset</span>
          </div>
          <h2 className="auth-card-title">Crea una nueva contraseña</h2>
          <p className="auth-card-subtitle">
            Define una nueva contraseña para tu cuenta institucional.
          </p>
        </header>

        {mensaje ? (
          <div className="auth-form-body">
            <p style={{ color: '#1e7d3c', textAlign: 'center' }}>{mensaje}</p>
            <p style={{ textAlign: 'center', fontSize: '0.85rem', color: '#64748b' }}>
              Te llevaremos al inicio de sesión en un momento...
            </p>
          </div>
        ) : (
          <form onSubmit={manejarEnvio} className="auth-form-body">
            {error && (
              <p style={{ color: '#c62828', fontSize: '0.85rem', margin: '0 0 0.75rem' }}>{error}</p>
            )}
            <div className="auth-input-group">
              <label className="campo-texto__etiqueta">Nueva contraseña</label>
              <input
                type="password"
                placeholder="Mínimo 8 caracteres"
                className="campo-texto__input"
                value={nuevaContrasena}
                onChange={(e) => setNuevaContrasena(e.target.value)}
                required
              />
            </div>
            <div className="auth-input-group">
              <label className="campo-texto__etiqueta">Confirmar nueva contraseña</label>
              <input
                type="password"
                placeholder="Repite la contraseña"
                className="campo-texto__input"
                value={confirmarContrasena}
                onChange={(e) => setConfirmarContrasena(e.target.value)}
                required
              />
            </div>

            <div className="auth-action-button-container">
              <button type="submit" className="boton boton--primario boton-bloque-completo" disabled={enviando}>
                {enviando ? 'Guardando...' : 'Restablecer contraseña'}
              </button>
            </div>
          </form>
        )}

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

export default VistaRestablecerContrasena;