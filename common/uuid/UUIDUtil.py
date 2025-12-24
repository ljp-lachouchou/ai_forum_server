import datetime
import uuid
from pathlib import Path


class UUIDUtil:
    @staticmethod
    def generate_object_key(original_filename):
        date_str = datetime.datetime.now().strftime("%Y%m%d")

        # 2. 生成一个短唯一标识，防止同名文件覆盖
        short_uuid = uuid.uuid4().hex[:8]

        # 3. 规范化文件名（移除特殊字符，防止 URL 报错）
        safe_name = Path(original_filename).name.replace(" ", "-")
        return f"r{date_str}-{short_uuid}-{safe_name}"