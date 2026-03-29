# Índice raíz de Skills por categorías

Usá este archivo como **puerta de entrada**: te dice **qué .md abrir** según lo que te pidan.

## Cómo usar (flujo recomendado)

1. **Identificá la intención** del pedido (p. ej. “analizar código”, “rediseñar layout”, “preparar CI/CD”, “emails transaccionales”).
2. En el **mapa tarea → categoría** de abajo, elegí 1–3 categorías relevantes.
3. Abrí los `.md` de esas categorías.
4. Dentro del `.md` de categoría, mirá el **Índice de skills** (arriba) y elegí la skill específica.
5. Usá el **Ejemplo de prompt** de esa skill como base y adaptalo a tu caso.

## Mapa rápido: tarea → qué .md leer

- **Analizar / depurar / refactorizar / revisar PRs / migrar frameworks** → `CAT_codigo_y_ingenieria.md`
- **Rediseñar layout, UI, componentes, responsive, pautas visuales** → `CAT_diseno_ui_ux.md`
- **Cloud, Kubernetes, CI/CD, monitoreo, despliegues** → `CAT_infra_devops.md`
- **Seguridad, auditorías, compliance, incidentes, accesibilidad/WCAG** → `CAT_seguridad_compliance.md`
- **ETL, pipelines de datos, BI, SQL/DB design, ML ops, trading cuantitativo** → `CAT_datos_ml_finanzas.md`
- **Construir apps con LLM (RAG, agentes, eval, guardrails)** → `CAT_ia_llm_aplicaciones.md`
- **Coordinar agentes/equipos, consolidar revisiones, orquestación** → `CAT_agentes_orquestacion.md`
- **Estrategia de producto/negocio, análisis startup, pagos** → `CAT_negocio_producto_pagos.md`
- **Emails transaccionales (Resend), plantillas HTML/TXT, deliverability (SPF/DKIM/DMARC), compliance, bounces/complaints** →
  - `CAT_negocio_producto_pagos.md` (copy/estructura/flujo de producto + “email-best-practices”)
  - `CAT_infra_devops.md` (DNS/DMARC/SPF/DKIM y configuración)
  - `CAT_codigo_y_ingenieria.md` (integración en código, templates, tests/scripts)
- **Blockchain/Web3** → `CAT_blockchain_web3.md`
- **Videojuegos** → `CAT_game_development.md`

## Archivos de categorías disponibles

- **CAT_codigo_y_ingenieria.md** — Código, análisis y desarrollo
- **CAT_diseno_ui_ux.md** — Diseño UI/UX y creación visual
- **CAT_infra_devops.md** — Infraestructura, DevOps y despliegue
- **CAT_seguridad_compliance.md** — Seguridad, compliance y respuesta a incidentes
- **CAT_datos_ml_finanzas.md** — Datos, analítica, ML y finanzas cuantitativas
- **CAT_ia_llm_aplicaciones.md** — IA aplicada y desarrollo de apps con LLM
- **CAT_agentes_orquestacion.md** — Agentes, orquestación y coordinación
- **CAT_negocio_producto_pagos.md** — Negocio, producto y pagos
- **CAT_blockchain_web3.md** — Blockchain y Web3
- **CAT_game_development.md** — Desarrollo de videojuegos

## Ejemplo de uso (rápido)

- Pedido: *“Rediseñar cómo se ve un layout y hacerlo responsive”*
  1) Abrí `CAT_diseno_ui_ux.md`.
  2) En su **Índice de skills**, buscá skills como `responsive-design`, `web-component-design`, etc.
  3) Elegí la skill y copiá su **Ejemplo de prompt**, agregando tu layout/constraints.

- Pedido: *“Revisar un PR y mejorar performance”*
  1) Abrí `CAT_codigo_y_ingenieria.md`.
  2) Usá skills como `code-review-excellence`, `application-performance` (si aparece) o equivalentes.

- Pedido: *“Actualizar los emails de autenticación/reset/recordatorios con Resend y mejorar deliverability”*
  1) Abrí `CAT_negocio_producto_pagos.md` (copy + flujos + email-best-practices).
  2) Abrí `CAT_infra_devops.md` (SPF/DKIM/DMARC).
  3) Abrí `CAT_codigo_y_ingenieria.md` (integración, templates, scripts de prueba con resend-automation).

## Nota importante
- Todos los `.md` **CAT** están en `.claude/`
- Todas las **skills** están en `.claude/Skills/`