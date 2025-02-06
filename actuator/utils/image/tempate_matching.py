import cv2
import numpy as np
import io
from PIL import Image as PILImage

from model import Point, Image

def _template_matching(image: Image, tmpl: Image, min_confidence: float = 0.93) -> tuple[dict[float, Point], list[float]]:
    """在输入图片中查找模板图像，并返回匹配结果。

    Args:
        image (Image): 输入的图片，在该图片中查找模板图像。
        tmpl (Image): 模板的图片，在输入图片中查找此模板。
        min_confidence (float, optional): 最小信心度，该方法返回大于此信心度的结果。默认为0.93。

    Returns:
        Tuple[Dict[float, Point], List[float]]: 
            - result_dic: 字典，键为信心度，值为匹配位置的坐标元组。
            - confidence_list: 信心度降序排列的列表。
    """
    
    image_bytes = image.image_bytes
    tmpl_bytes = tmpl.image_bytes
    
    img = PILImage.open(io.BytesIO(image_bytes))
    template = PILImage.open(io.BytesIO(tmpl_bytes))
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    template = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)
    
    # 灰度处理
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_tmpl = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    h_tmpl, w_tmpl = gray_tmpl.shape  # 获取模板尺寸

    # 模板匹配
    res = cv2.matchTemplate(gray_img, gray_tmpl, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= min_confidence)

    result_dict = {}
    confidence_list = []
    for pt in zip(*loc[::-1]):  # pt是(x, y)左上角坐标
        # 计算中心坐标
        center_x = pt[0] + w_tmpl // 2
        center_y = pt[1] + h_tmpl // 2
        confidence = res[pt[1], pt[0]]  # y轴在前，x轴在后
        result_dict[confidence] = Point(x= center_x, y= center_y)
        confidence_list.append(confidence)

    return result_dict, sorted(confidence_list, reverse=True)

def template_matching(image: Image, tmpl: Image, min_confidence: float = 0.93) -> tuple[dict[float, Point], list[float]]:
    
    results = _template_matching(image, tmpl, min_confidence)
    
    return list(results[0].values())


def _diff_size_template_matching(image: Image, tmpl: Image, min_confidence: float = 0.95) -> tuple[dict[float, Point], list[float]]:
    """在输入图片中查找模板图像，支持多尺度匹配，并返回匹配结果。

    Args:
        image (Image): 输入的图片，在该图片中查找模板图像。
        tmpl (Image): 模板的图片，在输入图片中查找此模板。
        min_confidence (float, optional): 最小信心度，该方法返回大于此信心度的结果。默认为0.95。

    Returns:
        Tuple[Dict[float, Point], List[float]]: 
            - result_dic: 字典，键为信心度，值为匹配位置的坐标元组。
            - confidence_list: 信心度降序排列的列表。
    """
    
    image_bytes = image.image_bytes
    tmpl_bytes = tmpl.image_bytes
    
    img = PILImage.open(io.BytesIO(image_bytes))
    template = PILImage.open(io.BytesIO(tmpl_bytes))
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    template = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)
    
    # 灰度处理
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_tmpl = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    h_tmpl_orig, w_tmpl_orig = gray_tmpl.shape  # 原始模板尺寸

    result_dict = {}
    confidence_list = []

    # 多尺度匹配
    for scale in np.linspace(0.2, 1.0, 100)[::-1]:
        # 计算缩放后尺寸
        w_resized = int(w_tmpl_orig * scale)
        h_resized = int(h_tmpl_orig * scale)
        if w_resized == 0 or h_resized == 0:
            continue  # 跳过无效尺寸
        
        # 缩放模板
        resized_tmpl = cv2.resize(gray_tmpl, (w_resized, h_resized))
        
        # 模板匹配
        result = cv2.matchTemplate(gray_img, resized_tmpl, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= min_confidence)
        
        # 处理匹配结果
        for pt in zip(*loc[::-1]):
            # 计算中心坐标
            center_x = pt[0] + w_resized // 2
            center_y = pt[1] + h_resized // 2
            confidence = result[pt[1], pt[0]]
            result_dict[confidence] = Point(x= center_x, y= center_y)
            confidence_list.append(confidence)

    return result_dict, sorted(confidence_list, reverse=True)


def diff_size_template_matching(image: Image, tmpl: Image, min_confidence: float = 0.93) -> tuple[dict[float, Point], list[float]]:
    
    results = _diff_size_template_matching(image, tmpl, min_confidence)
    
    return list(results[0].values())