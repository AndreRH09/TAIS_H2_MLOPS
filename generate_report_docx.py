import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def create_report():
    doc = Document()

    # Configure Margins: 2.54 cm (1 inch) all around
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)
        
        # Configure Header & Footer
        header = s.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("INFORME TÉCNICO EXPERIMENTAL: MLOPS VS. MODELO ESTÁTICO | TAIS_H2_MLOPS")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(120, 120, 120)

        footer = s.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        frun = fp.add_run("Proyecto TAIS_H2_MLOPS — Evaluación de Estrategias de Gobernanza MLOps")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(120, 120, 120)

    # Styles & Palette
    # Primary: #1B365D (Navy)
    # Secondary: #2B5B84 (Steel Blue)
    # Dark text: #222222
    # Light bg: #F0F4F8
    # Subtle border: #D0D7DE
    PRIMARY = RGBColor(27, 54, 93)
    SECONDARY = RGBColor(43, 91, 132)
    TEXT_COLOR = RGBColor(34, 34, 34)
    GRAY_TEXT = RGBColor(100, 100, 100)

    def style_run(run, font_name="Calibri", size_pt=11, bold=False, italic=False, color=TEXT_COLOR):
        run.font.name = font_name
        run.font.size = Pt(size_pt)
        run.bold = bold
        run.italic = italic
        run.font.color.rgb = color

    def add_para(doc, text="", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=6, line_spacing=1.15):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if text:
            r = p.add_run(text)
            style_run(r)
        return p

    def add_heading_1(doc, text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        style_run(r, font_name="Calibri", size_pt=15, bold=True, color=PRIMARY)
        return p

    def add_heading_2(doc, text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        style_run(r, font_name="Calibri", size_pt=12.5, bold=True, color=SECONDARY)
        return p

    def add_heading_3(doc, text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        style_run(r, font_name="Calibri", size_pt=11, bold=True, color=PRIMARY)
        return p

    def set_cell_props(cell, fill_hex=None, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        if fill_hex:
            shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
            tcPr.append(shd)
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def format_table(table, col_widths, align_cols=None):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for row in table.rows:
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
            for i, cell in enumerate(row.cells):
                cell.width = Inches(col_widths[i])
                if align_cols and i in align_cols:
                    for p in cell.paragraphs:
                        p.alignment = align_cols[i]

    # ==========================
    # TITLE & METADATA
    # ==========================
    p_meta = add_para(doc, "CÓDIGO: INF-MLOPS-2026-001 | RAMA: 001-mlops-drift-experiment", space_after=2)
    style_run(p_meta.runs[0], size_pt=9, bold=True, color=GRAY_TEXT)

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("INFORME TÉCNICO Y EXPERIMENTAL: EVALUACIÓN DE ESTRATEGIAS DE GOBERNANZA MLOps FRENTE A MODELOS ESTÁTICOS EN SERIES TEMPORALES FINANCIERAS")
    style_run(r_title, font_name="Calibri", size_pt=20, bold=True, color=PRIMARY)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("Estudio empírico de modelo estático (A) vs. monitoreo de deriva y reentrenamiento reactivo (B) vs. reentrenamiento periódico (C) sobre la serie diaria de MSFT (2021–2026)")
    style_run(r_sub, font_name="Calibri", size_pt=12, italic=True, color=SECONDARY)

    # Metadata Table
    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.autofit = False
    col_w = [2.2, 4.3]
    meta_data = [
        ("Proyecto / Código", "TAIS_H2_MLOPS — Feature Branch 001-mlops-drift-experiment"),
        ("Equipo de Investigación", "Andre, Frank, Paul, Willy (Equipo de Desarrollo MLOps)"),
        ("Activo y Periodo", "Microsoft Corporation (MSFT), 04-feb-2021 a 02-feb-2026 (1254 filas diarias)"),
        ("Dataset y Validación", "SHA-256 verificado (1617484d...), validado externamente contra Yahoo Finance"),
        ("Tecnologías y Stack", "Python 3.12, UV, Scikit-Learn 1.9, Evidently 0.7, MLflow 3.18, SciPy 1.18"),
        ("Fecha de Emisión", "Noviembre 2026 — Estado: Verificado y Reproducible")
    ]
    for idx, (label, val) in enumerate(meta_data):
        row = meta_table.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.text = label
        c1.text = val
        style_run(c0.paragraphs[0].runs[0], size_pt=9.5, bold=True, color=PRIMARY)
        style_run(c1.paragraphs[0].runs[0], size_pt=9.5, color=TEXT_COLOR)
        set_cell_props(c0, fill_hex="F0F4F8", top=60, bottom=60, left=100, right=100)
        set_cell_props(c1, fill_hex="FFFFFF", top=60, bottom=60, left=100, right=100)
    format_table(meta_table, col_w)

    add_para(doc, space_after=12)

    # Executive Summary Box
    summary_table = doc.add_table(rows=1, cols=1)
    summary_cell = summary_table.rows[0].cells[0]
    set_cell_props(summary_cell, fill_hex="F7FAFC", top=140, bottom=140, left=180, right=180)
    summary_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    summary_cell.width = Inches(6.5)
    
    p_sum_title = summary_cell.paragraphs[0]
    p_sum_title.paragraph_format.space_after = Pt(4)
    r_sum_title = p_sum_title.add_run("RESUMEN EJECUTIVO")
    style_run(r_sum_title, font_name="Calibri", size_pt=11.5, bold=True, color=PRIMARY)

    p_sum_body = summary_cell.add_paragraph()
    p_sum_body.paragraph_format.line_spacing = 1.15
    p_sum_body.paragraph_format.space_after = Pt(0)
    r_sum_body = p_sum_body.add_run(
        "El presente informe formaliza los resultados de un experimento cuantitativo diseñado para verificar si una arquitectura "
        "operada con MLOps mediante monitoreo continuo y reentrenamiento automático (Grupo B) o reentrenamiento periódico (Grupo C) "
        "ofrece una ventaja real frente a un modelo estático congelado (Grupo A) en la predicción direccional diaria de las acciones de Microsoft (MSFT). "
        "A través de una evaluación walk-forward semestral en 8 ventanas (2022-H1 a 2025-H2) sobre dos réplicas algorítmicas (Regresión Logística y Random Forest) "
        "y tres baselines ingenuos, los resultados demuestran que no existen diferencias estadísticamente significativas entre mantener el modelo fijo y "
        "reentrenarlo periódica o reactivamente (p = 0.8125 en LogReg; p = 0.9375 en RF mediante test de Wilcoxon pareado). "
        "La hipersensibilidad de los detectores de deriva de datos provocó reentrenamientos en 7 de las 8 ventanas, haciendo colapsar la política reactiva en la periódica. "
        "Asimismo, el clasificador ingenuo 'Siempre Sube' superó a todos los modelos de Machine Learning (F1 = 0.685 vs. 0.53-0.55), evidenciando el sesgo alcista secular del activo "
        "y la necesidad crítica de emplear baselines de referencia en la evaluación de sistemas MLOps."
    )
    style_run(r_sum_body, font_name="Calibri", size_pt=10, italic=False, color=TEXT_COLOR)

    add_para(doc, space_after=12)

    # ==========================
    # 1. INTRODUCCIÓN
    # ==========================
    add_heading_1(doc, "1. INTRODUCCIÓN")
    
    add_heading_2(doc, "1.1. Contexto y Motivación")
    p = add_para(doc)
    p.add_run(
        "En la ingeniería de aprendizaje automático aplicada a los mercados de capitales, la no estacionariedad de las series temporales "
        "constituye uno de los desafíos más complejos. Las condiciones macroeconómicas, la liquidez, las tasas de interés y los cambios estructurales "
        "en las expectativas de los inversores generan continuas alteraciones distributivas (conocidas como concept drift y data drift). "
        "Bajo un enfoque clásico de ciencia de datos, los modelos suelen desarrollarse y desplegarse como artefactos estáticos, asumiendo implícitamente "
        "cierta estabilidad funcional. Sin embargo, la evidencia ha demostrado que los modelos sufren de degradación temporal progresiva (model aging), "
        "perdiendo precisión predictiva conforme transcurre el tiempo desde su entrenamiento inicial."
    )

    add_heading_2(doc, "1.2. Planteamiento del Problema en Producción")
    p = add_para(doc)
    p.add_run(
        "Para responder a esta vulnerabilidad operativa ha surgido el paradigma de MLOps (Machine Learning Operations), que propone automatizar "
        "el ciclo de vida completo mediante monitoreo continuo del rendimiento y reentrenamiento reactivo. No obstante, en tareas financieras con baja "
        "relación señal-ruido, como la predicción de la dirección del precio de cierre del día siguiente, surge una disyuntiva crítica de ingeniería: "
        "¿Representa el reentrenamiento frecuente una mejora genuina de la capacidad predictiva o conduce a un sobreajuste al ruido transitorio reciente? "
        "¿Justifica el beneficio predictivo la sustancial sobrecarga computacional, de observabilidad y de gobernanza que exige un flujo continuo de MLOps?"
    )

    add_heading_2(doc, "1.3. Alcance y Propósito del Experimento")
    p = add_para(doc)
    p.add_run(
        "El proyecto TAIS_H2_MLOPS aborda este problema mediante una metodología estrictamente controlada y determinista. "
        "Se evalúan tres políticas de ciclo de vida sobre la cotización diaria de Microsoft Corporation (MSFT) entre febrero de 2021 y febrero de 2026: "
        "el Grupo A (control estático), el Grupo B (MLOps reactivo ante deriva estadística de features o caída de F1) y el Grupo C (MLOps periódico ciego). "
        "El objetivo es comparar objetivamente el desempeño predictivo, la tasa de reentrenamientos y la estabilidad operativa, contrastando el diseño frente a la literatura revisada por pares."
    )

    # ==========================
    # 2. TRABAJOS RELACIONADOS
    # ==========================
    add_heading_1(doc, "2. TRABAJOS RELACIONADOS")
    p = add_para(doc)
    p.add_run(
        "El diseño experimental se sustenta y contrasta rigurosamente con una base de 24 publicaciones científicas revisadas por pares (2015–2026) "
        "en formato IEEE, estructuradas en cuatro ejes conceptuales clave:"
    )

    add_heading_2(doc, "2.1. Marco Conceptual de MLOps y Operación Continua (Eje A)")
    p = add_para(doc)
    p.add_run(
        "El estudio pionero de Sculley et al. [1] introdujo el concepto de deuda técnica en sistemas de ML, resaltando que los cambios del entorno exterior "
        "representan uno de los mayores factores de riesgo que justifican el monitoreo continuo. Amershi et al. [2], en un estudio empírico dentro de Microsoft, "
        "evidenciaron que la gestión de la evolución de datos es el factor diferenciador crítico frente a la ingeniería de software clásica. "
        "Paleyes et al. [3] y Testi et al. [4] documentaron taxonomías de despliegue donde el entrenamiento y monitoreo continuo son componentes nucleares. "
        "Kreuzberger et al. [5] compilaron la arquitectura canónica de MLOps a través de 9 principios (P1–P9) y 9 componentes (C1–C9), distinguiendo explícitamente "
        "entre el reentrenamiento reactivo activado por monitoreo (Grupo B) y el reentrenamiento programado de forma periódica (Grupo C)."
    )

    add_heading_2(doc, "2.2. Detección de Deriva de Datos y Adaptación (Eje B)")
    p = add_para(doc)
    p.add_run(
        "La caracterización formal de la deriva de concepto fue delimitada por Webb et al. [7] y sistematizada por Lu et al. [8] bajo el esquema de "
        "detección, comprensión y adaptación. Rabanser et al. [9] demostraron empíricamente que las pruebas de dos muestras univariadas (como el test de Kolmogorov-Smirnov) "
        "con corrección de Bonferroni poseen una potencia de detección equiparable a métodos multivariados de alta complejidad. Gemaque et al. [10] y Hinder et al. [14] "
        "analizaron detectores no supervisados para escenarios donde las etiquetas se reciben con retardo. En adaptación de modelos, Celik y Vanschoren [11] evaluaron políticas "
        "por lotes y ventanas deslizantes. Bayram et al. [12] demostraron la necesidad de supervisar métricas basadas en desempeño para mitigar falsas alarmas derivadas "
        "de cambios distributivos inocuos. El antecedente empírico más directo de este proyecto es Cavalcante y Oliveira [6], quienes en series bursátiles aplicaron detectores "
        "explícitos (DDM/ECDD), concluyendo que reentrenar por eventos mantiene la precisión y reduce el costo operacional, aunque advirtieron periodos de inestabilidad transitoria."
    )

    add_heading_2(doc, "2.3. Metodología de Evaluación Temporal y Fuga de Información (Eje C)")
    p = add_para(doc)
    p.add_run(
        "Bergmeir et al. [15] demostraron que la validación cruzada k-fold clásica carece de validez teórica y empírica en series temporales cuando existen dependencias "
        "y variables de ventana móvil, exigiendo particiones estrictamente cronológicas out-of-sample, resultado corroborado por Cerqueira et al. [16]. "
        "Kapoor y Narayanan [19] documentaron cómo la fuga de información temporal (data leakage) distorsiona sistemáticamente la literatura: al corregir la fuga, "
        "la supuesta superioridad de modelos complejos sobre la regresión logística tradicional tiende a desaparecer. Hewamalage et al. [18] advirtieron sobre los sesgos "
        "de evaluar métodos sin baselines de referencia, mientras que Chicco y Jurman [17] fundamentaron las limitaciones del puntaje F1 en contextos con clases asimétricas."
    )

    add_heading_2(doc, "2.4. Predicción Direccional y Envejecimiento de Modelos Financieros (Eje D)")
    p = add_para(doc)
    p.add_run(
        "En el dominio bursátil, Ballings et al. [20] y Gu et al. [23] determinaron que Random Forest y los ensambles superan a los modelos lineales al capturar "
        "interacciones no lineales complejas. Krauss et al. [21] y Fischer y Krauss [22] analizaron extensamente el S&P 500 bajo evaluación out-of-sample, "
        "observando que la predictibilidad y los excesos de retorno decaen sustancialmente en épocas recientes. Bustos y Pomares-Quimbaya [24] estructuraron una revisión sistemática "
        "de técnicas predictivas de mercado. Finalmente, Vela et al. [13] estudiaron el deterioro de modelos en 32 datasets, concluyendo que los modelos lineales y basados en árboles "
        "envejecen a ritmos disímiles y demostrando empíricamente que la calidad de predicción puede deteriorarse aun sin deriva aparente en los datos de entrada, "
        "lo que justifica el disparador dual implementado en este estudio."
    )

    add_heading_2(doc, "2.5. Matriz de Contraste con Estudios Empíricos")
    p = add_para(doc)
    p.add_run("La Tabla 1 sintetiza las dimensiones de diseño de este experimento en relación con los trabajos empíricos más relevantes:")

    # Table 1: Literature Contrast
    t_lit = doc.add_table(rows=5, cols=5)
    t_lit_headers = ["Dimensión", "Este Estudio", "Cavalcante [6]", "Vela et al. [13]", "Fischer [22]"]
    t_lit_w = [1.3, 1.4, 1.3, 1.25, 1.25]
    
    t_lit_data = [
        ["Datos", "MSFT diario (2021-2026), 1254 filas", "S&P 500, Shanghái, Apple (Yahoo)", "32 datasets diversos", "S&P 500 (1992-2015)"],
        ["Partición", "2021 ajuste/val; walk-forward 8 ventanas", "1/3 inicial; 2/3 flujo continuo", "Entrenamiento t0, prueba t0 + edad", "Ventanas cronológicas out-of-sample"],
        ["Modelos", "Regresión Logística y Random Forest", "Extreme Learning Machines (ELM)", "Ridge Regressor y Random Forest", "LSTM, Random Forest y Reg. Logística"],
        ["Disparador", "Dual: KS Bonferroni o F1 < ref - 2σ", "Unilateral: DDM/ECDD en flujo", "No aplica (medición pasiva)", "No aplica (calendario periódico)"],
    ]

    for j, h in enumerate(t_lit_headers):
        cell = t_lit.rows[0].cells[j]
        cell.text = h
        style_run(cell.paragraphs[0].runs[0], size_pt=9.5, bold=True, color=RGBColor(255, 255, 255))
        set_cell_props(cell, fill_hex="1B365D", top=80, bottom=80, left=100, right=100)
    
    for i, row in enumerate(t_lit_data):
        for j, val in enumerate(row):
            cell = t_lit.rows[i+1].cells[j]
            cell.text = val
            fill = "F8F9FA" if i % 2 == 1 else "FFFFFF"
            style_run(cell.paragraphs[0].runs[0], size_pt=9, bold=(j==0), color=TEXT_COLOR)
            set_cell_props(cell, fill_hex=fill, top=60, bottom=60, left=100, right=100)
    format_table(t_lit, t_lit_w)

    add_para(doc, space_after=12)

    # ==========================
    # 3. PLANIFICACIÓN METODOLÓGICA
    # ==========================
    add_heading_1(doc, "3. PLANIFICACIÓN METODOLÓGICA DEL EXPERIMENTO")

    add_heading_2(doc, "3.1. Descripción del Problema")
    p = add_para(doc)
    p.add_run(
        "Se formula una tarea de clasificación binaria supervisada sobre la serie temporal de precios diarios de MSFT. "
        "El objetivo es predecir la dirección del precio de cierre al día hábil siguiente (t+1), definiendo la variable objetivo como:\n"
        "  • y_t = 1  si  Close_{t+1} > Close_t  (Clase positiva: 'sube')\n"
        "  • y_t = 0  si  Close_{t+1} <= Close_t (Clase negativa: 'no sube')\n"
        "La tarea se caracteriza por una baja relación señal-ruido debido a la eficiencia informacional de los mercados financieros. "
        "El reto experimental radica en probar si un pipeline MLOps reactivo puede identificar transiciones de régimen y reentrenar oportunamente "
        "sin incurrir en sobreajuste destructivo frente al modelo estático o al reentrenamiento periódico incondicional."
    )

    add_heading_2(doc, "3.2. Objetivos del Estudio")
    p = add_para(doc)
    p.add_run(
        "3.2.1. Objetivo General:\n"
        "Evaluar cuantitativamente el impacto de una política de gobernanza MLOps con monitoreo reactivo de deriva y reentrenamiento automático "
        "en el desempeño predictivo y la estabilidad operativa de modelos de aprendizaje automático frente a un modelo estático y un esquema periódico, "
        "mediante una evaluación secuencial walk-forward semestral sobre la serie diaria de MSFT (2021–2026).\n\n"
        "3.2.2. Objetivos Específicos:\n"
        "1. Construir un espacio de 9 características relativas y adimensionales garantizando matemáticamente la ausencia de fuga de información (leakage).\n"
        "2. Formular un disparador dual de adaptación: test Kolmogorov-Smirnov por feature con corrección de Bonferroni (data drift) y umbral bootstrap temporal de F1 (performance drift).\n"
        "3. Ejecutar la simulación walk-forward en 8 ventanas semestrales consecutivas sobre dos réplicas algorítmicas (Regresión Logística y Random Forest) y tres baselines ingenuos.\n"
        "4. Contrastar estadísticamente las diferencias de desempeño pareadas de F1 mediante la prueba no paramétrica de rangos con signo de Wilcoxon (α = 0.05)."
    )

    add_heading_2(doc, "3.3. Sistema de Variables: Dependientes, Independientes y de Control")
    p = add_para(doc)
    p.add_run(
        "• Variable Independiente Principal (Política de Ciclo de Vida MLOps):\n"
        "  - Grupo A (Control Estático): Modelo ajustado exclusivamente en el periodo base 2021; permanece congelado sin actualización.\n"
        "  - Grupo B (Monitoreo Reactivo MLOps): Al cierre de cada semestre w, evalúa deriva en features y caída de F1; si se activa el disparador, "
        "se reentrena con los datos del último año (252 días) y la nueva versión rige a partir de w+1.\n"
        "  - Grupo C (Reentrenamiento Periódico Ciego): Al término de cada semestre w, se reentrena incondicionalmente con los últimos 252 días, "
        "sin consultar detectores de deriva ni desempeño.\n\n"
        "• Variables Dependientes:\n"
        "  - Desempeño predictivo por ventana: F1-Score de la clase positiva ('sube'), complementado por Precision y Recall.\n"
        "  - Dinámica operativa: Número de versiones de modelos generadas, frecuencia de reentrenamientos y causa de activación (deriva, caída F1, ambas).\n"
        "  - Significancia inferencial: Estadístico W y p-valor bilateral de la prueba de Wilcoxon pareada sobre las 8 ventanas.\n\n"
        "• Variables de Control y Bloqueo:\n"
        "  - Réplicas algorítmicas: Regresión Logística (L2) y Random Forest Classifier.\n"
        "  - Hiperparámetros congelados: Seleccionados en la fase de validación temporal inicial y mantenidos fijos en todos los reentrenamientos.\n"
        "  - Espacio de características: Mismas 9 variables relativas calculadas estrictamente con información previa.\n"
        "  - Semilla fija: seed = 42 en todas las operaciones estocásticas."
    )

    add_heading_2(doc, "3.4. Cronograma de Trabajo y Recursos")
    p = add_para(doc)
    p.add_run(
        "La ejecución del proyecto se estructuró en cinco fases metodológicas secuenciales:\n"
        "  • Fase 1 (Setup y Constitución): Gobernanza inmutable, selección de stack y pipeline de integración continua con GitHub Actions.\n"
        "  • Fase 2 (Fundacional): Verificación de hash SHA-256 de datos, validación externa con Yahoo Finance y tests automáticos de no fuga de información.\n"
        "  • Fase 3 (Simulación Walk-Forward - US1): Bucle secuencial de evaluación, detectores KS, bootstrap de F1, logging en MLflow y salidas CSV deterministas.\n"
        "  • Fase 4 (Revisión de Literatura - US2): 24 referencias IEEE con DOI validado, matriz de contraste y justificación formal de decisiones D1 a D7.\n"
        "  • Fase 5 (Reporte y Análisis - US3): Test de Wilcoxon pareado, generación automatizada de gráficos de evolución y síntesis técnica.\n\n"
        "Recursos humanos y técnicos asignados:\n"
        "  - Equipo de desarrollo: Andre (MLOps y MLflow), Frank (series bursátiles y tests de Wilcoxon), Paul (detectores KS y deriva), Willy (bootstrap y model aging).\n"
        "  - Cómputo: Procesador estándar monohilo (n_jobs=1) para garantizar determinismo estricto de punto flotante. Ejecución completa en < 2 minutos.\n"
        "  - Almacenamiento: Git versionado; base de datos SQLite local para MLflow (mlflow.db); CSV deterministas en results/."
    )

    # ==========================
    # 4. CONDUCCIÓN DEL EXPERIMENTO
    # ==========================
    add_heading_1(doc, "4. CONDUCCIÓN DEL EXPERIMENTO")

    add_heading_2(doc, "4.1. Herramientas y Stack Tecnológico")
    p = add_para(doc)
    p.add_run(
        "El entorno de ejecución se definió de forma determinista mediante el gestor de paquetes UV (Astral) sobre Python 3.12.10. "
        "Las versiones exactas registradas en uv.lock y run_manifest.json garantizan reproducibilidad bit a bit:\n"
        "  • Scikit-Learn 1.9.1: Pipelines de clasificación, escalado estándar y cálculo de métricas.\n"
        "  • SciPy 1.18.1: Cálculo exacto de pruebas Kolmogorov-Smirnov y test de rangos con signo de Wilcoxon.\n"
        "  • Evidently 0.7.23: Monitoreo distributivo de características.\n"
        "  • MLflow 3.18.0: Servidor local embebido con backend SQLite para registro de ejecuciones, parámetros, métricas y linaje de artefactos.\n"
        "  • NumPy 2.5.4 y Pandas 2.3.3: Manipulación tabular y cálculo de variables técnicas.\n"
        "  • yfinance: Validación externa independiente contra la API de Yahoo Finance."
    )

    add_heading_2(doc, "4.2. Diseño de la Plataforma y Prototipo Experimental")
    p = add_para(doc)
    p.add_run(
        "El sistema fue desarrollado bajo una arquitectura modular encapsulada en el paquete msft_mlops. "
        "El flujo de datos garantiza la integridad temporal bajo un diseño de partición estricto:\n"
        "  1. Calibración de Hiperparámetros (2021-02-04 a 2021-09-30, 148 días): Búsqueda de la mejor configuración sobre una rejilla prefijada.\n"
        "  2. Validación Temporal (2021-10-01 a 2021-12-31, 63 días): Evaluación out-of-sample para seleccionar el hiperparámetro óptimo por F1.\n"
        "  3. Modelo Inicial (v1): Reentrenado sobre la unión de todo el año 2021 (211 días) con los hiperparámetros seleccionados y congelados.\n"
        "  4. Periodo de Prueba Walk-Forward: 8 semestres calendario consecutivos desde 2022-H1 hasta 2025-H2 (~126 días hábiles por ventana).\n"
        "  5. Tramo Excluido: 20 observaciones de enero de 2026 (2026-01-02 a 2026-01-30), excluidas de métricas y disparadores para evitar sesgos por ventanas incompletas."
    )

    add_heading_3(doc, "Ingeniería de Características sin Fuga Temporal")
    p = add_para(doc)
    p.add_run(
        "Para evitar que la tendencia alcista de largo plazo de MSFT (de ~USD 240 a más de USD 500) provocara disparos automáticos del detector de deriva, "
        "se definieron K = 9 características estrictamente relativas y adimensionales calculadas hacia atrás:\n"
        "  • ret_0: Rendimiento porcentual del día actual (Close_t / Close_{t-1} - 1).\n"
        "  • ret_1, ret_2, ret_3, ret_4: Rendimientos porcentuales rezagados de 1 a 4 días previos.\n"
        "  • ma5_rel, ma10_rel, ma20_rel: Precios relativos a medias móviles simples (Close_t / SMA_n(Close)_t - 1).\n"
        "  • vol_rel: Volumen relativo a su media móvil de 20 periodos (Volume_t / SMA20(Volume)_t - 1).\n"
        "Los tests unitarios de fuga (test_leakage.py) verificaron que las características calculadas con la serie truncada en t son idénticas "
        "a las de la serie completa, y que perturbar información posterior a t no altera los valores del vector de entrada en t."
    )

    add_heading_2(doc, "4.3. Implementación del Experimento")
    p = add_para(doc)
    p.add_run(
        "• Protocolo de Disparo del Grupo B:\n"
        "  - Deriva de Features (Data Drift): Test de Kolmogorov-Smirnov por variable frente a los datos de entrenamiento de la versión vigente. "
        "Se aplica la corrección de Bonferroni: umbral = 0.05 / 9 ≈ 0.00556. Hay deriva si min(p_k) < 0.00556.\n"
        "  - Caída de Desempeño (Performance Drift): Al entrenar cada versión se estiman su F1 de referencia y su desviación estándar σ mediante "
        "1000 iteraciones de bootstrap con remuestras de tamaño 126 sobre el hold-out de 63 filas. Se define el umbral de alerta DDM: "
        "F1_ventana < F1_ref - 2σ. Si ocurre, se dispara reentrenamiento.\n\n"
        "• Reglas de Causalidad del Reentrenamiento (Grupos B y C):\n"
        "  - El reentrenamiento toma las últimas 252 observaciones etiquetadas (1 año bursátil).\n"
        "  - Para evitar fuga temporal, la ventana de reentrenamiento termina en la penúltima fila de la ventana w cerrada (la última fila requiere Close_{t+1} "
        "que pertenece al inicio de la ventana w+1).\n"
        "  - La nueva versión resultante entra en vigencia estrictamente a partir de la ventana w+1.\n\n"
        "• Baselines de Comparación Heurística:\n"
        "  - Siempre Sube: Clasificador dummy que predice siempre 1.\n"
        "  - Persistencia: Predice que la dirección de mañana será igual al signo de hoy (ret_0 > 0).\n"
        "  - Estratificado: Muestreo pseudoaleatorio determinista proporcional a la tasa de subidas del año base 2021 (p ≈ 0.569).\n\n"
        "• Validación Externa de Datos (Yahoo Finance):\n"
        "  - Se verificaron las 1254 fechas contra la API de Yahoo Finance (yfinance). Coincidencia del 100% de fechas.\n"
        "  - Se identificó un factor constante de ajuste por dividendos de 1.006344, el cual es multiplicativo y no altera retornos ni features relativas.\n"
        "  - Las discrepancias en precios fueron inferiores al 0.46%, y la divergencia en volumen se limitó a la última fila excluida (2026-02-02)."
    )

    # ==========================
    # 5. RESULTADOS
    # ==========================
    add_heading_1(doc, "5. RESULTADOS")

    add_heading_2(doc, "5.1. Desempeño Predictivo: Réplica Regresión Logística (L2, C = 0.1)")
    p = add_para(doc)
    p.add_run(
        "La Tabla 2 presenta el comportamiento del puntaje F1 a lo largo de las 8 ventanas semestrales de prueba para el modelo lineal:"
    )

    # Table 2: LogReg F1
    t_lr = doc.add_table(rows=10, cols=7)
    t_lr_headers = ["Ventana", "Grupo A (Estático)", "Grupo B (Monitoreo)", "Grupo C (Periódico)", "Siempre Sube", "Persistencia", "Estratificado"]
    t_lr_w = [1.1, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
    t_lr_data = [
        ["2022-H1", "0.538", "0.538", "0.538", "0.652", "0.420", "0.512"],
        ["2022-H2", "0.528", "0.429", "0.429", "0.612", "0.513", "0.500"],
        ["2023-H1", "0.580", "0.449", "0.197", "0.681", "0.562", "0.543"],
        ["2023-H2", "0.600", "0.429", "0.429", "0.740", "0.554", "0.588"],
        ["2024-H1", "0.582", "0.655", "0.655", "0.702", "0.541", "0.492"],
        ["2024-H2", "0.490", "0.639", "0.639", "0.694", "0.584", "0.525"],
        ["2025-H1", "0.569", "0.566", "0.566", "0.723", "0.507", "0.569"],
        ["2025-H2", "0.568", "0.678", "0.678", "0.680", "0.485", "0.493"],
        ["Media", "0.557", "0.548", "0.516", "0.685", "0.521", "0.528"]
    ]
    for j, h in enumerate(t_lr_headers):
        cell = t_lr.rows[0].cells[j]
        cell.text = h
        style_run(cell.paragraphs[0].runs[0], size_pt=8.5, bold=True, color=RGBColor(255, 255, 255))
        set_cell_props(cell, fill_hex="1B365D", top=60, bottom=60, left=60, right=60)
    for i, row in enumerate(t_lr_data):
        for j, val in enumerate(row):
            cell = t_lr.rows[i+1].cells[j]
            cell.text = val
            fill = "EBF2FA" if i == len(t_lr_data)-1 else ("F8F9FA" if i % 2 == 1 else "FFFFFF")
            bold = (i == len(t_lr_data)-1) or (j == 0)
            style_run(cell.paragraphs[0].runs[0], size_pt=8.5, bold=bold, color=TEXT_COLOR)
            set_cell_props(cell, fill_hex=fill, top=50, bottom=50, left=60, right=60)
    align_center = {1: WD_ALIGN_PARAGRAPH.RIGHT, 2: WD_ALIGN_PARAGRAPH.RIGHT, 3: WD_ALIGN_PARAGRAPH.RIGHT, 4: WD_ALIGN_PARAGRAPH.RIGHT, 5: WD_ALIGN_PARAGRAPH.RIGHT, 6: WD_ALIGN_PARAGRAPH.RIGHT}
    format_table(t_lr, t_lr_w, align_center)

    add_para(doc, space_after=8)

    # Embed LogReg Chart if exists
    img_lr_path = "reports/f1_por_ventana_logreg.png"
    if os.path.exists(img_lr_path):
        doc.add_picture(img_lr_path, width=Inches(5.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap = add_para(doc, "Figura 1: Evolución temporal del F1 por ventana semestral — Réplica Regresión Logística.", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)
        style_run(p_cap.runs[0], size_pt=9, italic=True, color=GRAY_TEXT)

    add_heading_2(doc, "5.2. Desempeño Predictivo: Réplica Random Forest")
    p = add_para(doc)
    p.add_run(
        "La Tabla 3 expone el rendimiento del modelo no lineal basado en ensamble de árboles (Random Forest):"
    )

    # Table 3: RF F1
    t_rf = doc.add_table(rows=10, cols=7)
    t_rf_headers = ["Ventana", "Grupo A (Estático)", "Grupo B (Monitoreo)", "Grupo C (Periódico)", "Siempre Sube", "Persistencia", "Estratificado"]
    t_rf_w = [1.1, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
    t_rf_data = [
        ["2022-H1", "0.507", "0.507", "0.507", "0.652", "0.420", "0.512"],
        ["2022-H2", "0.625", "0.439", "0.439", "0.612", "0.513", "0.500"],
        ["2023-H1", "0.627", "0.480", "0.495", "0.681", "0.562", "0.543"],
        ["2023-H2", "0.531", "0.397", "0.397", "0.740", "0.554", "0.588"],
        ["2024-H1", "0.500", "0.579", "0.579", "0.702", "0.541", "0.492"],
        ["2024-H2", "0.476", "0.636", "0.636", "0.694", "0.584", "0.525"],
        ["2025-H1", "0.565", "0.623", "0.623", "0.723", "0.507", "0.569"],
        ["2025-H2", "0.419", "0.610", "0.610", "0.680", "0.485", "0.493"],
        ["Media", "0.531", "0.534", "0.536", "0.685", "0.521", "0.528"]
    ]
    for j, h in enumerate(t_rf_headers):
        cell = t_rf.rows[0].cells[j]
        cell.text = h
        style_run(cell.paragraphs[0].runs[0], size_pt=8.5, bold=True, color=RGBColor(255, 255, 255))
        set_cell_props(cell, fill_hex="1B365D", top=60, bottom=60, left=60, right=60)
    for i, row in enumerate(t_rf_data):
        for j, val in enumerate(row):
            cell = t_rf.rows[i+1].cells[j]
            cell.text = val
            fill = "EBF2FA" if i == len(t_rf_data)-1 else ("F8F9FA" if i % 2 == 1 else "FFFFFF")
            bold = (i == len(t_rf_data)-1) or (j == 0)
            style_run(cell.paragraphs[0].runs[0], size_pt=8.5, bold=bold, color=TEXT_COLOR)
            set_cell_props(cell, fill_hex=fill, top=50, bottom=50, left=60, right=60)
    format_table(t_rf, t_rf_w, align_center)

    add_para(doc, space_after=8)

    # Embed RF Chart if exists
    img_rf_path = "reports/f1_por_ventana_rf.png"
    if os.path.exists(img_rf_path):
        doc.add_picture(img_rf_path, width=Inches(5.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap = add_para(doc, "Figura 2: Evolución temporal del F1 por ventana semestral — Réplica Random Forest.", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)
        style_run(p_cap.runs[0], size_pt=9, italic=True, color=GRAY_TEXT)

    add_heading_2(doc, "5.3. Dinámica Operativa de Reentrenamientos")
    p = add_para(doc)
    p.add_run(
        "El análisis de los eventos de reentrenamiento evidenció un fenómeno de convergencia operativa:\n"
        "  • En el Grupo B se detectó deriva estadística de características en 7 de las 8 ventanas semestrales (min(p) < 0.00556). "
        "La única ventana sin deriva fue 2022-H2 (min(p) = 0.053).\n"
        "  • En 2025-H1 se activó simultáneamente el disparador por caída crítica de F1 en Regresión Logística (deriva + caida_f1).\n"
        "  • En consecuencia, el Grupo B ejecutó 7 reentrenamientos y el Grupo C ejecutó 8 reentrenamientos periódicos. "
        "Esto causó que a partir del segundo semestre de 2023, los modelos de B y C fueran prácticamente idénticos (B - C = 0.000)."
    )

    add_heading_2(doc, "5.4. Contraste Estadístico Formal: Prueba de Wilcoxon Pareada")
    p = add_para(doc)
    p.add_run(
        "Se aplicó la prueba no paramétrica de rangos con signo de Wilcoxon sobre las diferencias semestrales de F1 pareadas (α = 0.05):"
    )

    # Table 4: Wilcoxon
    t_wil = doc.add_table(rows=7, cols=8)
    t_wil_headers = ["Réplica", "Comparación", "Dif. Media F1", "Ganadas", "Perdidas", "Empates", "Estadístico W", "p-valor"]
    t_wil_w = [1.0, 1.0, 0.9, 0.7, 0.7, 0.7, 0.9, 0.6]
    t_wil_data = [
        ["LogReg", "B vs. A", "-0.0092", "3", "4", "1", "12.0", "0.8125"],
        ["LogReg", "C vs. A", "-0.0406", "3", "4", "1", "11.0", "0.6875"],
        ["LogReg", "B vs. C", "+0.0314", "1", "0", "7", "0.0", "1.0000"],
        ["Random Forest", "B vs. A", "+0.0026", "4", "3", "1", "13.0", "0.9375"],
        ["Random Forest", "C vs. A", "+0.0045", "4", "3", "1", "13.0", "0.9375"],
        ["Random Forest", "B vs. C", "-0.0019", "0", "1", "7", "0.0", "1.0000"]
    ]
    for j, h in enumerate(t_wil_headers):
        cell = t_wil.rows[0].cells[j]
        cell.text = h
        style_run(cell.paragraphs[0].runs[0], size_pt=8.5, bold=True, color=RGBColor(255, 255, 255))
        set_cell_props(cell, fill_hex="1B365D", top=60, bottom=60, left=60, right=60)
    for i, row in enumerate(t_wil_data):
        for j, val in enumerate(row):
            cell = t_wil.rows[i+1].cells[j]
            cell.text = val
            fill = "F8F9FA" if i % 2 == 1 else "FFFFFF"
            style_run(cell.paragraphs[0].runs[0], size_pt=8.5, bold=(j<=1), color=TEXT_COLOR)
            set_cell_props(cell, fill_hex=fill, top=50, bottom=50, left=60, right=60)
    format_table(t_wil, t_wil_w)

    add_para(doc, space_after=8)
    p = add_para(doc)
    p.add_run(
        "Interpretación inferencial: Dado que todos los p-valores superan ampliamente el umbral α = 0.05 (rango de 0.6875 a 1.0000), "
        "no se puede rechazar la hipótesis nula de equivalencia. No existe evidencia estadística de que operar con MLOps reactivo o periódico "
        "supere a mantener un modelo estático no actualizado en la tarea evaluada."
    )

    add_heading_2(doc, "5.5. Hallazgos Inesperados y Amenazas a la Validez")
    p = add_para(doc)
    p.add_run(
        "1. Dominancia del Baseline 'Siempre Sube': El clasificador ingenuo obtuvo un F1 promedio de 0.685, superando con holgura a todos los modelos "
        "de Machine Learning (0.557 en LogReg A y 0.536 en RF C). Esto obedece a la fuerte tendencia alcista secular de MSFT impulsada por la adopción de IA generativa. "
        "Los modelos supervisados intentaron anticipar correcciones diarias de corto plazo, acumulando errores que penalizaron su F1.\n\n"
        "2. Coste de Adaptación Transitorio: Durante los años 2022 y 2023, el modelo estático superó holgadamente a los reentrenados (p. ej., en 2022-H2 RF A obtuvo 0.625 vs. 0.439 en B y C). "
        "Reentrenar con la historia reciente forzó a B y C a sobreajustarse a la alta volatilidad bajista de 2022. Sin embargo, en 2024 y 2025 el modelo estático decayó "
        "por envejecimiento acumulado (RF A cayó a 0.419 en 2025-H2), permitiendo que B y C recuperaran ventaja (0.610).\n\n"
        "3. Amenazas a la Validez: Potencia limitada de Wilcoxon con N = 8 semestres (p mínimo teórico = 0.0078); remuestreo bootstrap i.i.d. que no modela autocorrelación; "
        "y especificidad de un único activo de gran capitalización tecnológica (MSFT)."
    )

    add_heading_2(doc, "5.6. Evaluación y Verificación Específica del Tramo Reciente (Julio 2025 – Enero 2026)")
    p = add_para(doc)
    p.add_run(
        "Para responder a la pregunta de si los modelos reentrenados se acercan más a la realidad en la etapa más reciente del dataset, "
        "se evaluó de forma independiente el tramo comprendido entre el 1 de julio de 2025 y el 30 de enero de 2026 (148 días bursátiles, 50.7% de subidas reales), "
        "comparando el modelo original congelado en 2021 frente al modelo reentrenado con la ventana del último año (julio 2024 a junio 2025, 252 días):\n"
    )

    t_rec = doc.add_table(rows=8, cols=6)
    t_rec_headers = ["Réplica", "Modelo / Configuración", "Periodo Entrenamiento", "F1", "Precision", "Recall"]
    t_rec_w = [1.0, 1.8, 1.6, 0.7, 0.7, 0.7]
    t_rec_data = [
        ["baseline", "Siempre Sube", "Heurística (dummy)", "0.673", "0.507", "1.000"],
        ["baseline", "Persistencia", "Heurística (signo ret_0)", "0.493", "0.493", "0.493"],
        ["baseline", "Estratificado", "Proporción 2021 (0.521)", "0.487", "0.469", "0.507"],
        ["logreg", "Grupo A (Estático)", "2021 (2021-03 a 2021-12)", "0.558", "0.495", "0.640"],
        ["logreg", "Grupo B/C (Reentrenado)", "Último año (2024-06 a 2025-06)", "0.650", "0.516", "0.880"],
        ["rf", "Grupo A (Estático)", "2021 (2021-03 a 2021-12)", "0.419", "0.425", "0.413"],
        ["rf", "Grupo B/C (Reentrenado)", "Último año (2024-06 a 2025-06)", "0.583", "0.510", "0.680"]
    ]
    for j, h in enumerate(t_rec_headers):
        cell = t_rec.rows[0].cells[j]
        cell.text = h
        style_run(cell.paragraphs[0].runs[0], size_pt=8.5, bold=True, color=RGBColor(255, 255, 255))
        set_cell_props(cell, fill_hex="1B365D", top=60, bottom=60, left=60, right=60)
    for i, row in enumerate(t_rec_data):
        for j, val in enumerate(row):
            cell = t_rec.rows[i+1].cells[j]
            cell.text = val
            fill = "F8F9FA" if i % 2 == 1 else "FFFFFF"
            bold = ("Reentrenado" in val) or (j == 3 and "0.650" in val)
            style_run(cell.paragraphs[0].runs[0], size_pt=8.5, bold=bold, color=TEXT_COLOR)
            set_cell_props(cell, fill_hex=fill, top=50, bottom=50, left=60, right=60)
    format_table(t_rec, t_rec_w, align_center)

    add_para(doc, space_after=8)
    p = add_para(doc)
    p.add_run(
        "Conclusión clave del tramo reciente: A diferencia de los primeros años (2022-2023) donde el reentrenamiento sufrió sobreajuste al ruido, "
        "en este tramo final el modelo reentrenado con el último año superó con amplitud al modelo estático en ambas réplicas (+9.2 puntos de F1 en Regresión Logística y +16.4 puntos en Random Forest). "
        "El modelo que más se acercó a la realidad fue la Regresión Logística reentrenada (F1 = 0.650, Recall = 0.880)."
    )

    # ==========================
    # 6. CONCLUSIONES
    # ==========================
    add_heading_1(doc, "6. CONCLUSIONES")
    p = add_para(doc)
    p.add_run(
        "1. Refutación empírica de la superioridad intrínseca de MLOps en predicción bursátil diaria:\n"
        "El experimento demostró rigurosamente que la instrumentación de monitoreo de deriva y reentrenamiento automático no garantiza una mayor precisión predictiva. "
        "El modelo estático no actualizado (Grupo A) obtuvo rendimientos medios comparables o ligeramente superiores en el mediano plazo (F1 = 0.557 frente a 0.548 en B y 0.516 en C para LogReg), "
        "sin que se observe significancia estadística en las diferencias pareadas (p > 0.80).\n\n"
        "2. Hipersensibilidad de los detectores univariados en finanzas:\n"
        "La prueba de Kolmogorov-Smirnov con corrección de Bonferroni detectó deriva estadística en el 87.5% de los periodos evaluados (7 de 8 ventanas). "
        "Esta hiper-reactividad desdibujó la frontera entre el reentrenamiento reactivo y el periódico ciego (B ≈ C). Para que el monitoreo MLOps sea costo-eficiente en finanzas, "
        "los detectores deben parametrizarse con tolerancias de negocio y funciones de pérdida económica, no con significancia puramente distributiva.\n\n"
        "3. Dinámica temporal bifásica (Sobreajuste reciente vs. Envejecimiento tardío):\n"
        "Se constató un patrón temporal dual: en los primeros dos años posteriores al despliegue, reentrenar perjudicó el desempeño al sobreajustar los modelos "
        "a regímenes volátiles transitorios. Por el contrario, a partir del tercer año el modelo estático sufrió obsolescencia severa, momento en el cual los modelos actualizados "
        "tomaron la delantera. El reentrenamiento continuo demuestra valor preventivo contra la degradación tardía, pero a expensas de inestabilidad transitoria inicial.\n\n"
        "4. Imperativo metodológico de baselines ingenuos:\n"
        "El triunfo sistemático de la regla heurística 'Siempre Sube' (F1 = 0.685 frente a ~0.53-0.55 en ML) ilustra el peligro de evaluar arquitecturas de MLOps en el vacío. "
        "Sin baselines ingenuos, un F1 moderado podría interpretarse equívocamente como un éxito de ingeniería, cuando en realidad el modelo rinde por debajo del sesgo macroeconómico natural.\n\n"
        "5. El verdadero aporte de MLOps:\n"
        "El valor sustancial de MLOps en entornos estocásticos no reside en incrementar mágicamente el F1 en horizontes ruidosos, sino en proveer reproducibilidad matemática integral, "
        "auditoría causal, linaje de modelos y datos, observabilidad de deriva y la infraestructura necesaria para gobernar institucionalmente la obsolescencia técnica en el largo plazo."
    )

    # ==========================
    # 7. REFERENCIAS BIBLIOGRÁFICAS
    # ==========================
    add_heading_1(doc, "7. REFERENCIAS BIBLIOGRÁFICAS (FORMATO IEEE)")
    
    refs = [
        "[1] D. Sculley et al., 'Hidden technical debt in machine learning systems,' in Advances in Neural Information Processing Systems 28 (NIPS 2015), 2015, pp. 2503–2511.",
        "[2] S. Amershi et al., 'Software engineering for machine learning: A case study,' in Proc. IEEE/ACM 41st Int. Conf. Softw. Eng.: Softw. Eng. Pract. (ICSE-SEIP), 2019, pp. 291–300, doi: 10.1109/ICSE-SEIP.2019.00042.",
        "[3] A. Paleyes, R.-G. Urma, and N. D. Lawrence, 'Challenges in deploying machine learning: A survey of case studies,' ACM Comput. Surv., vol. 55, no. 6, Art. no. 114, 2022, doi: 10.1145/3533378.",
        "[4] M. Testi et al., 'MLOps: A taxonomy and a methodology,' IEEE Access, vol. 10, pp. 63606–63618, 2022, doi: 10.1109/ACCESS.2022.3181730.",
        "[5] D. Kreuzberger, N. Kühl, and S. Hirschl, 'Machine learning operations (MLOps): Overview, definition, and architecture,' IEEE Access, vol. 11, pp. 31866–31879, 2023, doi: 10.1109/ACCESS.2023.3262138.",
        "[6] R. C. Cavalcante and A. L. I. Oliveira, 'An approach to handle concept drift in financial time series based on extreme learning machines and explicit drift detection,' in Proc. Int. Joint Conf. Neural Netw. (IJCNN), 2015, pp. 1–8, doi: 10.1109/IJCNN.2015.7280721.",
        "[7] G. I. Webb, R. Hyde, H. Cao, H. L. Nguyen, and F. Petitjean, 'Characterizing concept drift,' Data Min. Knowl. Discov., vol. 30, no. 4, pp. 964–994, 2016, doi: 10.1007/s10618-015-0448-4.",
        "[8] J. Lu, A. Liu, F. Dong, F. Gu, J. Gama, and G. Zhang, 'Learning under concept drift: A review,' IEEE Trans. Knowl. Data Eng., vol. 31, no. 12, pp. 2346–2363, 2019, doi: 10.1109/TKDE.2018.2876857.",
        "[9] S. Rabanser, S. Günnemann, and Z. Lipton, 'Failing loudly: An empirical study of methods for detecting dataset shift,' in Adv. Neural Inf. Process. Syst. 32 (NeurIPS 2019), 2019, pp. 1396–1408.",
        "[10] R. N. Gemaque, A. F. J. Costa, R. Giusti, and E. M. dos Santos, 'An overview of unsupervised drift detection methods,' WIREs Data Min. Knowl. Discov., vol. 10, Art. no. e1381, 2020, doi: 10.1002/widm.1381.",
        "[11] B. Celik and J. Vanschoren, 'Adaptation strategies for automated machine learning on evolving data,' IEEE Trans. Pattern Anal. Mach. Intell., vol. 43, no. 9, pp. 3067–3078, 2021, doi: 10.1109/TPAMI.2021.3062900.",
        "[12] F. Bayram, B. S. Ahmed, and A. Kassler, 'From concept drift to model degradation: An overview on performance-aware drift detectors,' Knowl.-Based Syst., vol. 245, Art. no. 108632, 2022, doi: 10.1016/j.knosys.2022.108632.",
        "[13] D. Vela et al., 'Temporal quality degradation in AI models,' Sci. Rep., vol. 12, Art. no. 11654, 2022, doi: 10.1038/s41598-022-15245-z.",
        "[14] F. Hinder, V. Vaquet, and B. Hammer, 'One or two things we know about concept drift—A survey on monitoring in evolving environments. Part A: Detecting concept drift,' Front. Artif. Intell., vol. 7, Art. no. 1330257, 2024, doi: 10.3389/frai.2024.1330257.",
        "[15] C. Bergmeir, R. J. Hyndman, and B. Koo, 'A note on the validity of cross-validation for evaluating autoregressive time series prediction,' Comput. Stat. Data Anal., vol. 120, pp. 70–83, 2018, doi: 10.1016/j.csda.2017.11.003.",
        "[16] V. Cerqueira, L. Torgo, and I. Mozetič, 'Evaluating time series forecasting models: An empirical study on performance estimation methods,' Mach. Learn., vol. 109, pp. 1997–2028, 2020, doi: 10.1007/s10994-020-05910-7.",
        "[17] D. Chicco and G. Jurman, 'The advantages of the Matthews correlation coefficient (MCC) over F1 score and accuracy in binary classification evaluation,' BMC Genomics, vol. 21, Art. no. 6, 2020, doi: 10.1186/s12864-019-6413-7.",
        "[18] H. Hewamalage, K. Ackermann, and C. Bergmeir, 'Forecast evaluation for data scientists: Common pitfalls and best practices,' Data Min. Knowl. Discov., vol. 37, no. 2, pp. 788–832, 2023, doi: 10.1007/s10618-022-00894-5.",
        "[19] S. Kapoor and A. Narayanan, 'Leakage and the reproducibility crisis in machine-learning-based science,' Patterns, vol. 4, no. 9, Art. no. 100804, 2023, doi: 10.1016/j.patter.2023.100804.",
        "[20] M. Ballings, D. Van den Poel, N. Hespeels, and R. Gryp, 'Evaluating multiple classifiers for stock price direction prediction,' Expert Syst. Appl., vol. 42, no. 20, pp. 7046–7056, 2015, doi: 10.1016/j.eswa.2015.05.013.",
        "[21] C. Krauss, X. A. Do, and N. Huck, 'Deep neural networks, gradient-boosted trees, random forests: Statistical arbitrage on the S&P 500,' Eur. J. Oper. Res., vol. 259, no. 2, pp. 689–702, 2017, doi: 10.1016/j.ejor.2016.10.031.",
        "[22] T. Fischer and C. Krauss, 'Deep learning with long short-term memory networks for financial market predictions,' Eur. J. Oper. Res., vol. 270, no. 2, pp. 654–669, 2018, doi: 10.1016/j.ejor.2017.11.054.",
        "[23] S. Gu, B. Kelly, and D. Xiu, 'Empirical asset pricing via machine learning,' Rev. Financ. Stud., vol. 33, no. 5, pp. 2223–2273, 2020, doi: 10.1093/rfs/hhaa009.",
        "[24] O. Bustos and A. Pomares-Quimbaya, 'Stock market movement forecast: A systematic review,' Expert Syst. Appl., vol. 156, Art. no. 113464, 2020, doi: 10.1016/j.eswa.2020.113464."
    ]

    for ref in refs:
        p_ref = add_para(doc, ref, space_before=2, space_after=4, line_spacing=1.05)
        p_ref.paragraph_format.left_indent = Inches(0.3)
        p_ref.paragraph_format.first_line_indent = Inches(-0.3)
        style_run(p_ref.runs[0], size_pt=9, color=TEXT_COLOR)

    # Save Document
    out_dir_reports = "reports"
    os.makedirs(out_dir_reports, exist_ok=True)
    out_path_reports = os.path.join(out_dir_reports, "Informe_Experimental_MLOps_MSFT.docx")
    out_path_root = "Informe_Experimental_MLOps_MSFT.docx"

    doc.save(out_path_reports)
    doc.save(out_path_root)
    print(f"Documento generado exitosamente en:\n - {os.path.abspath(out_path_reports)}\n - {os.path.abspath(out_path_root)}")

if __name__ == "__main__":
    create_report()
