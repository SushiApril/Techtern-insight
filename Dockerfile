FROM python

WORKDIR /web
COPY /web .

RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["flask", "run", "--host", "0.0.0.0"]

