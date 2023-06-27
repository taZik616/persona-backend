from io import BytesIO

from PIL import Image


def compressImage(respContent: bytes, format: str):
    imgData = BytesIO(respContent)
    img = Image.open(imgData)
    format = format if format.upper() != 'JPG' else 'JPEG'

    output = BytesIO()
    img.save(output, format=format, compress_level=9)
    withoutResizing = output.getvalue()

    # Если сделать используя 1 объект img, то картинка размеры не поменяет
    imgData2 = BytesIO(respContent)
    img2 = Image.open(imgData2)
    width, height = img2.size
    new_width = int(width * 0.55)
    new_height = int(height * 0.55)
    output2 = BytesIO()
    img2 = img2.resize((new_width, new_height), Image.ANTIALIAS)
    img2.save(output2, format=format, compress_level=9)

    resizedImage = output2.getvalue()
    return (withoutResizing, resizedImage)
