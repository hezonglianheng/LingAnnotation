# encoding: utf-8
# date: 2025/05/11

import pkuseg
from typing import List, Tuple

class NLPModule:
    """NLP模块的基类"""
    instance = None
    pkuseg_model = None
    """pkuseg模型"""

    @classmethod
    def get_instance(cls) -> 'NLPModule':
        """获取NLP模块的单例实例"""
        if cls.instance is None:
            cls.instance = NLPModule()
        return cls.instance

    @classmethod
    def get_model(cls):
        """获取NLP模型"""
        # 获取pkuseg模型
        if cls.pkuseg_model is None:
            try:
                cls.pkuseg_model = pkuseg.pkuseg(postag=True)
            except Exception as e:
                raise ValueError(f"加载pkuseg模型失败: {e}")
            if cls.pkuseg_model is None:
                raise ValueError("pkuseg模型加载失败，请检查")
        return 

    def __init__(self):
        """初始化NLP模块"""
        # 检查所有类变量，若有类变量为None，则调用get_model方法
        self.get_model()

    def pos_tagging(self, text: str, model: str = "pkuseg") -> List[Tuple[str, str]]:
        """对文本进行分词和词性标注

        Args:
            text (str): 待处理文本
            model (str, optional): 模型名称. Defaults to "pkuseg".

        Raises:
            ValueError: 不支持的模型

        Returns:
            List: 分词和词性标注结果
        """
        if model == "pkuseg":
            return self.pkuseg_model.cut(text)
        else:
            raise ValueError(f"不支持的模型: {model}")

if __name__ == "__main__":
    module = NLPModule.get_instance()
    print(module.pos_tagging("我爱北京天安门"))