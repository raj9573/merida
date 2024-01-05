# import os
# from google.cloud import vision_v1p3beta1 as vision
# from google.cloud import translate_v2 as translate
# from django.shortcuts import render
# from io import BytesIO
# import base64
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from django.http import HttpResponse
# from django.shortcuts import render



# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "googletranslate.json"  # Replace with your credentials file

# def generate_pdf(translated_text):
#     buffer = BytesIO()

#     # Create a canvas to generate PDF
#     pdf = canvas.Canvas(buffer, pagesize=letter)

#     # Add translated text to the PDF
#     pdf.drawString(100, 750, translated_text)  # Adjust coordinates as needed

#     translated_lines = translated_text.split('\n')

#     # Set starting position for text 
#     y_coordinate = 750  # Adjust as needed
#     x_coordinate = 100   # Adjust as needed

#     # # Add each line of translated text vertically
#     for line in translated_lines:
#         pdf.drawString(x_coordinate, y_coordinate, line)
#         y_coordinate -= 20  # Adjust vertical spacing as needed
#     # # Save the PDF
#     pdf.save()

#     # Move buffer's pointer to the beginning
#     buffer.seek(0)
#     return buffer.getvalue()

# def translate_image_text(request):
#     if request.method == 'POST' and request.FILES['image']:
#         image = request.FILES['image']

#         # Instantiates a client for Google Cloud Vision API
#         vision_client = vision.ImageAnnotatorClient()

#         # Reads the image file
#         content = image.read()
#         # print(content)
#         # Send the image content for OCR
#         image = vision.Image(content=content)
#         response = vision_client.text_detection(image=image)
#         print(response)
#         texts = response.text_annotations
#         # print(texts)
#         # Extract the detected text from the image
#         if texts:
#             detected_text = texts[0].description
#             #print(detected_text)
#         else:
#             detected_text = "No text detected in the image."
#         # Translate the detected text to the desired language
#         target_language = request.POST['target_language']  # Get target language from form
#         translate_client = translate.Client()
#         translated_text = translate_client.translate(detected_text, target_language=target_language)['translatedText']

#         # Split translated text into lines
#         translated_lines = translated_text.split('\n')
#         print("translated lines")
#         print(translated_lines)
#         # Generate PDF with translated text
#         pdf_buffer = generate_pdf(translated_text)

#         # Encode the PDF buffer to base64
#         encoded_pdf = base64.b64encode(pdf_buffer).decode('utf-8')

#         return render(request, 'translated_image_text.html', {'pdf_buffer': encoded_pdf, 'translated_lines': translated_lines})

#     return render(request, 'image_text_translation_form.html')


import os 
from google.cloud import vision
from google.cloud import translate_v2 as translate
from django.shortcuts import render
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader
from PIL import Image
from django.http import JsonResponse
import google.generativeai as genai
# Set your Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "googletranslate.json"  # Replace with your credentials file path

# Function to generate a PDF from text
def generate_pdf(translated_text):
    buffer = BytesIO()

    # Create a canvas to generate PDF
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # Add translated text to the PDF
    pdf.drawString(100, 750, translated_text)  # Adjust coordinates as needed

    translated_lines = translated_text.split('\n')

    # Set starting position for text 
    y_coordinate = 750  # Adjust as needed
    x_coordinate = 100   # Adjust as needed

    # Add each line of translated text vertically
    for line in translated_lines:
        pdf.drawString(x_coordinate, y_coordinate, line)
        y_coordinate -= 20  # Adjust vertical spacing as needed

    # Save the PDF
    pdf.save()

    # Move buffer's pointer to the beginning
    buffer.seek(0)
    return buffer.getvalue()

# Function to process image text
def process_image(image):
    vision_client = vision.ImageAnnotatorClient()

    # Read the image file
    content = image.read()
    
    # Send the image content for OCR
    image = vision.Image(content=content)
    response = vision_client.text_detection(image=image)
    texts = response.text_annotations

    # Extract the detected text from the image
    if texts:
        detected_text = texts[0].description
    else:
        detected_text = "No text detected in the image."
    
    return detected_text

# Django view function to handle file upload
def translate_file(request):
    if request.method == 'POST' and request.FILES:
        file = request.FILES['images']
        target_language = request.POST['target_language']  # Get target language from form

        # Check file type and process accordingly
        if file.content_type.startswith('image'):
            detected_text = process_image(file)
        elif file.content_type == 'application/pdf':
            pdf = PdfReader(file)
            pdf_text = ''
            for page in pdf.pages:
                pdf_text += page.extract_text()
            detected_text = pdf_text
        else:
            return render(request, 'unsupported_file.html')

        # Translate the detected text to the desired language
        translate_client = translate.Client()
        translated_text = translate_client.translate(detected_text, target_language=target_language)['translatedText']
        translated_lines = translated_text.splitlines()

        # Generate PDF with translated text
        pdf_buffer = generate_pdf(translated_text)

        # Encode the PDF buffer to base64

        encoded_pdf = base64.b64encode(pdf_buffer).decode('utf-8')

        return render(request, 'translated_image_text.html', {'pdf_buffer': encoded_pdf, 'translated_text': translated_lines})

    return render(request, 'image_text_translation_form.html')



def generate_content(request):
    api_key = 'AIzaSyBlrcjFCOerZSDkC7YvaHoJ4elXDjaYWg8'
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    question = request.GET.get('question','')
    s= "1 line definition of "+ question
    response =model.generate_content(s)
    generated_text = response.text

    return JsonResponse({'generated_text':generated_text})










