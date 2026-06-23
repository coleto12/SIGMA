import RutasAplicacion from './enrutamiento/RutasAplicacion.jsx';
import { ProveedorAutenticacion } from './contexto/ContextoAutenticacion.jsx';

function AplicacionPrincipal() {
  return (
    <ProveedorAutenticacion>
      <RutasAplicacion />
    </ProveedorAutenticacion>
  );
}

export default AplicacionPrincipal;
