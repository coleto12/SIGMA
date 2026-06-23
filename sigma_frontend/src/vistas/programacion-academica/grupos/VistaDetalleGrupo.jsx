import Tarjeta from '../../../componentes/comunes/Tarjeta.jsx';
import '../programacion-academica.css';

/**
 * Vista de detalle de un grupo específico (incluye su horario y salón asignado).
 */
function VistaDetalleGrupo() {
  return (
    <div className="vista-programacion-academica">
      <h2>Detalle del grupo</h2>

      <div className="vista-programacion-academica__detalle">
        <Tarjeta titulo="Información general">
          <p>Código: G-001</p>
          <p>Asignatura: Cálculo Diferencial</p>
          <p>Docente: Carlos A. Gómez</p>
        </Tarjeta>

        <Tarjeta titulo="Horario asignado">
          <p>Lunes y miércoles, 8:00 a.m. – 10:00 a.m.</p>
          <p>Salón: Bloque 7, Aula 203</p>
        </Tarjeta>
      </div>
    </div>
  );
}

export default VistaDetalleGrupo;
