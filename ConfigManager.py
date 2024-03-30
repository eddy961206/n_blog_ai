import configparser
import os

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            # 파일 생성 시 UTF-8 인코딩 명시
            with open(config_file, 'a', encoding='utf-8') as f:
                pass
        # 설정 파일 읽기 시 UTF-8 인코딩 사용
        self.config.read(config_file, encoding='utf-8')

    def save_config(self, section, key, value):
        if isinstance(value, list):
            value = ','.join(value)  # 리스트를 쉼표로 구분된 문자열로 변환
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        # 설정 파일 쓰기 시 UTF-8 인코딩 사용
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

    def load_config(self, section, key):
        # has_option과 has_section 메소드는 인코딩 변경과 무관하므로 그대로 유지
        return self.config.get(section, key) if self.config.has_section(section) and self.config.has_option(section, key) else ''
