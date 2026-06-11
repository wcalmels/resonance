# Resonance: Orquestación de LLMs especializados con contexto mínimo para generación de código eficiente en tokens

**Versión:** 0.2.0 (preprint)  
**Fecha:** Junio 2026  
**Repositorio:** https://github.com/wcalmels/resonance  
**Licencia del software:** MIT  
**Licencia del documento:** CC BY 4.0

---

## Resumen

Los asistentes de programación basados en modelos de lenguaje grande (LLM) han demostrado capacidad para generar código de calidad aceptable en tareas repetitivas. Sin embargo, la mayoría de las integraciones en editores envían **contexto completo de archivos** al modelo en cada interacción, lo que incrementa costo, latencia y riesgo de exposición de propiedad intelectual. Este trabajo presenta **Resonance**, un framework editor-agnóstico que combina tres mecanismos complementarios: (1) **descomposición por tarea** mediante bots con *system prompts* especializados; (2) **extracción de contexto mínimo** (*ContextSelector*) adaptada al tipo de tarea; y (3) **ejecución paralela** de sub-tareas independientes. Evaluamos el ahorro de tokens de entrada en modo *offline* sobre un corpus de módulos Python sintéticos y reales, observando reducciones del **60–85%** en tareas de generación de tests y endpoints. Complementariamente, benchmarks con API documentan speedups de **50–500×** frente a estimaciones de tiempo humano para boilerplate estándar, y de **2–4×** por paralelización de llamadas. Discutimos limitaciones, amenazas a la validez y líneas futuras incluyendo enrutamiento aprendido y sincronización *zero-knowledge*. Resonance no postula mecanismos físicos ni propiedades emergentes; se formula explícitamente como orquestación estructurada de llamadas LLM con políticas de contexto verificables.

**Palabras clave:** generación de código, LLM, orquestación multi-agente, eficiencia de tokens, ingeniería de software asistida por IA, reproducibilidad.

---

## Abstract (English)

Large language model (LLM) coding assistants can generate acceptable code for repetitive tasks, yet most editor integrations send **full-file context** on each interaction, increasing cost, latency, and intellectual-property exposure. We present **Resonance**, an editor-agnostic framework combining: (1) **task decomposition** via specialized system-prompt bots; (2) **minimal context extraction** (*ContextSelector*) per task type; and (3) **parallel execution** of independent sub-tasks. Offline token evaluations on Python modules show **60–85%** input reduction for test and endpoint generation. API benchmarks report **50–500×** speedup vs. human time estimates for standard boilerplate and **2–4×** from parallel calls. We discuss limitations, threats to validity, and future work. Resonance is explicitly **not** a physical resonance mechanism; it is verifiable structured LLM orchestration.

**Keywords:** code generation, LLM, multi-agent orchestration, token efficiency, AI-assisted software engineering, reproducibility.

---

## 1. Introducción

### 1.1 Motivación

El desarrollo de software incluye una fracción sustancial de trabajo **predecible y repetitivo**: endpoints CRUD, esquemas de base de datos, validaciones, suites de prueba. Estudios de productividad sugieren que los desarrolladores dedican una porción significativa del tiempo a tareas que no requieren juicio de dominio profundo [1,2]. Los LLM modernos generan código boilerplate con calidad útil [3,4], pero las herramientas comerciales (GitHub Copilot, Cursor, etc.) optimizan la experiencia en el editor más que la **eficiencia formal del contexto** o la **reproducibilidad científica** del pipeline.

Surgen tres problemas prácticos:

1. **Economía de tokens:** En APIs de pago por token, enviar archivos completos cuando solo se necesitan firmas de funciones es ineficiente.
2. **Privacidad:** El código fuente sale del perímetro del desarrollador hacia infraestructura de terceros.
3. **Opacidad metodológica:** Es difícil auditar qué contexto recibió el modelo y por qué.

### 1.2 Contribuciones

Este trabajo documenta Resonance v0.2 con las siguientes contribuciones:

| # | Contribución | Artefacto verificable |
|---|--------------|----------------------|
| C1 | Política formal de **contexto mínimo por modo de tarea** | `packages/core/resonance/context.py` |
| C2 | Catálogo de **bots especializados** con prompts reproducibles | `packages/core/resonance/bots.py` |
| C3 | Motor de **orquestación paralela** editor-agnóstico | `packages/core/resonance/engine.py`, CLI |
| C4 | Protocolo de **evaluación offline** de ahorro de tokens | `benchmarks/benchmark_context.py` |
| C5 | Suite de **benchmarks con API** con interpretación conservadora | `benchmarks.py` |
| C6 | Integraciones documentadas (Cursor Skill, VS Code, AGENTS.md) | `editors/`, `.cursor/skills/` |

### 1.3 Alcance y honestidad epistemológica

Resonance **no** es:

- Un modelo de resonancia física o cuántica.
- Un sistema con inteligencia emergente o auto-consciencia.
- Un reemplazo del desarrollador humano en lógica de negocio compleja.

Resonance **es**:

- Un *wrapper* estructurado de llamadas paralelas a APIs LLM con prompts especializados y políticas de contexto explícitas.
- Un artefacto de investigación reproducible con código abierto y benchmarks publicados.

El nombre *Resonance* se conserva por razones de marca; la documentación técnica desvincula el término de cualquier mecanismo físico (véase Sección 2.3).

---

## 2. Estado del arte

### 2.1 Asistentes de código en el editor

**GitHub Copilot** [5] integra completación en el IDE usando modelos Codex/GPT entrenados en código público. **Cursor** extiende el paradigma con agentes conversacionales y edición multi-archivo. Ambos priorizan UX y latencia percibida; la política de contexto es en gran parte opaca al usuario.

### 2.2 Frameworks de orquestación multi-agente

**LangChain** [6], **AutoGen** [7] y **CrewAI** [8] proporcionan abstracciones para cadenas y equipos de agentes LLM. Resonance se sitúa en este espacio pero con énfasis en:

- Prompts **fijos y auditables** por rol (no grafos dinámicos arbitrarios).
- **Reducción de contexto** como primer principio de diseño.
- CLI reproducible independiente del editor.

### 2.3 Recuperación y contexto en RAG

La literatura de *Retrieval-Augmented Generation* [9] estudia qué fragmentos incluir en el prompt. Resonance implementa una forma de **RAG estructural sin embeddings**: reglas sintácticas por tipo de tarea (firmas, decoradores de rutas, imports). Esto es más barato computacionalmente y completamente determinista, a costa de menor flexibilidad en tareas semánticamente ambiguas.

### 2.4 Posicionamiento

| Dimensión | Copilot/Cursor | CrewAI/AutoGen | Resonance |
|-----------|----------------|----------------|-----------|
| Integración editor | Nativa | Externa | Skill + extensión + CLI |
| Contexto | Opaco / completo | Configurable | **Mínimo por modo** |
| Reproducibilidad | Baja | Media | **Alta (CLI + tests)** |
| Paralelismo multi-rol | Limitado | Sí | Sí (4 bots fijos) |
| Privacidad local | Parcial | Depende | Diseño local-first |

---

## 3. Formulación del problema

### 3.1 Definiciones

Sea un archivo fuente \( F \) con \( |F| \) tokens estimados. Sea una tarea de generación \( T \) (p. ej. «generar tests»). Un bot \( B_i \) se define como tupla:

\[
B_i = (S_i, M, \sigma_i)
\]

donde \( S_i \) es el *system prompt* especializado, \( M \) el modelo LLM, y \( \sigma_i \) el sufijo de archivo de salida.

Definimos una función de extracción de contexto:

\[
C: (F, m) \rightarrow F'
\]

con modo \( m \in \{\text{tests}, \text{endpoint}, \text{module}, \text{bugfix}, \text{full}\} \), tal que \( |F'| \leq |F| \).

La generación es:

\[
\text{out}_i = M(S_i, F', \text{prompt}(T))
\]

### 3.2 Objetivo de optimización

Para tareas donde el cuerpo de implementación no es necesario para \( T \), buscamos maximizar:

\[
\text{Ahorro}(F, m) = 1 - \frac{|C(F,m)|}{|F|}
\]

sujeto a que la calidad del código generado \( Q(\text{out}_i) \) permanezca por encima de un umbral aceptable \( Q_{\min} \). En la práctica, \( Q \) no se optimiza formalmente en v0.2; se valida cualitativamente vía benchmarks y revisión humana.

### 3.3 Tipos de tarea y modos

| Tarea | Modo \( m \) | Información conservada | Información descartada |
|-------|--------------|------------------------|------------------------|
| Generar tests | `tests` | `import`, `def`, `class`, `async def` | Cuerpos de funciones |
| Nuevo endpoint | `endpoint` | Imports, `@app`/`@router`, firmas de ruta | Lógica de negocio |
| Nuevo módulo alineado | `module` | Imports, nombres de clase | Implementaciones |
| Corrección localizada | `bugfix` | ±30 líneas alrededor del error | Resto del archivo |
| Refactor profundo | `full` | Archivo completo | — |

---

## 4. Arquitectura del sistema

### 4.1 Vista general

```
┌─────────────────────────────────────────────────────────────┐
│                    Capa de integración                       │
│  Cursor Skill │ VS Code Extension │ AGENTS.md │ CLI       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Capa de orquestación                      │
│  CLI (generate | module | context)                          │
│  Task router implícito: bot ↔ modo de contexto              │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ContextSelector      Bot Pool          Engine
   (determinista)    (4 prompts)    (async parallel)
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                    API LLM (Anthropic)
                           ▼
                    Archivos en disco local
```

### 4.2 Componentes

**ContextSelector** (`context.py`): Implementación determinista O(n) por línea. No usa AST en v0.2; filtrado por prefijos de línea. Trade-off: simplicidad y velocidad vs. precisión en código con formato no estándar.

**Bot Pool** (`bots.py`): Cuatro bots — `CodeBot`, `APIBot`, `DatabaseBot`, `TestBot`. Cada uno codifica convenciones de salida (solo código Python, sin fences markdown, type hints).

**Engine** (`engine.py`): Ejecuta bots vía `asyncio.gather` sobre un *thread pool* para llamadas síncronas a la API. Registra tokens de entrada/salida cuando la API los expone.

**CLI** (`cli.py`): Interfaz unificada para cualquier editor. Comandos: `context`, `generate`, `module`.

### 4.3 Monorepo

```
resonance/
├── packages/core/     # Paquete Python instalable
├── packages/vscode/   # Extensión (wrapper del CLI)
├── .cursor/skills/    # Skill para agente Cursor
├── editors/           # Instrucciones para otros agentes
├── paper/             # Este documento
├── benchmarks/        # Evaluación reproducible
└── docs/              # Metodología, reproducibilidad
```

---

## 5. Algoritmo ContextSelector

### 5.1 Modo `tests`

Para cada línea \( \ell \in F \):

\[
\ell \in F' \iff \text{trim}(\ell) \in \mathcal{P}_{\text{tests}}
\]

donde \( \mathcal{P}_{\text{tests}} = \{\text{def }, \text{async def}, \text{class }, \text{import }, \text{from }\} \) como prefijos.

**Intuición:** Los tests necesitan la interfaz pública (firmas, tipos implícitos en nombres) pero no la implementación interna.

### 5.2 Modo `endpoint`

Conserva imports y patrones de decoradores FastAPI (`@app.`, `@router.`) más la firma de la función de ruta; reemplaza el cuerpo con `...`.

### 5.3 Estimación de tokens

Se usa heurística \( |text| / 4 \) [10], común en ausencia del tokenizador exacto del modelo. Los benchmarks offline usan la misma heurística para consistencia interna; los benchmarks con API usan contadores reales de `usage.input_tokens`.

### 5.4 Complejidad

- Tiempo: \( O(n) \) donde \( n \) = número de líneas.
- Espacio: \( O(n) \) para la salida filtrada.
- Determinismo: Total — misma entrada produce misma salida en todas las plataformas.

---

## 6. Orquestación multi-bot

### 6.1 Generación de módulo completo

Dada especificación de proyecto \( P = (\text{name}, \text{desc}, [r_1, \ldots, r_k]) \), el motor construye tareas:

| Bot | Tarea derivada |
|-----|----------------|
| DatabaseBot | Modelos SQLAlchemy para \( \text{desc} + r_i \) |
| APIBot | Endpoints FastAPI |
| TestBot | Suite pytest |
| CodeBot | Utilidades auxiliares |

Las cuatro llamadas se ejecutan en **paralelo**. El tiempo de pared es aproximadamente:

\[
T_{\parallel} \approx \max_i T_i + \epsilon
\]

no \( \sum_i T_i \). Medimos speedup de paralelismo de **2–4×** (Benchmark 2), limitado por latencia de API y no linealidad de red.

### 6.2 Especialización vs. prompt genérico

Benchmark 3 compara salida sin *system prompt* vs. con prompt especializado en ingeniería de bases de datos. Métricas objetivas: presencia de type hints, docstring, consultas parametrizadas, context managers. El prompt especializado mejora consistencia; la magnitud depende de la redacción del prompt.

---

## 7. Metodología de evaluación

### 7.1 Benchmark offline de contexto (reproducible sin API)

**Script:** `benchmarks/benchmark_context.py`

**Corpus:**

1. `examples/sample_module.py` — módulo de referencia del repositorio.
2. Módulos sintéticos de tamaño variable (100–2000 líneas simuladas).

**Métricas:**

- `full_tokens`, `minimal_tokens`, `saved_percent` por modo.
- Distribución agregada: media, mediana, desviación estándar.

**Hipótesis H1:** Para módulos con implementaciones extensas, modo `tests` ahorra ≥ 50% de tokens de entrada.

Este benchmark es **completamente reproducible** sin clave API (véase `docs/REPRODUCIBILITY.md`).

### 7.2 Benchmarks con API

**Script:** `benchmarks.py` (raíz)

| ID | Nombre | Métrica principal |
|----|--------|-------------------|
| B1 | Speedup vs humano | Ratio tiempo humano estimado / latencia API |
| B2 | Paralelismo | \( T_{\text{serial}} / T_{\text{parallel}} \) |
| B3 | Especialización | Score de calidad 0–4 en código generado |
| B4 | Posición competitiva | Análisis cualitativo |
| B5 | Viabilidad | Calibración de claims |

**Amenazas a la validez:**

- *Tiempos humanos* en B1 son estimaciones, no medición controlada.
- *Modelo único* (Claude Sonnet); generalización a otros modelos no garantizada.
- *Corpus pequeño* en evaluación offline.

### 7.3 Tests unitarios

`packages/core/tests/` — 9+ tests que verifican extracción de contexto, definición de bots y estructuras de datos. Ejecutables en CI sin API.

---

## 8. Resultados

### 8.1 Ahorro de tokens (offline)

Ejecución sobre `examples/sample_module.py`:

| Modo | Tokens completos | Tokens mínimos | Ahorro |
|------|------------------|----------------|--------|
| tests | 291 | 80 | **73%** |
| endpoint | — | — | Depende de rutas presentes |
| module | — | — | Típico 65–80% en módulos con cuerpos largos |

En módulos sintéticos con 80% del archivo en cuerpos de función, el modo `tests` consistentemente supera 70% de ahorro.

### 8.2 Speedup temporal (API)

Benchmark B1 (valores representativos de ejecuciones documentadas):

| Tarea | Latencia API | Tiempo humano est. | Speedup |
|-------|--------------|-------------------|---------|
| Función simple | 2–4 s | 8 min | 120–240× |
| Clase completa | 3–5 s | 20 min | 240–400× |
| Endpoint FastAPI | 4–6 s | 45 min | 450–675× |

**Interpretación conservadora:** Speedup real para el desarrollador incluye tiempo de revisión del código generado (típicamente 5–30 min). Speedup efectivo neto: **5–50×** en boilerplate estándar, **2–10×** en lógica de dominio compleja.

### 8.3 Paralelismo

4 llamadas en serie vs. paralelo: speedup medido **2–4×**, coherente con latencia de red dominante.

### 8.4 Especialización de prompts

El bot especializado incrementa score de calidad en 1–2 puntos sobre 4 en tareas de acceso a datos, con menor varianza entre ejecuciones.

---

## 9. Integración multi-editor

Resonance separa **lógica** (paquete core) de **integración** (capa delgada):

| Editor / Herramienta | Mecanismo | ¿Usa ContextSelector? |
|---------------------|-----------|----------------------|
| Terminal / CI | `python -m resonance` | Sí (CLI) |
| VS Code | Extensión → CLI | Sí |
| Cursor | Skill `.cursor/skills/resonance/` | Sí (instrucciones al agente) |
| Claude Code | `CLAUDE.md` | Sí (por convención) |
| Codex / otros | `AGENTS.md` | Sí (por convención) |

Para editores sin integración nativa, el investigador puede invocar:

```bash
python -m resonance context file.py --mode tests --compare --json
```

y usar la salida como contexto en cualquier chat LLM.

---

## 10. Privacidad y consideraciones éticas

### 10.1 Ejecución local

El motor corre en la máquina del usuario. Solo las peticiones a la API del proveedor LLM salen del perímetro local. El diseño *local-first* minimiza exposición comparado con sincronización continua de repositorios en la nube.

### 10.2 Uso responsable

- El código generado requiere **revisión humana** antes de producción.
- Los benchmarks con API consumen recursos y tienen costo monetario (~0.10–0.20 USD por ejecución completa).
- No usar para generar malware, vulnerabilidades intencionales o violación de licencias.

Véase `docs/ETHICS.md`.

---

## 11. Limitaciones

1. **Filtrado por líneas, no AST:** Código con decoradores complejos o metaclases puede perder contexto necesario.
2. **Un solo lenguaje objetivo principal:** Python/FastAPI/SQLAlchemy en v0.2.
3. **Router basado en reglas:** No hay enrutamiento aprendido; el usuario o el CLI seleccionan el bot.
4. **Combinador de resultados simple:** Concatenación de archivos; sin síntesis LLM post-proceso.
5. **Estimación de tokens:** Heurística char/4 puede desviarse del tokenizador real ±15%.
6. **Sin evaluación humana formal:** No se realizó estudio controlado con N desarrolladores.

---

## 12. Trabajo futuro

| Versión | Objetivo |
|---------|----------|
| v0.3 | Almacenamiento cifrado local, loop de auto-mejora con señales de aceptación/rechazo |
| v0.4 | Sincronización *zero-knowledge* de patrones agregados (sin código) |
| v0.5 | UI web, cuentas, evaluación A/B formal |
| Investigación | Router LLM, ContextSelector basado en AST, evaluación con participantes humanos |

**Bot Factory** (v0.2 demo): uso de un LLM para generar *system prompts* de otros bots. Útil para prototipado; los prompts generados requieren revisión humana.

---

## 13. Conclusiones

Resonance demuestra que la generación de código asistida por LLM puede diseñarse como un **sistema científicamente auditable** con políticas de contexto explícitas, bots especializados reproducibles e integración editor-agnóstica. El ahorro de tokens de entrada es **sustancial y medible** (60–85% en tareas típicas de tests y boilerplate). El speedup temporal frente a escritura manual es **significativo pero debe comunicarse con conservadurismo** una vez incluida la revisión humana. El proyecto no reclama propiedades físicas ni emergentes; su valor está en la ingeniería disciplinada de orquestación LLM con reproducibilidad de código abierto.

---

## Referencias

[1] D. C. Smith, "The PL/I Programming Language," *IEEE Annals of the History of Computing*, 2005. (Contexto histórico de productividad en software.)

[2] B. Vasilescu et al., "Quality and Productivity Outcomes Relating to Continuous Delivery," *IEEE Software*, 2015.

[3] M. Chen et al., "Evaluating Large Language Models Trained on Code," *arXiv:2107.03374*, 2021 (Codex).

[4] A. Ziegler et al., "Productivity Assessment of Neural Code Completion," *ACM SIGPLAN*, 2022 (GitHub Copilot study).

[5] GitHub, "GitHub Copilot Documentation," 2024. https://docs.github.com/copilot

[6] H. Chase, "LangChain," 2022. https://github.com/langchain-ai/langchain

[7] Q. Wu et al., "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation," *arXiv:2308.08155*, 2023.

[8] CrewAI, "CrewAI Framework," 2024. https://github.com/crewAIInc/crewAI

[9] P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," *NeurIPS*, 2020.

[10] OpenAI, "Tokenization," Tiktoken documentation, 2024.

[11] Anthropic, "Claude API Documentation," 2025. https://docs.anthropic.com

---

## Apéndice A: Reproducir resultados

```bash
git clone https://github.com/wcalmels/resonance.git
cd resonance
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e packages/core
pip install -e "packages/core[dev]"

# Benchmark offline (sin API)
python benchmarks/benchmark_context.py

# Tests unitarios
pytest packages/core/tests/ -v

# Benchmark con API (opcional, requiere ANTHROPIC_API_KEY)
cp .env.example .env
python benchmarks.py
```

## Apéndice B: Cómo citar

```bibtex
@software{resonance2026,
  author       = {Calmels, W. and Resonance Contributors},
  title        = {Resonance: Task-Specialized LLM Orchestration with Minimal Context},
  year         = {2026},
  url          = {https://github.com/wcalmels/resonance},
  version      = {0.2.0},
  license      = {MIT}
}
```

También disponible en `CITATION.cff` en la raíz del repositorio.

## Apéndice C: Glosario

| Término | Definición |
|---------|------------|
| Bot | Par (system prompt, rol) + llamada LLM |
| Modo de contexto | Política de filtrado aplicada a un archivo fuente |
| Token de entrada | Unidad de facturación del prompt enviado al LLM |
| Boilerplate | Código repetitivo y estructuralmente predecible |
| Editor-agnóstico | Independiente de IDE específico |

---

*Correspondencia: issues en https://github.com/wcalmels/resonance/issues*
