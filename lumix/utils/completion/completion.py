from pydantic import BaseModel
from typing import Optional
from lumix.types.openai.literal import TypeRole, TypeFinishReason
from lumix.types.openai.sse import ChatCompletionChunk
from lumix.types.openai.sync import ChatCompletion

from .sync import *
from .chunk import *


__all__ = [
    "TransCompletionContent",
]


class TransCompletionContent(BaseModel):
    role: TypeRole
    content: str
    model: str
    finish_reason: Optional[TypeFinishReason]

    def __init__(
            self,
            role: TypeRole,
            content: str,
            model: str,
            finish_reason: Optional[TypeFinishReason] = None,
            **kwargs
    ):
        """"""
        super().__init__(
            role=role, content=content, model=model,
            finish_reason=finish_reason,
            **kwargs)

    def chunk(
            self,
            chunk: Optional[ChatCompletionChunk] = None,
    ) -> ChatCompletionChunk:
        """"""
        return chat_completion_chunk(self.role, self.content, chunk=chunk, model=self.model)

    def completion(self) -> ChatCompletion:
        """"""
        return chat_completion(
            role=self.role, content=self.content,
            model=self.model, finish_reason=self.finish_reason
        )

    def ali_chunk(
            self,
            i: Optional[int] = 0,
            delta: Optional[bool] = False,
            chunk: Optional[ChatCompletionChunk] = None,
    ):
        """"""
        if delta:
            completion = self.chunk(chunk=chunk)
        else:
            completion = self.completion()
        return f"id: {i}\ndata: {completion.model_dump_json()}\r\n\r\n".encode("utf-8")
