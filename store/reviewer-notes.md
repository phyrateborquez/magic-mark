# Notas preparadas para revisión

Borrador local, sin enviar. Identidad, enlaces y material editorial pendientes deben cerrarse antes del envío. El identificador Firefox todavía es provisional.

## Construcción

Código JavaScript legible, sin minificación, ofuscación ni dependencias de ejecución. Node.js 24 LTS y Python 3.10+. `npm ci --ignore-scripts` instala solo herramientas de desarrollo; `npm run verify` genera y valida los paquetes, sin firmar ni publicar. scripts/build.mjs crea los dos manifiestos a partir de la versión de package.json.

## Prueba funcional sugerida

1. Abrir una página HTTP/HTTPS ordinaria con texto seleccionable.
2. Seleccionar un párrafo y solicitar destacar mediante botón, atajo configurado por el usuario o menú contextual.
3. Repetir en otro párrafo y otra pestaña; las marcas deben ser independientes.
4. Probar deshacer y borrar desde el menú.
5. Recargar o salir del documento: las marcas desaparecen y no se recuperan al volver.
6. Formularios/editores y páginas protegidas quedan excluidos. En una página restringida se muestra un texto explicativo al pasar por el icono; no se solicita acceso amplio para evitar la restricción.

No hay cuentas, credenciales de prueba, servicios externos, compras ni funciones de pago. No se recopilan ni transmiten datos. Las selecciones solo existen como referencias Range en memoria volátil del documento.

## Permisos

- activeTab: acceso tras invocación explícita.
- scripting: ejecutar la acción solicitada.
- contextMenus: destacar, deshacer y borrar.

No hay permisos permanentes de host ni de almacenamiento. Firefox declara data_collection_permissions.required = ["none"].

## Limitaciones para informar

No incluye PDF integrado, OCR, restauración, sincronización ni acceso garantizado a marcos de otros orígenes. No se anuncia certificación universal de accesibilidad. La matriz de pruebas del MVP está cerrada según ROADMAP.md; los límites de evidencia allí registrados no se deben omitir al preparar el envío.


## English

Local draft, not submitted. Desktop MVP testing is closed with scoped evidence in ROADMAP.md; maintainer identity, URLs, final Firefox ID and editorial material remain pending. Readable JavaScript, no minification or runtime dependencies. Node.js 24 LTS and Python 3.10+: npm ci --ignore-scripts and npm run verify build and validate without signing or publishing.

Test on an ordinary HTTP/HTTPS page: select and highlight, repeat across tabs, undo and clear, then reload and navigate away. Marks must disappear. Editors and protected pages are excluded. The main-document button and frame-aware context menu have different targets; cross-origin frames may be inaccessible. No accounts, purchases, test credentials, servers or data transmission. Permissions: activeTab for user-invoked access, scripting for the requested operation, contextMenus for actions. No host or storage permissions. The current interface uses Spanish labels. See PRIVACY.md, SECURITY.md and PRODUCTION-REVIEW.md.
