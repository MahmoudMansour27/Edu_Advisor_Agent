from spire.doc import Document, FileFormat
from spire.doc.common import *

# Create a Document object
document = Document()
document.LoadFromFile("text.md")
document.SaveToFile("ToPdf.pdf", FileFormat.PDF)


    
