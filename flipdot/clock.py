from datetime import datetime
import time
from flipdot.models import DisplayData, TextLine
from flipdot.text_helpers import render_display_data

last_time: datetime = datetime.min

def tick():
    '''
    Tick for clock thingy. It's crude and hacky now.
    Run from scheduler at maybe 15 sec intervals, I don't think it needs to be precise now.
    '''
    global last_time
    from flipdot.connector import default_id
    from flipdot.display import show_image
    current = datetime.now()
    if (current.minute != last_time.minute or current.hour != last_time.hour):
        last_time = current
        if default_id < 0:
            return
        try:
            text = f'{current.hour:02d}:{current.minute:02d}    {current.day:02d}.{current.month:02d}.{current.year:02d}'
            lines = [
                TextLine(text=text, font='(14) LED 120x16 CHUDE - LT', align='center')
            ]
            data: DisplayData = DisplayData(lines=lines)
            img = render_display_data(default_id, data)
            for i in range(1, 10):
                show_image(default_id, img, page=i)
                time.sleep(1)
        except Exception:
            pass
