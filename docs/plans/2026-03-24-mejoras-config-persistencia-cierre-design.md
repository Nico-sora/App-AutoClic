# Diseño: Mejoras — Countdown configurable, Persistencia completa, Diálogo de cierre

**Fecha:** 2026-03-24

## Resumen

Tres mejoras para AutoClic:
1. Countdown configurable (0-10s) antes del auto-clic
2. Persistencia completa del estado al cerrar/abrir (incluyendo última grabación)
3. Diálogo al cerrar con X: cerrar o minimizar a bandeja del sistema

---

## Mejora 1: Countdown configurable

**Ubicación:** Pestaña Configuración (TabSettings), sección Apariencia.

- Spinbox con rango 0-10 segundos (default: 3)
- Valor 0 = inicio inmediato sin countdown
- Se persiste en `config.json` como `countdown_seconds`
- `tab_autoclick.py` lee el valor desde config en vez del `3` hardcodeado

## Mejora 2: Persistencia completa

**Qué se guarda en `config.json`:**
- Estado completo de auto-clic: acción, botón, tipo clic, intervalo, variación random, duración, posición, zona random
- Última grabación: lista de eventos serializada
- Countdown, always_on_top, close_action

**Cuándo se guarda:** Al cerrar la app (`_on_close`) se recopila el estado actual de la UI.

**Cuándo se carga:** Al iniciar, después de construir la UI, se restaura el estado guardado.

**Métodos nuevos:**
- `TabAutoClick.get_state() -> dict` / `TabAutoClick.set_state(data: dict)`
- `TabRecorder.get_last_recording() -> list` / `TabRecorder.set_last_recording(data: list)`

## Mejora 3: Diálogo de cierre

**Nuevo archivo:** `src/ui/close_dialog.py`

**Diálogo custom CTkToplevel** con estilo neon:
- "¿Qué deseas hacer?"
- Botón rojo "Cerrar aplicación"
- Botón cyan "Minimizar a bandeja"
- Checkbox "No volver a preguntar"

**Config `close_action`:** `"ask"` | `"close"` | `"tray"`

**Flujo en `_on_close`:**
1. Si `close_action == "ask"` → mostrar diálogo
2. Si `close_action == "close"` → cerrar directamente
3. Si `close_action == "tray"` → minimizar a bandeja (pystray)

**En TabSettings:** Opción para resetear preferencia de cierre (volver a "preguntar siempre").

---

## Archivos a modificar

| Archivo | Cambios |
|---------|---------|
| `src/utils/config.py` | Ampliar defaults |
| `src/utils/i18n.py` | Nuevas strings |
| `src/ui/tab_settings.py` | Spinbox countdown, reset cierre |
| `src/ui/tab_autoclick.py` | Leer countdown config, get/set state |
| `src/ui/tab_recorder.py` | get/set last recording |
| `src/app.py` | Persistir al cerrar, restaurar al abrir, diálogo cierre |
| `src/ui/close_dialog.py` | **Nuevo** — diálogo custom |

## Config.json ampliado

```json
{
  "hotkey_autoclick": "F6",
  "hotkey_record": "F7",
  "hotkey_play": "F8",
  "theme": "dark",
  "language": "es",
  "countdown_seconds": 3,
  "always_on_top": false,
  "close_action": "ask",
  "autoclick_state": { ... },
  "last_recording": []
}
```
