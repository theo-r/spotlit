FROM python:3.7-slim-buster

WORKDIR /spotlit

EXPOSE 8501

COPY requirements.txt ./requirements.txt
COPY .spotify_caches/ ./.spotify_caches/
COPY creds.json creds.json

RUN pip3 install -r requirements.txt

ENV SPOTIPY_REDIRECT_URI=https://spotlit.azurewebsites.net/

RUN rm /usr/local/lib/python3.7/site-packages/tornado/routing.py

COPY routing.py /usr/local/lib/python3.7/site-packages/tornado/

COPY main.py main.py

CMD streamlit run main.py