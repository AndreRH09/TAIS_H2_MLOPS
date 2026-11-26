# Despliegue de la interfaz web

La interfaz (feature 002, [specs/002-interfaz-despliegue](../specs/002-interfaz-despliegue/spec.md))
responde a la pregunta del proyecto: **¿qué política es más efectiva, estática (A), con alarmas
(B) o cada seis meses (C)?** Tiene tres páginas:

| Página | Qué muestra |
|---|---|
| **Resultados del proyecto** | Resultados oficiales (`results/*.csv`) con el dataset MSFT y los modelos del proyecto (regresión logística y Random Forest): veredicto, F1 por ventana, diferencias, Wilcoxon, reentrenamientos y alarmas de deriva |
| **Comparar con tus datos** | El mismo walk-forward con un CSV de precios propio y/o un clasificador propio (`.skops`); permite ajustar α, k·σ y la ventana de reentrenamiento y descargar los resultados (.zip) |
| **Metodología** | Políticas, features, partición, métricas y amenazas a la validez |

---

## 1. Local sin Docker

```powershell
uv sync --group app
uv run streamlit run app/streamlit_app.py
```

Se abre en http://localhost:8501. La primera carga tarda porque importa Evidently, MLflow y
scikit-learn.

## 2. Local con Docker

Requiere Docker Desktop en ejecución.

```powershell
docker compose up --build
```

Se abre en http://localhost:7860. La misma imagen sirve en cualquier servicio de contenedores. Para detenerla:
`Ctrl+C` o `docker compose down`.

Para cargar modelos `.pkl`/`.joblib` **de confianza** en tu equipo, cambia
`ALLOW_UNSAFE_MODELS` a `"1"` en [compose.yaml](../compose.yaml). Cargar pickle ejecuta código,
así que nunca lo actives en el despliegue público.

---

## 3. Nube: Streamlit Community Cloud (gratis)

[Streamlit Community Cloud](https://share.streamlit.io) aloja apps Streamlit gratis y las
despliega directamente desde un repositorio público de GitHub. Instala solo
[app/requirements.txt](../app/requirements.txt) (sin MLflow ni el resto del proyecto) y la app
importa el paquete desde `src/`.

### 3.1 Requisitos

- Los cambios de la feature 002 deben estar **subidos a GitHub** en alguna rama (por ejemplo
  `002-interfaz-despliegue`); Streamlit Cloud puede desplegar desde cualquier rama.
- Tu cuenta de GitHub necesita acceso al repositorio. Si Streamlit no te deja elegirlo, pide
  permisos al dueño del repo o haz un *fork* en tu cuenta y despliega desde el fork.

### 3.2 Desplegar (una vez)

1. Entra en https://share.streamlit.io y elige **Continue with GitHub**. Autoriza el acceso.
2. Pulsa **Create app** → **Deploy a public app from GitHub**.
3. Completa el formulario:
   - **Repository**: `AndreRH09/TAIS_H2_MLOPS` (o tu fork);
   - **Branch**: la rama donde subiste los cambios;
   - **Main file path**: `app/streamlit_app.py`;
   - **App URL**: el subdominio que quieras, por ejemplo `msft-mlops-tais`.
4. Abre **Advanced settings** y elige **Python 3.12**. Es obligatorio: Evidently 0.7 no funciona
   con 3.13.
5. Pulsa **Deploy**. La primera instalación tarda unos minutos; el avance se ve en el panel
   **Manage app** (abajo a la derecha).

La URL queda como `https://<subdominio>.streamlit.app`; ese es el enlace para el docente. Cada
`git push` a esa rama vuelve a desplegar la app automáticamente.

### 3.3 Comprobar

1. «Resultados del proyecto» debe mostrar F1 medio 0,557 (A), 0,548 (B) y 0,516 (C) en regresión
   logística.
2. En «Comparar con tus datos», con el dataset del proyecto y la regresión logística, la ejecución
   debe dar las mismas cifras.

### 3.4 Alternativa: Hugging Face Spaces (requiere PRO)

Hugging Face ya no permite Spaces Docker en el hardware gratuito: crear uno devuelve
`402 Payment Required` y pide una suscripción PRO. Si alguien del equipo la tiene, la misma
imagen Docker está lista:

```powershell
python deploy/huggingface/build_bundle.py space_bundle
```

```powershell
$env:HF_TOKEN = "hf_..."; $env:HF_SPACE = "tu-usuario/msft-mlops"
```

```powershell
uv run --no-project --with huggingface_hub python deploy/huggingface/upload.py space_bundle
```

El workflow [.github/workflows/deploy-hf.yml](../.github/workflows/deploy-hf.yml) automatiza esa
subida tras cada CI verde en `main` si se definen el secreto `HF_TOKEN` y la variable `HF_SPACE`;
sin `HF_SPACE` se omite. La imagen también sirve en cualquier otro servicio que ejecute
contenedores (Render, Koyeb, Cloud Run…), con la salvedad de que sus planes gratuitos tienen poca
memoria o piden tarjeta.

---

## 4. Cómo lo usa el docente

1. **Ver nuestros resultados:** página principal, sin ejecutar nada.
2. **Probar con su dataset:** «Comparar con tus datos» → «Subir mi propio CSV». Columnas: fecha,
   apertura, máximo, mínimo, cierre y volumen (se aceptan `Date`, `Open`, `High`, `Low`, `Close`,
   `Volume` o sus equivalentes en español). Hacen falta ≥ 9 meses iniciales y ≥ 2 semestres de
   prueba completos; con menos de 6 semestres, Wilcoxon no puede dar p < 0,05.
3. **Probar con su modelo:** «Subir mi modelo» con un clasificador de scikit-learn guardado con
   skops. El modelo se usa como plantilla: las tres políticas lo reentrenan según su regla.

   ```python
   from sklearn.ensemble import GradientBoostingClassifier
   import skops.io as sio

   sio.dump(GradientBoostingClassifier(max_depth=2), "mi_modelo.skops")
   ```

4. **Descargar** el .zip con los CSV y el manifiesto (semilla, SHA-256 del dataset, parámetros,
   modelo y versiones).

---

## 5. Limitaciones del plan gratuito y del diseño

- Streamlit Community Cloud **suspende** la app tras un tiempo sin visitas; la siguiente visita
  la despierta con un botón y tarda en arrancar.
- El disco de la app es efímero: los resultados de cada visitante se descargan, no se guardan.
- Las ejecuciones de la interfaz son **exploratorias** y no se registran en MLflow. El
  experimento oficial sigue siendo `uv run msft-mlops run` (ver
  [plan 002](../specs/002-interfaz-despliegue/plan.md), *Complexity Tracking*).
- Una réplica tarda decenas de segundos en CPU (Random Forest, más). Los resultados se cachean
  por combinación de dataset, modelo y parámetros.
- Los modelos pickle están desactivados en el despliegue público; los `.skops` solo se cargan si
  contienen tipos de scikit-learn, numpy o scipy.
