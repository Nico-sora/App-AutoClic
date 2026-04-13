# Hold, Tipo Universal y Hotkeys de Ciclo — Plan de Implementación

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Añadir modo "mantener presionado", selector de tipo de acción universal (4 opciones), y dos hotkeys configurables para ciclar entre perfiles y macros guardados.

**Architecture:** 5 tareas independientes ordenadas de menor a mayor dependencia de UI. Cada tarea es atómica y hace commit propio. No hay tests previos en el proyecto — se crea `tests/test_clicker_hold.py` para la lógica del clicker (sin UI), el resto se verifica manualmente arrancando la app.

**Tech Stack:** Python 3.13, CustomTkinter, pynput, pytest (solo para clicker)

---

### Task 1: Strings i18n — nuevas claves

**Files:**
- Modify: `src/utils/i18n.py`

No hay tests para i18n — verificar visualmente al final.

**Step 1: Añadir las nuevas claves al diccionario `STRINGS` en `src/utils/i18n.py`**

Localizar el bloque de `"click_triple"` (alrededor de la línea que contiene esa clave) e insertar justo después:

```python
    "click_hold": {
        "es": "Mantener", "en": "Hold",
        "pt": "Segurar", "fr": "Maintenir",
        "de": "Halten", "it": "Tieni premuto",
        "ru": "Удерживать", "zh": "按住",
        "ja": "ホールド", "ko": "유지",
        "pl": "Przytrzymaj", "tr": "Basılı tut",
        "nl": "Ingedrukt houden", "ar": "اضغط مع الاستمرار",
    },
```

Localizar el bloque de `"hk_play"` e insertar justo después:

```python
    "hk_cycle_profile": {
        "es": "Ciclo perfiles", "en": "Cycle profiles",
        "pt": "Ciclo perfis", "fr": "Cycle profils",
        "de": "Profile wechseln", "it": "Ciclo profili",
        "ru": "Цикл профилей", "zh": "切换配置",
        "ja": "プロファイル切替", "ko": "프로필 순환",
        "pl": "Cykl profili", "tr": "Profil döngüsü",
        "nl": "Profielen wisselen", "ar": "تدوير الملفات",
    },
    "hk_cycle_macro": {
        "es": "Ciclo macros", "en": "Cycle macros",
        "pt": "Ciclo macros", "fr": "Cycle macros",
        "de": "Makros wechseln", "it": "Ciclo macro",
        "ru": "Цикл макросов", "zh": "切换宏",
        "ja": "マクロ切替", "ko": "매크로 순환",
        "pl": "Cykl makr", "tr": "Makro döngüsü",
        "nl": "Macro's wisselen", "ar": "تدوير الماكرو",
    },
    "label_cycle_behavior": {
        "es": "Al activar:", "en": "On trigger:",
        "pt": "Ao ativar:", "fr": "À l'activation :",
        "de": "Bei Auslösung:", "it": "All'attivazione:",
        "ru": "При активации:", "zh": "触发时：",
        "ja": "実行時：", "ko": "활성화 시:",
        "pl": "Po aktywacji:", "tr": "Tetiklenince:",
        "nl": "Bij activatie:", "ar": "عند التفعيل:",
    },
    "cycle_behavior_stop_load": {
        "es": "Parar y cargar", "en": "Stop and load",
        "pt": "Parar e carregar", "fr": "Arrêter et charger",
        "de": "Stoppen und laden", "it": "Ferma e carica",
        "ru": "Стоп и загрузить", "zh": "停止并加载",
        "ja": "停止して読込", "ko": "정지 후 로드",
        "pl": "Zatrzymaj i załaduj", "tr": "Durdur ve yükle",
        "nl": "Stop en laad", "ar": "إيقاف وتحميل",
    },
    "cycle_behavior_load_start": {
        "es": "Cargar y arrancar", "en": "Load and start",
        "pt": "Carregar e iniciar", "fr": "Charger et démarrer",
        "de": "Laden und starten", "it": "Carica e avvia",
        "ru": "Загрузить и запустить", "zh": "加载并启动",
        "ja": "読込して開始", "ko": "로드 후 시작",
        "pl": "Załaduj i uruchom", "tr": "Yükle ve başlat",
        "nl": "Laad en start", "ar": "تحميل وبدء",
    },
    "cycle_behavior_select": {
        "es": "Solo seleccionar", "en": "Select only",
        "pt": "Apenas selecionar", "fr": "Sélectionner seulement",
        "de": "Nur auswählen", "it": "Solo seleziona",
        "ru": "Только выбрать", "zh": "仅选择",
        "ja": "選択のみ", "ko": "선택만",
        "pl": "Tylko wybierz", "tr": "Sadece seç",
        "nl": "Alleen selecteren", "ar": "تحديد فقط",
    },
```

**Step 2: Commit**

```bash
git add src/utils/i18n.py
git commit -m "feat: add i18n strings for hold mode and cycle hotkeys"
```

---

### Task 2: Clicker — soporte para `click_type="hold"`

**Files:**
- Modify: `src/core/clicker.py`
- Create: `tests/test_clicker_hold.py`

**Step 1: Escribir el test fallido**

Crear `tests/__init__.py` (vacío) y `tests/test_clicker_hold.py`:

```python
"""Tests for clicker hold mode — no UI needed."""
import time
import threading
from unittest.mock import MagicMock, patch, call
import pytest


def test_hold_mouse_presses_and_releases():
    """Hold mode should press once before loop and release once on stop."""
    with patch("src.core.clicker.MouseController") as MockMouse, \
         patch("src.core.clicker.KbController"):
        mock_mouse = MagicMock()
        MockMouse.return_value = mock_mouse

        from src.core.clicker import Clicker
        c = Clicker()
        c.start(button="left", click_type="hold", interval_ms=50, duration_ms=0)
        time.sleep(0.15)
        c.stop()
        time.sleep(0.1)

        mock_mouse.press.assert_called_once()
        mock_mouse.release.assert_called_once()
        # click() must NOT have been called
        mock_mouse.click.assert_not_called()


def test_hold_does_not_increment_click_count_per_interval():
    """Hold mode click_count stays at 0 (no repeated clicks)."""
    with patch("src.core.clicker.MouseController"), \
         patch("src.core.clicker.KbController"):
        from src.core.clicker import Clicker
        c = Clicker()
        c.start(button="left", click_type="hold", interval_ms=30, duration_ms=0)
        time.sleep(0.15)
        c.stop()
        time.sleep(0.1)
        assert c.click_count == 0


def test_normal_single_click_still_works():
    """Regression: single click type should still call mouse.click."""
    with patch("src.core.clicker.MouseController") as MockMouse, \
         patch("src.core.clicker.KbController"):
        mock_mouse = MagicMock()
        MockMouse.return_value = mock_mouse

        from src.core.clicker import Clicker
        c = Clicker()
        c.start(button="left", click_type="single", interval_ms=30, duration_ms=120)
        time.sleep(0.25)
        c.stop()
        time.sleep(0.1)

        assert mock_mouse.click.call_count >= 2
        mock_mouse.press.assert_not_called()
```

**Step 2: Verificar que el test falla**

```bash
python -m pytest tests/test_clicker_hold.py -v
```
Esperado: FAIL con `AssertionError` (hold no implementado aún).

**Step 3: Implementar hold en `src/core/clicker.py`**

Reemplazar el método `_loop` completo:

```python
    def _loop(self, button, custom_key, interval_ms, duration_ms, fixed_pos,
              click_type, random_zone, random_interval_ms):
        interval = interval_ms / 1000.0
        start_time = time.perf_counter()
        click_count_map = {"single": 1, "double": 2, "triple": 3}
        n_clicks = click_count_map.get(click_type, 1)
        is_hold = (click_type == "hold")

        # ── Hold: press once before loop ──
        if is_hold:
            if custom_key:
                self._hold_key(custom_key, press=True)
            else:
                btn = BUTTON_MAP.get(button, Button.left)
                self._mouse.press(btn)

        try:
            while self._running.is_set():
                if duration_ms > 0:
                    elapsed = (time.perf_counter() - start_time) * 1000
                    if elapsed >= duration_ms:
                        break

                if not is_hold:
                    # Posición
                    if random_zone:
                        x1, y1, x2, y2 = random_zone
                        rx = random.randint(min(x1, x2), max(x1, x2))
                        ry = random.randint(min(y1, y2), max(y1, y2))
                        self._mouse.position = (rx, ry)
                    elif fixed_pos:
                        self._mouse.position = fixed_pos

                    # Acción
                    if custom_key:
                        self._press_key(custom_key)
                        self.click_count += 1
                    else:
                        btn = BUTTON_MAP.get(button, Button.left)
                        self._mouse.click(btn, n_clicks)
                        self.click_count += 1

                # Intervalo con variación aleatoria
                if random_interval_ms > 0:
                    variation = random.randint(-random_interval_ms, random_interval_ms) / 1000.0
                    actual_interval = max(0.01, interval + variation)
                else:
                    actual_interval = interval

                remaining = actual_interval
                while remaining > 0 and self._running.is_set():
                    sleep_time = min(remaining, 0.05)
                    time.sleep(sleep_time)
                    remaining -= sleep_time
        finally:
            # ── Hold: release on exit ──
            if is_hold:
                if custom_key:
                    self._hold_key(custom_key, press=False)
                else:
                    btn = BUTTON_MAP.get(button, Button.left)
                    self._mouse.release(btn)

        self._running.clear()
```

Añadir el método `_hold_key` justo después de `_press_key`:

```python
    def _hold_key(self, key_str: str, press: bool) -> None:
        action = self._kb.press if press else self._kb.release
        if len(key_str) == 1:
            action(key_str)
        else:
            try:
                k = getattr(Key, key_str.lower(), None)
                if k:
                    action(k)
            except Exception:
                pass
```

**Step 4: Verificar que los tests pasan**

```bash
python -m pytest tests/test_clicker_hold.py -v
```
Esperado: 3 PASSED.

**Step 5: Commit**

```bash
git add src/core/clicker.py tests/
git commit -m "feat: add hold click_type to Clicker (press+release around loop)"
```

---

### Task 3: UI — tipo de acción universal con opción "Mantener"

**Files:**
- Modify: `src/ui/tab_autoclick.py`

No hay tests de UI — verificar manualmente arrancando la app (`python -m src.main`).

**Step 1: En `_build_ui`, sección "Tipo de acción"**

Localizar este bloque (líneas ~102-107):

```python
        self._lbl_type = ctk.CTkLabel(self._frame_button, text=t("label_type"), font=T.FONT_BODY, text_color=T.text_secondary())
        self._lbl_type.pack(side="left", padx=(0, 8))
        self._click_type_var = ctk.StringVar(value=t("click_single"))
        self._type_menu = ctk.CTkOptionMenu(self._frame_button, variable=self._click_type_var,
                          values=[t("click_single"), t("click_double"), t("click_triple")], width=100, **T.option_menu_style())
        self._type_menu.pack(side="left")
```

Reemplazarlo por:

```python
        self._click_type_var = ctk.StringVar(value=t("click_single"))
```

(Solo dejar la variable — el widget se crea abajo en `_frame_type`.)

**Step 2: Después del bloque `_frame_extra` (tras la línea `self._capture_mouse_btn.pack(side="left")`), añadir `_frame_type`**

Localizar:

```python
        self._capture_mouse_btn.pack(side="left")

        # ── Intervalo ──
```

Insertar entre esas dos líneas:

```python
        # Tipo de acción (universal — para todos los modos)
        self._frame_type = ctk.CTkFrame(body, fg_color="transparent")
        self._frame_type.pack(fill="x", pady=4)
        self._lbl_type = ctk.CTkLabel(self._frame_type, text=t("label_type"), font=T.FONT_BODY, text_color=T.text_secondary())
        self._lbl_type.pack(side="left", padx=(0, 8))
        self._type_menu = ctk.CTkOptionMenu(
            self._frame_type, variable=self._click_type_var,
            values=[t("click_single"), t("click_double"), t("click_triple"), t("click_hold")],
            width=120, **T.option_menu_style(),
        )
        self._type_menu.pack(side="left")

```

**Step 3: Actualizar `_toggle_action` — ya no toca el tipo**

Reemplazar:

```python
    def _toggle_action(self):
        mode = self._action_var.get()
        self._frame_button.pack_forget()
        self._frame_key.pack_forget()
        self._frame_extra.pack_forget()
        if mode == "clic":
            self._frame_button.pack(fill="x", pady=4)
        elif mode == "tecla":
            self._frame_key.pack(fill="x", pady=4)
        elif mode == "extra":
            self._frame_extra.pack(fill="x", pady=4)
```

Por:

```python
    def _toggle_action(self):
        mode = self._action_var.get()
        self._frame_button.pack_forget()
        self._frame_key.pack_forget()
        self._frame_extra.pack_forget()
        if mode == "clic":
            self._frame_button.pack(fill="x", pady=4)
        elif mode == "tecla":
            self._frame_key.pack(fill="x", pady=4)
        elif mode == "extra":
            self._frame_extra.pack(fill="x", pady=4)
        # _frame_type always stays packed — no change needed
```

**Step 4: Actualizar `_do_start` — añadir "hold" al mapa de tipos**

Localizar (líneas ~672-678):

```python
        type_rev = {
            t("click_single"): "single", t("click_double"): "double", t("click_triple"): "triple",
        }
```

Reemplazar por:

```python
        type_rev = {
            t("click_single"): "single", t("click_double"): "double",
            t("click_triple"): "triple", t("click_hold"): "hold",
        }
```

**Step 5: Actualizar `_refresh_lang` — añadir `click_hold` a la lista de tipos**

Localizar (líneas ~456-462):

```python
        old_type = self._click_type_var.get()
        type_keys = ["click_single", "click_double", "click_triple"]
        new_type_vals = [t(k) for k in type_keys]
        self._type_menu.configure(values=new_type_vals)
        _all_type_translations = {STRINGS[k].get("es", ""): k for k in type_keys}
        _all_type_translations.update({STRINGS[k].get("en", ""): k for k in type_keys})
        matched_type = _all_type_translations.get(old_type, "click_single")
        self._click_type_var.set(t(matched_type))
```

Reemplazar por:

```python
        old_type = self._click_type_var.get()
        type_keys = ["click_single", "click_double", "click_triple", "click_hold"]
        new_type_vals = [t(k) for k in type_keys]
        self._type_menu.configure(values=new_type_vals)
        _all_type_translations = {STRINGS[k].get("es", ""): k for k in type_keys}
        _all_type_translations.update({STRINGS[k].get("en", ""): k for k in type_keys})
        matched_type = _all_type_translations.get(old_type, "click_single")
        self._click_type_var.set(t(matched_type))
```

**Step 6: Actualizar `refresh_theme` — eliminar referencias al antiguo `_lbl_type` ubicado en `_frame_button`**

Verificar que `refresh_theme` ya tiene estas líneas y que siguen siendo válidas (el widget `_lbl_type` y `_type_menu` siguen existiendo, solo cambiaron de padre):

```python
        self._lbl_type.configure(text_color=T.text_secondary())
        self._type_menu.configure(**T.option_menu_style())
```

Si existen, no cambiar nada. Si no existen, añadirlas en el bloque "Action type" de `refresh_theme`.

**Step 7: Arrancar la app y verificar manualmente**

```bash
python -m src.main
```

Verificar:
- El selector "Tipo:" aparece siempre visible con 4 opciones (Simple/Doble/Triple/Mantener)
- Cambiar entre modos (Clic ratón / Tecla / Botón extra) no oculta el selector de tipo
- Seleccionar "Mantener" y arrancar → el botón/tecla se mantiene presionado hasta pulsar Stop

**Step 8: Commit**

```bash
git add src/ui/tab_autoclick.py
git commit -m "feat: move action type selector to shared frame, add Hold option"
```

---

### Task 4: Config + Settings — 2 nuevos hotkeys de ciclo

**Files:**
- Modify: `src/utils/config.py`
- Modify: `src/ui/tab_settings.py`

**Step 1: Añadir defaults en `src/utils/config.py`**

Localizar `DEFAULT_CONFIG` y añadir las 4 nuevas claves al final del dict (antes del `}`):

```python
    "hotkey_cycle_profile": "",
    "hotkey_cycle_macro": "",
    "cycle_profile_behavior": "stop_load",
    "cycle_macro_behavior": "stop_load",
```

**Step 2: En `src/ui/tab_settings.py`, extender la sección Hotkeys**

Localizar la lista `hotkeys_info` (líneas ~139-143):

```python
        hotkeys_info = [
            ("hotkey_autoclick", "hk_autoclick", T.neon_green()),
            ("hotkey_record", "hk_record", T.neon_red()),
            ("hotkey_play", "hk_play", T.neon_cyan()),
        ]
```

Reemplazar por:

```python
        hotkeys_info = [
            ("hotkey_autoclick", "hk_autoclick", T.neon_green()),
            ("hotkey_record", "hk_record", T.neon_red()),
            ("hotkey_play", "hk_play", T.neon_cyan()),
            ("hotkey_cycle_profile", "hk_cycle_profile", T.neon_yellow()),
            ("hotkey_cycle_macro", "hk_cycle_macro", T.neon_purple()),
        ]
```

Actualizar también `_hk_color_fns` que está justo encima:

```python
        self._hk_color_fns = {
            "hotkey_autoclick": T.neon_green,
            "hotkey_record": T.neon_red,
            "hotkey_play": T.neon_cyan,
            "hotkey_cycle_profile": T.neon_yellow,
            "hotkey_cycle_macro": T.neon_purple,
        }
```

**Step 3: Añadir dropdowns de comportamiento después del bucle de hotkeys**

Localizar el cierre del bucle `for key, label_key, color in hotkeys_info:` (la última línea que hace `cap_btn.pack(...)`) y añadir justo después:

```python
        # ── Comportamiento de ciclo ──
        self._cycle_behavior_vars = {}
        cycle_behavior_items = [
            ("cycle_profile_behavior", "hk_cycle_profile"),
            ("cycle_macro_behavior", "hk_cycle_macro"),
        ]
        for cfg_key, label_key in cycle_behavior_items:
            row_b = ctk.CTkFrame(body, fg_color="transparent")
            row_b.pack(fill="x", pady=2)
            lbl_b = ctk.CTkLabel(
                row_b, text=f"  {t(label_key)} — {t('label_cycle_behavior')}",
                width=200, anchor="w", font=T.FONT_SMALL, text_color=T.text_muted(),
            )
            lbl_b.pack(side="left")
            saved_beh = self._config.get(cfg_key, "stop_load")
            beh_map = {
                "stop_load": t("cycle_behavior_stop_load"),
                "load_start": t("cycle_behavior_load_start"),
                "select": t("cycle_behavior_select"),
            }
            beh_var = ctk.StringVar(value=beh_map.get(saved_beh, t("cycle_behavior_stop_load")))
            self._cycle_behavior_vars[cfg_key] = beh_var
            beh_menu = ctk.CTkOptionMenu(
                row_b, variable=beh_var,
                values=[t("cycle_behavior_stop_load"), t("cycle_behavior_load_start"), t("cycle_behavior_select")],
                width=160, command=lambda val, k=cfg_key: self._save_cycle_behavior(k, val),
                **T.option_menu_style(),
            )
            beh_menu.pack(side="left", padx=(0, 8))
```

**Step 4: Añadir el método `_save_cycle_behavior` en `TabSettings`**

Localizar cualquier método `_capture_hotkey` u otro método privado y añadir antes de él:

```python
    def _save_cycle_behavior(self, cfg_key: str, display_val: str) -> None:
        rev = {
            t("cycle_behavior_stop_load"): "stop_load",
            t("cycle_behavior_load_start"): "load_start",
            t("cycle_behavior_select"): "select",
        }
        internal = rev.get(display_val, "stop_load")
        self._config = load_config()
        self._config[cfg_key] = internal
        save_config(self._config)
        if self._on_hotkeys_changed:
            self._on_hotkeys_changed(self._config)
```

**Step 5: Arrancar y verificar**

```bash
python -m src.main
```

Ir a Configuración → sección Hotkeys. Verificar que aparecen 2 filas nuevas (Ciclo perfiles / Ciclo macros) con botón capturar y dropdown de comportamiento. Capturar una tecla y comprobar que se guarda.

**Step 6: Commit**

```bash
git add src/utils/config.py src/ui/tab_settings.py
git commit -m "feat: add cycle profile/macro hotkeys and behavior settings"
```

---

### Task 5: App — registrar hotkeys y lógica de ciclo

**Files:**
- Modify: `src/app.py`

**Step 1: Extender `_rebind_hotkeys` con los 2 nuevos hotkeys**

Localizar (líneas ~119-130):

```python
    def _rebind_hotkeys(self, config: dict):
        self._hotkey_mgr.clear()
        hk_ac = config.get("hotkey_autoclick", "F6")
        hk_rec = config.get("hotkey_record", "F7")
        hk_play = config.get("hotkey_play", "F8")

        if hk_ac:
            self._hotkey_mgr.bind(hk_ac, self._toggle_autoclick)
        if hk_rec:
            self._hotkey_mgr.bind(hk_rec, self._toggle_record)
        if hk_play:
            self._hotkey_mgr.bind(hk_play, self._toggle_play)
```

Reemplazar por:

```python
    def _rebind_hotkeys(self, config: dict):
        self._hotkey_mgr.clear()
        hk_ac = config.get("hotkey_autoclick", "F6")
        hk_rec = config.get("hotkey_record", "F7")
        hk_play = config.get("hotkey_play", "F8")
        hk_cp = config.get("hotkey_cycle_profile", "")
        hk_cm = config.get("hotkey_cycle_macro", "")

        if hk_ac:
            self._hotkey_mgr.bind(hk_ac, self._toggle_autoclick)
        if hk_rec:
            self._hotkey_mgr.bind(hk_rec, self._toggle_record)
        if hk_play:
            self._hotkey_mgr.bind(hk_play, self._toggle_play)
        if hk_cp:
            self._hotkey_mgr.bind(hk_cp, self._cycle_profile)
        if hk_cm:
            self._hotkey_mgr.bind(hk_cm, self._cycle_macro)
```

**Step 2: Añadir `_cycle_profile` y `_cycle_macro` justo después de `_toggle_play`**

Localizar:

```python
    def _toggle_play(self):
        self.after(0, self._main_window.tab_recorder.toggle_play)
```

Añadir después:

```python
    def _cycle_profile(self):
        self.after(0, self._do_cycle_profile)

    def _do_cycle_profile(self):
        from src.utils.profiles import list_profiles, load_profile
        profiles = list_profiles()
        if not profiles:
            return
        tab = self._main_window.tab_autoclick
        current = tab._profile_var.get()
        try:
            idx = profiles.index(current)
            next_idx = (idx + 1) % len(profiles)
        except ValueError:
            next_idx = 0
        next_name = profiles[next_idx]
        data = load_profile(next_name)
        if data is None:
            return

        behavior = load_config().get("cycle_profile_behavior", "stop_load")
        if behavior == "stop_load":
            if self._clicker.is_running:
                tab.toggle()
            tab._set_state(data)
            tab._profile_var.set(next_name)
        elif behavior == "load_start":
            was_running = self._clicker.is_running
            if was_running:
                self._clicker.stop()
            tab._set_state(data)
            tab._profile_var.set(next_name)
            tab.toggle()
        elif behavior == "select":
            tab._set_state(data)
            tab._profile_var.set(next_name)

    def _cycle_macro(self):
        self.after(0, self._do_cycle_macro)

    def _do_cycle_macro(self):
        from src.utils.macros import list_macros, load_macro
        from src.core.recorder import Recording
        macros = list_macros()
        if not macros:
            return
        tab = self._main_window.tab_recorder
        current = tab._macro_var.get()
        try:
            idx = macros.index(current)
            next_idx = (idx + 1) % len(macros)
        except ValueError:
            next_idx = 0
        next_name = macros[next_idx]
        data = load_macro(next_name)
        if data is None:
            return

        behavior = load_config().get("cycle_macro_behavior", "stop_load")
        if behavior == "stop_load":
            if self._player.is_playing:
                self._player.stop()
            tab._macro_var.set(next_name)
            self._recorder.recording = Recording.from_list(data)
        elif behavior == "load_start":
            if self._player.is_playing:
                self._player.stop()
            tab._macro_var.set(next_name)
            self._recorder.recording = Recording.from_list(data)
            tab.toggle_play()
        elif behavior == "select":
            tab._macro_var.set(next_name)
            self._recorder.recording = Recording.from_list(data)
```

**Step 3: Verificar que `Recording.from_list` existe**

```bash
python -c "from src.core.recorder import Recording; print(dir(Recording))"
```

Si `from_list` no existe, buscar el método equivalente en `src/core/recorder.py` y ajustar la llamada.

**Step 4: Arrancar y probar**

```bash
python -m src.main
```

1. Crear al menos 2 perfiles guardados en la pestaña AutoClic.
2. Ir a Configuración → asignar una tecla al "Ciclo perfiles" (ej. F9).
3. Pulsar F9 fuera de la app → verificar que el perfil cambia en el dropdown.
4. Repetir para macros con "Ciclo macros".
5. Probar los 3 comportamientos (Parar y cargar / Cargar y arrancar / Solo seleccionar).

**Step 5: Commit**

```bash
git add src/app.py
git commit -m "feat: register cycle profile/macro hotkeys with configurable behavior"
```

---

## Orden de ejecución recomendado

1. Task 1 (i18n) — sin dependencias
2. Task 2 (clicker) — sin dependencias de UI, tiene tests
3. Task 3 (UI tipo universal) — depende de Task 1 para strings
4. Task 4 (config + settings UI) — depende de Task 1 para strings
5. Task 5 (app logic) — depende de Tasks 2, 3, 4
