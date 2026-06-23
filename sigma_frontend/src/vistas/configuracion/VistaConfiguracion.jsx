import Tarjeta from '../../componentes/comunes/Tarjeta.jsx';
import './configuracion.css';

/**
 * Vista de Configuración general del sistema
 * (preferencias, roles visibles, datos institucionales).
 */
function VistaConfiguracion() {
  return (
    <div className="vista-configuracion">
      <h2>Configuración</h2>

      <div className="vista-configuracion__tarjetas">
        <Tarjeta titulo="Perfil">Datos personales y credenciales de acceso.</Tarjeta>
        <Tarjeta titulo="Notificaciones">Preferencias de notificaciones por correo y en plataforma.</Tarjeta>
        <Tarjeta titulo="Roles y permisos">Visualiza el rol asignado dentro del sistema.</Tarjeta>
      </div>
    </div>
  );
}

export default VistaConfiguracion;
