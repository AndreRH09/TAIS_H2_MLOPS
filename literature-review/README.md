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
| [evidencia-clave.md](evidencia-clave.md) | Citas textuales con página de los 4 papers más cercanos ([5], [6], [12], [13]), para subrayar |

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

Cada archivo se nombra con el número de su referencia en [referencias.md](referencias.md).

- `papers/`: versión publicada con licencia abierta (CC BY). Está versionada en git.
- `papers/_local/`: preprint, working paper o PDF de acceso libre **sin** licencia de
  redistribución. Está excluida de git (`.gitignore`), así que cada miembro del equipo debe
  descargarla por su cuenta. La versión citable es siempre la del DOI.

| # | Archivo | Carpeta | Versión |
|---|---|---|---|
| [1] | 01-sculley-2015.pdf | _local | Actas NeurIPS |
| [2] | 02-amershi-2019.pdf | _local | PDF de autores (Microsoft Research) |
| [3] | 03-paleyes-2022.pdf | _local | arXiv v3 (aceptada) |
| [4] | 04-testi-2022.pdf | _local | arXiv v1 (preprint; la versión publicada es CC BY) |
| [5] | 05-kreuzberger-2023.pdf | papers | Publicada, CC BY |
| [6] | 06-cavalcante-2015.pdf | _local | Publicada (IEEE, acceso institucional) |
| [7] | 07-webb-2016.pdf | _local | arXiv |
| [8] | 08-lu-2019.pdf | _local | arXiv |
| [9] | 09-rabanser-2019.pdf | _local | Actas NeurIPS |
| [10] | 10-gemaque-2020.pdf | papers | Publicada, CC BY |
| [11] | 11-celik-2021.pdf | _local | arXiv |
| [12] | 12-bayram-2022.pdf | _local | arXiv |
| [13] | 13-vela-2022.pdf | papers | Publicada, CC BY |
| [14] | 14-hinder-2024.pdf | papers | Publicada, CC BY |
| [15] | 15-bergmeir-2018.pdf | _local | Publicada (Elsevier, acceso institucional) |
| [16] | 16-cerqueira-2020.pdf | _local | arXiv |
| [17] | 17-chicco-2020.pdf | papers | Publicada, CC BY |
| [18] | 18-hewamalage-2023.pdf | papers | Publicada, CC BY |
| [19] | 19-kapoor-2023.pdf | _local | Manuscrito aceptado (NSF PAR) |
| [20] | 20-ballings-2015.pdf | _local | Publicada (Elsevier, acceso institucional) |
| [21] | 21-krauss-2017.pdf | _local | Publicada (Elsevier, acceso institucional) |
| [22] | 22-fischer-2018.pdf | _local | Working paper FAU 11/2017 |
| [23] | 23-gu-2020.pdf | _local | Copia de AQR |
| [24] | 24-bustos-2020.pdf | _local | Publicada (Elsevier, acceso institucional) |

Las 24 fuentes tienen PDF: 6 versionados en `papers/` y 18 locales en `_local/`.
