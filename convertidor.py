# convertidor.py
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
    if not ruta_pdf_salida:
        ruta_pdf_salida = ruta_md.replace(".md", ".pdf")

    # Rutas absolutas de Windows
    ruta_md = os.path.abspath(ruta_md)
    ruta_pdf_salida = os.path.abspath(ruta_pdf_salida)

    # Ruta para el archivo temporal corregido
    ruta_md_temp = ruta_md.replace(".md", "_procesado_temp.md")

    print(f"🏛️ Compilando localmente a través de WSL con Pandoc + XeLaTeX...")
    try:
        # 1. Leer original, procesar notas al pie y guardar en el temporal de Windows
        with open(ruta_md, "r", encoding="utf-8") as f:
            contenido = f.read()

        contenido_corregido = preprocesar_notas_al_pie(contenido)

        with open(ruta_md_temp, "w", encoding="utf-8") as f:
            f.write(contenido_corregido)

        # 2. TRADUCCIÓN DE RUTAS PARA WSL (Vital en local)
        ruta_wsl_md = ruta_md_temp.replace("\\", "/").replace("C:", "/mnt/c").replace("c:", "/mnt/c")
        ruta_wsl_pdf = ruta_pdf_salida.replace("\\", "/").replace("C:", "/mnt/c").replace("c:", "/mnt/c")

        # 3. Construir el comando anteponiendo "wsl"
        # Detección inteligente: Si estamos en Linux/Docker, no usamos "wsl"
        # "os.name" devuelve "posix" en Linux/Docker y "nt" en Windows
        if os.name == 'posix':
            comando = [
                "pandoc", ruta_md_temp, # Usamos la ruta local directa
                "-o", ruta_pdf_salida,
                "--pdf-engine=xelatex",
                "-V", "geometry:margin=1in",
                "-V", "mainfont=Liberation Serif"
            ]
        else:
            # Tu configuración actual de Windows + WSL
            ruta_wsl_md = ruta_md_temp.replace("\\", "/").replace("C:", "/mnt/c").replace("c:", "/mnt/c")
            ruta_wsl_pdf = ruta_pdf_salida.replace("\\", "/").replace("C:", "/mnt/c").replace("c:", "/mnt/c")
            comando = [
                "wsl", "pandoc", ruta_wsl_md,
                "-o", ruta_wsl_pdf,
                "--pdf-engine=xelatex",
                "-V", "geometry:margin=1in",
                "-V", "mainfont=Liberation Serif"
            ]

        # 4. Ejecutar la compilación usando el Linux de tu WSL
        subprocess.run(comando, capture_output=True, text=True, check=True)

        # 5. Limpieza del archivo temporal
        if os.path.exists(ruta_md_temp):
            os.remove(ruta_md_temp)

        return ruta_pdf_salida

    except subprocess.CalledProcessError as e:
        # Esto te imprimirá en la consola de VS Code el error exacto si LaTeX llora por algo
        print(f"❌ Error crítico en el motor de Pandoc dentro de WSL:\n{e.stderr}")
        if os.path.exists(ruta_md_temp):
            os.remove(ruta_md_temp)
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        if os.path.exists(ruta_md_temp):
            os.remove(ruta_md_temp)
        return None
