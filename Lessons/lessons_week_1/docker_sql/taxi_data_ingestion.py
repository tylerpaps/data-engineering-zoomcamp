#!/usr/bin/env python
# coding: utf-8

import os
import argparse
from time import time
import pandas as pd
from sqlalchemy import create_engine


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    # the backup files are gzipped, and it's important to keep the correct extension
    # for pandas to be able to open the file
    if url.endswith('.csv.gz'):
        csv_name = 'output.csv.gz'
    else:
        csv_name = 'output.csv'

    # This will grab what ever URL is passed through the command line
    os.system(f"wget {url} -O {csv_name}")

    # Here we will create the engine to talk to postgres, we will then read in the file one chunk at a time
    # We then convert the columns to datetimes, write the create table command and then iterate over the data
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    df_iter = pd.read_csv(csv_name, iterator = True, chunksize=100000)
    df = next(df_iter)
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
    while True:
        try:
            t_start = time() # Used to capture the runtime
            df = next(df_iter) # Gets the next chunk, when there are none left this will return false
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            df.to_sql(name=table_name, con=engine, if_exists='append')
            t_end = time() #used to get the end time
            t_total = round(t_end - t_start,2) #calculated the total time taken
            print(f'Inserted Another Chunck, the total time was: {t_total} seconds')
        except StopIteration:
            print("Finished ingesting data into the postgres database")
            break

## allows us to create dynamic vairbles that get passed to the srcript when run from the command line
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')
    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db', required=True, help='database name for postgres')
    parser.add_argument('--table_name', required=True, help='name of the table where we will write the results to')
    parser.add_argument('--url', required=True, help='url of the csv file')
    args = parser.parse_args()

    main(args)



