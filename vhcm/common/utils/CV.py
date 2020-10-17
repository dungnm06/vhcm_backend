import os
import io
import PIL.Image as Image

from array import array


def readimage(path):
    count = os.stat(path).st_size / 2
    with open(path, "rb") as f:
        return bytearray(f.read())

# bytes = readimage(path+extension)
# image = Image.open(io.BytesIO(bytes))
# image.save(savepath)
