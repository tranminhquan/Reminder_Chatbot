import random
import firebase
from flask import Flask, request
from pymessenger.bot import Bot
from threading import Thread
import schedule

app = Flask(__name__)
ACCESS_TOKEN = 'EAAasT87RGaoBAMwZAkZBZAWJhLZAGaTCeWqfYa2zaPMiCJmir0GHLSk7EXnZCOwabS7v3r5CM2ryaAe71u99ZBo8U6aAR5WIYOZBHZCYUcVtQisoZBflCgSwMy8UZCAL0ZA0lPXgp3VZA1wMzws5aBsAs9NC0IU8738NqesZCmTmJer2IfA8HZByAApZApt'
VERIFY_TOKEN = 'PYTHON_CHATBOT_MQ'
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

def register_message(id, name):
	firebase.registerUser(id, name)
	users.remove(id)
	return "Chào " + name + ". Từ bây giờ mình sẽ hỗ trợ nhắc nhở công việc cho bạn\
	Cú pháp rất đơn giản, khi cần nhắn nhở bạn chỉ cần bạn nhắn NHACNHO <Ten viec> <Ngay> <Gio:Phut>\
	Vd: NHACNHO Làm bài tập 12/05 20:00."

def welcome_message(id, text):
	user = firebase.checkExistUser(id)
	if user==False:
		users.append(id)
		print("add new user to ongoing user")
		return "Chào bạn, mình là chatbot hỗ trợ nhắc nhở công việc, tên bạn là gì?"
	else:
		# Check the prefix
		if text.find("NHACNHO") >= 0:
			infos = text.split()
			time = infos[-1].split(':')
			hour = int(time[0])
			minute = int(time[1])
			date = infos[-2].split('/')
			day = int(date[0])
			month = int(date[1])
			name = ' '.join(infos[1:-2])

			firebase.createTask(id, name, day, month, hour, minute)
			print("create task: ", str(name), str(hour), str(minute), str(day), str(month))
			return "Đã xác nhận. Bạn sẽ được nhắc nhở " + str(name) + " vào lúc " + str(hour) + " giờ " + str(minute) + " phút\
			 ngày " + str(day) + " tháng " + str(month) + "."
		else:
			return "Chào " + user + ". Bạn cần nhắc nhở việc gì chăng?"

def checkReminder():
    listTasks = firebase.checkReminder()
    for item in listTasks:
        content = "Bạn cần " + item[1]['name'] + " vào lúc " + str(item[1]['hour']) + " giờ " + str(item[1]['minute']) + " phút."
        uid = item[1]['id']
        send_message(uid, content)

def setSchedule():
    schedule.every(1).minutes.do(checkReminder)
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
    app.run()