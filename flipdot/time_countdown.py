from time import sleep
from flask import Blueprint
import threading


thread_event = threading.Event()

bp = Blueprint('time_countdown', __name__, url_prefix='/time_countdown')

def backgroundTask():
    while thread_event.is_set():
        print('Background task running!')
        sleep(5)

@bp.route("/start", methods=["POST"])
def startBackgroundTask():
    try:
        thread_event.set()
        
        thread = threading.Thread(target=backgroundTask)
        thread.start()

        return "Background task started!"
    except Exception as error:
        return str(error)
    
@bp.route("/stop", methods=["POST"])
def stopBackgroundTask():
    try:
        thread_event.clear()

        return "Background task stopped!"
    except Exception as error:
        return str(error)