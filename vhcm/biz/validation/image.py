import io
from PIL import Image
import vhcm.common.config.config_manager as config
from vhcm.common.constants import COMMA


def image_validate(value):
    f = value
    image = Image.open(io.BytesIO(f))
    if image.format not in config.config_loader.get_setting_value_array(config.ACCEPT_IMAGE_FORMAT, COMMA):
        return 'Only accept jpg, png image file format'
    else:
        return ''
