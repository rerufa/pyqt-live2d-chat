import asyncio
from typing import Callable
import os
import functools
import logging
import requests
import common


def gemini_clo() -> Callable:
    loop = asyncio.get_event_loop()
    bk = []
    endpoint = os.environ.get("GEMINI_ENDPOINT")
    model = os.environ.get("GEMINI_MODEL")
    api_key = os.environ.get("GEMINI_API_KEY")
    prefixs = os.environ.get("GEMINI_PREFIX").split(",")
    url = f"{endpoint}/v1/models/{model}?key={api_key}"
    init_prompt = open("./prompts/bullet_init.txt").read()
    error_prompt = open("./prompts/bullet_error.txt").read()
    async def gemini_inner(text: str) -> str:
        for prefix in prefixs:
            if text.startswith(prefix):
                text = text[len(prefix):]
                break
        else:
            return None
        contents = [
            {
                "role": "user",
                "parts": [
                    {
                        "text": init_prompt
                    }
                ]
            },
            {
                "role": "model",
                "parts": [
                    {
                        "text": "我一定遵守."
                    }
                ]
            },
        ]
        contents.extend(bk)
        new_message = {
            "role": "user",
            "parts": [
                    {
                        "text": text
                    }
            ]
        }
        contents.append(new_message)
        resp = await loop.run_in_executor(
            None,
            functools.partial(
                requests.post,
                url=url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": contents
                }
            )
        )
        try:
            re_message = resp.json()['candidates'][0]['content']
        except Exception as e:
            logging.error(f"gemini error, response is {resp.text}")
            return error_prompt
        bk.append(new_message)
        bk.append(re_message)
        common.lru_pop(bk)
        return re_message['parts'][0]['text']
    return gemini_inner