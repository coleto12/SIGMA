import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  obtenerMiMatricula,
  obtenerAsignaturasDeSolicitud,
} from '../../servicios/servicioMatricula.js';
import './consultar-matricula-oficial.css';

function VistaConsultarMatriculaOficial() {
  const navegar = useNavigate();
  const [matricula, setMatricula] = useState(null);
  const [asignaturas, setAsignaturas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');
  const [descargando, setDescargando] = useState(false);

  useEffect(() => {
    async function cargar() {
      setCargando(true);
      setError('');
      try {
        const miMatricula = await obtenerMiMatricula();
        setMatricula(miMatricula);
        if (miMatricula) {
          const asigs = await obtenerAsignaturasDeSolicitud(miMatricula.solicitud_matricula);
          setAsignaturas(asigs);
        }
      } catch {
        setError('No se pudo cargar la información de tu matrícula oficial.');
      } finally {
        setCargando(false);
      }
    }
    cargar();
  }, []);

  async function manejarDescargar() {
    if (!matricula?.documento) return;
    setDescargando(true);
    try {
      // El documento ya es una URL pública (Cloudinary); abrirla en una
      // pestaña nueva permite al navegador visualizarla o descargarla
      // según su configuración, sin necesidad de manejar el archivo
      // binario manualmente desde el frontend.
      window.open(matricula.documento, '_blank', 'noopener,noreferrer');
    } finally {
      setDescargando(false);
    }
  }

  if (cargando) {
    return <p style={{ padding: '2rem' }}>Cargando tu matrícula oficial...</p>;
  }

  if (error) {
    return (
      <div className="sigma-form-card" style={{ margin: '2rem', backgroundColor: '#fbe9e9' }}>
        <p style={{ color: '#c62828', margin: 0 }}>{error}</p>
      </div>
    );
  }

  if (!matricula) {
    return (
      <div className="matricula-oficial-container">
        <header className="matricula-oficial-header">
          <h2>Consultar Matrícula Oficial</h2>
          <p>Consulta y descarga tu matrícula académica oficial una vez tu solicitud sea aprobada.</p>
        </header>
        <div className="sigma-form-card" style={{ backgroundColor: '#eef5ff' }}>
          <p style={{ margin: 0 }}>
            Todavía no tienes una matrícula oficial generada. Esto sucede automáticamente cuando
            el Jefe de Departamento aprueba tu solicitud de matrícula.
          </p>
          <button
            type="button"
            className="btn-sol-siguiente"
            style={{ marginTop: '1rem' }}
            onClick={() => navegar('/solicitudes/consultar-estado-solicitud')}
          >
            Consultar estado de mi solicitud
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="matricula-oficial-container">
      <header className="matricula-oficial-header">
        <h2>Consultar Matrícula Oficial</h2>
        <p>Esta es tu matrícula académica oficial para el periodo vigente.</p>
      </header>

      <section className="sigma-form-card">
        <div className="matricula-oficial-resumen-grid">
          <div>
            <span className="info-label">Estudiante</span>
            <p className="info-value-sm">{matricula.estudiante_nombre} ({matricula.estudiante_codigo})</p>
          </div>
          <div>
            <span className="info-label">Periodo académico</span>
            <p className="info-value-sm">{matricula.periodo_academico_nombre}</p>
          </div>
          <div>
            <span className="info-label">Fecha de emisión</span>
            <p className="info-value-sm">{new Date(matricula.fecha_emision).toLocaleString('es-CO')}</p>
          </div>
          <div>
            <span className="info-label">Estado</span>
            <p className="info-value-sm"><span className="badge badge-success">Vigente</span></p>
          </div>
        </div>
      </section>

      <section className="sigma-form-card no-padding">
        <div className="card-padding-title">
          <h4 className="form-section-title font-bold">Asignaturas matriculadas ({asignaturas.length})</h4>
        </div>
        <table className="sigma-table">
          <thead>
            <tr>
              <th>Asignatura</th>
              <th>Código</th>
              <th>Grupo</th>
            </tr>
          </thead>
          <tbody>
            {asignaturas.map((asig) => (
              <tr key={asig.id}>
                <td><strong>{asig.asignatura_nombre}</strong></td>
                <td className="text-muted-dark">{asig.asignatura_codigo}</td>
                <td>{asig.grupo_nombre}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <div className="matricula-oficial-acciones">
        <button type="button" className="btn-sol-siguiente" disabled={descargando} onClick={manejarDescargar}>
          <span className="material-icons-outlined">download</span>
          {descargando ? 'Abriendo...' : 'Descargar matrícula oficial (PDF)'}
        </button>
      </div>
    </div>
  );
}

export default VistaConsultarMatriculaOficial;