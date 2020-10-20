import os
import io
from pathlib import Path
import PIL.Image as Image

from array import array


def readimage(path):
    count = os.stat(path).st_size / 2
    with open(path, "rb") as f:
        return bytearray(f.read())


# bytes = readimage(path+extension)
# image = Image.open(io.BytesIO(bytes))
# image.save(savepath)

def to_abs_path(path):
    if os.path.isabs(path):
        return path
    else:
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        return os.path.join(project_root, path)


def string_to_array(input_str, separator=' '):
    return [s.strip() for s in input_str.split(separator)]
