from flask import Flask, Response, request
import requests
import pyngrok
import pandas as pd

SHOPS = {}
VEGETABLES = {}
EMOJI_VEGETABLES = {"מלפפון": '🥒', "עגבניה": '🍅', "בצל": '🧅', "גזר": '🥕', "smile": '😊',"חציל":'🍆',"תפוח-אדמה":'🥔',"ענבים":'🍇',"אבטיח":'🍉',"מלון": '🍈',"בננה":'🍌',"לימון":'🍋',"מנגו":'🥭',"אפרסק":'🍑',"תפוח":'🍏',"אגס":'🍐',"נקטרינה":'🍊',"פסיפלורה":'🍊',"קוקוס":'🥥',"רימון":'🍎',"גמבה":'🌶️',"קישוא":'',"כרוב":'',"שום":'',"סלק":'',"בטטה":'',"פלפל-חריף":'🌶️',"אבוקדו":'🥑'}
SHIPPING = {'רמי לוי': 29.9, 'שופרסל': 30, 'מעיין אלפים': 28}
data = {
    'מעיין אלפים': ['8.90', '18.90', '4.90', '2.90','10.90','16.90','7.90', '8.90','9.90','16.90', '', '','7.90','3.90', '','7.90','3.90', '2.90', '3.50', '5.90', '7.90', '6.90', '3.90', '7.90', '4.90'],
    'רמי לוי': ['7.90', '16', '4.90', '1.90', '12', '7.90', '7.90', '9.90', '8.90', '16.20', '7', '10', '7.90', '5.90', '7.90', '7.90', '5.90', '1.90', '3.90', '4.90', '4,90', '7.90', '4.90', '6.90', '2.90'],
    'שופרסל': ['7.9', '18.9', '4.9', '2.9',"10.9" ,"7.9" ,"10.9" ,"10.9", "8.9" ,"16" ,"" ,"10.9" ,"7.9" ,"5.9" ,"7.9" "", "8", "3.9", "4.9" ,"2", "5.9", "9.9", "7.9" ,"9.9" , "5.9",'14.9']
   }

df = pd.DataFrame(data, index=['אפרסק', "ענבים", "מלון" ,"אבטיח" ,"תפוח" ,"אגס" ,"מנגו" ,"נקטרינה", "בננה" ,"פסיפלורה" ,"קוקוס" ,"רימון" ,"גמבה" ,"עגבניה" ,"לימון" "קישוא", "חציל", "בצל", "תפוח-אדמה" ,"כרוב", "שום", "פלפל-חריף", "סלק" ,"בטטה" , "מלפפון",'אבוקדו'])

print(df)

TOKEN = "5711334526:AAHd7qg_DfVqrVHU61pC3XincRHBeQ5ggmI"
TELEGRAM_INIT_WEBHOOK_URL = 'https://api.telegram.org/bot{}/setWebhook?url=https://3c23-82-80-173-170.eu.ngrok.io/message'.format(
    TOKEN)

app = Flask(__name__)


def check_input(my_input_list: list) -> list:
    """
    :param my_input_list: input from user to check if valid.
    :return: list of relevant vegetables.
    """
    error_message = ''
    dict_of_vegetables = {}

    for item in range(len(my_input_list)):
        if my_input_list[item].isdigit():
            #if my_input_list[item + 1] not in df.index:
              #  error_message = error_message + "\n" + ("לא נמצא ירק בשם \"" + my_input_list[item] + "\"")
            if my_input_list[item + 1] in df.index:
                if my_input_list[item + 1] not in dict_of_vegetables.keys():
                    dict_of_vegetables[my_input_list[item + 1]] = float(my_input_list[item])
                else:
                    dict_of_vegetables[my_input_list[item + 1]] = dict_of_vegetables[my_input_list[item + 1]] + float(
                        my_input_list[item])
        else:
            if my_input_list[item] not in df.index:
                error_message = error_message + "\n" + ("לא נמצא ירק בשם \"" + my_input_list[item] + "\"")
            elif item == 0:
                if my_input_list[item] not in dict_of_vegetables.keys():
                    dict_of_vegetables[my_input_list[item]] = 1
                else:
                    dict_of_vegetables[my_input_list[item]] = dict_of_vegetables[
                                                                  my_input_list[item]] + 1
            elif item > 0:
                if not my_input_list[item - 1].isdigit():
                    if my_input_list[item] not in dict_of_vegetables.keys():
                        dict_of_vegetables[my_input_list[item]] = 1
                    else:
                        dict_of_vegetables[my_input_list[item]] = dict_of_vegetables[
                                                                      my_input_list[item]] + 1

    return dict_of_vegetables, error_message


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
    respond = respond + ' \n'
    if len(relevant_sorted_shops) > 0:
        best_price_shops = [shop for shop in relevant_sorted_shops if shop[1][0] == relevant_sorted_shops[0][1][0]]

    for best_price_shop in best_price_shops:
        respond = respond + "**" + best_price_shop[0] + " : " + str(
            round(best_price_shop[1][0], 4)) + " ש''ח " + str(
            best_price_shop[1][2]) + "**" + " (מתוכם " + str(SHIPPING[best_price_shop[0]]) + " דמי משלוח)\n"

    if len(relevant_sorted_shops) > len(best_price_shop):
        for shop in relevant_sorted_shops[len(best_price_shops):]:
            respond = respond + (
                        shop[0] + " : " + str(round(shop[1][0], 4)) + " ש''ח " + str(
                    shop[1][2])) + " (מתוכם " + str(SHIPPING[shop[0]]) + " דמי משלוח)\n"
    return respond + '.'


def average_calculation() -> None:
    """
    Calculation of an average purchase, including the amount of missing vegetables and information.
    """
    for shop in df.columns:
        d = SHIPPING[shop]
        SHOPS[shop] = [d, 0, ""]
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
            "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(TOKEN, chat_id, "**תודה ולהתראות!**",
                                                                                   parse_mode='Markdown'))
    elif input == "עזרה":
        message = "שלום" + EMOJI_VEGETABLES["smile"] + "\n"
        message = message + "כאן תוכלו למצוא את המחיר הזול ביותר לקניה שלכם!" + '\n'
        message = message + "על מנת לעשות זאת- כתבו כאן את רשימת הקניות שלכם ולבסוף הקישו enter." + '\n'
        message = message + "תוכלו להוסיף עוד פריטים ככל שתרצו." + '\n'
        message = message + "לסיום הקישו *סיום* לעזרה הקישו *עזרה*"+'\n'
        message = message+ "בהצלחה" + EMOJI_VEGETABLES["smile"] + "\n"
        res = requests.get(
            "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(TOKEN, chat_id, message,
                                                                                   parse_mode='Markdown'))
    else:
        dict_of_vegetables, error_message = check_input(input.split())
        if error_message:
            res = requests.get(
                "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(TOKEN, chat_id, error_message,
                                                                                       parse_mode='Markdown'))

        add_to_dict(dict_of_vegetables)
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
