from typing import Dict
from pydantic import BaseModel, Field


__all__ = [
    "Message"
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
