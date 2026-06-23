import React, { useEffect, useState } from 'react';
import { useAutenticacion } from '../../../contexto/ContextoAutenticacion.jsx';
import { obtenerPeriodoAcademicoActivo } from '../../../servicios/servicioAcademico.js';
import {
  obtenerPeriodosMatricula,
  obtenerRequisitosDocumentales,
} from '../../../servicios/servicioMatricula.js';
import './consultar-fechas-requisitos.css';

function VistaConsultarFechasRequisitos() {
  const { usuario } = useAutenticacion();
  const esJefe = usuario?.rol_nombre === 'Jefe de Departamento' || usuario?.rol_nombre === 'Administrador';

  const [periodoAcademico, setPeriodoAcademico] = useState(null);
  const [periodoMatricula, setPeriodoMatricula] = useState(null);
  const [requisitos, setRequisitos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function cargar() {
      setCargando(true);
      setError('');
      try {
        const periodo = await obtenerPeriodoAcademicoActivo();
        setPeriodoAcademico(periodo);
        if (!periodo) return;

        // El backend ya filtra: un Estudiante solo recibe periodos de
        // matrícula con estado 'publicado'; un Jefe/Admin ve todos.
        const periodos = await obtenerPeriodosMatricula();
        const periodoMat = periodos.find((p) => p.periodo_academico === periodo.id) ?? null;
        setPeriodoMatricula(periodoMat);

        if (periodoMat) {
          const listaRequisitos = await obtenerRequisitosDocumentales(periodoMat.id);
          setRequisitos(listaRequisitos);
        }
      } catch {
        setError('No se pudo cargar la información de fechas y requisitos.');
      } finally {
        setCargando(false);
      }
    }
    cargar();
  }, []);

  if (cargando) {
    return <p style={{ padding: '2rem' }}>Cargando fechas y requisitos...</p>;
  }

  if (error) {
    return (
      <div className="sigma-card-fechas" style={{ margin: '2rem', backgroundColor: '#fbe9e9' }}>
        <p style={{ color: '#c62828', margin: 0 }}>{error}</p>
      </div>
    );
  }

  if (!periodoAcademico) {
    return (
      <div className="sigma-card-fechas" style={{ margin: '2rem' }}>
        <p>No hay un periodo académico activo en este momento.</p>
      </div>
    );
  }

  if (!periodoMatricula) {
    return (
      <div className="sigma-fechas-container">
        <div className="sigma-fechas-main">
          <header className="sigma-fechas-header">
            <h2>Consultar Fechas y Requisitos</h2>
            <p>Consulta y verifica las fechas del proceso de matrícula y los documentos requeridos.</p>
          </header>
          <section className="sigma-card-fechas">
            <p>
              {esJefe
                ? 'Aún no has configurado las fechas y requisitos para este periodo. Ve a "Crear Fechas y Requisitos".'
                : 'El Jefe de Departamento aún no ha publicado las fechas y requisitos para este periodo.'}
            </p>
          </section>
        </div>
      </div>
    );
  }

  return (
    <div className="sigma-fechas-container">
      <div className="sigma-fechas-main">
        <header className="sigma-fechas-header">
          <h2>Consultar Fechas y Requisitos</h2>
          <p>Consulta y verifica las fechas del proceso de matrícula y los documentos requeridos.</p>
        </header>

        <section className="sigma-card-fechas">
          <div className="section-title-row">
            <span className="material-icons-outlined icon-amber">calendar_today</span>
            <h3>1. Fechas del Proceso</h3>
          </div>
          <p className="section-subtitle">Fechas del proceso de matrícula para el período {periodoAcademico.nombre}.</p>

          <div className="timeline-wrapper">
            <div className="timeline-line"></div>

            <div className="timeline-node">
              <div className="node-icon-circle blue-light">
                <span className="material-icons-outlined">edit_note</span>
              </div>
              <h4 className="node-title">Inicio de solicitudes</h4>
              <p className="node-date">{periodoMatricula.fecha_inicio}</p>
            </div>

            <div className="timeline-node">
              <div className="node-icon-circle green-light">
                <span className="material-icons-outlined">calendar_month</span>
              </div>
              <h4 className="node-title">Límite de solicitudes</h4>
              <p className="node-date">{periodoMatricula.fecha_fin}</p>
            </div>
          </div>
        </section>

        <section className="sigma-card-fechas">
          <div className="section-title-row">
            <span className="material-icons-outlined icon-amber">folder_open</span>
            <h3>2. Requisitos Documentales</h3>
          </div>
          <p className="section-subtitle">Documentos que los estudiantes deben adjuntar al realizar su solicitud.</p>

          {requisitos.length === 0 ? (
            <p>No hay requisitos documentales definidos para este periodo.</p>
          ) : (
            <div className="table-fechas-responsive">
              <table className="table-fechas-requisitos">
                <thead>
                  <tr>
                    <th style={{ width: '40px' }}>#</th>
                    <th>Documento requerido</th>
                    <th>Descripción</th>
                    <th>Formato permitido</th>
                  </tr>
                </thead>
                <tbody>
                  {requisitos.map((req, indice) => (
                    <tr key={req.id}>
                      <td className="text-muted-num">{indice + 1}</td>
                      <td className="fw-semibold text-slate">{req.nombre}</td>
                      <td className="text-muted-desc">{req.descripcion}</td>
                      <td className="font-mono">{req.formato}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="banner-info-footer">
            <span className="material-icons-outlined">info</span>
            <p>Asegúrese de que los documentos sean legibles y estén en los formatos permitidos.</p>
          </div>
        </section>
      </div>

      <aside className="sigma-fechas-aside">
        <div className="aside-fechas-card">
          <div className="aside-fechas-row">
            <div className="aside-calendar-box">
              <span className="material-icons-outlined">calendar_today</span>
            </div>
            <div>
              <span className="label-top">Periodo Académico</span>
              <h4>{periodoAcademico.nombre}</h4>
              <span className={`badge-vigente-verde`}>
                {periodoMatricula.estado === 'publicado' ? 'Publicado' : 'En configuración'}
              </span>
            </div>
          </div>
          <p className="aside-date-range">{periodoAcademico.fecha_inicio} a {periodoAcademico.fecha_fin}</p>
        </div>

        <div className="aside-fechas-card">
          <h5 className="aside-title">Resumen del Proceso</h5>
          <ul className="aside-resumen-list">
            <li>
              <span className="material-icons-outlined icon-summary">edit_note</span>
              <div>
                <p className="title-summary">Inicio de solicitudes</p>
                <p className="detail-summary">{periodoMatricula.fecha_inicio}</p>
              </div>
            </li>
            <li>
              <span className="material-icons-outlined icon-summary">calendar_month</span>
              <div>
                <p className="title-summary">Límite de solicitudes</p>
                <p className="detail-summary">{periodoMatricula.fecha_fin}</p>
              </div>
            </li>
          </ul>
        </div>

        <div className="aside-fechas-card alert-blue-bg">
          <div className="alert-title-row">
            <span className="material-icons-outlined text-blue">info</span>
            <strong className="text-blue">Información importante</strong>
          </div>
          <p className="alert-text">
            Las fechas pueden estar sujetas a cambios por disposiciones institucionales. Siga atento a los comunicados oficiales del departamento.
          </p>
        </div>
      </aside>
    </div>
  );
}

export default VistaConsultarFechasRequisitos;