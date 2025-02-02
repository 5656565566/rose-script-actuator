from pathlib import Path

import os
import shutil

class FileHelper:
    @staticmethod
    def file_rename(old_name: Path, new_name: Path) -> None:
        """文件重命名

        Args:
            old_name (Path): 旧文件名
            new_name (Path): 新文件名
        """
        return os.rename(old_name, new_name)
    
    @staticmethod
    def folder_create(folder_name: Path) -> None:
        """新建文件夹

        Args:
            folder_name (Path): 文件夹名
        """
        return os.mkdir(folder_name)

    @staticmethod
    def file_move(src: Path, dest: Path) -> None:
        """文件移动

        Args:
            src (Path): 源文件
            dest (Path): 目标文件
        """
        return shutil.move(src, dest)
        
    @staticmethod
    def filePathRemove(path: Path):
        """文件或路径删除"""
        try:
            if os.path.exists(path):  # 检查路径是否存在
                if os.path.isfile(path):  # 如果是文件
                    os.remove(path)
                elif os.path.isdir(path):  # 如果是目录
                    shutil.rmtree(path)  # 递归删除目录及其内容
                    
            return True
        except:
            return False
