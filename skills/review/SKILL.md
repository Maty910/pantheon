---
name: review
description: Review read-only de cambios con evidencia causal y refutación independiente.
---

# Review

## Preparación

Identificar el cambio, sus límites, riesgos declarados y evidencia disponible.
Leer las reglas de revisión y el mapa de gemelos del repositorio destino cuando
existan y sean accesibles; aplicar sus reglas sin copiarlas aquí. Registrar
fuentes, ausencias, permisos y límites de evidencia. No inventar un mapa ni
suponer que un control de CI existe o cubre un caso sin evidencia.

Declarar runtime, roles y modelos realmente usados, sus capacidades y permisos.
No asignar modelos por defecto ni sustituir automáticamente un rol no disponible.
Si falta independencia, contexto o permiso necesarios, declarar la revisión
afectada como bloqueada o inconclusa; no simular que ocurrió.

Informar archivos y líneas añadidas y eliminadas del cambio, además de coste
real si está disponible; si no, indicar que es desconocido. Si el cambio supera
400 líneas añadidas más eliminadas o supera 10 archivos, dividir la revisión por
áreas coherentes y mantener una pasada de integración entre áreas. Esta regla
es una heurística de organización, no una clasificación automática de riesgo.

## Revisión

En modo normal, un revisor inspecciona el cambio y sus conexiones relevantes.
Para cambios declarados de riesgo o críticos, el modo adversarial utiliza dos
jueces independientes en lugar del revisor normal para ese objetivo; no añade
una tercera revisión normal. Ambos registran sus conclusiones y desacuerdos.
La clasificación de riesgo proviene del contexto y las reglas aplicables; no
deducirla únicamente del tamaño. Los jueces no sustituyen al refutador.

Seguir valores relevantes desde su origen hasta su consumo: documentar unidades,
transformaciones y supuestos, y contrastar los extremos causales con archivo y
línea. Aplicar el mapa de gemelos y revisar las contrapartes pertinentes.
Indicar los límites cuando no sea posible seguir una cadena.

Proponer hallazgos sustentados en comportamiento y consecuencia observable.
Para cada uno, indicar consecuencia si fuera cierto, gravedad según esa
consecuencia —no según probabilidad— y evidencia con archivo y línea en ambos
extremos relevantes de la cadena causal. Si falta evidencia, no presentarlo como
hecho confirmado.

Excluir observaciones meramente de estilo o nombres, endurecimiento
especulativo y controles que estén efectivamente cubiertos por CI, salvo que
una regla aplicable o evidencia muestre un problema conductual no cubierto.
Una revisión sin hallazgos es un resultado válido, no una garantía de ausencia
de defectos.

## Refutación

Por cada candidato que bloquearía por su consecuencia, un refutador independiente,
en contexto separado, intenta desmentirlo con la evidencia accesible. Registrar:

- `corroborado`: sobrevive al intento de refutación con evidencia suficiente;
- `refutado`: la evidencia desmiente el candidato;
- `latente`: el riesgo depende de una condición no establecida;
- `inconcluso`: no alcanza la evidencia o capacidad para decidir.

Solo `corroborado` bloquea por ese hallazgo. No publicar el hallazgo refutado
como resultado. Comunicar los límites relevantes de los latentes e inconclusos
sin presentarlos como defectos confirmados. Si no puede realizarse la refutación
independiente, no afirmar corroboración.

Esta regla no elimina ni sustituye gates independientes de autorización,
evidencia o alcance. Una revisión no autoriza cambios y no reemplaza el gate
técnico de Heimdall ni la aprobación final de Mati. Odin coordina en modo
solo lectura según el protocolo aplicable.

## Resultado y medición

Entregar alcance, fuentes, tamaño, coste conocido o desconocido, roles y modelos
reales, modo, límites y hallazgos publicables con evidencia y veredicto.
Identificar áreas no revisadas y desacuerdos no resueltos. No inferir cobertura,
eficacia o paridad entre runtimes a partir de una sola ejecución.

La mejora de calidad requiere comparación antes/después con casos y criterios
definidos, datos permitidos y observaciones reales. Sin suite o baseline
adecuados, declarar que la eficacia no está medida. No importar casos privados
ni publicar información, historial o resultados sin autorización y revisión
de privacidad aplicables.
