from actuator.utils.image import image_ocr, exact_match, simple_fuzzy_match, fuzzy_match, regex_match

from pathlib import Path

import pytest

path = Path(__file__).parent / "test_image"

def open_image(image_path: Path) -> bytes:
    """从指定路径中读取图像文件并返回其字节数据。

    Args:
        image_path (Path): 输入图片的路径。

    Returns:
        bytes: 返回输入图片的字节数据。
    """

    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()


    return image_bytes

@pytest.fixture
def result():
    return image_ocr(open_image(path / "image.png"))

class TestOcr:
    def test_image_ocr(self, result):
        
        print(result[0])
        
        assert len(result) > 0, "OCR 识别失败"

    def test_exact_match(self, result):
        assert exact_match(result, "新建项目") != None, "OCR 识别失败"

    def test_simple_fuzzy_match(self, result):
        assert simple_fuzzy_match(result, "项目") != None, "OCR 识别失败"

    def test_fuzzy_match(self, result):
        assert fuzzy_match(result, "项目") != None, "OCR 识别失败"

    def test_regex_match(self, result):
        assert regex_match(result, r"项目") != None, "OCR 识别失败"