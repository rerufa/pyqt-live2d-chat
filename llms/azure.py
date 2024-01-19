import asyncio
from typing import Callable
import os
import functools
import requests
import common


def azure_clo() -> Callable:
    loop = asyncio.get_event_loop()
    bk = []
    endpoint = os.environ.get("AZURE_ENDPOINT")
    api_key = os.environ.get("AZURE_API_KEY")
    model = os.environ.get("AZURE_MODEL")
    prefixs = os.environ.get("AZURE_PREFIX").split(",")
    url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version=2023-03-15-preview"
    init_prompt = open("./prompts/bullet_init.txt").read()
    error_prompt = open("./prompts/bullet_error.txt").read()
    async def azure_inner(text: str) -> str:
        for prefix in prefixs:
            if text.startswith(prefix):
                text = text[len(prefix):]
                break
        else:
            return None
        messages = [
            {
                "role": "system",
                "content": init_prompt
            },
            {
                "role": "user",
                "content": text
            }
        ]
        messages.extend(bk)
        new_message = {
            "role": "user",
            "content": text
        }
        messages.append(new_message)
        resp = await loop.run_in_executor(
            None, 
            functools.partial(requests.post, 
            url=url,
            headers={"Content-Type": "application/json", "api-key": api_key},
            json={
                "messages": messages
            }
            )
        )
        if resp.json()['choices'][0]['finish_reason'] == "content_filter":
            return error_prompt
        re_message = resp.json()['choices'][0]['message']
        bk.append(new_message)
        bk.append(
            {
                "role": re_message['role'],
                "content": re_message['content']
            }
        )
        common.lru_pop(bk)
        return resp.json()['choices'][0]['message']['content']
    return azure_inner
