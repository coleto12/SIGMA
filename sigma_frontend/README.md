# SIGMA — Frontend

Sistema Integrado de Gestión de Matrícula Académica — Universidad de Cartagena.

Este repositorio contiene **únicamente las vistas (UI)** del frontend, construidas con **React + Vite**, sin lógica de negocio ni conexión real a la API. Los nombres de carpetas y archivos están en español para mantener consistencia con el resto del proyecto.

## Tecnologías

- React 18
- Vite
- React Router DOM (enrutamiento entre vistas)
- CSS plano (sin frameworks de UI)

## Estructura de carpetas

```
sigma-frontend/
├── public/
│   └── escudo.svg
├── src/
│   ├── activos/                  # Recursos estáticos
│   │   ├── estilos/               # CSS global y variables de tema
│   │   ├── iconos/
│   │   └── imagenes/
│   │
│   ├── componentes/              # Componentes reutilizables (presentacionales)
│   │   ├── diseño/                 # Layout: BarraLateral, EncabezadoSuperior, DisenoPrincipal
│   │   ├── comunes/                # Boton, Tarjeta, Insignia, EnlaceNavegacion, CargandoIndicador
│   │   ├── formularios/            # CampoTexto, ListaDesplegable, CasillaVerificacion, ZonaArrastrarArchivo
│   │   └── tablas/                 # TablaDatos, PaginacionTabla
│   │
│   ├── contexto/                  # Contextos de React (estado global de UI)
│   │   ├── ContextoAutenticacion.jsx
│   │   └── ContextoNotificaciones.jsx
│   │
│   ├── enrutamiento/
│   │   └── RutasAplicacion.jsx    # Definición de todas las rutas de la app
│   │
│   ├── ganchos/                   # Hooks personalizados (placeholders)
│   │   ├── usarFormulario.js
│   │   └── usarPeticionApi.js
│   │
│   ├── servicios/                 # Capa de acceso a la API (placeholders),
│   │   │                          # un servicio por cada app del backend
│   │   ├── clienteApi.js
│   │   ├── servicioAutenticacion.js   → app "usuarios"
│   │   ├── servicioAcademico.js       → app "academico"
│   │   ├── servicioMatricula.js       → app "matricula"
│   │   ├── servicioProgramacion.js    → app "programacion"
│   │   ├── servicioInstitucional.js   → app "institucional"
│   │   └── servicioNotificaciones.js  → app "notificaciones"
│   │
│   ├── utilidades/
│   │   ├── formato.js
│   │   └── validaciones.js
│   │
│   ├── vistas/                    # Una carpeta por módulo del sidebar
│   │   ├── autenticacion/           # Iniciar sesión, recuperar contraseña
│   │   ├── inicio/
│   │   ├── programacion-academica/
│   │   │   ├── grupos/
│   │   │   ├── horarios/
│   │   │   └── salones/
│   │   ├── fechas-y-tiqueteo/
│   │   ├── informacion-academica/
│   │   │   ├── carga/               # Mockup: Carga de Información Académica
│   │   │   └── consulta/            # Mockup: Consultar Información Académica
│   │   ├── solicitudes/
│   │   ├── estado-solicitud/
│   │   ├── mi-matricula/
│   │   ├── reportes/
│   │   ├── configuracion/
│   │   ├── notificaciones/
│   │   └── error/                   # Vista 404
│   │
│   ├── AplicacionPrincipal.jsx
│   └── principal.jsx               # Punto de entrada (equivalente a main.jsx)
│
├── index.html
├── package.json
├── vite.config.js
├── .env.example
└── .gitignore
```

## Relación con el backend (SIGMA_BACKEND)

Cada servicio en `src/servicios/` corresponde directamente a una app Django del backend:

| App del backend  | Servicio del frontend         | Módulos del sidebar relacionados                  |
|-------------------|-------------------------------|----------------------------------------------------|
| `usuarios`        | `servicioAutenticacion.js`    | Iniciar sesión, Configuración                       |
| `academico`       | `servicioAcademico.js`        | Información Académica (Carga / Consulta)            |
| `matricula`       | `servicioMatricula.js`        | Mi Matrícula, Solicitudes, Estado de Solicitud       |
| `programacion`    | `servicioProgramacion.js`     | Programación Académica (Grupos, Horarios, Salones), Fechas y Tiqueteo |
| `institucional`   | `servicioInstitucional.js`    | Filtros de Programa académico / Campus / Facultad   |
| `notificaciones`  | `servicioNotificaciones.js`   | Notificaciones                                       |

## Instalación

```bash
npm install
npm run dev
```

## Estado actual

Este frontend contiene **solo vistas estáticas** (sin llamadas reales a la API, sin validaciones, sin manejo de estado de autenticación). Los archivos en `servicios/`, `contexto/` y `ganchos/` están dejados como estructura base para la siguiente etapa de implementación funcional.
