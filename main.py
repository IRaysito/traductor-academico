import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import pypdf  # <--- Asegúrate de agregarlo a tu requirements.txt

# Importamos tu convertidor
from convertidor import markdown_a_pdf

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


# 1. RUTA RAÍZ: Para evitar el 404 al entrar a la URL principal y verificar que corre
@app.get("/")
def ruta_raiz():
    return {
        "mensaje": "Servidor de traducción académica activo 🚀",
        "interfaz_de_pruebas": "/docs"
    }


# 2. ENDPOINT DE PROCESAMIENTO
@app.post("/traducir-pdf/", response_class=FileResponse)
async def traducir_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="El archivo enviado debe ser un PDF válido.")

    ruta_pdf_original = os.path.join(CARPETA_INPUT, file.filename)
    nombre_base = os.path.splitext(file.filename)[0]
    ruta_md_traducido = os.path.join(CARPETA_OUTPUT, f"{nombre_base}_traducido.md")
    ruta_pdf_final = os.path.join(CARPETA_OUTPUT, f"{nombre_base}_Academico.pdf")

    try:
        # Guardar el PDF recibido en el servidor
        with open(ruta_pdf_original, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"📥 Archivo recibido con éxito: {file.filename}")

        # =========================================================================
        # SIMULACIÓN DE EXTRACTOR (Para que el archivo .md no esté vacío ni dé 404)
        # =========================================================================
        print("⚙️ Extrayendo texto del PDF real...")
        reader = pypdf.PdfReader(ruta_pdf_original)
        texto_extraido = f"# {nombre_base}\n\n"
        
        for page in reader.pages:
            texto_extraido += page.extract_text() + "\n"
        
        # Escribimos el contenido real del PDF en el archivo Markdown
        with open(ruta_md_traducido, "w", encoding="utf-8") as f:
            f.write(texto_extraido)
        # =========================================================================

        # Verificación de seguridad (ahora sí va a pasar porque arriba creamos el archivo)
        if not os.path.exists(ruta_md_traducido):
            raise HTTPException(status_code=404, detail="No se encontró el archivo .md procesado.")

        # 3. Compilar usando Pandoc + XeLaTeX
        archivo_resultado = markdown_a_pdf(ruta_md_traducido, ruta_pdf_final)

        if not archivo_resultado or not os.path.exists(ruta_pdf_final):
            raise HTTPException(status_code=500, detail="El motor de Pandoc falló al generar el PDF académico.")

        print(f"🚀 Enviando PDF final maquetado al usuario...")
        return FileResponse(path=ruta_pdf_final, filename=f"{nombre_base}_Academico.pdf", media_type="application/pdf")

    except Exception as e:
        print(f"❌ Error en el flujo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Limpieza de archivos temporales de entrada para no saturar el servidor
        if os.path.exists(ruta_pdf_original):
            os.remove(ruta_pdf_original)
