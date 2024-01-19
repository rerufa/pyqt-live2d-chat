import common
import os
import functools
import asyncio
import requests
from typing import Callable


def bert_vits_tts_clo(loop: asyncio.BaseEventLoop = None) -> Callable:
    if loop is None: loop = asyncio.get_event_loop()
    url = os.environ.get("TTS_ENDPOINT")
    @common.wrap_log_ts_async
    async def bert_vits_tts_inner(text: str) -> bytes:
        resp = await loop.run_in_executor(
            None,
            functools.partial(
                requests.get,
                url,
                params={
                    "text": requests.utils.quote(text),
                    "sdp_ratio": 0.2,
                    "noise_scale": 0.6,
                    "noise_scale_w": 0.8,
                    "length_scale": 1.0
                }))
        return resp.content
    return bert_vits_tts_inner