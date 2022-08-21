


from flask import Flask, Response,request
import requests

TOKEN = '5711334526:AAHd7qg_DfVqrVHU61pC3XincRHBeQ5ggmI'
TELEGRAM_INIT_WEBHOOK_URL = 'https://api.telegram.org/bot{}/setWebhook?url=https://b135-82-80-173-170.eu.ngrok.io/message'.format(TOKEN)

def is_factorial(n):
    """

    :param n: check if n is factorial number
    :return: correct message
    """
    help = 1
    if n == 0:
        return "not factorial"
    if n == 1:
        return "factorial"
    ["factorial"]
    for i in range(1, n + 1):
        help = help * i
        if help == n:
            return "factorial"
        if help > n:
            return "not factorial"

def isPalindrome(s):
    """

    :param s: a string
    :return: checks if a string is a palindrom
    """
    return "Palindrome!" if s == s[::-1] else "Not Palindrome"

def is_prime(n):
    """

        :param s: a string
        :return: checks if a string is a prime
        """
    if (n % 2) == 0:
        return "Come on dude, you know even numbers are not prime!"
    for i in range(3,n):
        if (n % i) == 0:
             return "not prime!"
        return "prime!"

def is_sqrt(n):
    """
    :param n: check if does the number have an integer square root
    :return: correct message
    """
    if n == 0 or n == 1:
        return str(n) + " have an integer square root!"
    res = "".join([str(n) + " have an integer square root!" for i in range(n) if i * i == n])
    return res if res != "" else str(n) + " have not an integer square root"



app = Flask(__name__)

@app.route('/message', methods=["POST"])
def handle_message():
    print("got message")
    chat_id = request.get_json()['message']['chat']['id']
    respond = ''
    input = request.get_json()['message']['text']
    print(input)
    if input.split()[0] == "/prime":
        respond = is_prime(int(input.split()[1]))

    elif input.split()[0] == "/sqrt":
        respond = is_sqrt(int(input.split()[1]))
    elif input.split()[0] == "/palindrom":
        respond = isPalindrome(str(input.split()[1]))
    elif input.split()[0] == "/factorial":
        respond = is_factorial(int(input.split()[1]))
    else:
        respond = "got it"

    #print(chat_id)

    res = requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(TOKEN, chat_id, respond))

    return Response("success")



@app.route('/')
def index():
    return "<h1>server is runnig!</h1>"


if __name__ == '__main__':
    requests.get(TELEGRAM_INIT_WEBHOOK_URL)
    app.run(port=5002)
   # response = requests.get(TELEGRAM_INIT_WEBHOOK_URL)
   #print(response.status_code)

