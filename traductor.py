import os
import socket
from langchain_community.llms import Ollama
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Carga el archivo .env si estás en local
load_dotenv()

def verificar_internet():
    """Prueba rápida para saber si la computadora tiene acceso a internet."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def traducir_con_gemini_nube(texto_markdown, prompt_instrucciones, api_key):
    """Envía la traducción a los servidores de Google Gemini."""
    print("☁️ Conectando con los servidores de Google Gemini en la nube (Proceso rápido)...")
    
    # Inicializa el cliente oficial moderno de Google con tu variable unificada
    client = genai.Client(api_key=api_key)

    # Usamos gemini-2.5-flash para maquetación rápida de Markdown y LaTeX
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
    """Coordinador híbrido: Elige Nube si hay internet y clave válida, o Local."""

    prompt_sistema = (
        "Eres un traductor académico de élite, especializado en economía matemática, "
        "teoría macroeconómica avanzada (incluyendo programación dinámica) and optimización intertemporal.\n\n"
        "Tu tarea es traducir el texto en Markdown adjunto del INGLÉS al ESPAÑOL cumpliendo estas reglas:\n\n"
        "1. ESTRUCTURA: Preserva intacto el formato Markdown (encabezados, listas, negritas).\n\n"
        "2. CORRECCIÓN UNIVERSAL DE PARÉNTESIS Y CORCHETES ROTOS:\n"
        "El extractor visual de PDFs dañó las ecuaciones metidas dentro de los párrafos (inline math), "
        "reemplazando los paréntesis o corchetes con caracteres corruptos como 'ð', 'Þ', 'þ', 'â', 'œ'. "
        "Detecta expresiones de funciones como Vð...Þ, Pð...Þ, fð.Þ y RECONSTRÚYELOS a notación LaTeX ($...$).\n\n"
        "3. RECONSTRUCCIÓN MATEMÁTICA POR CONTEXTO: Reconstruye índices temporales desalineados de la ecuación de Bellman.\n\n"
        "4. BLINDAJE DE FÓRMULAS BUENAS: No alteres los bloques entre $ o $$.\n\n"
        "5. TRADUCCIÓN ECONÓMICA: Usa terminología correcta ('Value function' -> 'Función de valor').\n\n"
        "Devuelve ÚNICAMENTE la traducción limpia en español sin introducciones ni notas."
    )

    tiene_internet = verificar_internet()

    # Buscamos la variable unificada GOOGLE_API_KEY
    api_key = os.getenv("GOOGLE_API_KEY")
    tiene_api_key = api_key is not None and len(api_key) > 10

    # Detectamos de forma automática si estamos corriendo dentro del servidor de Render
    es_servidor = os.getenv("RENDER") is not None

    if tiene_internet and tiene_api_key:
        try:
            return traducir_con_gemini_nube(texto_markdown, prompt_sistema, api_key)
        except Exception as e:
            print(f"⚠️ Error al conectar con la nube: {e}.")
            # CORRECCIÓN DE PRODUCCIÓN: Evita invocar Ollama si estamos en la nube
            if es_servidor:
                raise RuntimeError(f"El servidor de Render no pudo procesar la traducción con Gemini: {e}")
            
            print("Aplicando plan de respaldo local...")
            return traducir_con_ollama_local(texto_markdown, prompt_sistema)
    else:
        # CORRECCIÓN DE PRODUCCIÓN: Si falta la API Key o no hay red en el servidor, detenemos el proceso con elegancia
        if es_servidor:
            if not tiene_api_key:
                raise ValueError("Error crítico: GOOGLE_API_KEY no se encuentra configurada en el panel de Render.")
            if not tiene_internet:
                raise RuntimeError("Error crítico: El servidor de Render perdió conectividad saliente a internet.")

        if not tiene_api_key and tiene_internet:
            print("ℹ️ Nota: Tienes internet, pero no has configurado GOOGLE_API_KEY en tu entorno.")
        return traducir_con_ollama_local(texto_markdown, prompt_sistema)

def traducir_archivo_md(ruta_md_original):
    """Lee el archivo .md original, procesa su traducción y guarda el resultado."""
    print("📖 Leyendo archivo Markdown original...")
    with open(ruta_md_original, "r", encoding="utf-8") as f:
        contenido = f.read()

    contenido_traducido = traducir_texto_matematico(contenido)

    if "_original.md" in ruta_md_original:
        ruta_traducido = ruta_md_original.replace("_original.md", "_traducido.md")
    else:
        nombre_base, ext = os.path.splitext(ruta_md_original)
        ruta_traducido = f"{nombre_base}_traducido{ext}"

    print("💾 Guardando el documento traducido...")
    with open(ruta_traducido, "w", encoding="utf-8") as f:
        f.write(contenido_traducido)

    print(f"✨ ¡Traducción finalizada con éxito!")
    return ruta_traducido
