FROM python:3.9.1

RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2

COPY taxi_data_ingestion.py taxi_data_ingestion.py
ENTRYPOINT ["python","taxi_data_ingestion.py"]
