# import os
# import g4f
# import time
#
# def get_recommendation(purpose, role_play=0):
#     past_response_message = ""
#
#     # if os.path.exists('response.txt') and os.path.getsize('response.txt') > 0:
#     #     with open('response.txt', 'r', encoding='utf-8') as file:
#     #         past_response = file.read().strip()
#     #         past_response_message = f"Вот твой прошлый диалог: {past_response}"
#
#     user_message = f"{past_response_message} {purpose} Дай пошаговые инструкции. {role_play}" if past_response_message else f"{purpose} Дай пошаговые инструкции. {role_play}"
#     start_time = time.time()
#     response = g4f.ChatCompletion.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": "Ты помощник по развитию полезных привычек, "
#                                           "описывай подробно 10 шагов только по развитию привычки"},
#             {"role": "user", "content": user_message}
#         ]
#     )
#     if response:
#         print("Рекомендации:", response)
#         end_time = time.time()
#         duration = end_time - start_time
#         print(f"Время выполнения запроса: {duration:.2f} секунд")
#         # Записываем ответ в файл для будущего использования
#         with open('response.txt', 'w', encoding='utf-8') as file:
#             file.write(response)
#
#         return response
#     else:
#         print("Ошибка при получении рекомендаций.")
#         return None
import os
import g4f
import time
import asyncio

async def get_recommendation(purpose, role_play=0):
    user_message = f"{purpose}. Дай пошаговые инструкции. {role_play}"

    start_time = time.time()

    response = await asyncio.to_thread(g4f.ChatCompletion.create,
                                       model="gpt-4",
                                       messages=[{"role": "system",
                                                  "content": "Ты помощник по развитию полезных привычек, описывай подробно 10 шагов только по развитию привычки"},
                                                 {"role": "user", "content": user_message}],
                                       temperature=0.2,
                                       max_tokens=150)

    if response:
        print("Рекомендации:", response)
        end_time = time.time()
        duration = end_time - start_time
        print(f"Время выполнения запроса: {duration:.2f} секунд")

        with open('response.txt', 'w', encoding='utf-8') as file:
            file.write(response)

        return response
    else:
        print("Ошибка при получении рекомендаций.")
        return None

