from .tempate_matching import *
from .image_ocr import *

def crop_image(image_bytes: bytes, x1: int, y1: int, x2: int, y2: int) -> bytes:
    """裁切图片

    Args:
        image_bytes (bytes): 图片原始数据
        x1 (int): 裁切的坐标 x1
        y1 (int): 裁切的坐标 y1
        x2 (int): 裁切的坐标 x2
        y2 (int): 裁切的坐标 y2

    Returns:
        bytes: 裁切区域的图片数据
    """
    output_buffer = io.BytesIO()
    img = Image.open(io.BytesIO(image_bytes))
    
    cropped_img = img.crop((x1, y1, x2, y2))
    cropped_img.save(output_buffer, format="PNG")
    return output_buffer.getvalue()

def get_image_resolution(image_bytes: bytes) -> list[int, int]:
    """获取图像的分辨率（宽度和高度）。

    Args:
        image_bytes (bytes): 图片

    Returns:
        list[int, int]: 图片分辨率
    """
    img = Image.open(io.BytesIO(image_bytes))
    return list(img.size)