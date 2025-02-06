from PIL import Image as PILImage
from pathlib import Path
from io import BytesIO

class Tip:
    """返回的提示"""
    def __init__(self, message: str):
        self.message = message
    
    def __str__(self):
        return self.message

class Point:
    """记录一个点击位置"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __len__(self):
        return 2
    
    def __str__(self):
        return f"坐标 ({self.x}, {self.y})"
    
    def offset_x(self, value: int):
        self.x += value
        
    def offset_y(self, value: int):
        self.y += value
    
    def to_tuple(self) -> list[int, int]:
        return self.x, self.y
    
    def to_list(self) -> tuple[int, int]:
        return [self.x, self.y]
    
class Image:
    
    def __init__(self, image_bytes: bytes= b""):
        self._image_bytes: bytes = image_bytes
        self.name: str = None
    
    def __len__(self):
        return 1
    
    def open(self, path: Path) -> bytes:
        """打开图片

        Args:
            path (Path): 路径

        """
        self.name = path.name
        
        with PILImage.open(path) as img:
            byte_arr = BytesIO()
            img.save(byte_arr, format=img.format)
            self._image_bytes = byte_arr.getvalue()
            
        return self

    def crop(self, image_bytes: bytes, x1: int, y1: int, x2: int, y2: int):
        """裁切图片

        Args:
            image_bytes (bytes): 图片原始数据
            x1 (int): 裁切的坐标 x1
            y1 (int): 裁切的坐标 y1
            x2 (int): 裁切的坐标 x2
            y2 (int): 裁切的坐标 y2
        """
        output_buffer = BytesIO()
        img = PILImage.open(BytesIO(image_bytes))
        
        cropped_img = img.crop((x1, y1, x2, y2))
        cropped_img.save(output_buffer, format="PNG")
        self._image_bytes = output_buffer.getvalue()
        
        return self

    def get_resolution(self) -> tuple[int, int]:
        """获取图像的分辨率（宽度和高度）。

        Args:
            image_bytes (bytes): 图片

        Returns:
            tuple[int, int]: 图片分辨率
        """
        img = PILImage.open(BytesIO(self._image_bytes))
        return img.size
    
    @property
    def resolution(self) -> tuple[int, int]:
        """获取图像的分辨率（宽度和高度）。

        Args:
            image_bytes (bytes): 图片

        Returns:
            tuple[int, int]: 图片分辨率
        """
        img = PILImage.open(BytesIO(self._image_bytes))
        return img.size
    
    @property
    def image_bytes(self) -> bytes:
        return self._image_bytes
    
    def __str__(self):
        try:
            return f"图片 {self.name if self.name else '未命名'} 分辨率 {self.resolution}"
        except:
            return "图片损坏"