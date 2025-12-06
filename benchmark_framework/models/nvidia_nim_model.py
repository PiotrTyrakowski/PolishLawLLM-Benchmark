from openai import OpenAI

from benchmark_framework.models.nvidia_model import NvidiaModel


class NvidiaNimModel(NvidiaModel):
    """
    Model implementation via NVIDIA NIM API.
    Inherits from NvidiaModel, only changes the base URL.
    """

    def _set_client(self):
        self.client = OpenAI(
            base_url="https://nim.api.nvidia.com/v1", api_key=self._api_key
        )
