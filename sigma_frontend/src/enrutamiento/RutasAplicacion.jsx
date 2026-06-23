import { BrowserRouter, Routes, Route } from 'react-router-dom';

import DisenoPrincipal from '../componentes/diseno/DisenoPrincipal.jsx';
import RutaProtegida from './RutaProtegida.jsx';

import VistaIniciarSesion from '../vistas/autenticacion/VistaIniciarSesion.jsx';
import VistaRecuperarContrasena from '../vistas/autenticacion/VistaRecuperarContrasena.jsx';
import VistaRestablecerContrasena from '../vistas/autenticacion/VistaRestablecerContrasena.jsx';

import VistaInicio from '../vistas/inicio/VistaInicio.jsx';

import VistaListaGrupos from '../vistas/programacion-academica/grupos/VistaListaGrupos.jsx';
import VistaCrearFechasYRequisitos from "../vistas/fechas-y-requisitos/crear/VistaCrearFechasYRequisitos.jsx";
import VistaConsultarFechasYRequisitos from "../vistas/fechas-y-requisitos/consultar/VistaConsultarFechasRequisitos.jsx";
import CrearProgramacion from '../vistas/programacion-academica/crear/VistaCrearProgramacion.jsx';
import ConsultarProgramacion from '../vistas/programacion-academica/consultar/VistaConsultarProgramacion.jsx';
import PublicarInformacion from '../vistas/programacion-academica/publicar/VistaPublicarInformacion.jsx';
import VistaCargaInformacion from '../vistas/informacion-academica/carga/VistaCargaInformacion.jsx';
import VistaConsultarInformacion from '../vistas/informacion-academica/consulta/VistaConsultarInformacion.jsx';

import VistaDiligenciarFormulario from "../vistas/solicitudes/diligenciar-formulario/VIstaDiligenciarFormulario.jsx";
import VistaConsultarSolicitud from "../vistas/solicitudes/consultar-solicitud/VistaConsultarSolicitud.jsx";
import VistaValidarSolicitud from "../vistas/solicitudes/validar-solicitud/VistaValidarSolicitud.jsx";
import VistaConsultarEstadoSolicitud from "../vistas/solicitudes/consultar-estado-solicitud/VistaConsultarEstadoSolicitud.jsx";

import VistaConsultarMatriculaOficial from "../vistas/matriculas/VistaConsultarMatriculaOficial.jsx";


import VistaNotificaciones from '../vistas/notificaciones/VistaNotificaciones.jsx';

import VistaAyudaSoporte from '../vistas/ayuda/VistaAyudaSoporte.jsx';

import VistaNoEncontrado from '../vistas/error/VistaNoEncontrado.jsx';

function RutasAplicacion() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Autenticación (sin layout principal, sin protección) */}
        <Route path="/iniciar-sesion" element={<VistaIniciarSesion />} />
        <Route path="/recuperar-contrasena" element={<VistaRecuperarContrasena />} />
        <Route path="/restablecer-contrasena/:uid/:token" element={<VistaRestablecerContrasena />} />

        {/* Rutas internas: requieren sesión activa (ver RutaProtegida) */}
        <Route element={<RutaProtegida />}>
          <Route element={<DisenoPrincipal />}>
            <Route path="/" element={<VistaInicio />} />

            <Route path="/programacion-academica/grupos" element={<VistaListaGrupos />} />
            <Route path="/programacion-academica/crear" element={<CrearProgramacion />} />
            <Route path="/programacion-academica/consultar" element={<ConsultarProgramacion />} />
            <Route path="/programacion-academica/publicar" element={<PublicarInformacion />} />
            <Route path="/fechas-y-requisitos/crear" element={<VistaCrearFechasYRequisitos />} />
            <Route path="/fechas-y-requisitos/consultar" element={<VistaConsultarFechasYRequisitos />} />

            <Route path="/informacion-academica/carga" element={<VistaCargaInformacion />} />
            <Route path="/informacion-academica/consulta" element={<VistaConsultarInformacion />} />

            <Route path="/solicitudes/diligenciar-formulario" element={<VistaDiligenciarFormulario />} />
            <Route path="/solicitudes/consultar-solicitud" element={<VistaConsultarSolicitud />} />
            <Route path="/solicitudes/validar-solicitud/:id" element={<VistaValidarSolicitud />} />
            <Route path="/solicitudes/consultar-estado-solicitud" element={<VistaConsultarEstadoSolicitud />} />

            <Route path="/matriculas" element={<VistaConsultarMatriculaOficial />} />


            <Route path="/notificaciones" element={<VistaNotificaciones />} />

            <Route path="/ayuda-soporte" element={<VistaAyudaSoporte />} />
          </Route>
        </Route>

        {/* 404 */}
        <Route path="*" element={<VistaNoEncontrado />} />
      </Routes>
    </BrowserRouter>
  );
}

export default RutasAplicacion;