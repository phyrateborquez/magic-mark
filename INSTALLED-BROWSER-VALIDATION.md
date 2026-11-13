# Integración instalada: Edge 157

Magic Mark 0.1.2, Edge 157.0.4341.46 en Windows, perfil temporal separado, modo headless y página servida únicamente en localhost. Código de producción sin cambios en esta etapa.

## Comprobaciones que pasaron

- Carga del paquete Chromium y arranque de su service worker.
- Acción de la extensión instalada mediante CDP Extensions.triggerAction, con el destino de tipo tab correcto. Se ejercita activeTab, onClicked y scripting.executeScript; no se inyecta una copia del núcleo desde el controlador.
- Dos destacados en la misma página.
- Deshacer y borrar mediante la función run del fondo instalado, aprovechando el permiso concedido por la acción. No se presenta como prueba de menú contextual nativo o pulsación física.
- Marco del mismo origen: ruta con frameId correcto y documento principal sin alteraciones. Se usa el fondo instalado, no un clic de menú contextual.
- Dos pestañas con la misma URL mantienen estados independientes.
- Recarga y cierre/nueva pestaña eliminan o no recuperan las marcas.
- Captura artifacts/magic-mark-chromium-installed.png revisada visualmente.

Datos: artifacts/edge-installed-results.json. La instalación usa el paquete generado desde extension/background.js, sin añadir permisos al manifiesto.

## Herramientas y reproducción

Playwright Python y Edge instalado en la ruta Windows del script. Ejecutar `npm run test:edge:installed` después de `npm run verify`. Se habilita --enable-unsafe-extension-debugging exclusivamente en el navegador de prueba con perfil temporal; no se cambia la configuración del Edge habitual.

El Chromium 145 del entorno no implementa Extensions.triggerAction; por eso la prueba instalada se realizó con Edge 157. Eso no prueba el producto Chrome ni su versión mínima. La documentación del método experimental está en https://chromedevtools.github.io/devtools-protocol/tot/Extensions/ .

## Límites y ensayos inconclusos

- El control visual nativo de Windows continúa bloqueado para Firefox por la política de URLs de esa herramienta. No se afirma que estos ensayos sean clics o teclas físicos.
- No se ha validado Chrome como producto, versiones mínimas, lectores de pantalla, marcos de otros orígenes ni menú contextual nativo completo.
- Se intentó detener explícitamente el worker con CDP ServiceWorker.stopAllWorkers para comprobar la reactivación. La sonda no terminó y fue interrumpida; no se declara ese caso aprobado ni se infiere un fallo de Magic Mark. La sonda se retiró del ensayo normal para no dejar una prueba que pueda quedar bloqueada. El ciclo de suspensión/reactivación sigue pendiente de una prueba adecuada.
- Firefox: se intentaron el comando de historial y SessionStore desde el controlador. El mecanismo de restauración no estuvo disponible para el ensayo. Nueva pestaña limpia y navegación atrás sí están verificadas; deshacer cierre desde historial no.
- Las páginas públicas pueden agotar el tiempo de carga. El último ensayo volvió a aprobar Example.com y Wikipedia, mientras MDN agotó el tiempo; MDN había pasado en ejecuciones anteriores. Se conservan estados separados, sin transformar un timeout en un resultado funcional positivo.

El proyecto continúa local, sin cuenta nueva, publicación, firma ni envío a tiendas. No fue necesario modificar la extensión instalada para estos avances.

## Ampliación del 12 de noviembre de 2026

Chrome for Testing oficial 157.0.8103.78 pasó acción instalada con activeTab, deshacer/borrar desde fondo, marcos del mismo origen, aislamiento y recarga. Un iframe localhost, ajeno al padre 127.0.0.1, quedó excluido de inyección y sin marcas. Los datos están en artifacts/chrome-installed-results.json; no son una prueba de clic físico.

El caso de ciclo de vida ahora está confirmado: se asignó un nonce solo al global del worker de prueba; se cerró su destino, desapareció de la lista, las marcas se mantuvieron y la nueva acción creó otro contexto sin el nonce. El identificador de destino puede reutilizarse y el evento close de Playwright no se observó; por eso se verifica la pérdida del global, no se infiere por el ID. Una conexión DevTools nueva evita usar el contexto destruido. Es código exclusivo del controlador, no de Magic Mark.

Chrome for Testing 123.0.6312.122 pasó funciones y APIs con un permiso localhost añadido solo a una copia dentro del perfil de prueba. Ese ensayo no demuestra activeTab nativo. Posteriormente, el usuario confirmó haber realizado todas las pruebas pendientes en Chrome 123: se acepta como cierre manual, separado del ensayo automatizado; ver NATIVE-ACCESSIBILITY-CHECK.md. Firefox 140.0 pasó el paquete y comandos configurados; el informe ahora detecta la versión real, sin el valor 159 que el controlador anterior tenía fijo. Los perfiles antiguos solo visitaron contenido local.

La restauración de Firefox se resolvió usando la ruta moz-src del SessionStore del navegador actual, con fallback para Firefox 140. Pasó en ambas versiones: la pestaña reabierta tenía cero destacados. Los estados inconclusos descritos antes se conservan como historia de ensayos y quedan sustituidos por estos resultados concretos.

La comparación A/B repetida está en AB-RESOURCE-VALIDATION.md. Permanecen las comprobaciones nativas/lector detalladas en NATIVE-ACCESSIBILITY-CHECK.md. No se anuncia certificación universal de accesibilidad ni compatibilidad con todos los navegadores/versiones.

## Zoom y foco — 12/11/2026

Chrome 157 pasó con zoom real de pestaña 1 y 2: tres marcas se conservaron y sus rectángulos permanecieron dentro del ancho visible. Se revisó la captura de viewport al 200%. La acción inyectada conservó el elemento DOM enfocado; no se afirma verificación de foco de controles nativos. El ensayo incluyó nuevamente la reactivación del worker, marcos, aislamiento y recarga, todos aprobados. Reproducir: python scripts/test_chromium_installed.py --chrome --lifecycle --zoom.

El usuario confirmó las tres acciones del menú contextual en Firefox. El uso dentro de un marco no fue explícito y permanece pendiente.


Nota de conservación / Retention note (13/11/2026): los diagnósticos, perfiles y navegadores locales de artifacts se eliminaron para conservar solo el repositorio fuente. Sus rutas en este documento son referencias históricas, no archivos distribuidos. Las capturas seleccionadas permanecen en store/screenshots. / Local diagnostics, profiles and browsers in artifacts were removed to retain only source repository files. Paths in this document are historical references, not distributed files. Selected screenshots remain in store/screenshots.
