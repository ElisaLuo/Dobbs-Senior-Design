import json
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

db_url = 'mysql+pymysql://[username]:[password]@[host]/dobbs_senior_design_db'
dobbs_engine = create_engine(db_url)

df = pd.read_csv('/home/luoli/senior_design/geolocation_extraction/output_11_8_geocode.csv')

with dobbs_engine.connect() as connection:
    for i, user in enumerate(df['user_id']):
        if (i+1) % 100 == 0:
            print(f'Processing row {i+1}')
        
        if df['country_argmax'][i] == 'US':
            county = df['county_argmax'][i]
            state = df['state_argmax'][i]
            user_id = user.split(".json")[0]
            
            query = text('''
                UPDATE users 
                SET county = :county, state = :state 
                WHERE user_id = :user_id
            ''')
            connection.execute(query, {'county': county, 'state': state, 'user_id': user_id})
