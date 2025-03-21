import unittest
from lumix.agent.tools import BaiduSearch, baidu_search
from lumix.llm import OpenAI
from lumix.agent import ToolsAgent, Tools
from lumix.types.messages import SystemMessage, UserMessage, AssistantMessage


class TestBaiduSearch(unittest.TestCase):
    """"""
    def setUp(self):
        """"""
        self.baidu = BaiduSearch(verbose=True)

    def test_Baidu_search(self):
        """"""
        data = self.baidu.search(query="杭州天气", pages=1)
        print(len(data))
        for item in data:
            print(item)
            print()


class TestSearchAgent(unittest.TestCase):
    """"""
    def setUp(self):
        """"""
        self.base_url = "https://api-inference.modelscope.cn/v1/"
        self.model = "Qwen/Qwen2.5-14B-Instruct-1M"
        self.llm = OpenAI(model=self.model, base_url=self.base_url, key_name="MODELSCOPE_TOKEN", verbose=False)
        self.tools = Tools(tools=[baidu_search])

    def test_search(self):
        """"""
        agent = ToolsAgent(tools=self.tools, llm=self.llm, verbose=True)
        messages = [
            SystemMessage(content="You are a helpful assistant. Use search tool before answer user's question. Answer in Markdown format and give the corresponding url quote."),
            UserMessage(content="目前国际乒乓积分排名前五的是哪些人，积分是多少？")
        ]
        completion = agent.completion(messages=messages)
        print(completion.choices[0].message.content)

