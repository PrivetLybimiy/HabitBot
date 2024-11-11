import os
import g4f
import time
import asyncio

async def get_recommendation(purpose):
    user_message = f"{purpose}. Дай пошаговые инструкции."

    response = await asyncio.to_thread(g4f.ChatCompletion.create,
                                       model="gpt-4",
                                       messages=[{"role": "system",
                                                  "content": "Ты помощник по развитию полезных привычек, описывай подробно 10 шагов только по развитию привычки"},
                                                 {"role": "user", "content": user_message}],
                                       temperature=0.2,
                                       max_tokens=150)

    if response:
        return response
    else:
        return None

