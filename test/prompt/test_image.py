import unittest
from lumix.llm import OpenAI
from lumix.types.messages import ImageMessage
from lumix.prompt.prompts import template_extract_table


class TestExtractTablePrompt(unittest.TestCase):
    """"""
    def setUp(self):
        """"""
        base_url = "https://api-inference.modelscope.cn/v1/"
        model = "Qwen/Qwen2.5-VL-32B-Instruct"
        self.llm = OpenAI(model=model, base_url=base_url, key_name="MODELSCOPE_TOKEN", verbose=False)

    def test_image_message_dict(self):
        """"""
        messages = [
            ImageMessage(
                role="user",
                content=template_extract_table,
                images=["../data/extract-image-table.png"],
            ).to_openai()
        ]
        completion = self.llm.completion(messages=messages)
        print(completion.choices[0].message.content)

