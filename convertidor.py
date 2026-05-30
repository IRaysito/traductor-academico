import os
import re
import subprocess

def preprocesar_notas_al_pie(texto_md):
    """
    Detecta etiquetas HTML como <sup>1</sup> o <sup>[1]</sup>
    y las convierte al formato nativo de notas al pie académico de Pandoc [^1].
    """
    patron_sup = r'<sup>\[?(\d+)\]?</sup>'
    texto_procesado = re.sub(patron_sup, r'[^\1]', texto_md)
    return texto_procesado

def markdown_a_pdf(ruta_md, ruta_pdf_salida=None):
    """
    Procesa el archivo Markdown, limpia caracteres extraños, 
    y compila a PDF usando Pandoc + XeLaTeX con diagnóstico detallado.
    """
    if not ruta_pdf_salida:
        ruta_pdf_salida = ruta_md.replace(".md", ".pdf")

    ruta_md = os.path.abspath(ruta_md)
    ruta_pdf_salida = os.path.abspath(ruta_pdf_salida)
    ruta_md_temp = ruta_md.replace(".md", "_procesado_temp.md")

    print(f"🏛️ Iniciando compilación académica...")
    try:
        # 1. Leer original
        with open(ruta_md, "r", encoding="utf-8") as f:
            contenido = f.read()
        
        # --- DIAGNÓSTICO: Tamaño del archivo ---
        print(f"📊 Tamaño del contenido recibido: {len(contenido)} caracteres")

        contenido_corregido = preprocesar_notas_al_pie(contenido)
        
        # 2. LIMPIEZA PROFUNDA: Elimina caracteres que rompen XeLaTeX
        contenido_limpio = contenido_corregido.encode('utf-8', 'ignore').decode('utf-8')
        
        with open(ruta_md_temp, "w", encoding="utf-8") as f:
            f.write(contenido_limpio)
        
        print(f"✅ Archivo temporal creado: {os.path.getsize(ruta_md_temp)} bytes")

        # 3. Construcción del comando
        if os.name == 'posix':
            comando = [
                "pandoc", ruta_md_temp,
                "-o", ruta_pdf_salida,
                "--pdf-engine=xelatex",
                "--standalone",
                "--top-level-division=chapter",
                "-V", "geometry:margin=1in",
                "-V", "mainfont=Liberation Serif",
                "-V", "fontsize=12pt",
                "-V", "linestretch=1.5",
                "--wrap=auto",
                "--verbose"  # <--- Habilita logs detallados de Pandoc
            ]
        else:
            ruta_wsl_md = ruta_md_temp.replace("\\", "/").replace("C:", "/mnt/c").replace("c:", "/mnt/c")
            ruta_wsl_pdf = ruta_pdf_salida.replace("\\", "/").replace("C:", "/mnt/c").replace("c:", "/mnt/c")
            comando = [
                "wsl", "pandoc", ruta_wsl_md,
                "-o", ruta_wsl_pdf,
                "--pdf-engine=xelatex",
                "-V", "geometry:margin=1in",
                "-V", "mainfont=Liberation Serif"
            ]

        # 4. Ejecución con diagnóstico de salida
        print(f"⚙️ Ejecutando Pandoc...")
        resultado = subprocess.run(comando, capture_output=True, text=True)
        
        # --- DIAGNÓSTICO: Salida de Pandoc ---
        if resultado.stdout:
            print(f"📋 Salida de Pandoc (stdout): {resultado.stdout[:1000]}")
        
        if resultado.returncode != 0:
            print(f"❌ ERROR EN PANDOC:\nSTDERR: {resultado.stderr}")
            raise subprocess.CalledProcessError(resultado.returncode, comando, stderr=resultado.stderr)

        # 5. Limpieza
        if os.path.exists(ruta_md_temp):
            os.remove(ruta_md_temp)

        print(f"🚀 PDF generado exitosamente. Tamaño final: {os.path.getsize(ruta_pdf_salida) if os.path.exists(ruta_pdf_salida) else 0} bytes")
        return ruta_pdf_salida

    except Exception as e:
        print(f"❌ Error crítico en convertidor: {e}")
        if 'ruta_md_temp' in locals() and os.path.exists(ruta_md_temp):
            os.remove(ruta_md_temp)
        return None
