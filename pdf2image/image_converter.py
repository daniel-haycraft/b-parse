from pdf2image import convert_from_path
from tkinter import *
from tkinter import messagebox
 
images = convert_from_path("C:/Users/Daniel Haycraft/Downloadss/Sales Poster V2-1 (1).pdf", poppler_path="C:/Users/Daniel Haycraft/poppler-24.02.0")
for img in images:
    img.save('output.jpg', 'JPEG')