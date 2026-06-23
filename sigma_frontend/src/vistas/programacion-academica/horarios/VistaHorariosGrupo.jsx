import TablaDatos from '../../../componentes/tablas/TablaDatos.jsx';
import '../programacion-academica.css';

/**
 * Vista de horarios de grupo (modelo "Horarios de Grupo" del backend).
 */
function VistaHorariosGrupo() {
  const columnas = ['Día', 'Hora inicio', 'Hora fin', 'Grupo', 'Salón'];
  const filas = [['Lunes', '08:00', '10:00', 'G-001', 'Bloque 7 - 203']];

  return (
    <div className="vista-programacion-academica">
      <h2>Horarios de grupo</h2>
      <p>Visualiza y administra los horarios asignados a cada grupo.</p>
      <TablaDatos columnas={columnas} filas={filas} />
    </div>
  );
}

export default VistaHorariosGrupo;
