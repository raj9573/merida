from google.cloud import vision
from google.cloud import translate_v2 as translate
from pdf2image import convert_from_path
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

# Function to extract text from an image
def extract_text_from_image(image_path):
    client = vision.ImageAnnotatorClient()

    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    text = response.text_annotations[0].description if response.text_annotations else ''
    return text

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ''
    images = convert_from_path(pdf_path)
    for img in images:
        img_byte_array = BytesIO()
        img.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)

        extracted_text = extract_text_from_image(img_byte_array)
        text += extracted_text + '\n'

    return text

# Function to generate a PDF from translated text
def generate_pdf(translated_text):
    buffer = BytesIO()

    # Create a canvas to generate PDF
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # Add translated text to the PDF
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

    # Return the PDF buffer
    return buffer.getvalue()

# Function to translate text using Google Cloud Translation API
def translate_text(text, target_language='en'):
    client = translate.Client()
    result = client.translate(text, target_language=target_language)
    return result['translatedText']

# Path to the PDF or image file
file_path = 'path_to_your_file.pdf'  # Replace with your file path

# Extract text from PDF or image
if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
    extracted_text = extract_text_from_image(file_path)
elif file_path.lower().endswith('.pdf'):
    extracted_text = extract_text_from_pdf(file_path)
else:
    raise ValueError("Unsupported file format. Only PDF or images are supported.")

# Translate the extracted text
translated_text = translate_text(extracted_text)

# Generate a PDF from the translated text
pdf_buffer = generate_pdf(translated_text)

# Save the translated PDF file
with open('translated_text.pdf', 'wb') as f:
    f.write(pdf_buffer)
