FROM python:3.10-slim-bullseye

RUN pip install --upgrade pip
RUN mkdir /work
WORKDIR /work
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD [ "streamlit", "run", "app.py" ]