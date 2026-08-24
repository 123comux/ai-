"""pytest 会话级配置：让 SQLite 测试使用独立的临时库，不污染开发库 data/cms.db。

关键点：必须在任何 `import database` / `import backend.main` 之前设置 DB_PATH 环境变量，
因为 config.py 在 import 时就会读取 DB_PATH 并固化为模块级常量。conftest.py 的模块级代码
由 pytest 在加载 test_*.py 之前执行，因此这里设置的环境变量会先生效。

MySQL 引擎（CI 的 backend-mysql job）不受影响：走真实 MySQL，由 `python -m database`
预先建表灌种子，本文件不重复建/灌，避免二次 insert 产生重复行。
"""

import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (ROOT, BACKEND):
    if p not in sys.path:
        sys.path.insert(0, p)

# 测试必须走 DEV_MODE（假 code 登录），强制覆盖 .env 里的 DEV_MODE=false。
# load_dotenv 默认不覆盖已存在的环境变量，所以这里先设好再 import config 即可生效。
os.environ["DEV_MODE"] = "true"

_is_sqlite = os.getenv("DB_ENGINE", "sqlite").lower() != "mysql"
if _is_sqlite:
    _tmp = tempfile.NamedTemporaryFile(prefix="test_cms_", suffix=".db", delete=False)
    _tmp.close()
    os.environ["DB_PATH"] = _tmp.name
    os.environ["DB_ENGINE"] = "sqlite"

# 现在才 import，让 config.py 读到上面设置的环境变量。
from database import init_db, seed_from_json  # noqa: E402

if _is_sqlite:
    # 建表 + 灌种子（courses/projects/videos/directions/banners/faq/admin 等）。
    # init_db 幂等；seed_from_json 每次会话只跑一次。
    init_db()
    seed_from_json()
