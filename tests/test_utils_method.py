from actuator.utils.method import dynamic_call
from actuator.model import Point, Image

def click(x, y):
    return x, y

def image_print(image_bytes: bytes):
    return image_bytes

def test_dynamic_call():
    assert dynamic_call(click, Point(x=1, y=2)) == (1, 2), "Point 类型判断错误"
    assert dynamic_call(image_print, Image(b"123456")) == b"123456", "Image 类型判断错误"
    