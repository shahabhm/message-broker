FROM python:3.10

WORKDIR /broker
COPY . .
RUN pip install -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/"
EXPOSE 5000

CMD ["python", "main.py"]