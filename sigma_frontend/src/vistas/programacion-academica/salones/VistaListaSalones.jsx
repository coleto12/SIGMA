import TablaDatos from '../../../componentes/tablas/TablaDatos.jsx';
import '../programacion-academica.css';

/**
 * Vista de listado de salones (modelo "Salones" del backend).
 */
function VistaListaSalones() {
  const columnas = ['Código', 'Bloque', 'Capacidad', 'Tipo', 'Campus'];
  const filas = [['203', 'Bloque 7', '40', 'Aula teórica', 'Piedra de Bolívar']];

  return (
    <div className="vista-programacion-academica">
      <h2>Salones</h2>
      <p>Consulta los salones disponibles por campus.</p>
      <TablaDatos columnas={columnas} filas={filas} />
    </div>
  );
}

export default VistaListaSalones;
