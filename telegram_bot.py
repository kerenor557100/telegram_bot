import telegram as telegram
from flask import Flask, Response, request
import requests
import pyngrok
import pandas as pd

SHOPS = {}
VEGETABLES = {}
EMOJI_VEGETABLES = {"מלפפון": '🥒', "עגבניה":'🍅',"בצל":'🧅', "גזר":'🥕'}
data = {
    'יש': ['', '0.3', '1.1'],
    'רמי לוי': ['0.5', '0.3', '1.3'],
    'שופרסל': ['0.6', '0.3', '1'],
    'אושר עד': ['0.5', '0.3', '']}

df = pd.DataFrame(data, index=['מלפפון', 'עגבניה', 'בצל'])
print(df)

TOKEN = "5644359637:AAG3m8x0zSNOJRttMEE7dZh7C0YhtJ9GivQ"
TELEGRAM_INIT_WEBHOOK_URL = 'https://api.telegram.org/bot{}/setWebhook?url=https://1bea-2a10-800a-3a76-0-1d53-ae49-ff43-61e.eu.ngrok.io/message'.format(
    TOKEN)

app = Flask(__name__)


def check_input(my_input_list: list) -> list:
    """

    :param my_input_list: input from user to check if valid.
    :return: list of relevant vegetables.
    """
    error_message = ''
    list_of_vegetables = {}

    for item in range(len(my_input_list)):
        if my_input_list[item].isdigit():
            if my_input_list[item+1] not in df.index:
                error_message = error_message + "\n" + ("לא נמצא ירק בשם \"" + item + "\"")
            else:
                if my_input_list[item+ 1] not in list_of_vegetables.keys():
                    list_of_vegetables[my_input_list[item+ 1]] = float(my_input_list[item])
                else:
                    list_of_vegetables[my_input_list[item + 1]] = list_of_vegetables[my_input_list[item+ 1]] + float(my_input_list[item])
        else:
            if my_input_list[item] not in df.index:
                error_message = error_message + "\n" + ("לא נמצא ירק בשם \"" + my_input_list[item] + "\"")
            elif item == 0:
                if my_input_list[item] not in list_of_vegetables.keys():
                    list_of_vegetables[my_input_list[item]] = 1
                else:
                    list_of_vegetables[my_input_list[item]] = list_of_vegetables[
                                                                      my_input_list[item]] + 1
            elif item>0:
                if not my_input_list[item-1].isdigit():
                    if my_input_list[item ] not in list_of_vegetables.keys():
                        list_of_vegetables[my_input_list[item ]] = 1
                    else:
                        list_of_vegetables[my_input_list[item]] = list_of_vegetables[
                                                                          my_input_list[item]] + 1

    # for item in my_input_list:
    #     if item not in df.index:
    #         error_message = error_message + "\n" + ("לא נמצא ירק בשם \"" + item + "\"")
    #     else:
    #         list_of_vegetables.append(item)

    return list_of_vegetables, error_message


def add_to_dict(vegetables: dict) -> None:
    """

    :param vegetables: list of vegetables
    add vegetables and amount to VEGETABLES dict from given list
    """
    for vegetable in vegetables.keys():
        if vegetable in VEGETABLES.keys():
            VEGETABLES[vegetable] += vegetables[vegetable]
        else:
            VEGETABLES[vegetable] = vegetables[vegetable]


def delete_dicts():
    VEGETABLES.clear()
    SHOPS.clear()


def show_results():
    """

    Show the sorted shop by the sum of buy and missing vegetable.
    """
    sorted_shop_by_price = sorted(SHOPS.items(), key=lambda x: x[1][0])
    sorted_shop = sorted(sorted_shop_by_price, key=lambda x: x[1][1])
    relevant_sorted_shops = [shop for shop in sorted_shop if shop[1][0] != 0]
    respond = 'בסל הקניות: '
    for vegetable in VEGETABLES.keys():
        respond = respond + EMOJI_VEGETABLES[vegetable]
    respond = respond +' \n'
    if len(relevant_sorted_shops) > 0:
        best_price_shops = [shop for shop in relevant_sorted_shops if shop[1][0] == relevant_sorted_shops[0][1][0]]

    for best_price_shop in best_price_shops:
        respond = respond +"**" + best_price_shop[0] + " : " + str(round(best_price_shop[1][0],4)) + " ש''ח " + str(best_price_shop[1][2]) + "**" +"\n"

    if len(relevant_sorted_shops) > len( best_price_shop):
        for shop in relevant_sorted_shops[len(best_price_shops):]:
            respond = respond + (shop[0] + " : " + str(round(shop[1][0], 4)) + " ש''ח " + str(shop[1][2])) + "\n"
    return respond


def average_calculation() -> None:
    """

    Calculation of an average purchase, including the amount of missing vegetables and information.
    """
    for shop in df.columns:
        SHOPS[shop] = [0, 0, ""]
    for need_vegetable in list(df.index):
        if need_vegetable in list(VEGETABLES.keys()):
            amount = VEGETABLES[need_vegetable]
            for shop in SHOPS.keys():
                if df[shop][need_vegetable]:
                    SHOPS[shop][0] = SHOPS[shop][0] + float(df[shop][need_vegetable]) * amount
                else:
                    SHOPS[shop][2] = SHOPS[shop][2] + "ללא " + need_vegetable + " "
                    SHOPS[shop][1] = SHOPS[shop][1] + 1


@app.route('/message', methods=["POST"])
def handle_message():
    print("got message")
    chat_id = request.get_json()['message']['chat']['id']
    input = request.get_json()['message']['text']
    if input == "סיום":
        delete_dicts()
        res = requests.get(
            "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(TOKEN, chat_id, "**תודה ולהתראות!**",parse_mode= 'Markdown'))
    elif input == "עזרה":
        message = " שלום וברכה! כאן תוכלו למצוא את המחיר הזול ביותר לקניה שלכם! על מנת לעשות זאת- כתבו כאן את רשימת הקניות שלכם ולבסוף הקישו enter.תוכלו להוסיף עוד פריטים ככל שתרצו. לסיום הקישו *סיום* לעזרה הקישו *עזרה* "
        res = requests.get(
            "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(TOKEN, chat_id, message,
                                                                                   parse_mode='Markdown'))
    else:
        list_of_vegetables, error_message = check_input(input.split())
        if error_message:
            res = requests.get(
                "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(TOKEN, chat_id, error_message,
                                                                                       parse_mode='Markdown'))

        add_to_dict(list_of_vegetables)
        average_calculation()
        respond = show_results()
        res = requests.get(
            "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(TOKEN, chat_id, respond,
                                                                                   parse_mode='Markdown'))

    return Response("success")


@app.route('/')
def index():
    return "<h1>server is runnig!</h1>"


if __name__ == '__main__':
    requests.get(TELEGRAM_INIT_WEBHOOK_URL)
    app.run(port=5002)
