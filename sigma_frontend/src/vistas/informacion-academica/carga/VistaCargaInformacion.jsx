import React, { useState } from 'react';
import {
  cargarAsignaturasCSV,
  cargarPlanEstudioCSV,
  cargarHistorialAcademicoCSV,
} from '../../../servicios/servicioAcademico.js';
import { cargarDocentesCSV } from '../../../servicios/servicioUsuarios.js';
import './cargaInformacion.css';

const TIPOS_CARGA = [
  {
    clave: 'asignaturas',
    titulo: 'Asignaturas',
    columnas: ['codigo', 'nombre'],
    funcionCarga: (archivo) => cargarAsignaturasCSV(archivo),
    permiteReemplazar: false,
  },
  {
    clave: 'docentes',
    titulo: 'Docentes',
    columnas: ['codigo', 'primer_nombre', 'segundo_nombre (opcional)', 'primer_apellido', 'segundo_apellido (opcional)', 'correo'],
    funcionCarga: (archivo, reemplazar) => cargarDocentesCSV(archivo, reemplazar),
    permiteReemplazar: true,
  },
  {
    clave: 'plan',
    titulo: 'Plan de estudio',
    columnas: ['codigo_asignatura', 'semestre', 'creditos'],
    funcionCarga: (archivo, reemplazar) => cargarPlanEstudioCSV(archivo, reemplazar),
    permiteReemplazar: true,
  },
  {
    clave: 'historial',
    titulo: 'Historial Académico Estudiante',
    columnas: ['codigo_estudiante', 'codigo_asignatura', 'periodo_academico', 'estado', 'nota (opcional)'],
    funcionCarga: (archivo, reemplazar) => cargarHistorialAcademicoCSV(archivo, reemplazar),
    permiteReemplazar: true,
  },
];

// ==========================================
// SUB-COMPONENTE: una sección de carga (1 por tipo de información)
// ==========================================
function SeccionCarga({ tipo }) {
  const [archivo, setArchivo] = useState(null);
  const [reemplazar, setReemplazar] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState('');
  const [erroresDetallados, setErroresDetallados] = useState([]);

  function manejarSeleccionArchivo(evento) {
    const seleccionado = evento.target.files?.[0];
    setArchivo(seleccionado || null);
    setResultado(null);
    setError('');
    setErroresDetallados([]);
  }

  async function manejarCargar() {
    if (!archivo) {
      setError('Selecciona un archivo CSV antes de cargar.');
      return;
    }
    if (reemplazar) {
      const confirmado = window.confirm(
        `Esto eliminará TODOS los registros existentes de "${tipo.titulo}" de tu programa antes de cargar el archivo nuevo. ¿Confirmas?`
      );
      if (!confirmado) return;
    }
    setError('');
    setErroresDetallados([]);
    setResultado(null);
    setCargando(true);
    try {
      const respuesta = await tipo.funcionCarga(archivo, reemplazar);
      setResultado(respuesta);
      setArchivo(null);
      setReemplazar(false);
    } catch (err) {
      setError(err.message);
      if (err.errores) {
        setErroresDetallados(err.errores);
      }
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="carga-info__tarjeta" style={{ marginBottom: '1rem' }}>
      <h3 className="carga-info__tarjeta-titulo">{tipo.titulo}</h3>

      <p className="carga-info__columnas-label">Columnas requeridas:</p>
      <div className="carga-info__columnas-tokens">
        {tipo.columnas.map((columna) => (
          <span key={columna} className="carga-info__token">{columna}</span>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginTop: '0.75rem', flexWrap: 'wrap' }}>
        <input type="file" accept=".csv" onChange={manejarSeleccionArchivo} disabled={cargando} />
        <button
          type="button"
          className="carga-info__btn-seleccionar"
          disabled={!archivo || cargando}
          onClick={manejarCargar}
        >
          {cargando ? 'Cargando...' : 'Cargar archivo'}
        </button>
      </div>

      {tipo.permiteReemplazar && (
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.6rem', fontSize: '0.85rem', color: '#b5750a' }}>
          <input
            type="checkbox"
            checked={reemplazar}
            onChange={(e) => setReemplazar(e.target.checked)}
            disabled={cargando}
          />
          Reemplazar todo (elimina los registros existentes de "{tipo.titulo}" de tu programa antes de cargar)
        </label>
      )}

      {error && (
        <div style={{ marginTop: '0.75rem', backgroundColor: '#fbe9e9', borderRadius: '8px', padding: '0.65rem 0.9rem' }}>
          <p style={{ color: '#c62828', margin: 0, fontSize: '0.85rem', fontWeight: 600 }}>{error}</p>
          {erroresDetallados.length > 0 && (
            <ul style={{ margin: '0.5rem 0 0', paddingLeft: '1.2rem' }}>
              {erroresDetallados.map((e, indice) => (
                <li key={indice} style={{ color: '#c62828', fontSize: '0.8rem' }}>{e}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {resultado && (
        <div style={{ marginTop: '0.75rem', backgroundColor: '#e6f4ea', borderRadius: '8px', padding: '0.65rem 0.9rem' }}>
          <p style={{ color: '#1e7d3c', margin: 0, fontSize: '0.85rem', fontWeight: 600 }}>{resultado.detail}</p>
          <p style={{ color: '#1e7d3c', margin: '0.25rem 0 0', fontSize: '0.8rem' }}>
            {resultado.creadas ?? resultado.creados ?? 0} nuevos, {resultado.actualizadas ?? resultado.actualizados ?? 0} actualizados
            {(resultado.eliminadas || resultado.eliminados) ? `, ${resultado.eliminadas ?? resultado.eliminados} eliminados antes de cargar` : ''}
            {' '}({resultado.total_filas} filas procesadas).
          </p>
        </div>
      )}
    </div>
  );
}

// ==========================================
// VISTA PRINCIPAL
// ==========================================
export default function VistaCargaInformacion() {
  return (
    <div className="carga-info-container">
      <header className="carga-info__header">
        <h2 className="carga-info__titulo-vista">Carga de Información Académica</h2>
        <p className="carga-info__subtitulo-vista">
          Importa la información académica desde el sistema institucional externo.
        </p>
      </header>

      <div className="carga-info__alerta-azul">
        <div className="carga-info__alerta-contenido">
          <span className="carga-info__alerta-icono">i</span>
          <p>
            <strong>Asegúrate de utilizar un archivo .csv con codificación UTF-8.</strong>
            <br />
            Cada tipo de información se carga por separado, con sus propias columnas requeridas.
            Si alguna fila tiene errores, no se guarda nada y se muestra el detalle para corregir el archivo.
          </p>
        </div>
      </div>

      <div className="carga-info__seguridad-box" style={{ marginBottom: '1rem' }}>
        <div className="carga-info__seguridad-icono">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#d97706" strokeWidth="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
        </div>
        <div>
          <h4 className="carga-info__seguridad-titulo">Seguridad de los datos</h4>
          <p className="carga-info__seguridad-texto">
            Las asignaturas y docentes que cargues aquí quedan disponibles para todos los programas.
            El plan de estudio y el historial académico solo afectan a tu propio programa académico.
          </p>
        </div>
      </div>

      {TIPOS_CARGA.map((tipo) => (
        <SeccionCarga key={tipo.clave} tipo={tipo} />
      ))}
    </div>
  );
}