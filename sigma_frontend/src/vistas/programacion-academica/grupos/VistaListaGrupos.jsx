import TablaDatos from '../../../componentes/tablas/TablaDatos.jsx';
import PaginacionTabla from '../../../componentes/tablas/PaginacionTabla.jsx';
import Insignia from '../../../componentes/comunes/Insignia.jsx';
import Boton from '../../../componentes/comunes/Boton.jsx';
import '../programacion-academica.css';

/**
 * Vista de listado de grupos (Programación Académica).
 * Corresponde al modelo "Grupos" del backend.
 */
function VistaListaGrupos() {
  const columnas = ['Código', 'Asignatura', 'Docente', 'Cupos', 'Periodo', 'Estado'];
  const filas = [
    ['G-001', 'Cálculo Diferencial', 'Carlos A. Gómez', '35/40', '2026-1', <Insignia texto="Abierto" estado="exito" key="1" />],
  ];

  return (
    <div className="vista-programacion-academica">
      <div className="vista-programacion-academica__encabezado">
        <h2>Grupos</h2>
        <Boton>+ Nuevo grupo</Boton>
      </div>
      <p>Consulta y administra los grupos programados por periodo académico.</p>

      <TablaDatos columnas={columnas} filas={filas} />
      <PaginacionTabla paginaActual={1} totalPaginas={5} />
    </div>
  );
}

export default VistaListaGrupos;
