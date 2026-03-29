# Diseño: Instalador AutoClic con Inno Setup

**Fecha:** 2026-03-24

## Resumen

Crear un instalador `.exe` profesional usando Inno Setup que permita a cualquier usuario instalar AutoClic en su PC.

## Flujo del instalador

1. Pantalla de bienvenida con logo AutoClic
2. Selección de carpeta (default: `C:\Program Files\AutoClic Gz`)
3. Instalación con barra de progreso
4. Opciones post-instalación: acceso directo en Escritorio y/o Menú Inicio
5. Pantalla final con opción de ejecutar la app

## Estructura instalada

```
C:\Program Files\AutoClic Gz\
├── AutoClic.exe
├── config.json         (se crea al primer uso)
├── profiles\           (se crea al primer uso)
├── session_log.json    (se crea al primer uso)
└── unins000.exe        (desinstalador)
```

## Características

- Registro en "Agregar o quitar programas"
- Desinstalador incluido
- Icono personalizado (assets/icon.ico)
- Branding: nombre "AutoClic", publisher "AutoClic Gz"

## Implementación

- Script Inno Setup: `installer/AutoClic_Setup.iss`
- Output: `AutoClic_Setup.exe`
- Requiere Inno Setup 6+ para compilar
