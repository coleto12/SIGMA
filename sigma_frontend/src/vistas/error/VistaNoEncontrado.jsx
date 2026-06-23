import Boton from '../../componentes/comunes/Boton.jsx';
import './error.css';

/**
 * Vista de error 404 — ruta no encontrada.
 */
function VistaNoEncontrado() {
  return (
    <div className="vista-error">
      <h1>404</h1>
      <p>La página que buscas no existe o fue movida.</p>
      <Boton>Volver al inicio</Boton>
    </div>
  );
}

export default VistaNoEncontrado;
