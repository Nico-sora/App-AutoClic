# AutoClic — Reglas del Proyecto

## Regla principal: Brainstorming obligatorio

Antes de implementar cualquier funcionalidad nueva, cambio de comportamiento, o feature — **SIEMPRE** usa la Skill `brainstorming` para:

1. Entender la intención real detrás del input del usuario
2. Hacer preguntas clarificadoras (una a la vez)
3. Proponer 2-3 enfoques con trade-offs y tu recomendación
4. Sugerir mejoras a la idea original del usuario
5. Obtener aprobación del diseño antes de escribir código

Esto aplica incluso si la tarea parece simple. No asumas — pregunta y explora.

## Flujo de trabajo

1. Usuario pide algo → Invocar Skill `brainstorming`
2. Explorar contexto del proyecto
3. Preguntas clarificadoras + sugerencias de mejora
4. Proponer enfoques con recomendación
5. Diseño aprobado → Implementar

## Stack

- Python 3.13, CustomTkinter, pynput, Pillow
- Entry point: `src/main.py`
- UI en español
