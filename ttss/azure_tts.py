import requests
import asyncio
from typing import Callable
import common
import os
import functools


def azure_tts_clo(loop: asyncio.BaseEventLoop=None) -> Callable:
    if loop is None: loop = asyncio.get_event_loop()
    azure_tts_endpoint = os.environ.get("AZURE_TTS_ENDPOINT")
    azure_tts_api_key = os.environ.get("AZURE_TTS_API_KEY")
    azure_tts_name = os.environ.get("AZURE_TTS_NAME")
    url = f"{azure_tts_endpoint}/cognitiveservices/v1"
    @common.wrap_log_ts_async
    async def azure_tts_inner(text: str) -> bytes:
        resp = await loop.run_in_executor(
            None,
            functools.partial(
                requests.post,
                url,
                headers={
                    "Ocp-Apim-Subscription-Key": azure_tts_api_key,
                    "Content-Type": "application/ssml+xml",
                    "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
                    "User-Agent": azure_tts_name
                },
                data=f"""
                <speak version="1.0" xml:lang="en-CN">
                    <voice name="{azure_tts_name}">
                        {text}
                    </voice>
                </speak>
                """
            )
            )
        return resp.content
    return azure_tts_inner
