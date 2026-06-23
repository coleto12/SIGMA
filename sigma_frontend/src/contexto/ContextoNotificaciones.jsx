import { createContext, useContext } from 'react';

/**
 * Contexto de notificaciones en tiempo real.
 * Pendiente de implementación: solo estructura.
 */
const ContextoNotificaciones = createContext(null);

export function useNotificaciones() {
  return useContext(ContextoNotificaciones);
}

export default ContextoNotificaciones;
