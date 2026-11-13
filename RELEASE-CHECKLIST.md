# Preparación del lanzamiento

Estado: repositorio GitHub público creado y canales habilitados. Envío a tiendas aplazado; ver PUBLICAR.md. Las instrucciones históricas siguientes son pasos de lanzamiento, no acciones de tienda autorizadas.

## Preparado

- Licencia MIT, privacidad, instrucciones de contribución, cambios y política de seguridad.
- Plantillas de errores, mejoras y pull requests.
- CI para comprobar sintaxis, pruebas, manifiestos, lint Firefox y paquetes. Primera ejecución en GitHub aprobada: https://github.com/phyrateborquez/magic-mark/actions/runs/43522541969.
- Construcción desde versión única en package.json, ZIP reproducibles y SHA-256.
- Paquete de código fuente con lista explícita de archivos; excluye cachés, perfiles y dependencias.
- Descripción de tienda y capturas locales de pruebas.

## Antes de darlo por publicado

1. Elegir cuenta propietaria, contacto y nombre disponible. Fijar identificador Firefox antes de la primera publicación: todavía se usa magic-mark@magic-mark.local.
2. Crear repositorio público cuando el usuario lo autorice. Subir el código fuente, no artifacts, dist, node_modules ni .npm-cache. El ZIP source contiene los archivos previstos.
3. Activar el canal privado de avisos de seguridad y sustituir la nota provisional de SECURITY.md.
4. Ejecutar el CI en el repositorio real; no asumir que su configuración escrita ya equivale a una ejecución aprobada.
5. Revisar evidencia de pruebas: controles nativos de Brave completados, Firefox con confirmaciones humanas, integración Chrome/Edge automatizada y cierre manual de Chrome 123 confirmado por el usuario. Matriz prevista del MVP de escritorio cerrada; ver ROADMAP.md y los límites de cada ensayo.
6. Publicar URLs de soporte y privacidad, revisar ficha y añadir capturas adecuadas para la tienda.
7. Crear cuenta Mozilla, aceptar acuerdos y enviar ZIP a AMO para firma y revisión. Los archivos actuales siguen sin firma. No anunciar aprobación hasta recibirla.

No se requiere añadir persistencia, nube, cuentas de usuario final o telemetría para publicar.

## Comandos locales

Node.js 24 LTS y Python 3.10+:

```
npm ci --ignore-scripts
npm run verify
npm run test:firefox
```

El comando verify no instala, firma ni publica. El test Firefox abre solo un perfil de pruebas. La prueba Chromium requiere Playwright y su navegador de desarrollo; ver VALIDATION.md.

## Paquete local de revisión

Ver PUBLICAR.md. npm run verify ahora comprueba también los archivos, CRC y SHA-256 de los ZIP mediante scripts/verify_archives.py. Los textos de ficha español/inglés y notas para el revisor están en store y se incluyen en el ZIP source, sin añadirlos a los paquetes instalables.
