# encoding: utf-8
# date: 2025/05/14

from .utils import NLPModule
from typing import List, Tuple

class NLPService:
    @staticmethod
    def pos_tagging(text: str, model: str = "pkuseg") -> List[Tuple[str, str]]:
        """对文本进行分词和词性标注

        Args:
            text (str): 待处理文本
            model (str, optional): 模型名称. Defaults to "pkuseg".

        Raises:
            ValueError: 不支持的模型

        Returns:
            List: 分词和词性标注结果
        """
        nlp_module = NLPModule.get_instance()
        return nlp_module.pos_tagging(text, model)