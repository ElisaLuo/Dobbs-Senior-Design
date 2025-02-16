import pandas as pd
import json
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine, text

db_url = 'mysql+pymysql://[username]:[password]@[host]/dobbs_senior_design_db'
dobbs_engine = create_engine(db_url)

reddit_url = 'mysql+pymysql://[username]:[password]@[host]/reddit'
nsehgal_reddit_engine = create_engine(reddit_url)

# subreddit tables
com_tables = [
    f'com_{year}_{month:02}' 
    for year in range(2010, 2023) 
    for month in range(1, 13)
]
com_tables += ['com_2024_01', 'com_2024_02', 'com_2024_03', 'com_2024_04', 'com_2024_05', 'com_2024_06']
print(com_tables)

sub_tables = [
    f'sub_{year}_{month:02}' 
    for year in range(2010, 2023) 
    for month in range(1, 13)
]

sub_tables += ['sub_2024_01', 'sub_2024_02', 'sub_2024_03', 'sub_2024_04', 'sub_2024_05', 'sub_2024_06']
print(sub_tables)

try:
    users_df = pd.read_sql_table('users', con=dobbs_engine)
    read_users = pd.read_sql_table('filtered_accepted_user_data_75', con=dobbs_engine)
    user_list = read_users['user_id'].unique().tolist()
    escaped_user_list = ["'" + user_id + "'" for user_id in user_list]
    user_list_str = ', '.join(escaped_user_list)
    sql_query = f"SELECT user_id FROM users WHERE user_id NOT IN ({user_list_str})"
    df = pd.read_sql_query(sql_query, dobbs_engine)
    users_df = np.array(df).squeeze(1)
    users_df = np.random.choice(users_df, size=20000, replace=False).tolist()
    
except Exception as e:
    print("Error reading users table:", e)

# with open('user_list_gave_accepted_comments.txt', 'r') as f:
#     user_id_list = f.read().splitlines()

# Escape and quote user IDs
escaped_user_ids = ["'"+str(user_id)+"'" for user_id in users_df]
user_ids_str = ', '.join(escaped_user_ids)

print('Len of users:', len(users_df))
# get comment data
user_comment_data = pd.DataFrame()

for table in com_tables:
    sql_query = f"SELECT user_id, message, created_utc, subreddit FROM {table} WHERE user_id IN ({user_ids_str})"
    df = pd.read_sql_query(sql_query, nsehgal_reddit_engine)
    user_comment_data = pd.concat([user_comment_data, df], ignore_index=True)
    print(table)

print('user_comment_data shape:', user_comment_data.shape)
user_comment_data.to_sql('accepted_commenters_com_data', dobbs_engine, if_exists='replace', index=False)

# get post data
user_posts_data = pd.DataFrame()

for table in sub_tables:
    sql_query = f"SELECT * FROM {table} WHERE user_id IN ({user_ids_str})"
    df = pd.read_sql_query(sql_query, nsehgal_reddit_engine)
    user_posts_data = pd.concat([user_posts_data, df], ignore_index=True)
    print(table)

print('user_posts_data shape:', user_posts_data.shape)

user_posts_data.to_sql('accepted_commenters_posts_data', dobbs_engine, if_exists='replace', index=False)


user_posts_data = user_posts_data[['user_id', 'title', 'message', 'created_utc', 'subreddit']]
user_posts_data['message'] = user_posts_data['title'] + ': ' + user_posts_data['message']
user_posts_data.drop('title', axis=1, inplace=True)

# Concatenate the comment and post dataframes
post_comment_df = pd.concat([user_comment_data, user_posts_data])

# print shape
print("Shape of post_comment_df:", post_comment_df.shape)

# filter out where user_id is [deleted]
post_comment_df = post_comment_df[post_comment_df['user_id'] != '[deleted]']

print("Shape of post_comment_df after dropping deleted:", post_comment_df.shape)


# Count the number of messages per user_id
user_message_counts = post_comment_df['user_id'].value_counts()


# Filter to keep only user_ids with at least 50 messages
filtered_user_ids = user_message_counts[user_message_counts >= 75].index
filtered_df = post_comment_df[post_comment_df['user_id'].isin(filtered_user_ids)]

print("Shape of filtered_df:", filtered_df.shape)

# save to sql
filtered_df.to_sql('filtered_accepted_user_data_75_2', con=dobbs_engine, if_exists='replace', index=False)