# extractor.py
import os
from pypdf import PdfReader

# IMPORTACIONES OFICIALES PARA MARKER 1.10+
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser

def es_pdf_digital(ruta_pdf):
    """
    Analiza las primeras páginas del PDF para detectar si contiene
    texto digital incrustado (seleccionable) o si es puramente una imagen.
    """
    try:
        reader = PdfReader(ruta_pdf)
        paginas_a_comprobar = min(3, len(reader.pages))
        texto_detectado = ""

        for i in range(paginas_a_comprobar):
            texto_detectado += reader.pages[i].extract_text() or ""

        return len(texto_detectado.strip()) > 50
    except Exception as e:
        print(f"⚠️ No se pudo analizar la estructura interna: {e}. Se usará OCR por seguridad.")
        return False

def pdf_a_markdown(ruta_pdf, carpeta_salida="salida"):
    """
    Convierte el PDF a Markdown usando la nueva estructura de PdfConverter de Marker,
    desactivando el OCR si el archivo es digital.
    """
    print("🔍 Analizando el tipo de PDF (Digital vs Escaneado)...")
    es_digital = es_pdf_digital(ruta_pdf)

    # Configuramos los argumentos usando el diccionario de Marker
    opciones = {}

    if es_digital:
        print("⚡ ¡Detectado PDF Digital Nativo! Desactivando OCR para máxima velocidad.")
        opciones["FORCE_OCR"] = False
    else:
        print("📸 ¡Detectado PDF Escaneado o Foto! Activando motor OCR local (Proceso lento)...")
        opciones["FORCE_OCR"] = True

    # Optimización de hilos en paralelo (Multiprocesamiento)
    opciones["NUM_THREADS"] = 4

    print("🧠 Inicializando configuraciones y modelos de Marker...")
    # Creamos la configuración oficial a partir de nuestras opciones
    config_parser = ConfigParser(opciones)
    config = config_parser.generate_config_dict()

    # Cargamos los modelos internos requeridos
    model_dict = create_model_dict()

    print("⏳ Extrayendo texto y convirtiendo ecuaciones a LaTeX...")
    # Instanciamos el convertidor moderno de PDFs
    converter = PdfConverter(
        config=config,
        artifact_dict=model_dict
    )

    # Ejecutamos la extracción de la ruta seleccionada
    rendered = converter(ruta_pdf)

    # Extraemos el texto en formato Markdown limpio
    full_text = rendered.markdown

    # Guardar el borrador en la carpeta de salida
    nombre_base = os.path.basename(ruta_pdf).replace(".pdf", "")
    ruta_salida_md = os.path.join(carpeta_salida, f"{nombre_base}_original.md")

    print(f"💾 Guardando borrador en inglés...")
    with open(ruta_salida_md, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"✨ Fase de extracción completada con éxito.")
    return ruta_salida_md
