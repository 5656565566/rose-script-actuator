from pydantic import BaseModel, ValidationError, model_validator
from pathlib import Path

import os
import yaml

from log import logger, set_log_level

PATH_WORKING = Path.cwd()
"""
当前工作目录路径
"""

class YamlConfig:
    def __init__(self, filepath):
        self.filepath = filepath

    def read_config(self):
        try:
            with open(self.filepath, 'r', encoding="utf-8") as file:
                config = yaml.safe_load(file)
                return config
        except FileNotFoundError:
            logger.error(f"File not found: {self.filepath}")
        except yaml.YAMLError as e:
            logger.error(f"Error reading YAML file: {e}")

    def write_config(self, config):
        try:
            with open(self.filepath, 'w', encoding="utf-8") as file:
                yaml.safe_dump(config, file, default_flow_style=False)
        except yaml.YAMLError as e:
            logger.error(f"Error writing YAML file: {e}")

    def get_config_value(self, key):
        config = self.read_config()
        if config:
            return config.get(key)
        else:
            logger.warning(f"Could not read config to get the value for key: {key}")
            return None

    def update_config_value(self, key, value):
        config = self.read_config()
        if config is not None:
            config[key] = value
            self.write_config(config)
        else:
            logger.warning(f"Could not read config to update the value for key: {key}")

    def delete_config_value(self, key):
        config = self.read_config()
        if config and key in config:
            del config[key]
            self.write_config(config)
        else:
            logger.warning(f"Key {key} not found in config")
            
    @staticmethod
    def create_file(filepath: str, content: dict):
        try:
            with open(filepath, 'w', encoding="utf-8") as file:
                yaml.safe_dump(content, file, default_flow_style=False)
            logger.opt(colors=True).debug(f"<g>File '{filepath}' created successfully.</g>")
        except Exception as e:
            logger.error(f"Error creating file '{filepath}': {e}")
            

class Setting(BaseModel):
    log_level: str = "DEBUG"
    
    stop_key: str = "F9"
    start_key: str = "F10"
    mapping: dict = {}
    save_screenshot: bool = False
    
    extra: dict = {}

    class Config:
        extra= "allow"
    
    @model_validator(mode= "after")
    def gather_extra(self):
        extra = {}
        config = self.model_dump()
        for key, value in config.items():
            if key not in self.model_fields:
                extra[key] = value
                delattr(self, key)
        self.extra = extra
        return self

    
    @classmethod
    def from_yaml(cls, yaml_file):
        
        if not os.path.exists(PATH_WORKING / yaml_file):
            YamlConfig.create_file(PATH_WORKING / yaml_file, cls().model_dump(exclude = {"extra"}))
        
        yaml_config = YamlConfig(yaml_file)
        config_data = yaml_config.read_config()
        
        if config_data:
            try:
                return cls(**config_data)
            except ValidationError as e:
                logger.error(f"Validation error: {e}")
        return None

    def to_yaml(self, yaml_file):
        yaml_config = YamlConfig(yaml_file)
        yaml_config.write_config(self.model_dump(exclude = {"extra"}))


setting: Setting = None

def get_config():
    global setting
    if setting:
        return setting
    else:
        logger.debug(f"配置文件未加载 !")

def read_conifg(path: str = ""):
    global setting
    
    file = Path(path)
    
    if path == "":
        file = PATH_WORKING / "config.yaml"
    
    setting = Setting.from_yaml(file)
    set_log_level(setting.log_level)
    logger.info(f"成功载入配置文件 {file}")
    logger.debug(f"使用快捷键 {setting.start_key} 快捷启动上一个脚本")
    logger.debug(f"使用快捷键 {setting.stop_key} 停止所有脚本")
