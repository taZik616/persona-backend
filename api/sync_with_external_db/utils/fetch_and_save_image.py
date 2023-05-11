import os
import urllib.request
from django.conf import settings


def fetchAndSaveImage(imagePath: str, subdirectory: str = 'resource'):
    """
    @param `imagePath` путь относительно `https://personashop.com/netcat_files/{imagePath}`
    """
    if not subdirectory:
        raise ValueError('"fetchAndSaveImage": subdirectory is required')
    filePath = imagePath[imagePath.rindex(':') + 1:]
    url = f"https://personashop.com/netcat_files/{filePath}"

    media_root = settings.MEDIA_ROOT
    relative_path = subdirectory
    try:
        # Эта штука кинуть ошибку может
        fileSubDir = imagePath[imagePath.rindex(':') + 1:imagePath.rindex('/')]

        fileName = imagePath[imagePath.rindex('/') + 1:]

        relative_path = os.path.join(relative_path, fileSubDir)
        os.makedirs(os.path.join(media_root, relative_path), exist_ok=True)
        relative_path = os.path.join(relative_path, fileName)
    except:
        os.makedirs(os.path.join(media_root, relative_path), exist_ok=True)
        relative_path = os.path.join(relative_path, filePath)

    response = urllib.request.urlopen(url)
    with open(os.path.join(media_root, relative_path), 'wb') as f:
        f.write(response.read())

    return os.path.join('media', relative_path)
