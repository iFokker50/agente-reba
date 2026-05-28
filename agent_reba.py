from google import genai
from google.genai import errors
from PIL import Image
import fitz
import os
import time


PROMPT_REBA = """
Eres un agente experto en ergonomía y evaluación postural usando el método REBA
(Rapid Entire Body Assessment).

Tu tarea es analizar una imagen de una situación cotidiana, laboral, académica o doméstica
y generar un reporte ergonómico usando REBA.

Debes usar como base el contenido técnico REBA suministrado en el contexto.

Instrucciones importantes:

- Analiza solamente lo que sea visible en la imagen.
- Si una parte del cuerpo no se ve claramente, debes indicarlo.
- No inventes ángulos exactos si la imagen no permite medirlos.
- Puedes estimar rangos de postura de forma visual, pero debes marcarlo como estimación.
- REBA debe evaluar un solo lado del cuerpo para brazo, antebrazo y muñeca.
- No mezcles la puntuación del lado izquierdo con la del lado derecho.
- El lado a evaluar será indicado por el usuario.

Usa la lógica REBA:

Grupo A:
- Tronco
- Cuello
- Piernas
- Carga/Fuerza

Grupo B:
- Brazo del lado seleccionado
- Antebrazo del lado seleccionado
- Muñeca del lado seleccionado
- Agarre del lado seleccionado

Adicional:
- Actividad
- Puntuación final REBA
- Nivel de riesgo
- Nivel de acción requerido

Si no es posible calcular una puntuación REBA confiable por falta de información visual,
entrega una puntuación aproximada y explica las limitaciones.

Estructura obligatoria del reporte:

# Reporte de Análisis REBA

## 1. Descripción general de la imagen

## 2. Lado evaluado

## 3. Segmentos corporales visibles

## 4. Evaluación REBA - Grupo A

## 5. Evaluación REBA - Grupo B

## 6. Carga, agarre y actividad

## 7. Tabla de puntuación REBA estimada

La tabla debe tener este formato Markdown:

| Elemento REBA | Observación visual | Puntuación estimada | Justificación |
|---|---|---:|---|
| Tronco | ... | ... | ... |
| Cuello | ... | ... | ... |
| Piernas | ... | ... | ... |
| Carga/Fuerza | ... | ... | ... |
| Brazo lado seleccionado | ... | ... | ... |
| Antebrazo lado seleccionado | ... | ... | ... |
| Muñeca lado seleccionado | ... | ... | ... |
| Agarre | ... | ... | ... |
| Actividad | ... | ... | ... |
| Puntuación REBA final estimada | ... | ... | ... |

## 8. Nivel de riesgo e interpretación

## 9. Faltas ergonómicas encontradas

Usa una tabla Markdown:

| Falta ergonómica | Escuela o criterio relacionado | Riesgo asociado | Recomendación |
|---|---|---|---|
| ... | ... | ... | ... |

## 10. Recomendaciones de mejora

## 11. Limitaciones del análisis

## 12. Conclusión

El reporte debe ser claro, académico y fácil de entender.
"""


def leer_pdfs_reba(folder: str = "reba_docs") -> str:
    texto_total = ""

    if not os.path.exists(folder):
        raise FileNotFoundError(f"No existe la carpeta: {folder}")

    pdfs = [
        file for file in os.listdir(folder)
        if file.lower().endswith(".pdf")
    ]

    if not pdfs:
        raise FileNotFoundError(f"No hay PDFs en la carpeta: {folder}")

    for pdf in pdfs:
        pdf_path = os.path.join(folder, pdf)
        doc = fitz.open(pdf_path)

        texto_total += f"\n\n===== DOCUMENTO: {pdf} =====\n\n"

        for page in doc:
            texto_total += page.get_text()

        doc.close()

    return texto_total


def recortar_contexto(texto: str, max_chars: int = 8000) -> str:
    if len(texto) <= max_chars:
        return texto

    return texto[:max_chars]


def analizar_imagen_reba(ruta_imagen: str, body_side: str = "izquierdo") -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("No se encontró GEMINI_API_KEY. Revisa tu archivo .env o variable de entorno.")

    if not os.path.exists(ruta_imagen):
        raise FileNotFoundError(f"No existe la imagen: {ruta_imagen}")

    body_side = body_side.lower().strip()

    if body_side not in ["izquierdo", "derecho"]:
        raise ValueError("body_side debe ser 'izquierdo' o 'derecho'.")

    client = genai.Client(api_key=api_key)

    image = Image.open(ruta_imagen)

    contexto_reba = leer_pdfs_reba("reba_docs")
    contexto_reba = recortar_contexto(contexto_reba, max_chars=8000)

    prompt_final = f"""
{PROMPT_REBA}

LADO DEL CUERPO A EVALUAR:

El usuario solicitó evaluar únicamente el lado {body_side} del cuerpo.

Instrucciones específicas sobre lateralidad:

- El método REBA debe aplicarse a un solo lado del cuerpo para el análisis de extremidad superior.
- Evalúa principalmente el brazo, antebrazo y muñeca del lado {body_side}.
- Para tronco, cuello y piernas, evalúa la postura general visible de la persona.
- No mezcles puntuaciones del lado izquierdo y derecho.
- Si el lado {body_side} no es visible claramente en la imagen, indícalo como limitación.
- Si el lado contrario presenta una postura más crítica, puedes mencionarlo como observación secundaria.
- La puntuación REBA principal debe corresponder al lado {body_side}.
- En la sección "Lado evaluado", escribe explícitamente: "Lado evaluado: {body_side}".
- En la tabla de puntuación, usa las filas:
  - Brazo {body_side}
  - Antebrazo {body_side}
  - Muñeca {body_side}
- La conclusión debe indicar explícitamente que el resultado corresponde al lado {body_side}.

CONTEXTO TÉCNICO REBA EXTRAÍDO DE LOS PDFs:

{contexto_reba}

Ahora analiza la imagen usando el método REBA para el lado {body_side}.
"""

    modelos = [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash"
    ]

    for modelo in modelos:
        for intento in range(1, 4):
            try:
                print(f"Probando modelo: {modelo} | intento {intento}")

                response = client.models.generate_content(
                    model=modelo,
                    contents=[
                        prompt_final,
                        image
                    ]
                )

                return response.text

            except errors.ClientError as e:
                error_text = str(e)

                if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                    print(f"Cuota agotada o sin cuota para {modelo}. Esperando 35 segundos...")
                    time.sleep(35)
                    break

                raise e

            except errors.ServerError:
                print(f"Error temporal del servidor con {modelo}. Reintentando...")

                if intento < 3:
                    time.sleep(5 * intento)
                else:
                    print(f"Modelo {modelo} falló después de 3 intentos.")

            except Exception as e:
                raise e

    raise RuntimeError("Todos los modelos fallaron. Intenta nuevamente más tarde.")