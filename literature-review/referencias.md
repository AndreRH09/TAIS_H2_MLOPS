# Referencias (IEEE)

Leyenda de ejes: **A** MLOps · **B** deriva y reentrenamiento · **C** evaluación temporal ·
**D** predicción de dirección bursátil.

| # | Eje | Lectura | Decisiones que respalda |
|---|---|---|---|
| [1]–[5] | A | resumen | Marco general (D5, D6) |
| [6]–[14] | B | resumen | D5, D6 |
| [15]–[19] | C | resumen | D1, D2, D4, D7 |
| [20]–[24] | D | resumen | D1, D3, D4 |

## A. MLOps general

**[1]** D. Sculley *et al.*, "Hidden technical debt in machine learning systems," in *Adv.
Neural Inf. Process. Syst. 28 (NIPS 2015)*, 2015, pp. 2503–2511. [Online]. Available:
https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems
> Describe costos de mantenimiento ocultos en sistemas de ML. Entre los factores de riesgo
> incluye los "cambios en el mundo externo", que son la motivación del monitoreo continuo.

**[2]** S. Amershi *et al.*, "Software engineering for machine learning: A case study," in
*Proc. IEEE/ACM 41st Int. Conf. Softw. Eng.: Softw. Eng. Pract. (ICSE-SEIP)*, 2019, pp. 291–300,
doi: [10.1109/ICSE-SEIP.2019.00042](https://doi.org/10.1109/ICSE-SEIP.2019.00042).
> Caso Microsoft: flujo de ML de nueve etapas que termina en monitoreo. Señala la gestión de
> datos como la diferencia principal frente al software tradicional.

**[3]** A. Paleyes, R.-G. Urma, and N. D. Lawrence, "Challenges in deploying machine learning:
A survey of case studies," *ACM Comput. Surv.*, vol. 55, no. 6, Art. no. 114, 2022,
doi: [10.1145/3533378](https://doi.org/10.1145/3533378).
> Revisión de casos de despliegue: hay problemas en todas las etapas, también en la de
> monitoreo y actualización.

**[4]** M. Testi *et al.*, "MLOps: A taxonomy and a methodology," *IEEE Access*, vol. 10,
pp. 63606–63618, 2022, doi: [10.1109/ACCESS.2022.3181730](https://doi.org/10.1109/ACCESS.2022.3181730).
> Taxonomía de MLOps y un pipeline de diez pasos que incluye entrenamiento y monitoreo
> continuos.

**[5]** D. Kreuzberger, N. Kühl, and S. Hirschl, "Machine learning operations (MLOps):
Overview, definition, and architecture," *IEEE Access*, vol. 11, pp. 31866–31879, 2023,
doi: [10.1109/ACCESS.2023.3262138](https://doi.org/10.1109/ACCESS.2023.3262138).
> Definición de MLOps a partir de una revisión de literatura, revisión de herramientas y
> entrevistas. Es la referencia del concepto "operado con MLOps" en este estudio.

## B. Deriva y reentrenamiento

**[6]** R. C. Cavalcante and A. L. I. Oliveira, "An approach to handle concept drift in
financial time series based on extreme learning machines and explicit drift detection," in
*Proc. Int. Joint Conf. Neural Netw. (IJCNN)*, 2015, pp. 1–8,
doi: [10.1109/IJCNN.2015.7280721](https://doi.org/10.1109/IJCNN.2015.7280721).
> Series financieras: el modelo se actualiza solo cuando un detector explícito (DDM, ECDD)
> señala deriva. Mantiene la precisión y reduce el costo. Es el antecedente más cercano al
> grupo B.

**[7]** G. I. Webb, R. Hyde, H. Cao, H. L. Nguyen, and F. Petitjean, "Characterizing concept
drift," *Data Min. Knowl. Discov.*, vol. 30, no. 4, pp. 964–994, 2016,
doi: [10.1007/s10618-015-0448-4](https://doi.org/10.1007/s10618-015-0448-4).
> Definiciones formales y taxonomía de los tipos de deriva, con un marco cuantitativo para
> analizarla.

**[8]** J. Lu, A. Liu, F. Dong, F. Gu, J. Gama, and G. Zhang, "Learning under concept drift:
A review," *IEEE Trans. Knowl. Data Eng.*, vol. 31, no. 12, pp. 2346–2363, 2019,
doi: [10.1109/TKDE.2018.2876857](https://doi.org/10.1109/TKDE.2018.2876857).
> Revisa más de 130 trabajos. Marco de tres componentes: detección, comprensión y adaptación
> a la deriva. (Acceso anticipado en 2018.)

**[9]** S. Rabanser, S. Günnemann, and Z. Lipton, "Failing loudly: An empirical study of
methods for detecting dataset shift," in *Adv. Neural Inf. Process. Syst. 32 (NeurIPS 2019)*,
2019, pp. 1396–1408. [Online]. Available:
https://proceedings.neurips.cc/paper/2019/hash/846c260d715e5b854ffad5f70a516c88-Abstract.html
> Compara métodos de detección de cambio de distribución. Los mejores resultados los dan los
> tests de dos muestras sobre representaciones de baja dimensión.

**[10]** R. N. Gemaque, A. F. J. Costa, R. Giusti, and E. M. dos Santos, "An overview of
unsupervised drift detection methods," *WIREs Data Min. Knowl. Discov.*, vol. 10, Art. no.
e1381, 2020, doi: [10.1002/widm.1381](https://doi.org/10.1002/widm.1381).
> Detectores no supervisados, para cuando las etiquetas no están disponibles inmediatamente
> después de la predicción. Taxonomía.

**[11]** B. Celik and J. Vanschoren, "Adaptation strategies for automated machine learning on
evolving data," *IEEE Trans. Pattern Anal. Mach. Intell.*, vol. 43, no. 9, pp. 3067–3078, 2021,
doi: [10.1109/TPAMI.2021.3062900](https://doi.org/10.1109/TPAMI.2021.3062900).
> Seis estrategias de adaptación ante la deriva, evaluadas sobre flujos reales y sintéticos.
> Sirve para comparar políticas de reentrenamiento.

**[12]** F. Bayram, B. S. Ahmed, and A. Kassler, "From concept drift to model degradation: An
overview on performance-aware drift detectors," *Knowl.-Based Syst.*, vol. 245, Art. no.
108632, 2022, doi: [10.1016/j.knosys.2022.108632](https://doi.org/10.1016/j.knosys.2022.108632).
> Revisa 66 detectores basados en desempeño (por ejemplo, control estadístico del error).
> Respalda el disparador "caída de F1".

**[13]** D. Vela *et al.*, "Temporal quality degradation in AI models," *Sci. Rep.*, vol. 12,
Art. no. 11654, 2022, doi: [10.1038/s41598-022-15245-z](https://doi.org/10.1038/s41598-022-15245-z).
> "Envejecimiento" de modelos en 32 datasets (incluye finanzas) con 4 modelos estándar. El
> desempeño puede degradarse aunque los datos parezcan estables.

**[14]** F. Hinder, V. Vaquet, and B. Hammer, "One or two things we know about concept
drift—A survey on monitoring in evolving environments. Part A: Detecting concept drift,"
*Front. Artif. Intell.*, vol. 7, Art. no. 1330257, 2024,
doi: [10.3389/frai.2024.1330257](https://doi.org/10.3389/frai.2024.1330257).
> Revisión reciente de la detección de deriva no supervisada en flujos de datos.

## C. Evaluación temporal

**[15]** C. Bergmeir, R. J. Hyndman, and B. Koo, "A note on the validity of cross-validation
for evaluating autoregressive time series prediction," *Comput. Stat. Data Anal.*, vol. 120,
pp. 70–83, 2018, doi: [10.1016/j.csda.2017.11.003](https://doi.org/10.1016/j.csda.2017.11.003).
> La validación cruzada K-fold solo es válida para modelos puramente autorregresivos con
> errores no correlacionados. Fuera de ese caso hace falta evaluación temporal.

**[16]** V. Cerqueira, L. Torgo, and I. Mozetič, "Evaluating time series forecasting models:
An empirical study on performance estimation methods," *Mach. Learn.*, vol. 109,
pp. 1997–2028, 2020, doi: [10.1007/s10994-020-05910-7](https://doi.org/10.1007/s10994-020-05910-7).
> Estudio empírico que compara métodos de estimación del desempeño (validación cruzada frente
> a out-of-sample) en series reales.

**[17]** D. Chicco and G. Jurman, "The advantages of the Matthews correlation coefficient (MCC)
over F1 score and accuracy in binary classification evaluation," *BMC Genomics*, vol. 21,
Art. no. 6, 2020, doi: [10.1186/s12864-019-6413-7](https://doi.org/10.1186/s12864-019-6413-7).
> F1 ignora los verdaderos negativos y cambia si se intercambia la clase positiva. MCC es
> simétrico y más informativo.

**[18]** H. Hewamalage, K. Ackermann, and C. Bergmeir, "Forecast evaluation for data
scientists: Common pitfalls and best practices," *Data Min. Knowl. Discov.*, vol. 37, no. 2,
pp. 788–832, 2023, doi: [10.1007/s10618-022-00894-5](https://doi.org/10.1007/s10618-022-00894-5).
> Errores de evaluación (partición, métricas, tests) que hacen parecer competitivos a métodos
> que no lo son.

**[19]** S. Kapoor and A. Narayanan, "Leakage and the reproducibility crisis in
machine-learning-based science," *Patterns*, vol. 4, no. 9, Art. no. 100804, 2023,
doi: [10.1016/j.patter.2023.100804](https://doi.org/10.1016/j.patter.2023.100804).
> La fuga de información afecta a al menos 294 artículos en 17 disciplinas. Al corregirla, ML
> deja de superar a la regresión logística.

## D. Predicción de dirección bursátil

**[20]** M. Ballings, D. Van den Poel, N. Hespeels, and R. Gryp, "Evaluating multiple
classifiers for stock price direction prediction," *Expert Syst. Appl.*, vol. 42, no. 20,
pp. 7046–7056, 2015, doi: [10.1016/j.eswa.2015.05.013](https://doi.org/10.1016/j.eswa.2015.05.013).
> En 5 767 empresas europeas, Random Forest queda primero y la regresión logística última
> (AUC, horizonte de un año).

**[21]** C. Krauss, X. A. Do, and N. Huck, "Deep neural networks, gradient-boosted trees,
random forests: Statistical arbitrage on the S&P 500," *Eur. J. Oper. Res.*, vol. 259, no. 2,
pp. 689–702, 2017, doi: [10.1016/j.ejor.2016.10.031](https://doi.org/10.1016/j.ejor.2016.10.031).
> S&P 500, 1992–2015, con evaluación fuera de muestra. RF entre los modelos comparados; la
> rentabilidad cae en los años recientes.

**[22]** T. Fischer and C. Krauss, "Deep learning with long short-term memory networks for
financial market predictions," *Eur. J. Oper. Res.*, vol. 270, no. 2, pp. 654–669, 2018,
doi: [10.1016/j.ejor.2017.11.054](https://doi.org/10.1016/j.ejor.2017.11.054).
> Dirección fuera de muestra en el S&P 500 con RF y regresión logística como benchmarks. El
> exceso de retorno desaparece después de 2010.

**[23]** S. Gu, B. Kelly, and D. Xiu, "Empirical asset pricing via machine learning," *Rev.
Financ. Stud.*, vol. 33, no. 5, pp. 2223–2273, 2020,
doi: [10.1093/rfs/hhaa009](https://doi.org/10.1093/rfs/hhaa009).
> Comparación de métodos de ML para estimar primas de riesgo. Árboles y redes rinden mejor por
> las interacciones no lineales.

**[24]** O. Bustos and A. Pomares-Quimbaya, "Stock market movement forecast: A systematic
review," *Expert Syst. Appl.*, vol. 156, Art. no. 113464, 2020,
doi: [10.1016/j.eswa.2020.113464](https://doi.org/10.1016/j.eswa.2020.113464).
> Revisión sistemática 2014–2018 de técnicas para predecir el movimiento del mercado.
