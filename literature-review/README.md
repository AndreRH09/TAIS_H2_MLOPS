# Revisión de literatura

Respaldo bibliográfico de las decisiones de diseño de
[specs/001-mlops-drift-experiment/spec.md](../specs/001-mlops-drift-experiment/spec.md),
exigido por el Principio IV de la [constitución](../.specify/memory/constitution.md).

## Contenido

| Archivo | Qué contiene |
|---|---|
| [referencias.md](referencias.md) | 24 fuentes revisadas por pares en formato IEEE, anotadas, con DOI o fuente editorial |
| [decisiones.md](decisiones.md) | Cada decisión del diseño (D1–D7) con las fuentes que la respaldan o la cuestionan |
| [matriz-contraste.md](matriz-contraste.md) | Comparación del diseño propio con los estudios empíricos |

## Criterios de inclusión

- Revisión por pares (revista o actas de conferencia con arbitraje). Sin preprints sin publicar
  ni literatura gris.
- Publicadas entre 2015 y 2026.
- Identificador verificable: DOI que resuelve al documento, o página de las actas oficiales
  (NeurIPS no asigna DOI).
- Ejes temáticos: (A) MLOps general; (B) deriva de datos/concepto y reentrenamiento;
  (C) evaluación temporal y walk-forward; (D) predicción de dirección bursátil, como referencia
  para la tarea concreta.

## Excluidas por no poder verificar su DOI

| Fuente | Motivo |
|---|---|
| E. Breck *et al.*, "The ML Test Score…", IEEE BigData 2017 | No se confirmó el DOI en IEEE Xplore |
| A. Mahadevan y M. Mathioudakis, "Cost-aware retraining…", Knowl.-Based Syst. 2024 | No se confirmó el DOI de la versión publicada |

Se pueden reincorporar cuando su DOI se verifique de forma manual.

## Estado de lectura

Las anotaciones se basan en el resumen y en los metadatos verificados de cada fuente. La
columna **Lectura** de [referencias.md](referencias.md) indica `resumen` hasta que alguien del
equipo lea el texto completo; en ese momento se cambia a `completa`. Las afirmaciones de
[decisiones.md](decisiones.md) que dependen de detalles no presentes en el resumen están
marcadas con ⚠.

## PDFs

No se guardan PDFs en el repositorio por derechos de autor. Cada referencia enlaza al DOI y,
cuando existe, a una versión de acceso abierto (PMC, arXiv, repositorio institucional).
