import fitz  # PyMuPDF
from pptx import Presentation

def extraer_texto_pdf(ruta):
    """
    Extrae el texto completo desde un archivo PDF.
    """
    texto = ""
    with fitz.open(ruta) as doc:
        for pagina in doc:
            texto += pagina.get_text()
    return texto


def extraer_texto_ppt(ruta):
    """
    Extrae el texto desde las diapositivas de una presentación PPT o PPTX.
    """
    prs = Presentation(ruta)
    texto = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                texto += shape.text + "\n"
    return texto
