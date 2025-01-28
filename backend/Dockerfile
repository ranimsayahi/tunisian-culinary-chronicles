FROM python:3.13.0
EXPOSE 5005
WORKDIR /app
RUN pip install flask
COPY . .
CMD ["flask","run","--host","0.0.0.0"]
RUN python3 -m pip install flask-smorest flask-jwt-extended python-dotenv flask-cors flask-sqlalchemy bcrypt marshmallow requests
