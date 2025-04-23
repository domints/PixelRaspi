FROM python:3.13-slim-bookworm

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY flipdot ./flipdot
COPY fonts ./fonts
COPY icons ./icons

#CMD [ "python3", "-m" , "flask", "flipdot", "run", "--host=0.0.0.0"]

#CMD [ "ls" ]

CMD [ "flask", "--app", "flipdot", "run", "--host=0.0.0.0" ]