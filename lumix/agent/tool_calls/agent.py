from logging import Logger
from typing import List, Tuple, Literal, Callable, Optional, Union

from lumix.utils import LoggerMixin
from lumix.utils.completion import TransCompletionContent
from lumix.types.openai.sse import ChatCompletionChunk, Stream
from lumix.types.openai.sync import ChatCompletion
from lumix.types.messages import Message, ToolMessage
from lumix.agent.tool_calls.tools import Tools
from lumix.llm import TypeLLM


__all__ = ["ToolsAgent"]


class ToolsAgent(LoggerMixin):
    """
    todo: 1. 区分Agent模型与Reasoning模型
    todo: 2. 增加sse模式
    """
    model: str
    api_key: Optional[str]
    api_key_name: Optional[str]
    base_url: str
    tools: Tools

    def __init__(
            self,
            llm: TypeLLM,
            tools: Tools,
            split: Literal["think"] = "think",
            logger: Optional[Union[Logger, Callable]] = None,
            verbose: Optional[bool] = True,
    ):
        """"""
        self.llm = llm
        self.tools = tools
        self.split = split
        self.logger = logger
        self.verbose = verbose

    def completion(
            self,
            prompt: Optional[str] = None,
            messages: Optional[List[Message]] = None,
            stream: Optional[bool] = False,
            **kwargs,
    ) -> Union[ChatCompletion | Stream[ChatCompletionChunk]]:
        """"""
        if prompt is not None:
            messages = [Message(role="user", content=prompt)]
        self._logger(msg=f"[User] {messages[-1].content}\n", color="blue")
        if stream:
            return self.sse(messages)
        else:
            return self.sync(messages)

    def function_call_content_split(self) -> Tuple[str, str]:
        """"""
        if self.split == "think":
            return "<think>", "</think>"
        else:
            return "", ""

    def sync(
            self,
            messages: Optional[List[Message]] = None,
    ) -> ChatCompletion:
        """"""
        completion = self.llm.completion(
            messages=messages, tools=self.tools.descriptions)
        if completion.choices[0].finish_reason == "tool_calls":
            messages.append(completion.choices[0].message)
            function = completion.choices[0].message.tool_calls[0].function
            self._logger(msg=f"[Assistant] name: {function.name}, arguments: {function.arguments}\n", color="green")

            observation = self.tools.dispatch_function(function=function)
            self._logger(msg=f"[Observation] \n{observation}\n", color="magenta")

            messages.append(ToolMessage(role="tool", content=observation, tool_call_id=completion.choices[0].message.tool_calls[0].id))
            completion = self.llm.completion(messages=messages, tools=self.tools.descriptions)
        content = completion.choices[0].message.content
        self._logger(msg=f"[Assistant] {content}\n", color="green")
        return completion

    def sse(
            self,
            messages: Optional[List[Message]] = None,
    ) -> Stream[ChatCompletionChunk]:
        """"""
        start_split, end_split = self.function_call_content_split()
        completion = self.llm.completion(
            messages=messages, tools=self.tools.descriptions, stream=True)

        chunk: Optional[ChatCompletionChunk] = None
        function = None
        tool_call_id = None
        for i, chunk in enumerate(completion):
            if i == 0:
                yield TransCompletionContent(
                    role="tool", content=start_split, model=chunk.model,
                    finish_reason=None, chunk=chunk,
                ).completion_chunk()
            if chunk.choices[0].delta.tool_calls:
                function = chunk.choices[0].delta.tool_calls[0].function
                tool_call_id = chunk.choices[0].delta.tool_calls[0].id
                messages.append(chunk.choices[0].delta)
                self._logger(msg=f"[Tool] Function: {function.name}; Arguments: {function.arguments}\n", color="yellow")
            yield chunk

        if function is not None:
            observation = self.tools.dispatch_function(function=function)
            self._logger(msg=f"[Observation]: \n{observation}\n\n", color="cyan")
            yield TransCompletionContent(
                role="tool", content=f"\n\n{observation}\n\n{end_split}",
                model=chunk.model, finish_reason=None, chunk=chunk,
            ).completion_chunk()
            messages.append(
                ToolMessage(role="tool", content=observation, tool_call_id=tool_call_id))
            completion = self.llm.completion(messages=messages, tools=self.tools.descriptions, stream=True)

            content = ""
            for chunk in completion:
                yield chunk
                if chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content
            self._logger(msg=f"[Assistant]: {content}", color="green")
