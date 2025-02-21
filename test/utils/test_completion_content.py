import unittest
from lumix.utils.completion import TransCompletionContent


class TestCompletionContent(unittest.TestCase):
    def test_trans_completion_content(self):
        """"""
        trans_content = TransCompletionContent(
            role="assistant", content="Hello World", model="chat", finish_reason="stop")
        completion = trans_content.completion()
        print(completion)

    def test_trans_chunk_content(self):
        """"""
        trans_content = TransCompletionContent(
            role="assistant", content="Hello World", model="chat", finish_reason="stop")
        chunk = trans_content.chunk()
        print(chunk)

    def test_ali_chunk(self):
        """"""
        trans_content = TransCompletionContent(
            role="assistant", content="Hello World", model="chat", finish_reason=None)
        chunk = trans_content.ali_chunk(delta=True)
        print(chunk)
