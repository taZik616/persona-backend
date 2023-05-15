from PIL import Image
from io import BytesIO


def compressImage(respContent: bytes, format: str):
    imgData = BytesIO(respContent)
    img = Image.open(imgData)

    width, height = img.size
    new_width = int(width * 0.75)
    new_height = int(height * 0.75)
    img = img.resize((new_width, new_height), Image.ANTIALIAS)
    format = format if format.upper() != 'JPG' else 'JPEG'
    output = BytesIO()
    img.save(output, format=format, compress_level=6)
    return output.getvalue()
