from actuator.utils.image import template_matching, diff_size_template_matching

from pathlib import Path

path = Path(__file__).parent / "test_image"

def open_image(image_path: Path, tmpl_path: Path) -> tuple[bytes, bytes]:
    """从指定路径中读取图像文件并返回其字节数据。

    Args:
        image_path (Path): 输入图片的路径。
        tmpl_path (Path): 模板图片的路径。

    Returns:
        Tuple[bytes, bytes]: 返回输入图片和模板图片的字节数据。
    """

    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()

    with open(tmpl_path, "rb") as tmpl_file:
        tmpl_bytes = tmpl_file.read()

    return image_bytes, tmpl_bytes

def test_diff_size_template_matching():
    image, tmpl = open_image(path / "diff_image.png", path / "tmpl.png")
    
    result = diff_size_template_matching(image, tmpl)
    
    assert len(result[0]) > 0, "模板匹配失败"

def test_template_matching():
    image, tmpl = open_image(path / "image.png", path / "tmpl.png")
    
    result = template_matching(image, tmpl)
    
    assert len(result[0]) > 0, "模板匹配失败"