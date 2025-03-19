import json
from logging import Logger
from typing import Any, List, Dict, Union, Callable, Optional
from openai import OpenAI as OpenAIOriginal
from pydantic._internal._model_construction import ModelMetaclass
from lumix.api.openai import OpenAIMixin
from lumix.utils.logger import LoggerMixin
from lumix.types.messages import Message, TypeMessage
from lumix.types.openai.sync import ChatCompletion
from lumix.types.openai.sse import Stream, ChatCompletionChunk


__all__ = [
    "OpenAI",
]


class OpenAI(LoggerMixin, OpenAIMixin):
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
        self.api_key = api_key
        self.key_name = key_name
        self.set_client(client)
        self.logger = logger
        self.verbose = verbose
        self.kwargs = kwargs

    def completion(
            self,
            prompt: Optional[str] = None,
            messages: Optional[Union[List[TypeMessage], List[Dict]]] = None,
            stream: Optional[bool] = False,
            tools: List[Dict] = None,
            **kwargs,
    ) -> Union[ChatCompletion | Stream[ChatCompletionChunk]]:
        """"""
        if prompt is not None:
            messages = [Message(role="user", content=prompt)]

        if not isinstance(messages[0], dict):
            messages = [msg.to_dict() for msg in messages]

        self._logger(msg=f"[User] {messages[-1].get("content")}\n", color="blue")
        completion = self.client.chat.completions.create(
            model=self.model, messages=messages, tools=tools, stream=stream, **kwargs)
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

    def structured_schema(self, schema: ModelMetaclass,) -> List[Dict]:
        """"""
        json_schema = schema.model_json_schema()
        schema_tools = [{
            'type': 'function',
            'function': {
                'name': json_schema.get("title"),
                'description': json_schema.get("description"),
                "parameters": {
                    "type": "object",
                    'properties': json_schema.get("properties"),
                    'required': json_schema.get("required")
                },
            }}]
        return schema_tools

    def parse_dict(self, arguments: str) -> Dict:
        """"""
        try:
            return json.loads(arguments)
        except Exception as e:
            raise ValueError(f"Invalid JSON: {e}")

    def structured_output(
            self,
            schema: ModelMetaclass,
            prompt: Optional[str] = None,
            messages: Optional[Union[List[TypeMessage], List[Dict]]] = None,
            **kwargs
    ) -> Dict:
        """"""
        schema_tools = self.structured_schema(schema)
        completion = self.completion(
            prompt=prompt, messages=messages, stream=False, tools=schema_tools, **kwargs)
        if completion.choices[0].message.tool_calls is not None:
            return self.parse_dict(completion.choices[0].message.tool_calls[0].function.arguments)
        else:
            content = completion.choices[0].message.content
            self.error(msg=f"[{__class__.__name__}] No structured data found in the response: {content}")
            return {}
