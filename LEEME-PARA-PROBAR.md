# Probar Magic Mark

La versión más reciente preparada localmente es **0.1.3**.

Firefox: entra a `about:debugging#/runtime/this-firefox`, pulsa **Cargar complemento temporal** y selecciona `artifacts/magic-mark-0.1.3-firefox.zip`.

Selecciona texto y pulsa el icono o el menú contextual de Magic Mark. Recargar o salir de la página elimina sus marcas. El menú permite deshacer y borrar.

Es un paquete sin firma para pruebas: se desinstala al reiniciar Firefox. No se ha subido a GitHub ni a tiendas. Los ZIP antiguos 0.1.0 y 0.1.1 se conservan como referencia; usa 0.1.3 para estas pruebas.

El ZIP `artifacts/magic-mark-0.1.3-source.zip` contiene el código preparado para revisión y futuro repositorio público. No es el paquete que se instala en Firefox.

## Atajos opcionales desde 0.1.3

No hay combinación predeterminada: Alt+Shift+M abrió Marcadores en la prueba del usuario. Puedes seguir usando el clic secundario. Si quieres asignar una combinación propia, abre about:addons, entra a Extensiones, pulsa la rueda dentada y elige Administrar atajos de extensiones. Escoge una combinación que Firefox permita y que no uses ya. Fuente: https://support.mozilla.org/en-US/kb/manage-extension-shortcuts-firefox .

Después de cargar el ZIP 0.1.3, recarga la página de prueba. Si Firefox conserva una combinación que habías asignado, elimínala o cámbiala desde ese gestor.
