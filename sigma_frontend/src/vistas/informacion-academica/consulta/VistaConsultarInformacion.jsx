import React, { useEffect, useState, useCallback } from 'react';
import { useAutenticacion } from '../../../contexto/ContextoAutenticacion.jsx';
import {
  obtenerPlanVigente,
  obtenerAsignaturasDelPlan,
  obtenerAsignaturas,
  obtenerPrerrequisitos,
  obtenerHistorialAcademico,
} from '../../../servicios/servicioAcademico.js';
import { obtenerDocentes } from '../../../servicios/servicioUsuarios.js';
import './ConsultarInformacion.css';

const TIPOS_INFO = [
  { clave: 'plan', titulo: 'Plan de Estudios', descripcion: 'Consulta el plan de estudio vigente de tu programa.' },
  { clave: 'docentes', titulo: 'Docentes', descripcion: 'Consulta la información del personal docente.' },
  { clave: 'asignaturas', titulo: 'Asignaturas', descripcion: 'Consulta la oferta de asignaturas disponibles.' },
  { clave: 'historial', titulo: 'Historial Académico Estudiante', descripcion: 'Consulta el historial académico de los estudiantes.' },
];

const ETIQUETAS_ESTADO_HISTORIAL = {
  aprobada: 'Aprobada',
  reprobada: 'Reprobada',
  en_curso: 'En curso',
};

// ==========================================
// SUB-COMPONENTE: tabla de Plan de Estudios
// ==========================================
function TablaPlanEstudios({ programaAcademicoId }) {
  const [plan, setPlan] = useState(null);
  const [filas, setFilas] = useState([]);
  const [prerequisitosPorAsignatura, setPrerequisitosPorAsignatura] = useState({});
  const [filtroSemestre, setFiltroSemestre] = useState('todos');
  const [busqueda, setBusqueda] = useState('');
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    async function cargar() {
      setCargando(true);
      const planVigente = await obtenerPlanVigente(programaAcademicoId);
      setPlan(planVigente);
      if (planVigente) {
        const filasDelPlan = await obtenerAsignaturasDelPlan(planVigente.id);
        setFilas(filasDelPlan);
        const mapaPrereqs = {};
        await Promise.all(
          filasDelPlan.map(async (f) => {
            const prereqs = await obtenerPrerrequisitos(f.asignatura);
            mapaPrereqs[f.asignatura] = prereqs;
          })
        );
        setPrerequisitosPorAsignatura(mapaPrereqs);
      }
      setCargando(false);
    }
    cargar();
  }, [programaAcademicoId]);

  const semestresDisponibles = [...new Set(filas.map((f) => f.semestre))].sort((a, b) => a - b);
  const filasFiltradas = filas.filter((f) => {
    const pasaSemestre = filtroSemestre === 'todos' || f.semestre === Number(filtroSemestre);
    const pasaBusqueda = !busqueda ||
      f.asignatura_nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
      f.asignatura_codigo.toLowerCase().includes(busqueda.toLowerCase());
    return pasaSemestre && pasaBusqueda;
  });

  if (cargando) return <p style={{ padding: '1rem' }}>Cargando plan de estudios...</p>;
  if (!plan) return <p style={{ padding: '1rem' }}>Tu programa académico no tiene un plan de estudios vigente.</p>;

  return (
    <>
      <section className="consultar-info__filtros-panel">
        <div className="consultar-info__filtro-grupo">
          <label>Semestre</label>
          <select value={filtroSemestre} onChange={(e) => setFiltroSemestre(e.target.value)}>
            <option value="todos">Todos</option>
            {semestresDisponibles.map((s) => (
              <option key={s} value={s}>Semestre {s}</option>
            ))}
          </select>
        </div>
        <div className="consultar-info__filtro-grupo consultar-info__filtro-grupo--buscar">
          <label>Buscar asignatura</label>
          <div className="consultar-info__buscar-wrapper">
            <input
              type="text"
              placeholder="Código o nombre de asignatura"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
            <span className="consultar-info__lupa-icono">🔍</span>
          </div>
        </div>
      </section>

      <section className="consultar-info__resultados">
        <div className="consultar-info__resultados-header">
          <h3 className="consultar-info__resultados-titulo">{plan.nombre} (v{plan.version})</h3>
        </div>
        <table className="consultar-info__tabla">
          <thead>
            <tr>
              <th>Semestre</th>
              <th>Código</th>
              <th>Asignatura</th>
              <th>Créditos</th>
              <th>Prerrequisitos</th>
            </tr>
          </thead>
          <tbody>
            {filasFiltradas.map((f) => {
              const prereqs = prerequisitosPorAsignatura[f.asignatura] || [];
              return (
                <tr key={f.id}>
                  <td>{f.semestre}</td>
                  <td className="consultar-info__tabla-codigo">{f.asignatura_codigo}</td>
                  <td>{f.asignatura_nombre}</td>
                  <td>{f.creditos}</td>
                  <td>
                    {prereqs.length === 0
                      ? 'Ninguno'
                      : prereqs.map((p) => p.asignatura_prerrequisito_codigo).join(', ')}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <div className="consultar-info__footer-tabla">
          <span className="consultar-info__contador">Mostrando {filasFiltradas.length} de {filas.length} asignaturas</span>
        </div>
      </section>
    </>
  );
}

// ==========================================
// SUB-COMPONENTE: tabla de Docentes
// ==========================================
function TablaDocentes() {
  const [docentes, setDocentes] = useState([]);
  const [busqueda, setBusqueda] = useState('');
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    obtenerDocentes().then((d) => { setDocentes(d); setCargando(false); });
  }, []);

  const filtrados = docentes.filter((d) =>
    !busqueda ||
    `${d.primer_nombre} ${d.primer_apellido}`.toLowerCase().includes(busqueda.toLowerCase()) ||
    d.codigo.toLowerCase().includes(busqueda.toLowerCase())
  );

  if (cargando) return <p style={{ padding: '1rem' }}>Cargando docentes...</p>;

  return (
    <>
      <section className="consultar-info__filtros-panel">
        <div className="consultar-info__filtro-grupo consultar-info__filtro-grupo--buscar">
          <label>Buscar docente</label>
          <div className="consultar-info__buscar-wrapper">
            <input
              type="text"
              placeholder="Código o nombre del docente"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
            <span className="consultar-info__lupa-icono">🔍</span>
          </div>
        </div>
      </section>

      <section className="consultar-info__resultados">
        <div className="consultar-info__resultados-header">
          <h3 className="consultar-info__resultados-titulo">Docentes de tu programa académico</h3>
        </div>
        <table className="consultar-info__tabla">
          <thead>
            <tr>
              <th>Código</th>
              <th>Nombre completo</th>
              <th>Correo</th>
            </tr>
          </thead>
          <tbody>
            {filtrados.map((d) => (
              <tr key={d.id}>
                <td className="consultar-info__tabla-codigo">{d.codigo}</td>
                <td>{d.primer_nombre} {d.segundo_nombre || ''} {d.primer_apellido} {d.segundo_apellido || ''}</td>
                <td>{d.correo}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="consultar-info__footer-tabla">
          <span className="consultar-info__contador">Mostrando {filtrados.length} de {docentes.length} docentes</span>
        </div>
      </section>
    </>
  );
}

// ==========================================
// SUB-COMPONENTE: tabla de Asignaturas (catálogo global)
// ==========================================
function TablaAsignaturas() {
  const [asignaturas, setAsignaturas] = useState([]);
  const [busqueda, setBusqueda] = useState('');
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    obtenerAsignaturas().then((a) => { setAsignaturas(a); setCargando(false); });
  }, []);

  const filtradas = asignaturas.filter((a) =>
    !busqueda ||
    a.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
    a.codigo.toLowerCase().includes(busqueda.toLowerCase())
  );

  if (cargando) return <p style={{ padding: '1rem' }}>Cargando asignaturas...</p>;

  return (
    <>
      <section className="consultar-info__filtros-panel">
        <div className="consultar-info__filtro-grupo consultar-info__filtro-grupo--buscar">
          <label>Buscar asignatura</label>
          <div className="consultar-info__buscar-wrapper">
            <input
              type="text"
              placeholder="Código o nombre de asignatura"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
            <span className="consultar-info__lupa-icono">🔍</span>
          </div>
        </div>
      </section>

      <section className="consultar-info__resultados">
        <div className="consultar-info__resultados-header">
          <h3 className="consultar-info__resultados-titulo">Catálogo de asignaturas (todos los programas)</h3>
        </div>
        <table className="consultar-info__tabla">
          <thead>
            <tr>
              <th>Código</th>
              <th>Nombre</th>
            </tr>
          </thead>
          <tbody>
            {filtradas.slice(0, 50).map((a) => (
              <tr key={a.id}>
                <td className="consultar-info__tabla-codigo">{a.codigo}</td>
                <td>{a.nombre}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="consultar-info__footer-tabla">
          <span className="consultar-info__contador">
            Mostrando {Math.min(filtradas.length, 50)} de {filtradas.length} asignaturas
            {filtradas.length > 50 ? ' (usa la búsqueda para acotar)' : ''}
          </span>
        </div>
      </section>
    </>
  );
}

// ==========================================
// SUB-COMPONENTE: tabla de Historial Académico
// ==========================================
function TablaHistorialAcademico() {
  const [historial, setHistorial] = useState([]);
  const [busqueda, setBusqueda] = useState('');
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    obtenerHistorialAcademico().then((h) => { setHistorial(h); setCargando(false); });
  }, []);

  const filtrado = historial.filter((h) =>
    !busqueda || h.estudiante_codigo?.toLowerCase().includes(busqueda.toLowerCase())
  );

  if (cargando) return <p style={{ padding: '1rem' }}>Cargando historial académico...</p>;

  return (
    <>
      <section className="consultar-info__filtros-panel">
        <div className="consultar-info__filtro-grupo consultar-info__filtro-grupo--buscar">
          <label>Buscar por código de estudiante</label>
          <div className="consultar-info__buscar-wrapper">
            <input
              type="text"
              placeholder="Código del estudiante"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
            <span className="consultar-info__lupa-icono">🔍</span>
          </div>
        </div>
      </section>

      <section className="consultar-info__resultados">
        <div className="consultar-info__resultados-header">
          <h3 className="consultar-info__resultados-titulo">Historial académico de tu programa</h3>
        </div>
        {historial.length === 0 ? (
          <p style={{ padding: '1rem' }}>No hay registros de historial académico todavía.</p>
        ) : (
          <table className="consultar-info__tabla">
            <thead>
              <tr>
                <th>Estudiante</th>
                <th>Asignatura</th>
                <th>Periodo</th>
                <th>Estado</th>
                <th>Nota</th>
              </tr>
            </thead>
            <tbody>
              {filtrado.map((h) => (
                <tr key={h.id}>
                  <td>{h.estudiante_codigo || h.estudiante}</td>
                  <td>{h.asignatura_codigo || h.asignatura}</td>
                  <td>{h.periodo_academico_nombre || h.periodo_academico}</td>
                  <td>
                    <span className={`consultar-info__badge-estado ${h.estado === 'aprobada' ? 'consultar-info__badge-estado--vigente' : ''}`}>
                      {ETIQUETAS_ESTADO_HISTORIAL[h.estado] || h.estado}
                    </span>
                  </td>
                  <td>{h.nota ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <div className="consultar-info__footer-tabla">
          <span className="consultar-info__contador">Mostrando {filtrado.length} de {historial.length} registros</span>
        </div>
      </section>
    </>
  );
}

// ==========================================
// VISTA PRINCIPAL
// ==========================================
export default function VistaConsultarInformacion() {
  const { usuario } = useAutenticacion();
  const [tipoInfoSeleccionado, setTipoInfoSeleccionado] = useState('plan');

  return (
    <div className="consultar-info-container">
      <header className="consultar-info__header">
        <h2 className="consultar-info__titulo-vista">Consultar Información Académica</h2>
        <p className="consultar-info__subtitulo-vista">
          Visualiza la información académica proporcionada por otras dependencias de la universidad.
        </p>
      </header>

      <div className="consultar-info__alerta">
        <span className="consultar-info__alerta-icono">i</span>
        <p className="consultar-info__alerta-texto">
          Selecciona el tipo de información que deseas consultar. Los datos mostrados corresponden a la información cargada desde los sistemas institucionales.
        </p>
      </div>

      <section className="consultar-info__selector-seccion">
        <h3 className="consultar-info__seccion-titulo">Selecciona el tipo de información</h3>
        <div className="consultar-info__grid-tarjetas">
          {TIPOS_INFO.map((tipo) => (
            <div
              key={tipo.clave}
              className={`consultar-info__tarjeta ${tipoInfoSeleccionado === tipo.clave ? 'consultar-info__tarjeta--seleccionada' : ''}`}
              onClick={() => setTipoInfoSeleccionado(tipo.clave)}
            >
              <div className="consultar-info__tarjeta-contenido">
                <h4>{tipo.titulo}</h4>
                <p>{tipo.descripcion}</p>
              </div>
              {tipoInfoSeleccionado === tipo.clave && <span className="consultar-info__tarjeta-check">✓</span>}
            </div>
          ))}
        </div>
      </section>

      {tipoInfoSeleccionado === 'plan' && <TablaPlanEstudios programaAcademicoId={usuario?.programa_academico_id} />}
      {tipoInfoSeleccionado === 'docentes' && <TablaDocentes />}
      {tipoInfoSeleccionado === 'asignaturas' && <TablaAsignaturas />}
      {tipoInfoSeleccionado === 'historial' && <TablaHistorialAcademico />}
    </div>
  );
}