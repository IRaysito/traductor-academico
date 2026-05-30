#convertidor.py
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
    y compila a PDF usando Pandoc + XeLaTeX.
    """
    if not ruta_pdf_salida:
        ruta_pdf_salida = ruta_md.replace(".md", ".pdf")

    ruta_md = os.path.abspath(ruta_md)
    ruta_pdf_salida = os.path.abspath(ruta_pdf_salida)
    ruta_md_temp = ruta_md.replace(".md", "_procesado_temp.md")

    print(f"🏛️ Iniciando compilación académica...")
    try:
        # 1. Leer original y procesar notas al pie
        with open(ruta_md, "r", encoding="utf-8") as f:
            contenido = f.read()

        contenido_corregido = preprocesar_notas_al_pie(contenido)

        # 2. LIMPIEZA PROFUNDA: Evita caracteres que rompen XeLaTeX en Linux
        contenido_limpio = contenido_corregido.encode('utf-8', 'ignore').decode('utf-8')
        
        with open(ruta_md_temp, "w", encoding="utf-8") as f:
            f.write(contenido_limpio)

        # 3. Construcción del comando según el entorno
        if os.name == 'posix':
            # Configuración para el Servidor (Render/Linux)
            comando = [
                "pandoc", ruta_md_temp,
                "-o", ruta_pdf_salida,
                "--pdf-engine=xelatex",
                "--standalone",              # Asegura proceso completo
                "--top-level-division=chapter",
                "-V", "geometry:margin=1in",
                "-V", "mainfont=Liberation Serif",
                "-V", "fontsize=12pt",
                "-V", "linestretch=1.5",
                "--wrap=auto"
            ]
        else:
            # Configuración para Windows + WSL
            ruta_wsl_md = ruta_md_temp.replace("\\", "/").replace("C:", "/mnt/c").replace("c:", "/mnt/c")
            ruta_wsl_pdf = ruta_pdf_salida.replace("\\", "/").replace("C:", "/mnt/c").replace("c:", "/mnt/c")
            comando = [
                "wsl", "pandoc", ruta_wsl_md,
                "-o", ruta_wsl_pdf,
                "--pdf-engine=xelatex",
                "-V", "geometry:margin=1in",
                "-V", "mainfont=Liberation Serif"
            ]

        # 4. Ejecución con captura de errores detallada
        resultado = subprocess.run(comando, capture_output=True, text=True)
        
        if resultado.returncode != 0:
            print(f"❌ ERROR EN PANDOC:\nSTDOUT: {resultado.stdout}\nSTDERR: {resultado.stderr}")
            raise subprocess.CalledProcessError(resultado.returncode, comando, stderr=resultado.stderr)

        # 5. Limpieza
        if os.path.exists(ruta_md_temp):
            os.remove(ruta_md_temp)

        print(f"🚀 PDF generado exitosamente.")
        return ruta_pdf_salida

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        if 'ruta_md_temp' in locals() and os.path.exists(ruta_md_temp):
            os.remove(ruta_md_temp)
        return None
