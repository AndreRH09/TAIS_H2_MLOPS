# Constitución del proyecto TAIS_H2_MLOPS

Estudio experimental: modelo estático frente a modelo operado con MLOps (monitoreo de deriva y
reentrenamiento) sobre la serie diaria de MSFT.

## Core Principles

### I. Integridad temporal (NO NEGOCIABLE)

- Toda partición de datos MUST ser temporal; se prohíbe la partición aleatoria y el barajado
  entre periodos.
- Cada feature del instante *t* MUST calcularse solo con información disponible hasta *t*;
  la etiqueta de *t* (dirección en *t+1*) MUST NOT filtrarse a las features.
- Escalado, selección de hiperparámetros y referencias de deriva MUST ajustarse solo con datos
  anteriores a la ventana evaluada.
- La ausencia de fuga (*leakage*) MUST verificarse con tests automatizados.

**Razón:** con series temporales, la fuga de información infla las métricas e invalida la
comparación entre grupos.

### II. Reproducibilidad

- Dependencias MUST fijarse en `pyproject.toml` + `uv.lock`.
- Toda fuente de aleatoriedad MUST usar una semilla fija y registrada.
- El dataset de entrada MUST versionarse (archivo + hash) y su procedencia documentarse.
- Todo run (entrenamiento, predicción por ventana, reentrenamiento) MUST registrarse en MLflow
  con parámetros, métricas, semilla y versión de datos.
- Ejecutar el experimento dos veces con la misma configuración MUST producir métricas idénticas.

**Razón:** un resultado experimental que no puede repetirse no puede evaluarse.

### III. Comparabilidad entre grupos experimentales

- Los grupos A (control, sin reentrenamiento), B (reentrenamiento por monitoreo) y C
  (reentrenamiento periódico) MUST compartir, dentro de cada réplica, algoritmo,
  hiperparámetros iniciales, features, ventanas de prueba y métricas.
- La única diferencia permitida entre grupos MUST ser la política de reentrenamiento.
- Umbrales de deriva y de F1, y la ventana de reentrenamiento, MUST fijarse antes de ver los
  resultados de prueba y documentarse en la especificación.
- Las métricas (Precision, Recall, F1) MUST reportarse por ventana para todos los grupos, junto
  con el número de reentrenamientos de B y C.

**Razón:** el efecto medido debe atribuirse a la operación MLOps y no a otra variable.

### IV. Evidencia verificada y simplicidad

- Cada decisión de diseño experimental (partición, baseline, disparador de reentrenamiento,
  métricas) MUST respaldarse en al menos una fuente revisada por pares, citada en formato IEEE.
- Cada referencia MUST verificarse por DOI o fuente editorial; se prohíben citas no verificadas.
- Las referencias MUST mantenerse legibles en el repositorio (Markdown).
- Herramientas de producción a escala (Kubernetes, Kafka, Feast, Prometheus/Grafana, Kubeflow)
  MUST NOT incorporarse salvo justificación documentada ligada al objetivo del experimento.

**Razón:** el estudio contrasta su diseño con la literatura; la complejidad sin propósito
añade riesgo sin aportar validez.

## Restricciones técnicas

- Lenguaje: Python, entorno gestionado con `uv`.
- Modelado y métricas: scikit-learn.
- Detección de deriva: Evidently.
- Seguimiento y registro de modelos: MLflow con backend SQLite local.
- Datos: archivos CSV/Parquet versionados; sin servidor de base de datos.
- Orquestación: script Python que ejecuta el bucle walk-forward y decide el reentrenamiento.
- Integración continua: GitHub Actions con lint (ruff) y tests (pytest).

## Flujo de trabajo y calidad

- Todo trabajo MUST realizarse en una rama dedicada (`chore/…`, `docs/…` o rama de feature de
  Spec Kit `NNN-…`); `main` MUST NOT recibir commits directos.
- Cada cambio MUST seguir el flujo Spec Kit: constitución → especificación → plan → tareas →
  implementación.
- CI MUST pasar (ruff + pytest) antes de integrar una rama.
- Documentación del proyecto en español; términos técnicos en inglés.

## Governance

- Esta constitución prevalece sobre cualquier otra práctica del repositorio.
- Las enmiendas MUST documentarse en este archivo, con justificación y aumento de versión.
- Versionado semántico: MAJOR para eliminar o redefinir principios; MINOR para añadir principios
  o secciones; PATCH para aclaraciones de redacción.
- Cada especificación y plan MUST incluir una verificación de cumplimiento de estos principios.

**Version**: 1.1.0 | **Ratified**: 2026-11-03 | **Last Amended**: 2026-11-03
