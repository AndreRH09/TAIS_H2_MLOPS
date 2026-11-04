# Andre: [5] Kreuzberger, Kühl y Hirschl (2023)

"Machine Learning Operations (MLOps): Overview, Definition, and Architecture",
*IEEE Access* 11. PDF: `papers/05-kreuzberger-2023.pdf` (CC BY-NC-ND 4.0).

## Por qué te toca

Es la definición de MLOps que usamos. El grupo B se llama "operado con MLOps" porque cumple
lo que este paper define, así que tu lectura sostiene el título del experimento.

## Qué leer (en orden)

1. **p. 5, principios P6–P9:** entrenamiento continuo, metadata, monitoreo y feedback loops.
2. **p. 5–7, componentes C1–C9:** cada uno con herramientas de ejemplo.
3. **p. 9–11, arquitectura y flujo de trabajo:** en especial el monitoreo, el feedback loop y
   los tres modos de disparar el reentrenamiento (p. 11).
4. p. 1–4 si tienes tiempo (metodología: revisión, herramientas y entrevistas).

## Lo clave frente a nuestro experimento

| Lo que dice el paper | Nuestro diseño | ¿Coincide? |
|---|---|---|
| CT = reentrenamiento periódico + evaluación de calidad (p. 5, P6) | B reentrena y registra las métricas de validación (FR-015) | ✔ |
| Registrar parámetros, métricas, datos y código de cada entrenamiento (p. 5, P7) | MLflow con SQLite (Principio II) | ✔ |
| Monitorear datos **y** desempeño (p. 5, P8) | Deriva de features + F1 por ventana | ✔ |
| El reentrenamiento se dispara por umbral, por datos nuevos **o** por calendario (p. 11) | Solo por umbral (deriva o F1) | ◐ Los otros dos modos sirven de comparación (grupo C opcional) |
| Model registry: MLflow como ejemplo (p. 6, C6) | MLflow | ✔ |
| Orquestación: Airflow, Kubeflow… (p. 6, C3) | Script Python | ↔ Justificar como simplificación (Principio IV) |
| Feature store, serving (C4, C8) | No aplica (simulación por lotes) | ↔ Declarar fuera de alcance |

## Qué reutilizar o adaptar (sin copiar)

- **Checklist P1–P9:** convertir los 9 principios en una tabla "principio → cómo lo cumple
  nuestro pipeline → evidencia (archivo o test)". Va en el plan de Spec Kit.
- **Mapa C1–C9 → nuestro stack:** C1 GitHub Actions · C2 GitHub · C3 script Python ·
  C5 local · C6 y C7 MLflow (SQLite) · C9 Evidently · C4 y C8 fuera de alcance.
- **Diagrama de arquitectura:** dibujar **nuestro propio** diagrama, inspirado en el flujo
  end-to-end del paper (p. 9–11) y citándolo. No se reproduce su figura.

## Entregable

- 5 viñetas: qué confirma, qué cuestiona y qué falta en nuestro diseño.
- La tabla P1–P9 completada.
- Propuesta de diagrama (boceto).
