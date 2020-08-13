FROM python:3.7-slim-buster

WORKDIR /spotlit

COPY requirements.txt ./requirements.txt
COPY .spotify_caches/ ./.spotify_caches/

RUN pip3 install -r requirements.txt

RUN rm /usr/local/lib/python3.7/site-packages/tornado/routing.py

COPY routing.py /usr/local/lib/python3.7/site-packages/tornado/

EXPOSE 8501

ADD main.py main.py

CMD streamlit run main.py