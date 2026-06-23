import CampoTexto from '../../componentes/formularios/CampoTexto.jsx';
import Boton from '../../componentes/comunes/Boton.jsx';
import './configuracion.css';

/**
 * Vista de edición del perfil del usuario autenticado
 * (relacionado con los modelos Docentes/Estudiantes/Usuarios del backend).
 */
function VistaPerfilUsuario() {
  return (
    <div className="vista-configuracion">
      <h2>Mi perfil</h2>

      <form className="vista-configuracion__formulario">
        <CampoTexto etiqueta="Nombre completo" marcadorPosicion="Nombre Apellido" />
        <CampoTexto etiqueta="Correo institucional" tipo="email" marcadorPosicion="usuario@unicartagena.edu.co" icono="correo" />
        <CampoTexto etiqueta="Nueva contraseña" tipo="password" marcadorPosicion="Dejar en blanco para no cambiar" icono="candado" />

        <Boton tipo="submit">Guardar cambios</Boton>
      </form>
    </div>
  );
}

export default VistaPerfilUsuario;
