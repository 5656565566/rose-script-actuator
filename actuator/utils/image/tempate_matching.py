import cv2
import numpy as np
import io
from PIL import Image

def template_matching(image_bytes: bytes, tmpl_bytes: bytes, min_confidence: float = 0.93) -> tuple[dict[float, tuple[int, int]], list[float]]:
    """在输入图片中查找模板图像，并返回匹配结果。

    Args:
        image_bytes (bytes): 输入图片的字节数据，在该图片中查找模板图像。
        tmpl_bytes (bytes): 模板图片的字节数据，在输入图片中查找此模板。
        min_confidence (float, optional): 最小信心度，该方法返回大于此信心度的结果。默认为0.93。

    Returns:
        Tuple[Dict[float, Tuple[int, int]], List[float]]: 
            - result_dic: 字典，键为信心度，值为匹配位置的坐标元组。
            - confidence_list: 信心度降序排列的列表。
    """
    # 将字节数据转换为PIL图像
    img = Image.open(io.BytesIO(image_bytes))
    template = Image.open(io.BytesIO(tmpl_bytes))

    # 将PIL图像转换为OpenCV格式
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    template = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)

    # 转换为灰度图像
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # 模板匹配
    res = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= min_confidence)

    result_dic: dict[float, tuple[int, int]] = {}
    confidence_list: list[float] = []
    for pt in zip(*loc[::-1]):
        result_dic[res[pt[1]][pt[0]]] = pt
        confidence_list.append(res[pt[1]][pt[0]])

    return [result_dic, sorted(confidence_list, reverse=True)]

def diff_size_template_matching(image_bytes: bytes, tmpl_bytes: bytes, min_confidence: float = 0.95) -> tuple[dict[float, tuple[int, int]], list[float]]:
    """在输入图片中查找模板图像，支持多尺度匹配，并返回匹配结果。

    Args:
        image_bytes (bytes): 输入图片的字节数据，在该图片中查找模板图像。
        tmpl_bytes (bytes): 模板图片的字节数据，在输入图片中查找此模板。
        min_confidence (float, optional): 最小信心度，该方法返回大于此信心度的结果。默认为0.95。

    Returns:
        Tuple[Dict[float, Tuple[int, int]], List[float]]: 
            - result_dic: 字典，键为信心度，值为匹配位置的坐标元组。
            - confidence_list: 信心度降序排列的列表。
    """
    # 将字节数据转换为PIL图像
    img = Image.open(io.BytesIO(image_bytes))
    template = Image.open(io.BytesIO(tmpl_bytes))

    # 将PIL图像转换为OpenCV格式
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    template = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)

    # 转换为灰度图像
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    result_dic: dict[float, tuple[int, int]] = {}
    confidence_list: list[float] = []

    # 多尺度模板匹配
    for scale in np.linspace(0.2, 1.0, 100)[::-1]:
        resized = cv2.resize(template, (int(template.shape[1] * scale), int(template.shape[0] * scale)))
        result = cv2.matchTemplate(gray_img, resized, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= min_confidence)
        for pt in zip(*loc[::-1]):
            result_dic[result[pt[1]][pt[0]]] = pt
            confidence_list.append(result[pt[1]][pt[0]])

    return [result_dic, sorted(confidence_list, reverse=True)]