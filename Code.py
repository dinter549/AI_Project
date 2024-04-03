from openai import OpenAI
import telebot
import base64
import requests
from sympy import preview

# Выбор нужной модели ИИ
model = "gpt-4-vision-preview"

# Ознакоммительное сообщение
welcome_message = """🤖 Добро пожаловать в умного помощника с ИИ! Я здесь, чтобы помогать вам с информацией, обучением и многим другим, используя передовые технологии искусственного интеллекта.

💡 **Как использовать:**
Просто отправьте мне текстовый запрос или изображение, и я предоставлю вам необходимую информацию или поддержку. Для очистки диалога используйте команду /clear

📚 **Идеально подходит для:**
- Быстрого доступа к информации
- Помощи в учебе и самообразовании
- Решения повседневных задач
- Исследования и анализа данных"""


# Функция конвертации изображений в формат base64x
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# Создание клиента Telegram для управления ботом
bot = telebot.TeleBot("api_key", parse_mode="MarkdownV2")

# Создание клиента OpenAI для доступа к модели ИИ
api_key = "api_key"
client = OpenAI(api_key=api_key)

cyrillic_to_latin = {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
        'Е': 'E', 'Ё': 'E', 'Ж': 'Zh', 'З': 'Z', 'И': 'I',
        'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
        'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T',
        'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch',
        'Ш': 'Sh', 'Щ': 'Sch', 'Ъ': '', 'Ы': 'Y', 'Ь': '',
        'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya'
    }

# Создание словаря, состоящего из ID пользователей и их диалогов с ботом
dialogs = {}


# Обработчик команды /clear
@bot.message_handler(commands=['clear'])
def clear_dialog(message):
    global dialogs
    dialogs[message.from_user.id] = []
    bot.reply_to(message, "Диалог очищен\!")


# Функция для форматирования сообщений под формат Telegram
def format_message(message):
    response = ""
    for i in range(len(message)):
        if message[i] in ['_', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'] and message[
            i - 1] != "\\":
            response += f"\{message[i]}"
        else:
            response += message[i]
    response = response.replace("**", "sljkgfnjekrghjserf")
    response = response.replace("*", "\*")
    response = response.replace("sljkgfnjekrghjserf", "*")
    return response


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id, format_message(welcome_message))


# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    global dialogs, model
    # Отправка стикера с песочными часами, изображающих генерацию ответа
    waiting = bot.send_sticker(message.from_user.id,
                               "CAACAgEAAxkBAAED12Rl4foXrjDjB89gE7OA-SIKP4i7BQACgAIAAqFjGUSrWD-iBcJN3DQE")
    # Добавление сообщения пользователя в диалог
    if message.from_user.id in dialogs:
        dialogs[message.from_user.id].append({"role": "user", "content": message.text})
    else:
        dialogs[message.from_user.id] = [{"role": "user", "content": message.text}]
    # Генерация ответа от ИИ
    completion = client.chat.completions.create(
        model=model,
        messages=dialogs[message.from_user.id]
    )
    # Удаление стикера с песочными часами
    bot.delete_message(chat_id=message.chat.id, message_id=waiting.message_id)
    # Далее идёт нахождение формул, записанных в LaTeX, их отделение от основного текста и конвертация в изображение
    # Т. к. в тг нет другого способа красиво отобразить формулы
    response1 = completion.choices[0].message.content
    obr = 0
    starts = [0]
    for i in range(len(response1) - 1):
        if response1[i] + response1[i + 1] == "\[":
            formula = "\["
            for j in range(i + 2, len(response1)):
                formula += response1[j]
                if formula[-2] + formula[-1] == "\]":
                    obr = j
                    starts.append(j + 1)
                    break
            piece = ""
            for x in range(starts[-2], i):
                piece += response1[x]
            if piece.replace("\n", "").replace(" ", "") != "":
                bot.send_message(message.from_user.id, format_message(piece))
            try:
                for d in cyrillic_to_latin:
                    formula = formula.replace(d, cyrillic_to_latin[d])
                preview(r'$$' + formula[2:][:-2] + '$$', viewer='file',
                        filename='formula.png',
                        euler=False,
                        dvioptions=["-D", "600"])
                with open('formula.png', 'rb') as photo:
                    bot.send_photo(message.from_user.id, photo)
            except:
                bot.send_message(message.from_user.id, format_message(formula))
    if obr == 0:
        response = format_message(response1)
    else:
        response = format_message(response1[obr + 1:])
    bot.send_message(message.from_user.id, response)
    # Добавление ответа ИИ в диалог
    dialogs[message.from_user.id].append({"role": "assistant", "content": response1})


# Обработчик сообщений, содержащих фотографию
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Отправка стикера с песочными часами, изображающих генерацию ответа
    waiting = bot.send_sticker(message.from_user.id,
                               "CAACAgEAAxkBAAED12Rl4foXrjDjB89gE7OA-SIKP4i7BQACgAIAAqFjGUSrWD-iBcJN3DQE")
    # API Телеграма возвращает несколько фотографий в различном качестве в виде списка, где качество идёт по
    # возврастанию, поэтому выбирается последняя фотография в наилучшем качестве(исходном)
    file_id = message.photo[-1].file_id

    file_info = bot.get_file(file_id)

    downloaded_file = bot.download_file(file_info.file_path)

    with open("photo.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)

    image_path = "photo.jpg"
    # Конвертация изображения в формат base64, т. к. только в таком формате их воспринимает модель
    base64_image = encode_image(image_path)
    # Тут идёт создание запроса для его последующей отправки
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    if message.from_user.id in dialogs:
        if message.caption is not None:
            dialogs[message.from_user.id].append({"role": "user", "content": [{"type": "text", "text": message.caption},
                                                                              {"type": "image_url", "image_url": {
                                                                                  "url": f"data:image/jpeg;base64,{base64_image}"
                                                                              }}]})
        else:
            dialogs[message.from_user.id].append({"role": "user", "content": [{"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }}]})
    else:
        if message.caption is not None:
            dialogs[message.from_user.id] = [{"role": "user", "content": [{"type": "text", "text": message.caption},
                                                                          {"type": "image_url", "image_url": {
                                                                              "url": f"data:image/jpeg;base64,{base64_image}"
                                                                          }}]}]
        else:
            dialogs[message.from_user.id] = [{"role": "user", "content": [{"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }}]}]
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": dialogs[message.from_user.id],
        "max_tokens": 4096
    }
    # Получение ответа от ИИ
    response0 = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # Удаление стикера
    bot.delete_message(chat_id=message.chat.id, message_id=waiting.message_id)
    # Нахождение текста ответа ИИ
    response1 = response0.json()['choices'][0]['message']['content']
    # Форматирование формул
    obr = 0
    starts = [0]
    for i in range(len(response1) - 1):
        if response1[i] + response1[i + 1] == "\[":
            formula = "\["
            for j in range(i + 2, len(response1)):
                formula += response1[j]
                if formula[-2] + formula[-1] == "\]":
                    obr = j
                    starts.append(j + 1)
                    break
            piece = ""
            for x in range(starts[-2], i):
                piece += response1[x]
            if piece.replace("\n", "").replace(" ", "") != "":
                bot.send_message(message.from_user.id, format_message(piece))
            try:
                for d in cyrillic_to_latin:
                    formula = formula.replace(d, cyrillic_to_latin[d])
                preview(r'$$' + formula[2:][:-2] + '$$', viewer='file',
                        filename='formula.png',
                        euler=False,
                        dvioptions=["-D", "600"])
                with open('formula.png', 'rb') as photo:
                    bot.send_photo(message.from_user.id, photo)
            except:
                bot.send_message(message.from_user.id, format_message(formula))
    if obr == 0:
        response = format_message(response1)
    else:
        response = format_message(response1[obr + 1:])
    # Отправка ответа ИИ пользователю
    bot.send_message(message.from_user.id, response)
    # Добавление ответа ИИ в диалог
    dialogs[message.from_user.id].append({"role": "assistant", "content": response1})


# Эта строчка позволяет бесконечно работать и принимать сообщения пользователей
bot.infinity_polling()
