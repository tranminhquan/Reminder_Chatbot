import firebase_admin
import datetime
from firebase_admin import credentials, db
from threading import Thread
import schedule

# firebase_admin.initializaApp({
# 	credential: admin.credential.cert({
# 		projectId: 'reminder-chatbot',
# 		clientEmail: 'firebase-adminsdk-r6lsh@reminder-chatbot.iam.gserviceaccount.com',
# 		privateKey: '-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC+M0uQ54viyB6M\nxyRwF7Da9wUT41JSYrU3FGv/fTLe+t3FZqQf7d8LnsAjcUZIraV0hhyfID7kHI8b\nJr+lorzw4D0QR5E4LcAhTi2/fGlz0fEZuTaXGlSh3hH95Us7l/raprH/VUnKe9xJ\nbYMQcMP5JDsofdgIDBW0xdQ4J1x3Bz4p3OMiB170y2SNPdcrz71k+BmOInRPiqp7\nQrnEdS6LkijVF9SgMJdsw2+v4msXO+dJogL1T/mZOCnb+OJFteL5uV6F3r28m0tr\neUjPwCeBiD0D+VlnmkTxqCyts990zpkE3I6trdRkAtN9vBYVpxn2dud0M+2AFK2K\noAVCAOXXAgMBAAECggEAWVi7TKyYl8WuJC+APG/EknermPYWO8FGo0MioHftp7Vs\n7EgVHTKerlS6qWuSup1ntd8yHsYFBR8tUnHXYTWbUAPma3lTDHLhaEPTVbpZxyB+\nA7lvnXeu/gLVrNFDkBEKtB/OScWEzmt0xcF96gEu7iBI8fJ7wvv6TlsIIADNfNPI\nnLAMOkwV3RRL6cwbPzJpMnzp+H8PLca3bmSNzbsRCRz6+AREifg6vPV84M9l8jnI\nylhWDiU9dHAH/SVPGzejSCEUvVJrsarQWUhhpOpKUEKWRyJIeb/v4NM4tD2qEGFR\nJKMA0wxzlZN+rfUbpniB9NlCs9YDgtkTWLuvNG8GwQKBgQDn1WV8w8qjY3POLvPQ\nOCrjA+rz551j5cEPld0Sf7wwhuKJZ+bb8WtKDXH9MAeWP3md+f7bAdgnokAvQNdx\nTjeqfXvMWbUFTBHsosVYlX4OjRkpJkLv3Rsc+CdJFj3B02BlRszYwgn1EzwQAxyW\nyBBkg49omtqGi73f13lB2xKk5wKBgQDSBuTscaBVgrjjAL1v6lVe2ooXa1ad2jap\nI7reYYlr4XprclHppXe2iVe37l12DLKLiM4cRan7fq5u8juQ/lr9/wow2EzWKIl8\njXUZWFgXCaXBcgoJLluecnN9CHtvY01tL6IANd65VIrsYQegd/rKSvJXtRI6KQEe\ni1yU3iOpkQKBgAQSVGD3k1SBR6RkYLXUdrRb+kFkXPhHLbfXWvWbNrPneo0NPRm5\nyLeZOtpGgKub28fxfw9bne88Q0JRMjd0NzgQUh9JqAs6xcnRJgQjQ/5/beSyHlTW\nHkbI+O+oq1b/Hl9I+goIhmI+fzyMwXDIfLk3MkqVBad9Rs1qnF+SuGYbAoGAV68b\nKf+yQaEG0XcAn9XEeIpitq5QhiyRP4I0RR2RguGq+2rJ+fLkDOhAIAE7McrRS+H8\nst7+vYnBB37IEZuvn3U36vaS9aIM7FwedEtm049qjV2wBO8+vuLnhl7hMbrSm3AU\ngWP8LYG3UkKcLYmJwaUSkj19c5yk4/yo1Vn8p5ECgYEA1cdyj3mMjccO7aYboEDn\nsZCxwxJk4eEfIrONTRHojq/CX+bV7ZgL7SANJsvAMXmDQ8hrRJKoemeTRnQ+RIoe\ndJrMBs7Ugg4XrfS1/nqYBIWfoZQgSNR/AkMxo/nS/INsbLKtUpYV6KuetXpv+dLf\nWrtUASx3w8UvUM5TG06+7oM=\n-----END PRIVATE KEY-----\n'
# 		}),
# 	databaseURL: 'https://reminder-chatbot.firebaseio.com/'
# 	});

def init():
	cred = credentials.Certificate('reminder-chatbot-firebase.json')
	firebase_admin.initialize_app(cred,{
	 	'databaseURL': 'https://reminder-chatbot.firebaseio.com/'
		})

def registerUser(id, name):
	ref = db.reference('/users')
	userRef = ref.child(id)
	userRef.set({
		'name': name
		})

def createTask(userid, name, day, month, hour, minute):
	db.reference('/tasks').child(userid).push().set({
		'name': name,
		'day': day,
		'month': month,
		'hour': hour,
		'minute': minute
		})

def removeTask(userid, taskid):
	db.reference('/tasks').child(userid).child(taskid).set({taskid: None})

def getAllUser():
	# get all user
	snapshot = db.reference('/users').order_by_key().get()
	# for item in snapshot.items():
	# 	print(item[0])
	return snapshot

def checkExistUser(id):
	listUsers = getAllUser()
	for user in listUsers.items():
		if str(user[0]) == id:
			return user[1]['name']
	return False

def checkReminder():
	listTasks = []
	now = datetime.datetime.now()
	users = getAllUser()
	for user in users.items():
		uid = user[0]
		# try:
		try:
			snapshot = db.reference('/tasks').child(uid).order_by_child('month').equal_to(now.month).get()
			for task in snapshot.items():
				if task[1]['day'] == now.day and task[1]['hour'] == now.hour and task[1]['minute'] == now.minute:
					task[1]['id'] = uid
					listTasks.append(task)
					removeTask(uid, task[0])
		except:
			print('exception in checkReminder')
			continue

	return listTasks

init()

# registerUser('123456', 'Nguyen Van A')
# registerUser('2313156', 'Bui Thi B')
# registerUser('1623325', ' TM DC')

# text = "NHACNHO Làm bài tập gì đó 18/06 20:00"
# infos = text.split()
# time = infos[-1].split(':')
# hour = int(time[0])
# minute = int(time[1])
# date = infos[-2].split('/')
# day = int(date[0])
# month = int(date[1])
# name = ' '.join(infos[1:-2])
# print(hour, minute, day, month, name)