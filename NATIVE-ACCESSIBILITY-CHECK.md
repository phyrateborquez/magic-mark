# Comprobación nativa y lector de pantalla

Estado: pruebas nativas de controles completadas en Brave, sin certificación exhaustiva de accesibilidad. Los bloqueos históricos de Firefox/Chrome no impidieron la prueba posterior en Brave conectado, descrita al final. El usuario confirmó el 12 de noviembre de 2026 que se anuncian correctamente Magic Mark y las opciones destacar selección, deshacer y borrar.

1. En un perfil de prueba con el paquete distribuido sin modificar, seleccionar texto y ejecutar un atajo propio previamente asignado en el navegador. Confirmar el destacado, sin escribir en formularios.
2. Seleccionar otro fragmento y pulsar el botón Magic Mark; confirmar que se conservan ambos.
3. Usar el menú contextual para destacar, deshacer y borrar. Repetir dentro de un marco del mismo origen. En un marco ajeno sin permiso, se espera rechazo, sin ampliar permisos automáticamente.
4. Con NVDA o Narrador activo, enfocar el botón y comprobar que anuncia Magic Mark. Abrir el menú y comprobar que se leen destacar selección, deshacer y borrar, y que se pueden activar con teclado.
5. Comprobar foco visible, zoom de 200% y selección en modo claro/oscuro. Los controles pertenecen al navegador; no hay paneles HTML personalizados de Magic Mark.

Hay evidencia programática de contraste 13.75:1, conservación de HTML del artículo, comandos configurables, acción instalada y ruta de frame. La lectura de los nombres está verificada mediante confirmación humana. No se especificaron navegador/versión ni lector/versión; no se inventan esos datos. La confirmación no acredita activación por teclado, foco, zoom o uso dentro de marcos, ni constituye una certificación de accesibilidad completa.

Chrome 123 se probó inicialmente con código de producción y un permiso localhost añadido solo a una copia aislada. Ese ensayo verifica APIs y funciones; el flujo nativo pendiente se cerró después por confirmación del usuario, registrada al final.

## Evidencia humana recibida

- [x] Nombre del botón Magic Mark anunciado correctamente.
- [x] Opciones destacar selección, deshacer y borrar anunciadas correctamente.
- Fuente: respuesta explícita del usuario «Sí, los nombres se anuncian correctamente», 12/11/2026.
- [x] Recorrido de controles con teclado, foco, zoom y marco del mismo origen en Brave: evidencia del agente al final. No se ejecutó un lector de pantalla durante esa sesión.

## Evidencia adicional recibida y automatizada

- [x] Menú contextual de Firefox: el usuario respondió «probe el 3 y todo bien» al paso de destacar, deshacer y borrar (12/11/2026). No indicó versión de Firefox, extensión ni si utilizó un marco; no se extrapola al caso de marcos.
- [x] Chrome for Testing 157 con Magic Mark 0.1.2: zoom real de pestaña al 100% y 200%, tres rangos conservados y rectángulos dentro del ancho visible, sin desbordamiento horizontal en la página de prueba.
- [x] El código inyectado conserva el elemento DOM enfocado durante la acción vía CDP. No acredita foco/recorrido en la barra o menú nativos.
- Capturas de viewport revisadas: artifacts/magic-mark-zoom-100.png y magic-mark-zoom-200.png. La primera captura full-page se descartó porque el controlador recortaba el ancho con zoom; se regeneró con captura del viewport. No fue necesario modificar la extensión.
- Datos: zoomAndFocus en artifacts/chrome-installed-results.json.

El recorrido nativo y menú en marcos se completaron posteriormente en Brave. Chrome 123 quedó cerrado por la confirmación humana posterior. Un atajo propio permanece como comprobación opcional si se configura; no bloquea el MVP. La prueba de Brave no sustituye la de Chrome 123.

## Resultado manual y corrección 0.1.3

El usuario informó que Alt+Shift+M abre Marcadores en su Firefox. Se retira la combinación predeterminada; no se reasigna otra potencialmente reservada. Los comandos quedan disponibles para asignación voluntaria desde el gestor del navegador. Esto no desactiva el atajo propio de Firefox.

El usuario destacó dos líneas mediante selección, clic secundario y la opción de Magic Mark: resultado correcto. Su captura muestra un destacado amarillo y el submenú con deshacer y borrar; deshacer aparece visualmente enfocado. La captura sola no prueba la activación con Enter ni el uso de un marco; la respuesta posterior del usuario sí confirma Enter. No hay pregunta del ensayo que deba deducirse del texto del artículo.

## Confirmación posterior del usuario — 12/11/2026

- [x] Al seleccionar texto y pulsar el icono de Magic Mark, lo seleccionado queda marcado.
- [x] Al enfocar deshacer último destacado y pulsar Enter, se deshace la última marca.
- Fuentes: respuestas «lo que hace esto es marcar lo seleccionado» y «deshace lo ultimo destacado», a las dos instrucciones inmediatamente anteriores.
- No se especificaron versiones de navegador/extensión. No se interpreta como prueba de atajo propio, todos los controles, marcos o Chrome 123.

## Prueba nativa del agente en Brave — 12/11/2026

El usuario cargó Magic Mark en Brave y puso en primer plano la página local `tests/native.html`. Se usó la interfaz nativa del navegador conectado, sin añadir permisos al paquete ni ejecutar las acciones mediante CDP. La versión exacta de Brave no se obtuvo; el directorio preparado corresponde a Magic Mark 0.1.3.

- [x] Selección con ratón y clic en el botón: primera marca amarilla.
- [x] Segunda selección, Shift+F10, submenú Magic Mark, flecha derecha y Enter: segunda marca; ambas visibles al quitar la selección azul.
- [x] Menú con flechas y Enter: deshacer quitó únicamente la segunda marca y borrar quitó la restante.
- [x] Marco local del mismo origen: selección y destacado mediante menú, tanto con Enter como con clic; deshacer quitó la marca. Se repitió el destacado y se enfocó explícitamente borrar con flecha derecha/abajo; Enter quitó la marca. El foco de borrar se observó en la captura nativa.
- [x] Zoom real al 200%, confirmado por el indicador del navegador. Alt+Shift+T enfocó la barra; Tab alcanzó Magic Mark con contorno visible y Enter destacó el texto seleccionado. Se observó el resultado amarillo al quitar la selección azul.
- [x] Restauración del zoom inicial al 90% al finalizar. Recarga final realizada; el marco visible quedó sin marcas.

Capturas de la página, sin la barra de pestañas del usuario: `artifacts/brave-native-frame.jpg` y `artifacts/brave-native-zoom-200.jpg`. Son evidencia local de pruebas, no capturas finales de tienda; se excluyen de los ZIP distribuidos. No se cambió código de producción durante esta sesión.

Alcance: controles nativos de Brave y un marco del mismo origen, página principal clara y marco oscuro. No se prueba con ello Chrome 123, Android, todas las tecnologías de asistencia ni un atajo personalizado. Los nombres leídos por lector conservan la confirmación humana anterior y sus limitaciones.

## Cierre humano de Chrome 123 — 12/11/2026

Después de que la herramienta detuviera el control de Chrome 123 por no poder determinar la URL con suficiente confianza, el usuario confirmó: «yo hice todas las pruebas en Chrome 123, así que avanza nomás».

Se acepta esta respuesta como cierre manual de las pruebas pendientes de Chrome 123, incluido el flujo nativo activeTab del paquete original que se estaba verificando. No se presenta como prueba ejecutada u observada por el agente. El usuario no aportó capturas, número de parche, versión de extensión ni resultados individuales; no se inventan esos datos ni se atribuye la confirmación a la copia con permisos localhost usada en el ensayo automatizado anterior.

Con esta confirmación se cierra la matriz prevista para el MVP de escritorio. El atajo personalizado es opcional y no se afirma que se haya asignado. Android y una certificación exhaustiva de accesibilidad quedan fuera del alcance probado. GitHub, firma y tiendas siguen pendientes.


Nota de conservación / Retention note (13/11/2026): los diagnósticos, perfiles y navegadores locales de artifacts se eliminaron para conservar solo el repositorio fuente. Sus rutas en este documento son referencias históricas, no archivos distribuidos. Las capturas seleccionadas permanecen en store/screenshots. / Local diagnostics, profiles and browsers in artifacts were removed to retain only source repository files. Paths in this document are historical references, not distributed files. Selected screenshots remain in store/screenshots.
