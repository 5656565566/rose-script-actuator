from paddleocr import PaddleOCR
from fuzzywuzzy import fuzz

import re
import logging

logging.disable(logging.CRITICAL)

PaddleOCRResult = list[list[tuple[list[tuple[int, int]], tuple[str, float]]]]

def image_ocr(image: bytes, lang: str = "ch") -> PaddleOCRResult:
    """
    使用 PaddleOCR 对图像进行 OCR 识别。

    Args:
        image (bytes): 输入的图像数据，格式为字节流。
        lang (str, optional): 识别语言，默认为 "ch"（中文）。

    Returns:
        PaddleOCRResult: OCR 识别结果，包含识别出的文本及其位置信息。
    """
    
    if isinstance(image, tuple):
        image = image[0]
    
    paddleOCR = PaddleOCR(use_angle_cls=True, lang=lang)
    return paddleOCR.ocr(image, cls=True)

def exact_match(ocr_result: PaddleOCRResult, target: str) -> list[int, int]:
    """
    在全词匹配中查找目标字符串，并返回其中心点坐标。

    Args:
        ocr_result (list): OCR 识别结果，包含识别出的文本及其位置信息。
        target (str): 要匹配的目标字符串。

    Returns:
        list[int, int]: 匹配文字的中心点坐标 (x, y)。
    """
    
    for item in ocr_result:
        for word in item:
            text = word[1][0]
            if text == target:
                bbox = word[0]
                x_center = (bbox[0][0] + bbox[2][0]) // 2
                y_center = (bbox[0][1] + bbox[2][1]) // 2
                return [x_center, y_center]
    return None

def simple_fuzzy_match(ocr_result: PaddleOCRResult, target: str) -> list[int, int]:
    """
    在简单模糊匹配中查找目标字符串，并返回其中心点坐标。

    Args:
        ocr_result (list): OCR 识别结果，包含识别出的文本及其位置信息。
        target (str): 要匹配的目标字符串。

    Returns:
        list[int, int]: 匹配文字的中心点坐标 (x, y)。
    """
    
    for item in ocr_result:
        for word in item:
            text = word[1][0]
            if target.lower() in text.lower():
                bbox = word[0]
                x_center = (bbox[0][0] + bbox[2][0]) // 2
                y_center = (bbox[0][1] + bbox[2][1]) // 2
                return [x_center, y_center]
    return None

def fuzzy_match(ocr_result: PaddleOCRResult, target: str) -> list[int, int]:
    """
    在模糊匹配中查找目标字符串，并返回其中心点坐标。
    
    Args:
        ocr_result (list): OCR 识别结果，包含识别出的文本及其位置信息。
        target (str): 要匹配的目标字符串。
    
    Returns:
        list[int, int]: 匹配文字的中心点坐标 (x, y)。
    """
    
    best_match = None
    best_score = 0
    
    for item in ocr_result:
        for word in item:
            text = word[1][0]
            score = fuzz.ratio(target.lower(), text.lower())
            
            if score > best_score:
                best_score = score
                best_match = word
    
    if best_match:
        bbox = best_match[0]
        x_center = (bbox[0][0] + bbox[2][0]) // 2
        y_center = (bbox[0][1] + bbox[2][1]) // 2
        return [x_center, y_center]
    
    return None

def regex_match(ocr_result: PaddleOCRResult, pattern: str) -> list[int, int]:
    """
    使用正则表达式匹配目标字符串，并返回其中心点坐标。

    Args:
        ocr_result (list): OCR 识别结果，包含识别出的文本及其位置信息。
        pattern (str): 要匹配的正则表达式。

    Returns:
        list[int, int]: 匹配文字的中心点坐标 (x, y)。
    """
    
    regex = re.compile(pattern)
    for item in ocr_result:
        for word in item:
            text = word[1][0]
            if regex.search(text):
                bbox = word[0]
                x_center = (bbox[0][0] + bbox[2][0]) // 2
                y_center = (bbox[0][1] + bbox[2][1]) // 2
                return [x_center, y_center]
    return None