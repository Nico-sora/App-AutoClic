# Diseño: Hold, Tipo de Acción Universal y Hotkeys de Ciclo
**Fecha:** 2026-04-12

## Resumen

Tres grupos de cambios para AutoClic:
1. Modo "mantener presionado" para ratón, tecla y botón extra
2. Selector de tipo de acción (simple/doble/triple/mantener) disponible para todos los modos
3. Hotkeys configurables para ciclar entre perfiles y macros guardados

---

## Feature 1: Hold (Mantener Presionado)

### Comportamiento
- El botón/tecla se presiona **una sola vez al inicio** de la sesión y se suelta al detener el autoclicker.
- El loop interno solo duerme el intervalo — no ejecuta clics adicionales.
- Aplica a: botones de ratón (left/middle/right), botones extra (x1/x2) y teclas.
- `duration_ms` sigue funcionando: el hold termina al agotarse el tiempo o al detener manualmente.

### Cambios en `src/core/clicker.py`
- `click_type` acepta `"hold"` además de `"single"/"double"/"triple"`.
- En `_loop`: si `click_type == "hold"`, hacer `press()` antes del `while` y `release()` en `finally`.
- Para ratón/extra: `self._mouse.press(btn)` / `self._mouse.release(btn)`.
- Para tecla: `self._kb.press(key)` / `self._kb.release(key)`.

---

## Feature 2: Tipo de Acción Universal

### Comportamiento
- El selector de tipo (simple/doble/triple/mantener) se muestra para **todos los modos** (ratón, tecla, botón extra).
- Se extrae de `_frame_button` y se convierte en un `_frame_type` independiente, siempre visible, debajo del frame de modo activo.

### UI resultante
```
○ Clic ratón  ○ Tecla  ○ Botón extra
[Botón: Izquierdo ▼]          ← solo en modo ratón
[Tipo: Simple ▼]              ← siempre visible (4 opciones)
```

### Cambios en `src/ui/tab_autoclick.py`
- Eliminar el selector de tipo de `_frame_button` (dejar solo el selector de botón).
- Añadir `_frame_type` nuevo con `_click_type_var` y 4 opciones: simple, doble, triple, mantener.
- `_frame_type` se empaqueta siempre, no se oculta.
- `_toggle_action` ya no necesita mostrar/ocultar el tipo.

---

## Feature 3 & 4: Hotkeys de Ciclo

### Nuevas claves de configuración
```json
"hotkey_cycle_profile": "",
"hotkey_cycle_macro": "",
"cycle_profile_behavior": "stop_load",
"cycle_macro_behavior": "stop_load"
```

### UI en `src/ui/tab_settings.py`
Dos filas nuevas en la sección Hotkeys, cada una con:
- Label + display de tecla + botón Capturar
- Dropdown de comportamiento: Parar y cargar / Cargar y arrancar / Solo seleccionar

### Lógica de ciclo (app.py / main_window.py)
Métodos `_cycle_profile()` y `_cycle_macro()` registrados en el listener global:

1. Obtener lista (perfiles o macros guardadas)
2. Si lista vacía → no hacer nada
3. Encontrar índice actual → avanzar al siguiente (circular)
4. Aplicar comportamiento:
   - `stop_load`: detener autoclicker → cargar → actualizar UI
   - `load_start`: cargar → iniciar autoclicker automáticamente
   - `select`: solo mover el dropdown, sin aplicar

### Strings i18n nuevos
- `click_hold`, `hk_cycle_profile`, `hk_cycle_macro`
- `cycle_behavior_stop_load`, `cycle_behavior_load_start`, `cycle_behavior_select`
- `label_cycle_behavior`

---

## Archivos afectados
| Archivo | Cambio |
|---|---|
| `src/core/clicker.py` | Soporte para `click_type="hold"` |
| `src/ui/tab_autoclick.py` | `_frame_type` universal, 4 opciones |
| `src/ui/tab_settings.py` | 2 filas nuevas en hotkeys + dropdowns comportamiento |
| `src/utils/config.py` | Defaults para 4 nuevas claves |
| `src/utils/i18n.py` | Strings nuevos en todos los idiomas |
| `src/app.py` o `main_window.py` | `_cycle_profile()` y `_cycle_macro()` |
