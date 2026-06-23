import React, { useEffect, useState } from 'react';
import Insignia from '../../componentes/comunes/Insignia.jsx';
import {
  obtenerNotificaciones,
  marcarNotificacionLeida,
  marcarTodasLeidas,
} from '../../servicios/servicioNotificaciones.js';
import './notificaciones.css';

function formatearFechaRelativa(fechaIso) {
  const fecha = new Date(fechaIso);
  const ahora = new Date();
  const segundos = Math.floor((ahora - fecha) / 1000);

  if (segundos < 60) return 'Hace unos momentos';
  const minutos = Math.floor(segundos / 60);
  if (minutos < 60) return `Hace ${minutos} minuto${minutos === 1 ? '' : 's'}`;
  const horas = Math.floor(minutos / 60);
  if (horas < 24) return `Hace ${horas} hora${horas === 1 ? '' : 's'}`;
  const dias = Math.floor(horas / 24);
  if (dias < 30) return `Hace ${dias} día${dias === 1 ? '' : 's'}`;
  return fecha.toLocaleDateString('es-CO');
}

/**
 * Vista de listado de notificaciones del usuario. Trae TODAS las
 * notificaciones reales (leídas y no leídas) del usuario autenticado;
 * el backend ya filtra por usuario, sin excepción de rol.
 */
function VistaNotificaciones() {
  const [notificaciones, setNotificaciones] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');
  const [marcandoTodas, setMarcandoTodas] = useState(false);

  async function cargar() {
    setCargando(true);
    setError('');
    try {
      const lista = await obtenerNotificaciones();
      setNotificaciones(lista);
    } catch {
      setError('No se pudieron cargar tus notificaciones.');
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    cargar();
  }, []);

  async function manejarClicNotificacion(notificacion) {
    if (notificacion.leida) return;
    try {
      await marcarNotificacionLeida(notificacion.id);
      setNotificaciones((previo) =>
        previo.map((n) => (n.id === notificacion.id ? { ...n, leida: true } : n))
      );
    } catch {
      // Si falla marcar como leída, no es crítico: se deja como estaba.
    }
  }

  async function manejarMarcarTodas() {
    setMarcandoTodas(true);
    try {
      await marcarTodasLeidas();
      setNotificaciones((previo) => previo.map((n) => ({ ...n, leida: true })));
    } catch {
      setError('No se pudieron marcar todas las notificaciones como leídas.');
    } finally {
      setMarcandoTodas(false);
    }
  }

  const hayNoLeidas = notificaciones.some((n) => !n.leida);

  return (
    <div className="vista-notificaciones">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Notificaciones</h2>
        {hayNoLeidas && (
          <button
            type="button"
            onClick={manejarMarcarTodas}
            disabled={marcandoTodas}
            style={{ background: 'none', border: 'none', color: '#1f4e5f', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600 }}
          >
            {marcandoTodas ? 'Marcando...' : 'Marcar todas como leídas'}
          </button>
        )}
      </div>

      {error && (
        <p style={{ color: '#c62828', fontSize: '0.85rem' }}>{error}</p>
      )}

      {cargando ? (
        <p>Cargando notificaciones...</p>
      ) : notificaciones.length === 0 ? (
        <p>No tienes notificaciones todavía.</p>
      ) : (
        <ul className="vista-notificaciones__lista">
          {notificaciones.map((notificacion) => (
            <li
              key={notificacion.id}
              onClick={() => manejarClicNotificacion(notificacion)}
              style={{ cursor: notificacion.leida ? 'default' : 'pointer', opacity: notificacion.leida ? 0.7 : 1 }}
            >
              <div>
                <p className="vista-notificaciones__titulo">{notificacion.mensaje}</p>
                <p className="vista-notificaciones__fecha">{formatearFechaRelativa(notificacion.created_at)}</p>
              </div>
              {!notificacion.leida && <Insignia texto="Nueva" estado="info" />}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default VistaNotificaciones;