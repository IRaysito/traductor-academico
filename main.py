# main.py
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Importamos tu convertidor nativo (el que ya preprocesa notas al pie y usa Pandoc)
from convertidor import markdown_a_pdf

# Supongamos que tienes estas funciones ya definidas en tus otros archivos:
# from extractor import extraer_pdf_a_markdown
# from traductor import traducir_texto_markdown

app = FastAPI(
    title="API de Traducción y Maquetación Académica",
    description="Servicio en la nube para convertir PDFs escaneados a Markdown, traducirlos y compilarlos en PDFs con LaTeX real."
)

# Carpetas de trabajo dentro del servidor
CARPETA_INPUT = "archivos_entrada"
CARPETA_OUTPUT = "archivos_salida"
os.makedirs(CARPETA_INPUT, exist_ok=True)
os.makedirs(CARPETA_OUTPUT, exist_ok=True)

@app.get("/")
def ruta_raiz():
    return {
        "mensaje": "Servidor de traducción académica activo",
        "interfaz_de_pruebas": "/docs"
    }

@app.post("/traducir-pdf/", response_class=FileResponse)
async def traducir_pdf(file: UploadFile = File(...)):
    """
    Endpoint principal: Recibe un PDF, extrae su estructura, traduce el contenido,
    compila las ecuaciones LaTeX y retorna el PDF maquetado con calidad editorial.
    """
    # Validar que sea un archivo PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="El archivo enviado debe ser un PDF válido.")

    # Definir rutas de control de archivos para esta petición
    ruta_pdf_original = os.path.join(CARPETA_INPUT, file.filename)
    nombre_base = os.path.splitext(file.filename)[0]
    ruta_md_traducido = os.path.join(CARPETA_OUTPUT, f"{nombre_base}_traducido.md")
    ruta_pdf_final = os.path.join(CARPETA_OUTPUT, f"{nombre_base}_Academico.pdf")

    try:
        # 1. Guardar el PDF que enviaste dentro del disco del servidor
        with open(ruta_pdf_original, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"📥 Archivo recibido con éxito: {file.filename}")

        # =========================================================================
        # REEMPLAZA ESTAS LÍNEAS CON TUS FUNCIONES REALES DE EXTRACTOR Y TRADUCTOR
        # =========================================================================
        # 2. Extraer PDF a Markdown usando Marker (extractor.py)
        # texto_markdown_sucio = extraer_pdf_a_markdown(ruta_pdf_original)

        # 3. Traducir el Markdown manteniendo intacto el LaTeX (traductor.py)
        # texto_markdown_traducido = traducir_texto_markdown(texto_markdown_sucio)

        # Simulamos que ya tenemos el archivo traducido listo para la prueba del convertidor:
        # (Para tus pruebas reales, aquí escribirías el resultado de la traducción en 'ruta_md_traducido')
        # with open(ruta_md_traducido, "w", encoding="utf-8") as f:
        #     f.write(texto_markdown_traducido)
        # =========================================================================

        # A modo de prueba inicial del flujo, asumimos que ya tienes un archivo .md de prueba
        # en la ruta_md_traducido para probar la integración con Pandoc en el servidor:
        if not os.path.exists(ruta_md_traducido):
            # Creamos un Markdown de prueba rápido si no existe el pipeline completo aún
            with open(ruta_md_traducido, "w", encoding="utf-8") as f:
                f.write(f"# {nombre_base}\n\nDocumento procesado en el servidor.\n\n$$V(I, p) = \\max_{{c}} u(c)$$")

        # 4. Compilar el Markdown Traducido a PDF usando Pandoc + XeLaTeX
        archivo_resultado = markdown_a_pdf(ruta_md_traducido, ruta_pdf_final)

        if not archivo_resultado or not os.path.exists(ruta_pdf_final):
            raise HTTPException(status_code=500, detail="El motor de Pandoc falló al generar el PDF académico.")

        print(f"🚀 Enviando PDF final maquetado al usuario...")

        # 5. Retornar el archivo físico para que el navegador lo descargue automáticamente
        return FileResponse(
            path=ruta_pdf_final,
            filename=f"{nombre_base}_Academico.pdf",
            media_type="application/pdf"
        )

    except Exception as e:
        print(f"❌ Error en el flujo de la API: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno en el servidor: {str(e)}")

    finally:
        # 6. LIMPIEZA DE SEGURIDAD: Borramos el archivo original de entrada para ahorrar espacio
        if os.path.exists(ruta_pdf_original):
            os.remove(ruta_pdf_original)
