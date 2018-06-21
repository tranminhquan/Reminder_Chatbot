import random
import firebase
from flask import Flask, request
from pymessenger.bot import Bot
from threading import Thread
import schedule
import os
import datetime
import requests


app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))
ACCESS_TOKEN = 'EAAasT87RGaoBAMwZAkZBZAWJhLZAGaTCeWqfYa2zaPMiCJmir0GHLSk7EXnZCOwabS7v3r5CM2ryaAe71u99ZBo8U6aAR5WIYOZBHZCYUcVtQisoZBflCgSwMy8UZCAL0ZA0lPXgp3VZA1wMzws5aBsAs9NC0IU8738NqesZCmTmJer2IfA8HZByAApZApt'
VERIFY_TOKEN = 'PYTHON_CHATBOT_MQ'
SERVER_URL = 'https://reminder-tmq-chatbot.herokuapp.com/'
bot = Bot(ACCESS_TOKEN)

users=[]

@app.route("/", methods=['GET', 'POST'])

# def job():
    

# thread = Thread(target=job)
# thread.start()

def receive_message():
    print("recive message")
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                text_message = message['message'].get('text')
                if text_message:
                    if (checkOnGoingUser(recipient_id)):
                        response_sent_text = register_message(recipient_id, text_message)
                    elif text_message.lower().find("help") >= 0 or isInterger(text_message):
                        response_sent_text = help_message(recipient_id, text_message)
                    else:
                        response_sent_text = welcome_message(recipient_id, text_message)
                    send_message(recipient_id, response_sent_text)
                    
                    
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"

def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    print("send message")
    return random.choice(sample_responses)

def checkOnGoingUser(id):
    for uid in users:
        if uid == id:
            return True
    return False

def isInterger(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def register_message(id, name):
    firebase.registerUser(id, name)
    users.remove(id)
    return "Chào " + name + ". Từ bây giờ mình sẽ hỗ trợ nhắc nhở công việc cho bạn\
    Cú pháp rất đơn giản, khi cần nhắc nhở chỉ cần bạn nhắn NHACNHO <Ten viec> <Ngay> <Gio:Phut>\
    Vd: NHACNHO Làm bài tập 12/05 20:00."

def welcome_message(id, text):
    user = firebase.checkExistUser(id)
    if user==False:
        users.append(id)
        print("add new user to ongoing user")
        return "Chào bạn, mình là chatbot hỗ trợ nhắc nhở công việc, tên bạn là gì?"
    else:
        # Check the prefix
        if text.lower().find("nhacnho") >= 0:
            try:
                infos = text.split()
                time = infos[-1].split(':')
                hour = int(time[0])
                minute = int(time[1])
                date = infos[-2].split('/')
                day = int(date[0])
                month = int(date[1])
                name = ' '.join(infos[1:-2])
                if validTask(name, hour, minute, day, month):
                    firebase.createTask(id, name, day, month, hour, minute)
                    print("create task: ", str(name), str(hour), str(minute), str(day), str(month))
                    return "Đã xác nhận. Bạn sẽ được nhắc nhở " + str(name) + " vào lúc " + str(hour) + " giờ " + str(minute) + " phút\
                     ngày " + str(day) + " tháng " + str(month) + "."
                else:
                    return "Ngày hoặc khung giờ chưa hợp lý. Bạn kiểm tra lại nhé"
            except:
                return "Bạn nhập chưa đúng cú pháp thì phải. Kiểm tra lại nhé"
        else:
            return "Chào " + user + ". Bạn cần nhắc nhở việc gì chăng? Nếu cần giúp đỡ bạn gõ 'HELP' nhé."

def help_message(id, text):
    if isInterger(text):
        num = int(text)
        if num == 1:
            return "Khi cần nhắc nhở chỉ cần bạn nhắn NHACNHO <Ten viec> <Ngay> <Gio:Phut>\
            Vd: NHACNHO Làm bài tập 12/05 20:00."
        if num == 2:
            return "Chatbot này được phát triển để hỗ trợ nhắc nhở những việc hằng ngày. Được viết trên python\
            Phiên bản hiện tại: thử nghiệm"
        if num == 3:
            return "Được phát triển bởi Trần Minh Quân, sinh viên tại trường ĐH Công nghệ Thông tin - ĐHQG TP.HCM. Thông tin liên hệ:\n \
            Email: tranminhquan1201@gmail.com\n Website: https://quantranminh.000webhostapp.com/"
        else:
            return "Danh mục nằm ngoài danh mục giúp đỡ rồi, kiểm tra lại nhé"
    else:
        return "Mình có thế giúp gì cho bạn?\n \
        1.Làm sao để đặt nhắc nhở?\n \
        2.Mục đích của mày đến Trái Đất để làm gì\n \
        3.Ai là người tạo ra mày?"

def validTask(name, hour, minute, day, month):
    now = datetime.datetime.now()
    try:
        date = datetime.date(now.year, month, day)
        time = datetime.time(hour, minute)
        return True
    except ValueError:
        return False

def checkReminder():
    now = datetime.datetime.now()
    listTasks = firebase.checkReminder()
    print("[", now, "] ", "Checking task from database: ", listTasks)
    for item in listTasks:
        content = "Bạn cần " + item[1]['name'] + " vào lúc " + str(item[1]['hour']) + " giờ " + str(item[1]['minute']) + " phút."
        uid = item[1]['id']
        send_message(uid, content)

    # Good morning message
    if now.hour == 6 and now.minute == 0:
        print('send good morning message')
        ls = firebase.getAllTaskInDay(now.day, now.month)
        for item in ls:
            msg = 'Chào buổi sáng!\nChúc bạn ngày mới tốt lành. Hôm nay bạn có những việc cần thực hiện như sau:\n'
            uid = item['id']
            for task in item['tasks']:
                msg += task['name'] + ' vào lúc ' + str(task['hour']) + ' giờ ' + str(task['minute']) + ' phút\n'
            # send to user
            send_message(uid, msg)
            print('send message to ', uid)
            print(msg)


def requestServer():
    print("----------auto ping server----------")
    requests.get(SERVER_URL)

def setSchedule():
    schedule.every(1).minutes.do(checkReminder)
    schedule.every(10).minutes.do(requestServer)
    while True:
        schedule.run_pending()

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    checkingThread = Thread(target=setSchedule)
    checkingThread.daemon = True
    checkingThread.start()
    app.run(host='0.0.0.0', port=port)