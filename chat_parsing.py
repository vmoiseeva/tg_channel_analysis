from telethon.sync import TelegramClient
import csv
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import MessageService, MessageMediaPhoto, MessageMediaDocument
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')
channel_name = 'aimylogic'

client = TelegramClient(phone, api_id, api_hash)
client.start()

all_messages = []
offset_id = 0
limit = 100
total_messages = 0
total_count_limit = 0

# Собираем все сообщения из чата
while True:
    message_history = client(GetHistoryRequest(
        peer=channel_name,
        offset_id=offset_id,
        offset_date=None,
        add_offset=0,
        limit=limit,
        max_id=0,
        min_id=0,
        hash=0
    ))

    # Если больше нет сообщений, выходим из цикла
    if not message_history.messages:
        break

    messages = message_history.messages
    # Запишем основные типы сообщений
    for message in messages:
        message_type = 'text'   # По умолчанию сообщение текстовое

        if isinstance(message, MessageService):
            message_type = 'service'
        elif message.media:
            # Проверим тип медиафайла
            if isinstance(message.media, MessageMediaPhoto):
                message_type = 'photo'
            elif isinstance(message.media, MessageMediaDocument):
                mime_type = message.media.document.mime_type
                if 'video' in mime_type:
                    message_type = 'video'
                elif 'audio' in mime_type:
                    message_type = 'audio'
                else:
                    message_type = 'document'

        # Соберем информацию о реакциях на сообщение
        reactions = []
        if message.reactions:
            for reaction in message.reactions.results:
                reactions.append(f'{reaction.reaction.emoticon}: {reaction.count}')

        # Сохраним всю информацию о сообщениях в список
        all_messages.append([
            message.id,
            message.date.strftime('%Y-%m-%d %H:%M:%S'),
            message.sender_id,
            message.reply_to_msg_id if message.reply_to else None,
            message.message,
            message_type,
            ", ".join(reactions) if reactions else None
        ])
        total_messages += 1

        # Отслеживаем прогресс сохранения каждые 1000 сообщений
        if total_messages % 1000 == 0:
            print(f"Сохранено {total_messages} сообщений...")

    # Обновим offset_id для следующей порции сообщений
    offset_id = messages[len(messages) - 1].id

    # Проверим ограничение на количество сообщений
    if total_count_limit != 0 and total_messages >= total_count_limit:
        break

# Сохраним все сообщения в csv
with open('channel_messages.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=',', lineterminator='\n')
    writer.writerow(['message_id', 'date', 'sender_id', 'reply_to', 'message', 'message_type', 'reactions'])
    writer.writerows(all_messages)

print("Все сообщения сохранены.")