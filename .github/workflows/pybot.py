import telebot
from datetime import datetime
from bs4 import BeautifulSoup
import requests

access_token="6241727026:AAFb7DPfizf-Bbc1t4jE45vsDAjvwLG0nRY"
bot=telebot.TeleBot(access_token)

def get_page(group):
    url = "https://itmo.ru/ru/schedule/0/{group}/raspisanie_zanyatiy_{group}.htm".format(group = group)
    response = requests.get(url)
    web_page = response.text
    return web_page

def get_schedule(web_page, day):
    soup = BeautifulSoup(web_page, "html.parser")
    schedule_table = soup.find("table", attrs={"id": str(day)+"day"})
    try:
        times_list = schedule_table.find_all("td", attrs={"class": "time"})
        times_list = [time.span.text for time in times_list]

        # Место проведения занятий
        locations_list = schedule_table.find_all("td", attrs={"class": "room"})

        audit_list = [room.text.split('\n\n') for room in locations_list]
        audit_list = [audit[1].split(', ') for audit in audit_list]
        audit_list = [audit[0].split('\n')[0] for audit in audit_list]

        locations_list = [room.span.text for room in locations_list]

        # Название дисциплин и имена преподавателей
        lessons_list = schedule_table.find_all("td", attrs={"class": "lesson"})
        lessons_list = [lesson.text.split('\n\n\n') for lesson in lessons_list]
        lessons_list = [','.join([info for info in lesson_info if info]) for lesson_info in lessons_list]

        return times_list, locations_list, lessons_list, audit_list
    except Exception:
        return 'null'

def get_day(ms):
    commands = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'tommorow', 'near']
    i = 1
    for comm in commands:
        st = ms[1:]
        if comm == st:
            return i
        else:
            i+=1
    return i

def get_tommorows():
    time = datetime.now()
    weekday = datetime.isoweekday(time)
    day = weekday + 1
    if day == 7:
        day = 1
    print(day)
    return day


@bot.message_handler(commands=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
def get_monday(message):
    ms = message.text.split(' ')
    day = get_day(ms[0])
    web_page = get_schedule(get_page(ms[1]), day)
    if web_page != 'null':
        times_lst, locations_lst, lessons_lst, audit_lst = web_page
        resp = ''
        for time, location, lession, audit in zip(times_lst, locations_lst, lessons_lst, audit_lst):
            resp += '<b>{} - {}</b>, {} {}\n\n'.format(time, audit, location, lession)
    else:
        resp = 'Занятий нет'

    bot.send_message(message.chat.id, resp, parse_mode='HTML')

@bot.message_handler(commands=['tommorow'])
def get_tommorow(message):
    ms = message.text.split(' ')
    day = get_tommorows()
    web_page = get_schedule(get_page(ms[1]), day)
    if web_page != 'null':
        times_lst, locations_lst, lessons_lst, audit_lst = web_page
        resp = ''
        for time, location, lession, audit in zip(times_lst, locations_lst, lessons_lst, audit_lst):
            resp += '<b>{} - {}</b>, {} {}\n\n'.format(time, audit, location, lession)
    else:
        resp = 'Занятий нет'

    bot.send_message(message.chat.id, resp, parse_mode='HTML')



if __name__ == '__main__':
    bot.polling(none_stop=True)
