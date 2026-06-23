import { Outlet } from 'react-router-dom';
import BarraLateral from './BarraLateral.jsx';
import EncabezadoSuperior from './EncabezadoSuperior.jsx';
import './diseno.css';

function DisenoPrincipal() {
  return (
    <div className="diseño-principal">
      <BarraLateral />
      <div className="diseño-principal__contenido">
        <EncabezadoSuperior />
        <main className="diseño-principal__vista">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default DisenoPrincipal;
