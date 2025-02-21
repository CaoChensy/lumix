from typing import Dict, Union, List, Literal, Optional
from pydantic import BaseModel, Field
from lumix.types.messages.content import TextContent


__all__ = [
    "Message",
    "SystemMessage",
    "UserMessage",
    "AssistantMessage",
]


class Message(BaseModel):
    """"""
    role: str = Field(default="", description="角色")
    content: str = Field(default="", description="对话内容")

    def to_dict(self) -> Dict:
        """"""
        return self.model_dump()

    def to_message(self):
        """"""
        return self


class SystemMessage(Message):
    """"""
    role: Literal["system"] = Field(default="system", description="角色")
    content: Optional[str] = Field(..., description="对话内容")


class UserMessage(Message):
    """"""
    role: Literal["user"] = Field("user", description="角色")
    content: Optional[Union[str, List[TextContent]]] = Field(..., description="对话内容")


class AssistantMessage(Message):
    """"""
    role: Literal["assistant"] = Field("assistant", description="角色")
    content: Optional[str] = Field(..., description="对话内容")
