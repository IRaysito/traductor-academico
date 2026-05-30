# traductor.py
import os
import socket
from langchain_community.llms import Ollama
from google import genai
from google.genai import types

# 🔑 COLOCA TU API KEY REAL EN LA SIGUIENTE LÍNEA:
os.environ["GEMINI_API_KEY"] = "AIzaSyAIX2afkUW1NR07e9jXqUpDgfYdMqv38vY"

def verificar_internet():
    """Prueba rápida para saber si la computadora tiene acceso a internet."""
    try:
        # Intentamos conectar al DNS de Google
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def traducir_con_gemini_nube(texto_markdown, prompt_instrucciones):
    """Envía la traducción a los servidores ultra rápidos de Google Gemini."""
    print("☁️ Conectando con los servidores de Google Gemini en la nube (Proceso rápido)...")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "TU_CODIGO_LARGO_DE_GEMINI_AQUÍ":
        raise ValueError("Debes configurar una API Key real de Gemini.")

    client = genai.Client(api_key=api_key)

    # Usamos gemini-2.5-flash (ultra rápido y preciso para texto)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"{prompt_instrucciones}\n\nTexto original:\n\n{texto_markdown}"
    )
    return response.text

def traducir_con_ollama_local(texto_markdown, prompt_instrucciones):
    """Ejecuta la traducción de respaldo local con Ollama en tu máquina."""
    print("🏠 Usando el plan de respaldo: Iniciando Ollama (Llama 3) local...")
    llm = Ollama(model="llama3", temperature=0.2)

    prompt_completo = f"{prompt_instrucciones}\n\nTexto original:\n\n{texto_markdown}"
    respuesta = llm.invoke(prompt_completo)
    return respuesta

def traducir_texto_matematico(texto_markdown):
    """Coordinador híbrido: Elige Nube si hay internet, o Local si no hay."""

    # PROMPT INTELIGENTE: Traduce y además repara los destrozos de Marker
    prompt_sistema = (
        "Eres un traductor académico de élite, especializado en economía matemática, "
        "teoría macroeconómica avanzada (incluyendo programación dinámica) y optimización intertemporal.\n\n"

        "Tu tarea es traducir el texto en Markdown adjunto del INGLÉS al ESPAÑOL cumpliendo estas reglas:\n\n"

        "1. ESTRUCTURA: Preserva intacto el formato Markdown (encabezados, listas, negritas).\n\n"

        "2. CORRECCIÓN UNIVERSAL DE PARÉNTESIS Y CORCHETES ROTOS:\n"
        "El extractor visual de PDFs dañó las ecuaciones metidas dentro de los párrafos (inline math), "
        "reemplazando los paréntesis '(', ')' o corchetes con caracteres corruptos "
        "como 'ð', 'Þ', 'þ', 'â', 'œ', entre otros símbolos extraños.\n"
        "Detecta CUALQUIER texto que use estos patrones (ej. expresiones de funciones como Vð...Þ, Pð...Þ, fð.Þ) "
        "y RECONSTRÚYELOS de forma inteligente convirtiéndolos a notación matemática estándar envuelta en LaTeX inline "
        "utilizando el símbolo de dólar simple ($...$).\n\n"

        "3. RECONSTRUCCIÓN MATEMÁTICA POR CONTEXTO:\n"
        "Si encuentras letras griegas rotas o subíndices temporales desalineados (como 't', 't+1'), "
        "usa tu profundo conocimiento de la ecuación de Bellman y teoría económica para deducir qué variable corresponde "
        "y escríbela en código LaTeX limpio ($...$).\n\n"

        "4. BLINDAJE DE FÓRMULAS BUENAS: No alteres ni traduzcas los bloques matemáticos que ya vengan perfectamente "
        "formateados entre símbolos de dólar ($ o $$).\n\n"

        "5. TRADUCCIÓN ECONÓMICA: Traduce el texto al español usando la terminología técnica correcta de la disciplina "
        "(ej. 'Value function' como 'Función de valor', 'State variables' como 'Variables de estado').\n\n"

        "Devuelve ÚNICAMENTE la traducción limpia en español con el texto y las matemáticas corregidas. "
        "No agregues introducciones, saludos ni notas aclaratorias al inicio o al final."
    )

    tiene_internet = verificar_internet()
    # Verificamos que tenga la clave y que no sea el texto por defecto
    tiene_api_key = "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"] != "TU_CODIGO_LARGO_DE_GEMINI_AQUÍ"

    if tiene_internet and tiene_api_key:
        try:
            return traducir_con_gemini_nube(texto_markdown, prompt_sistema)
        except Exception as e:
            print(f"⚠️ Error al conectar con la nube: {e}. Aplicando plan de respaldo...")
            return traducir_con_ollama_local(texto_markdown, prompt_sistema)
    else:
        if not tiene_api_key and tiene_internet:
            print("ℹ️ Nota: Tienes internet, pero no has configurado una API Key válida en traductor.py.")
        return traducir_con_ollama_local(texto_markdown, prompt_sistema)

def traducir_archivo_md(ruta_md_original):
    print("📖 Leyendo archivo Markdown original...")
    with open(ruta_md_original, "r", encoding="utf-8") as f:
        contenido = f.read()

    contenido_traducido = traducir_texto_matematico(contenido)
    ruta_traducido = ruta_md_original.replace("_original.md", "_traducido.md")

    print("💾 Guardando el documento traducido...")
    with open(ruta_traducido, "w", encoding="utf-8") as f:
        f.write(contenido_traducido)

    print(f"✨ ¡Traducción finalizada con éxito!")
    print(f"📝 Archivo en español guardado en: {ruta_traducido}")
    return ruta_traducido
