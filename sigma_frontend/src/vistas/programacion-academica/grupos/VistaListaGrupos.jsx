import React, { useEffect, useState } from 'react';
import { useAutenticacion } from '../../../contexto/ContextoAutenticacion.jsx';
import { obtenerPlanVigente, obtenerAsignaturasDelPlan } from '../../../servicios/servicioAcademico.js';
import { obtenerGrupos, obtenerHorarios } from '../../../servicios/servicioProgramacion.js';
import '../programacion-academica.css';

const DIAS_ABREVIADOS = {
  lunes: 'Lun', martes: 'Mar', miercoles: 'Mié',
  jueves: 'Jue', viernes: 'Vie', sabado: 'Sáb',
};

function formatearHorarios(horarios) {
  if (!horarios || horarios.length === 0) return 'Sin horario definido';
  return horarios
    .map((h) => `${DIAS_ABREVIADOS[h.dia_semana] || h.dia_semana} ${h.hora_inicio}-${h.hora_fin} (${h.salon_nombre})`)
    .join(', ');
}

/**
 * Vista de consulta de oferta académica (CU06 - Consultar Programación
 * Académica), para el Estudiante. Es de solo lectura: el backend ya
 * filtra los grupos a solo los de programaciones publicadas y los del
 * propio plan de estudios del estudiante.
 */
function VistaListaGrupos() {
  const { usuario } = useAutenticacion();
  const [grupos, setGrupos] = useState([]);
  const [horariosPorGrupo, setHorariosPorGrupo] = useState({});
  const [semestrePorAsignaturaId, setSemestrePorAsignaturaId] = useState({});
  const [semestreSeleccionado, setSemestreSeleccionado] = useState('todos');
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function cargar() {
      setCargando(true);
      setError('');
      try {
        const [listaGrupos, plan] = await Promise.all([
          obtenerGrupos(),
          obtenerPlanVigente(usuario.programa_academico_id),
        ]);
        setGrupos(listaGrupos);

        const entradasHorarios = await Promise.all(
          listaGrupos.map((g) => obtenerHorarios(g.id).then((h) => [g.id, h]))
        );
        setHorariosPorGrupo(Object.fromEntries(entradasHorarios));

        if (plan) {
          const filasPlan = await obtenerAsignaturasDelPlan(plan.id);
          const mapaSemestre = {};
          filasPlan.forEach((fila) => { mapaSemestre[fila.asignatura] = fila.semestre; });
          setSemestrePorAsignaturaId(mapaSemestre);
        }
      } catch {
        setError('No se pudo cargar la oferta académica disponible.');
      } finally {
        setCargando(false);
      }
    }
    cargar();
  }, [usuario]);

  const semestresDisponibles = [...new Set(Object.values(semestrePorAsignaturaId))].sort((a, b) => a - b);
  const gruposFiltrados = semestreSeleccionado === 'todos'
    ? grupos
    : grupos.filter((g) => semestrePorAsignaturaId[g.asignatura] === Number(semestreSeleccionado));

  const gruposPorSemestre = {};
  gruposFiltrados.forEach((grupo) => {
    const semestre = semestrePorAsignaturaId[grupo.asignatura] ?? 'Sin semestre asignado';
    if (!gruposPorSemestre[semestre]) gruposPorSemestre[semestre] = [];
    gruposPorSemestre[semestre].push(grupo);
  });
  const semestresOrdenados = Object.keys(gruposPorSemestre).sort((a, b) => {
    if (a === 'Sin semestre asignado') return 1;
    if (b === 'Sin semestre asignado') return -1;
    return Number(a) - Number(b);
  });

  return (
    <div className="vista-programacion-academica">
      <div className="vista-programacion-academica__encabezado">
        <h2>Oferta Académica</h2>
      </div>
      <p>Consulta los grupos y horarios disponibles en el periodo vigente.</p>

      <div style={{ margin: '0.75rem 0' }}>
        <label style={{ fontSize: '0.85rem', fontWeight: 600, marginRight: '0.5rem' }}>Filtrar por semestre:</label>
        <select value={semestreSeleccionado} onChange={(e) => setSemestreSeleccionado(e.target.value)}>
          <option value="todos">Todos los semestres</option>
          {semestresDisponibles.map((s) => (
            <option key={s} value={s}>{s}° semestre</option>
          ))}
        </select>
      </div>

      {error && (
        <div className="sigma-form-card" style={{ backgroundColor: '#fbe9e9' }}>
          <p style={{ color: '#c62828', margin: 0 }}>{error}</p>
        </div>
      )}

      {cargando ? (
        <p>Cargando oferta académica...</p>
      ) : grupos.length === 0 ? (
        <p>No hay grupos disponibles en este momento.</p>
      ) : (
        semestresOrdenados.map((semestre) => (
          <div key={semestre} className="sigma-form-card no-padding" style={{ marginBottom: '1.25rem' }}>
            <div className="card-padding-title">
              <h4 className="form-section-title font-bold">
                {semestre === 'Sin semestre asignado' ? semestre : `${semestre}° Semestre`}
              </h4>
            </div>
            <table className="sigma-table">
              <thead>
                <tr>
                  <th>Asignatura</th>
                  <th>Código</th>
                  <th>Grupo</th>
                  <th>Docente</th>
                  <th>Horario</th>
                  <th>Cupo disponible</th>
                </tr>
              </thead>
              <tbody>
                {gruposPorSemestre[semestre].map((grupo) => (
                  <tr key={grupo.id}>
                    <td><strong>{grupo.asignatura_nombre}</strong></td>
                    <td className="text-muted-dark">{grupo.asignatura_codigo}</td>
                    <td>{grupo.nombre}</td>
                    <td>{grupo.docente_nombre}</td>
                    <td className="text-muted-dark" style={{ fontSize: '0.8rem' }}>
                      {formatearHorarios(horariosPorGrupo[grupo.id])}
                    </td>
                    <td>
                      <span className={`badge ${grupo.cupo_disponible > 0 ? 'badge-success' : 'badge-danger'}`}>
                        {grupo.cupo_disponible > 0 ? `${grupo.cupo_disponible} disponibles` : 'Sin cupo'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))
      )}
    </div>
  );
}

export default VistaListaGrupos;