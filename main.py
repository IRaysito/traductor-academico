import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from convertidor import markdown_a_pdf
from dotenv import load_dotenv

load_dotenv() # Esto busca el archivo .env en tu laptop
api_key = os.getenv("GOOGLE_API_KEY") # Esto funciona tanto en tu laptop como en Render

app = FastAPI(title="API de Traducción y Maquetación Académica")

CARPETA_INPUT = "archivos_entrada"
CARPETA_OUTPUT = "archivos_salida"
os.makedirs(CARPETA_INPUT, exist_ok=True)
os.makedirs(CARPETA_OUTPUT, exist_ok=True)

@app.post("/traducir-pdf/", response_class=FileResponse)
async def traducir_pdf(file: UploadFile = File(...)):
    ruta_pdf_original = os.path.join(CARPETA_INPUT, file.filename)
    nombre_base = os.path.splitext(file.filename)[0]
    ruta_md_traducido = os.path.join(CARPETA_OUTPUT, f"{nombre_base}_traducido.md")
    ruta_pdf_final = os.path.join(CARPETA_OUTPUT, f"{nombre_base}_Academico.pdf")

    try:
        # Guardar el PDF recibido
        with open(ruta_pdf_original, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"📥 Archivo recibido: {file.filename}")

        # --- AQUÍ DEBES INTEGRAR TU EXTRACTOR ---
        # Si no existe el .md, no lo inventamos, lanzamos error para saber que falta el extractor
        if not os.path.exists(ruta_md_traducido):
            raise HTTPException(status_code=404, detail="No se encontró el archivo .md procesado. Verifica que el extractor/traductor se haya ejecutado.")

        # Compilar
        archivo_resultado = markdown_a_pdf(ruta_md_traducido, ruta_pdf_final)

        if not archivo_resultado:
            raise HTTPException(status_code=500, detail="Error en Pandoc.")

        return FileResponse(path=ruta_pdf_final, filename=f"{nombre_base}_Academico.pdf", media_type="application/pdf")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(ruta_pdf_original):
            os.remove(ruta_pdf_original)
