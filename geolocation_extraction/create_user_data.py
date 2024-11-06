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

reddit_url = 'mysql+pymysql://[username]:[password]@[host]/reddit'
nsehgal_reddit_engine = create_engine(reddit_url)

print("--- Reading Data ---")
df = pd.read_sql_table('filtered_accepted_user_data_75', con=dobbs_engine)
print("shape of messages and posts: ", df.shape)

users_path = "/sandata/luoli/dobbs/user_data"
user_list_path = "/sandata/luoli/dobbs/user_list.txt"

user_list = df['user_id'].unique().tolist()

print("Number of users:", len(user_list))

print("--- Storing data ---")
count = 0
user_file = open(user_list_path, "a")

for idx, user in enumerate(user_list):
    user_file_path = f"{users_path}/{user}.json"

    if os.path.exists(user_file_path):
        print(f"User {user} already processed. Skipping.")
        continue  # Skip to the next user if this one is already processed


    if (idx + 1) % 10 == 0:
        print(f"Users read: {idx + 1}")
    user_df = df[df['user_id'] == user]
    user_data_li = []
    for index, row in user_df.iterrows():
        count += 1
        row_dict = {}
        row_dict['author'] = user
        row_dict['body'] = row['message']
        try:
            # https://stackoverflow.com/a/55941915, https://stackoverflow.com/questions/255035/converting-datetime-to-posix-time
            created_utc = int(datetime.strptime(str(row['created_utc']), '%Y-%m-%d %H:%M:%S').timestamp())
        except ValueError:
            continue
        row_dict['created_utc'] = created_utc
        row_dict['subreddit'] = row['subreddit']
        # row_dict['author_flair_text'] = row['author_flair_text']
        user_data_li.append(row_dict)
    try:    
        data_file = open(f"{users_path}/{user}.json", "w")
    except:
        print(f"Error opening file for user {user}.")
        # save the users name to /home/nsehgal/reddit_advice/error_users/errors.txt
        with open('/sandata/luoli/dobbs/error_users/errors.txt', 'a') as error_file:
            error_file.write(f"{user}\n")
        continue
    json.dump(user_data_li, data_file, indent=2)
    user_file.write(f"{user}\n")

print("Messages read:", count)