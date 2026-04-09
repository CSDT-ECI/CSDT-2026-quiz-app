# 🧪 Bitácora de laboratorio

## Vibe Coding vs Spec-Driven Development

---

## 🚧 Desarrollo del laboratorio

Durante el laboratorio construimos una **calculadora de huella de carbono en frontend**, trabajando con dos enfoques distintos de desarrollo asistido por IA. La experiencia estuvo dividida en fases que evidencian cómo cambia completamente el resultado dependiendo de cómo se interactúa con la IA.

### 🟥 Fase 1: Vibe Coding — rapidez sin control

En la primera fase comenzamos con un enfoque de *Vibe Coding*, es decir, interactuar con la IA usando instrucciones vagas, sin definir arquitectura ni requisitos claros. El primer prompt fue deliberadamente ambiguo: pedir una página “bonita” que calcule la huella de carbono.

El resultado inicial fue engañosamente bueno. La IA generó una interfaz funcional en muy poco tiempo, lo que da una sensación de eficiencia y facilidad. Sin embargo, este “éxito” inicial ocultaba un problema: no había ningún control sobre cómo estaba construido el sistema.

Cuando empezamos a pedir cambios más complejos (agregar una tabla de resultados, una gráfica interactiva, estilos dinámicos y exportación a PDF) el sistema comenzó a degradarse. La IA empezó a tomar decisiones implícitas, como incluir librerías externas sin justificación clara, y el código creció de manera desorganizada.

El punto crítico llegó cuando se solicitó un nuevo cambio aparentemente simple: eliminar la gráfica, simplificar el diseño y modificar la lógica de cálculo. En ese momento, el sistema perdió coherencia. Se rompieron funcionalidades anteriores, partes útiles desaparecieron y el código se volvió difícil de entender. Aquí se hizo evidente el llamado **“efecto mariposa”**: pequeños cambios en los prompts generan impactos grandes e impredecibles en el sistema.

---

### 🟦 Fase 2: Spec-Driven Development — control desde el diseño

En la segunda fase reiniciamos el proceso, pero esta vez con un enfoque estructurado. En lugar de pedir directamente código, definimos primero un conjunto de especificaciones claras: el rol de la IA, las tecnologías permitidas, restricciones arquitectónicas y una historia de usuario concreta.

Este cambio obligó a pensar el problema antes de implementarlo. Como resultado, la IA generó un código mucho más organizado, sin dependencias innecesarias y con una separación clara entre estructura, estilos y lógica.

Aunque el inicio fue más lento, el comportamiento del sistema fue mucho más estable. Al agregar nuevas funcionalidades mediante historias de usuario, como un modo oscuro, el sistema creció de forma incremental sin romper lo anterior. A diferencia de la fase anterior, cada cambio era predecible y controlado.

Esto evidencia que el *spec* no es solo documentación, sino una herramienta que guía directamente las decisiones de implementación.

---

### 🟪 Fase 3: Quality Gate — la IA como evaluadora

En la última fase utilizamos la IA no para generar código, sino para evaluarlo. Se le pidió asumir el rol de experto en QA y UX, analizando posibles errores y problemas de accesibilidad.

Este paso permitió identificar situaciones no contempladas, como entradas inválidas o problemas de contraste, y proponer mejoras específicas sin afectar todo el sistema. Más que generar código nuevo, la IA actuó como una capa de validación, lo que introduce una práctica clave en el desarrollo: verificar antes de dar por terminado el producto.

---

## 🧠 Análisis

Lo más interesante del laboratorio es cómo cambia el rol de la IA en cada enfoque. En *Vibe Coding*, la IA toma decisiones por el desarrollador, lo que lleva a resultados rápidos pero impredecibles. El sistema evoluciona sin una dirección clara, y cada cambio introduce el riesgo de romper lo existente.

En contraste, en *Spec-Driven Development*, el desarrollador define el problema y la IA se limita a implementarlo. Esto reduce la ambigüedad y permite que el sistema crezca de forma controlada. La diferencia no está en la herramienta, sino en el nivel de precisión con el que se le dan instrucciones.

---

## ⚖️ Ventajas y retos

El *Vibe Coding* destaca por su rapidez y facilidad para explorar ideas, especialmente en etapas tempranas donde no se tiene claridad sobre el problema. Sin embargo, esta misma flexibilidad lo convierte en una fuente de desorden, dependencia de la IA y acumulación de deuda técnica.

Por otro lado, el *Spec-Driven Development* exige más esfuerzo inicial, ya que requiere definir claramente qué se quiere construir. A cambio, ofrece mayor control, mejor organización del código y una evolución más estable del sistema. Su principal reto es la disciplina: si las especificaciones son incorrectas o incompletas, el resultado también lo será.

---

## 🧾 Conclusión

El laboratorio demuestra que la diferencia entre ambos enfoques no es la capacidad de la IA, sino la forma en que se utiliza. Programar únicamente con “intuición” puede ser útil para prototipar, pero no es sostenible en sistemas reales.

La principal lección es que **la calidad del software depende más del diseño que de la implementación**. En este contexto, el *spec* deja de ser documentación y se convierte en el elemento central del desarrollo: el desarrollador diseña, y la IA ejecuta.

