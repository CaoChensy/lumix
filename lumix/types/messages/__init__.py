from .base import *
from .tool import *
from typing import Union


TypeMessage = Union[
    Message,
    ToolMessage,
    ChoiceDelta,
    ChatCompletionMessage,
]
