"""课程小节内容扩充库：为 250 个小节提供「详实理论讲解 + 实战案例分析」。

每个条目键为小节 id，值为：
  content: 详实理论讲解（是什么/为什么/怎么做/注意事项，约 200-350 字）
  case:    实战案例分析（背景/做法/效果/启示，约 120-220 字）
  knowledge_points: 可选的补充知识点列表（不提供则保留原有）

由 curriculum_2026.main() 在生成数据时合并到对应小节。
"""
from .s1 import SECTION_ENRICH as _S1
from .s2 import SECTION_ENRICH as _S2
from .s3 import SECTION_ENRICH as _S3
from .s4 import SECTION_ENRICH as _S4
from .s5 import SECTION_ENRICH as _S5
from .s6 import SECTION_ENRICH as _S6
from .s7 import SECTION_ENRICH as _S7

SECTION_ENRICH: dict[str, dict] = {}
for _d in (_S1, _S2, _S3, _S4, _S5, _S6, _S7):
    SECTION_ENRICH.update(_d)
