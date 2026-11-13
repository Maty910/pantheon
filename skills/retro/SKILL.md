---
name: retro
description: Retrospectiva por sprint o entrega basada en evidencia para proponer mejoras verificables de calidad.
---

# Retro

## Alcance y evidencia

Delimitar el sprint o la entrega, el período, el baseline, el runtime y los
gates realizados cuando esa información esté disponible. Identificar las
fuentes y declarar lo desconocido, inaccesible o no ejecutado. Si falta un dato
necesario, pedir el mínimo que permita continuar o informar el límite.

Separar hechos observados, evidencia y sus límites, e hipótesis causales. No
inventar defectos, escapes, resultados, éxito ni métricas. Un escenario
`NOTRUN` no es un escape verificado.

Leer y aplicar las reglas pertinentes del repositorio destino y, cuando exista,
su mapa de gemelos; citar las fuentes sin duplicar sus reglas. No asumir que CI
u otro control existe o cubre un caso sin evidencia.

## Selección y candidatos

Seleccionar pocos escapes verificables y explicar su prioridad por consecuencia
o repetición observada, sin inventar estadísticas. Una revisión exhaustiva de
código o una lista general de refactors no es el objetivo de esta retrospectiva.

Para cada candidato, relacionar el escape y la hipótesis causal con su evidencia,
y buscar la fuente, regla o comprobación existente pertinente. Indicar si ya
cubre el caso, si queda una brecha o si no pudo determinarse. Considerar las
variantes o gemelos relevantes y los límites conocidos de CI. No proponer
duplicados cuando un control existente cubra efectivamente el caso.

Cuando corresponda a comportamiento ejecutable, proponer una comprobación
determinista del resultado observable. Para prompts, documentación o
configuración, proponer una regla o comprobación contractual apropiada, sin
fabricar tests de software. Para cada propuesta, explicar qué comprobaría,
qué no comprobaría, qué variantes deja fuera y qué evidencia falta.

## Resultado y límites

Entregar alcance, fuentes, límites, escapes verificados seleccionados, hipótesis
identificadas como tales y candidatos de mejora con su relación con controles
existentes. «No hay escapes verificados» y «evidencia insuficiente» son
resultados válidos; el primero no garantiza ausencia de defectos.

Si se propone evaluar eficacia, definir antes una comparación futura con
baseline, criterios y datos permitidos. No afirmar que una propuesta mejoró la
calidad sin observaciones reales comparables.

Retro no reemplaza una review, sus reglas de refutación ni sus gates. Tampoco
reemplaza a Athena ni exige un ejercicio o aprendizaje de Mati como gate de
calidad.

## Autoridad y privacidad

Las acciones son propuestas, no autorización para ejecutarlas. Una mutación
propuesta vuelve a Odin y sigue el protocolo aplicable: Themis, aprobación
inicial explícita de Mati, Thor, Heimdall, aprobación final de Mati, Nemesis o
N/A objetivo cuando corresponda, y Saga.

Retro no edita archivos, ejecuta tests, crea tickets, escribe en el vault o
Engram automáticamente, ni publica resultados. No crea un registro permanente
o archivo adicional por sí misma. Odin puede gestionar una síntesis sanitizada
conforme al protocolo de memoria existente, sin que esta skill conceda una
autorización nueva.

Usar únicamente fuentes y datos permitidos. No incorporar casos privados ni
publicar información sin la autorización y revisión de privacidad aplicables.
