import os
import shutil
import time  # <--- 1. Importamos el módulo de tiempo nativo
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import pypdf  

# Importamos tu convertidor
from convertidor import markdown_a_pdf
# Importamos tu traductor real
from traductor import traducir_texto_markdown  

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

app = FastAPI(
    title="API de Traducción y Maquetación Académica",
    description="Servicio en la nube para procesar documentos académicos."
)

CARPETA_INPUT = "archivos_entrada"
CARPETA_OUTPUT = "archivos_salida"
os.makedirs(CARPETA_INPUT, exist_ok=True)
os.makedirs(CARPETA_OUTPUT, exist_ok=True)


@app.get("/")
def ruta_raiz():
    return {
        "mensaje": "Servidor de traducción académica activo 🚀",
        "interfaz_de_pruebas": "/docs"
    }


@app.post("/traducir-pdf/", response_class=FileResponse)
async def traducir_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="El archivo enviado debe ser un PDF válido.")

    ruta_pdf_original = os.path.join(CARPETA_INPUT, file.filename)
    nombre_base = os.path.splitext(file.filename)[0]
    ruta_md_traducido = os.path.join(CARPETA_OUTPUT, f"{nombre_base}_traducido.md")
    ruta_pdf_final = os.path.join(CARPETA_OUTPUT, f"{nombre_base}_Academico.pdf")

    # Inicializamos el cronómetro global y el diccionario de métricas
    inicio_total = time.time()
    tiempos = {}

    try:
        # Guardar el PDF recibido en el servidor
        with open(ruta_pdf_original, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"📥 Archivo recibido con éxito: {file.filename}")

        # --- FASE 1: EXTRACCIÓN ---
        print("⚙️ [FASE 1] Extrayendo texto del PDF real...")
        inicio_fase = time.time()
        
        reader = pypdf.PdfReader(ruta_pdf_original)
        texto_extraido = f"# {nombre_base}\n\n"
        for page in reader.pages:
            texto_extraido += page.extract_text() + "\n"
            
        tiempos["extraccion"] = time.time() - inicio_fase

        # --- FASE 2: TRADUCCIÓN REAL ---
        print("🤖 [FASE 2] Conectando con el pipeline de traducción (GOOGLE_API_KEY)...")
        inicio_fase = time.time()
        
        # Enviamos el texto extraído a tu traductor avanzado
        texto_traducido = traducir_texto_markdown(texto_extraido)
        
        with open(ruta_md_traducido, "w", encoding="utf-8") as f:
            f.write(texto_traducido)
            
        tiempos["traduccion"] = time.time() - inicio_fase

        # Verificación de seguridad
        if not os.path.exists(ruta_md_traducido):
            raise HTTPException(status_code=404, detail="No se encontró el archivo .md procesado.")

        # --- FASE 3: COMPILACIÓN ---
        print("📄 [FASE 3] Compilando Markdown Traducido usando Pandoc + XeLaTeX...")
        inicio_fase = time.time()
        
        archivo_resultado = markdown_a_pdf(ruta_md_traducido, ruta_pdf_final)
        
        tiempos["compilacion_pdf"] = time.time() - inicio_fase

        if not archivo_resultado or not os.path.exists(ruta_pdf_final):
            raise HTTPException(status_code=500, detail="El motor de Pandoc falló al generar el PDF académico.")

        # --- REPORTE DE TIEMPOS EN LOGS ---
        tiempo_total = time.time() - inicio_total
        print("\n" + "="*60)
        print(f"⏱️ REPORTE DE RENDIMIENTO EN SERVIDOR ({file.filename})")
        print(f"├─ 📁 Extracción de texto: {tiempos['extraccion']:.2f}s")
        print(f"├─ 🤖 Traducción Gemini:  {tiempos['traduccion']:.2f}s")
        print(f"├─ 📝 Compilación LaTeX:  {tiempos['compilacion_pdf']:.2f}s")
        print(f"▀▀ TIEMPO NETO DE CÓMPUTO: {tiempo_total:.2f} segundos.")
        print("="*60 + "\n")

        print(f"🚀 Enviando PDF final maquetado al usuario...")
        return FileResponse(path=ruta_pdf_final, filename=f"{nombre_base}_Academico.pdf", media_type="application/pdf")

    except Exception as e:
        print(f"❌ Error en el flujo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Limpieza de archivos temporales de entrada para no saturar el servidor
        if os.path.exists(ruta_pdf_original):
            os.remove(ruta_pdf_original)
