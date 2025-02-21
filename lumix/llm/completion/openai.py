import os
from logging import Logger
from typing import Any, List, Dict, Union, Callable, Optional
from openai import OpenAI as OpenAIOriginal
from lumix.utils.logger import LoggerMixin
from lumix.types.message import Message
from lumix.types.openai.sync import ChatCompletion
from lumix.types.openai.sse import Stream, ChatCompletionChunk


__all__ = [
    "OpenAI",
]


class OpenAI(LoggerMixin):
    """"""
    api_key: str
    client: OpenAIOriginal

    def __init__(
            self,
            model: str,
            base_url: Optional[str] = "https://api.openai.com/v1",
            api_key: Optional[str] = None,
            key_name: Optional[str] = None,
            client: Optional[OpenAIOriginal] = None,
            verbose: Optional[bool] = False,
            logger: Optional[Union[Logger, Callable]] = None,
            **kwargs: Any,
    ):
        """"""
        self.model = model
        self.base_url = base_url
        self.set_api_key(api_key, key_name)
        self.set_client(client)
        self.logger = logger
        self.verbose = verbose
        self.kwargs = kwargs

    def set_api_key(self, api_key: Optional[str] = None, key_name: Optional[str] = None):
        """"""
        if api_key is not None:
            self.api_key = api_key
        elif key_name is not None:
            self.api_key = os.getenv(key_name)
        if self.api_key is None:
            raise ValueError("API key not found")

    def set_client(self, client: Optional[OpenAIOriginal] = None,):
        """"""
        if isinstance(client, OpenAIOriginal):
            self.client = client
        else:
            self.client = OpenAIOriginal(api_key=self.api_key, base_url=self.base_url)

    def list_models(self):
        """"""
        return self.client.models.list()

    def completion(
            self,
            prompt: Optional[str] = None,
            messages: Optional[List[Message]] = None,
            stream: Optional[bool] = False,
            tools: List[Dict] = None,
            **kwargs,
    ) -> Union[ChatCompletion | Stream[ChatCompletionChunk]]:
        """"""
        if prompt is not None:
            messages = [Message(role="user", content=prompt)]
        self._logger(msg=f"[User] {messages[-1].content}\n", color="blue")
        completion = self.client.chat.completions.create(
            model=self.model, messages=[msg.to_dict() for msg in messages],
            tools=tools, stream=stream, **kwargs)
        if stream:
            return self.sse(completion)
        else:
            return self.sync(completion)

    def sse(self, completion: Stream[ChatCompletionChunk]) -> Stream[ChatCompletionChunk]:
        """"""
        content = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                content += chunk.choices[0].delta.content
            yield chunk
        self._logger(msg=f"[Assistant] {content}\n", color="green")

    def sync(self, completion: ChatCompletion) -> ChatCompletion:
        """"""
        self._logger(msg=f"[Assistant] {completion.choices[0].message.content}\n", color="green")
        return completion
