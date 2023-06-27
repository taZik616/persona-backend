import os

from PIL import Image


class OpenImageError(Exception):
    def __init__(self, message):
        super().__init__(message)


def compressImg(image_name, new_size_ratio=0.9, quality=80, width=None, height=None, to_jpg=True):
    try:
        img = Image.open(image_name)
    except:
        raise OpenImageError(f"Ошибка открытия картинки: '{image_name}'")
    # image_size = os.path.getsize(image_name)
    if new_size_ratio < 1.0:
        img = img.resize((int(img.size[0] * new_size_ratio),
                         int(img.size[1] * new_size_ratio)), Image.ANTIALIAS)
    elif width and height:
        img = img.resize((width, height), Image.ANTIALIAS)
    filename, ext = os.path.splitext(image_name)
    if to_jpg:
        new_filename = f"{filename}_compressed.jpg"
    else:
        new_filename = f"{filename}_compressed{ext}"
    try:
        img.save(new_filename, quality=quality, optimize=True)
    except OSError:
        img = img.convert("RGB")
        img.save(new_filename, quality=quality, optimize=True)
    return new_filename
