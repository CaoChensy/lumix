import os
from typing import Optional
from openai import OpenAI


__all__ = ['OpenAIMixin']


class OpenAIMixin:
    """"""
    api_key: str
    key_name: str
    client: OpenAI

    def set_api_key(self, api_key: Optional[str] = None, key_name: Optional[str] = None):
        """"""
        if api_key is not None:
            self.api_key = api_key
        elif key_name is not None:
            self.api_key = os.getenv(key_name)
        if self.api_key is None:
            raise ValueError("API key not found")

    def set_client(self, client: Optional[OpenAI] = None,):
        """"""
        self.set_api_key(self.api_key, self.key_name)
        if isinstance(client, OpenAI):
            self.client = client
        else:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def list_models(self):
        """"""
        return self.client.models.list()
