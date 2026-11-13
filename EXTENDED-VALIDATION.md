# Validación ampliada — 0.1.2

Firefox 159.0.1 en perfil aislado, extensión instalada temporalmente. El controlador selecciona texto y activa el evento del comando registrado por Firefox; no se presenta como clic/teclado físico de Windows.

## Comprobado

- Tres páginas públicas: Example.com, MDN Web/API/Range y Wikipedia Web_browser. Se destacó un párrafo real en cada una sin iniciar sesión. Solo se registran URL pública, cantidad de caracteres y estado; no se archiva el texto seleccionado.
- Política CSP local default-src/style-src/script-src 'none': el estilo de la página se bloquea, el destacado de la extensión se ve. Captura artifacts/magic-mark-strict-csp.png revisada visualmente.
- Selección entre párrafos y selección con formato: funcionamiento correcto.
- Selección que cruza un editor: excluida.
- Cambio ajeno al párrafo marcado: la marca se conserva. Reemplazo del párrafo: la marca anterior queda vacía y se depura al pedir una nueva marca, sin restauración automática ni observadores.
- Selección en iframe del mismo origen: el comando del documento principal no pinta incorrectamente el padre. No se ha validado el menú contextual de marcos externos.
- Contraste calculado de los colores fijos: 13.75:1. El body del artículo conserva exactamente su HTML tras destacar. Esto no equivale a validación completa de accesibilidad o lector de pantalla.
- Regresión habitual: dos marcas simultáneas, aislamiento de pestañas, recarga, navegación atrás y exclusión de editor.
- Deshacer y borrar: comandos registrados ejecutados correctamente en una copia de prueba con atajos temporales U/L. Solo se modifica la asignación de atajos del manifiesto de esa copia dentro del perfil aislado; el código de producción permanece idéntico y el paquete distribuido mantiene sus atajos opcionales sin asignar.
- Chromium 145: carga de worker y ensayo separado del núcleo. Posteriormente Edge 157 pasó acción instalada y rutas de fondo: ver INSTALLED-BROWSER-VALIDATION.md, sin afirmar UI física completa.

## Corrección encontrada

El primer ajuste de limpieza utilizó el iterador nativo de Highlight. Firefox devuelve 'Xray wrapping of iterators not supported' entre ejecuciones; forEach tampoco permitió acceder a los rangos. La implementación final mantiene un array pequeño con referencias a los mismos Range, sin duplicar texto. Deshacer tampoco enumera el Highlight nativo. La regresión real de dos marcas pasó tras la corrección y se añadió una prueba que simula la restricción del navegador.

Diez pruebas locales pasan, junto con web-ext lint sin errores/avisos/advertencias. La prueba dinámica exige tanto un solo rango retenido como texto no vacío, para evitar confundir una marca anterior vacía con una nueva marca válida.

## Pendiente

El controlador no expuso undoCloseTab; restaurar desde historial de pestañas cerradas queda sin verificar. No se anuncian lector de pantalla, interacción física nativa completa, versiones mínimas comprobadas ni integración completa Chrome/Edge. La medición multiproceso anterior de RESOURCE-USAGE.md corresponde a 0.1.1 y no se reetiqueta como medición de 0.1.2.

Reproducir: npm run verify; npm run test:firefox; npm run test:firefox:extended; npm run test:firefox:commands. Resultados ampliados: artifacts/firefox-extended-results.json. Los ensayos requieren procesos y conexiones locales autorizados; la prueba extendida navega a las tres páginas públicas indicadas.

Actualización 12/11: SessionStore restauró la pestaña sin marcas en Firefox 140 y 159. El pendiente anterior de restauración quedó resuelto. Para la ampliación Chrome/Edge y las limitaciones de versiones mínimas, ver INSTALLED-BROWSER-VALIDATION.md.


Nota de conservación / Retention note (13/11/2026): los diagnósticos, perfiles y navegadores locales de artifacts se eliminaron para conservar solo el repositorio fuente. Sus rutas en este documento son referencias históricas, no archivos distribuidos. Las capturas seleccionadas permanecen en store/screenshots. / Local diagnostics, profiles and browsers in artifacts were removed to retain only source repository files. Paths in this document are historical references, not distributed files. Selected screenshots remain in store/screenshots.
