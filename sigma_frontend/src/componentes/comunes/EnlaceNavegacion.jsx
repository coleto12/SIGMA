import { NavLink } from 'react-router-dom';

/**
 * Ítem de navegación reutilizable para la barra lateral.
 */
function EnlaceNavegacion({ etiqueta, ruta, icono }) {
  return (
    <NavLink
      to={ruta}
      className={({ isActive }) =>
        isActive ? 'enlace-navegacion enlace-navegacion--activo' : 'enlace-navegacion'
      }
    >
      <span className={`enlace-navegacion__icono enlace-navegacion__icono--${icono}`} />
      <span>{etiqueta}</span>
    </NavLink>
  );
}

export default EnlaceNavegacion;
