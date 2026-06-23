/**
 * Botón reutilizable. Solo presentación (sin manejo de eventos real).
 * variante: "primario" | "secundario" | "texto"
 */
function Boton({ children, variante = 'primario', tipo = 'button' }) {
  return (
    <button type={tipo} className={`boton boton--${variante}`}>
      {children}
    </button>
  );
}

export default Boton;
