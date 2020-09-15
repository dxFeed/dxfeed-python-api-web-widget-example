FROM python:3

WORKDIR /usr/src/app

RUN pip install dash dxfeed

CMD ["python", "app.py"]