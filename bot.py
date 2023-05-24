from telebot import types, TeleBot
from math import ceil
import gspread
import func


#коннект гугл таблицы
gs = gspread.service_account(filename='key.json')  # подключаем файл с ключами и пр.
sh = gs.open_by_key('17EWj8qBIiPJUyf1MWOUTSvgWKLXPa21M9u2VN7x80wc')  # подключаем таблицу по ID
worksheet = sh.sheet1  # получаем первый лист
res = worksheet.get_all_records()


token = '6294596617:AAEQ1woVal-6-6wMrnw0mwyYsL3xzWZI3wM'
bot = TeleBot(token)

# параметры
# цена, количество людей, тип места через запятую именно в таком порядке
param = [-1, -1, -1]
num_page = pages = 1
result = []
length = 0


@bot.message_handler(commands=['start'])
def first(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Начать', callback_data=3))

    bot.send_message(message.chat.id, text='Привет, {0.first_name}\nЯ бот для выбора мест проведения неформалок!\n\n'
                                      'Буду предлагать тебе различные варианты в зависимости от фильтрации по категориям :)'.format(message.from_user, bot.get_me()), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global param, num_page, pages, result, length
    if call.data == '3':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Цена', callback_data=5))
        markup.add(types.InlineKeyboardButton(text='Число людей', callback_data=6))
        markup.add(types.InlineKeyboardButton(text='Тип места', callback_data=7))
        markup.add(types.InlineKeyboardButton(text='Результат', callback_data=9))

        msg = bot.send_message(call.message.chat.id, text='Выбери категорию и установи нужное значение', reply_markup=markup)
        bot.register_next_step_handler(msg, query_handler)

    if len(call.data) == 2 and call.data[0] in {'5', '6', '7'}: #нажали кнопку начать
        param[int(call.data[0]) % 5] = -1 if call.data in {'55', '65', '73'} else int(call.data[1])

        txt = func.text(param)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Цена', callback_data=5))
        markup.add(types.InlineKeyboardButton(text='Число людей', callback_data=6))
        markup.add(types.InlineKeyboardButton(text='Тип места', callback_data=7))
        markup.add(types.InlineKeyboardButton(text='Результат', callback_data=9))

        if txt:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выбери категорию и установи нужное значение\n\nУстановленные параметры:\n\n' + txt, reply_markup=markup)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выбери категорию и установи нужное значение', reply_markup=markup)

    if call.data == '5': #изменение цены
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Бесплатно', callback_data=50))
        markup.add(types.InlineKeyboardButton(text='до 300₽', callback_data=51))
        markup.add(types.InlineKeyboardButton(text='300₽ - 700₽', callback_data=52))
        markup.add(types.InlineKeyboardButton(text='700₽ - 1000₽', callback_data=53))
        markup.add(types.InlineKeyboardButton(text='1000₽+', callback_data=54))
        markup.add(types.InlineKeyboardButton(text='Сбросить', callback_data=55))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Какой бюджет на человека или компанию', reply_markup=markup)

    if call.data == '6': #изменение числа людей
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='до 5', callback_data=60))
        markup.add(types.InlineKeyboardButton(text='5 - 10', callback_data=61))
        markup.add(types.InlineKeyboardButton(text='11 - 20', callback_data=62))
        markup.add(types.InlineKeyboardButton(text='21 - 30', callback_data=63))
        markup.add(types.InlineKeyboardButton(text='30+', callback_data=64))
        markup.add(types.InlineKeyboardButton(text='Сбросить', callback_data=65))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Сколько человек будет', reply_markup=markup)

    if call.data == '7': #изменение типа места
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Помещение', callback_data=70))
        markup.add(types.InlineKeyboardButton(text='Улица', callback_data=71))
        markup.add(types.InlineKeyboardButton(text='Сбросить', callback_data=73))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Какой тип места предпочтительнее', reply_markup=markup)

    if call.data == '9': #вывод результатов
        result = [elem['Название'] + ' ({})'.format(elem['Станция метро']) for elem in res if (elem['Деньги'] == -1 or param[0] in {elem['Деньги'], -1}) and (elem['Сколько человек'] == -1 or param[1] in {elem['Сколько человек'], -1}) and (elem['На улице?'] == -1 or param[2] in {elem['На улице?'], -1})]
        if result is None or result == []:
            result = ['Нет мест с такими параметрами :(']
        pages = ceil(len(result) / 8)
        param = [-1, -1, -1]
        length = len(result)
        print(result)
        if pages > 1:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text='Следующая страница', callback_data=91))

            msg = bot.send_message(call.message.chat.id, text='Результат:\n\n' + '\n'.join(result[0:8]), reply_markup=markup)
            bot.register_next_step_handler(msg, query_handler)
        else:
            bot.send_message(call.message.chat.id, text='Результат:\n\n' + '\n'.join(result))

    if call.data == '91': #перелистывание страницы вперед
        num_page += 1
        if num_page == pages - 1 or (num_page + 1) * 8 >= length - 1:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text='Предыдущая страница', callback_data=90))

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='\n'.join(result[(pages - 1) * 8:length]), reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text='Предыдущая страница', callback_data=90))
            markup.add(types.InlineKeyboardButton(text='Следующая страница', callback_data=91))

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='\n'.join(result[num_page * 8:(num_page + 1) * 8]), reply_markup=markup)

    if call.data == '90': #перелистывание страницы назад
        num_page -= 1
        if num_page == 1:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text='Следующая страница', callback_data=91))

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='\n'.join(result[0:8]), reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text='Предыдущая страница', callback_data=90))
            markup.add(types.InlineKeyboardButton(text='Следующая страница', callback_data=91))

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='\n'.join(result[num_page * 8:(num_page + 1) * 8]), reply_markup=markup)


bot.polling(none_stop=True)


@bot.message_handler(content_types=['text'])
def answer(message):
    if 'спасибо' in message.lower():
        bot.send_message(chat_id=message.chat.id, text='Обращайся <3')
    else:
        bot.send_message(chat_id=message.chat.id, text='Я не понимаю тебя')
