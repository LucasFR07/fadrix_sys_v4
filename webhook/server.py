
from flask import Flask,request
app = Flask(__name__)



@app.route('/task_event', methods=['GET'])

def getID():
	taskGid = request.args.get('taskGid')
	if taskGid != None:
		print(taskGid)
		return 'success', 200
	else:
		return 'not found', 400


if __name__ == '__main__':
	app.run(port=5000)
