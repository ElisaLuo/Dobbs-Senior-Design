import json
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
import os
from datetime import datetime
import warnings
import numpy as np
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')

db_url = 'mysql+pymysql://[username]:[password]@[host]/dobbs_senior_design_db'
dobbs_engine = create_engine(db_url)

liwc_df = pd.read_sql_table('feat$cat_LIWC2022_lw$liwc1_2022$user_id_pre_post_dobbs$1gra', con=dobbs_engine)
user_df = pd.read_sql_table('users', con=dobbs_engine)

f_pos_pre = []
f_pos_post = []
f_neg_pre = []
f_neg_post = []

m_pos_pre = []
m_pos_post = []
m_neg_pre = []
m_neg_post = []

for i, group in enumerate(liwc_df['group_id']):
    if i % 10000 == 0:
        print(i)

    if(liwc_df['feat'][i] == 'TONE_POS' or liwc_df['feat'][i] == 'TONE_NEG'):
        posTone = True if liwc_df['feat'][i] == 'TONE_POS' else False
        preDobbs = True if (liwc_df['group_id'][i][-1] == '0') else False
        user_id = liwc_df['group_id'][i][:-2]
        user_row = user_df[user_df['user_id'] == user_id]
        male = (user_df['user_id'] == user_id).any() and (user_df.loc[user_df['user_id'] == user_id, 'gender'] == 'M').any()
        value = liwc_df['value'][i]
        if value > 500: # remove outliers
            continue

        if male:
            if (posTone and preDobbs):
                m_pos_pre.append(value)
            elif (not posTone and preDobbs):
                m_neg_pre.append(value)
            elif (posTone and not preDobbs):
                m_pos_post.append(value)
            elif (not posTone and not preDobbs):
                m_neg_post.append(value)
        else:
            if (posTone and preDobbs):
                f_pos_pre.append(value)
            elif (not posTone and preDobbs):
                f_neg_pre.append(value)
            elif (posTone and not preDobbs):
                f_pos_post.append(value)
            elif (not posTone and not preDobbs):
                f_neg_post.append(value)

data_to_plot = [m_pos_pre, m_pos_post, m_neg_pre, m_neg_post, f_pos_pre, f_pos_post, f_neg_pre, f_neg_post]
categories = ['m_p_pr', 'm_p_po', 'm_n_pr', 'm_n_po', 'f_p_pr', 'f_p_po', 'f_n_pr', 'f_n_po']

plt.figure(figsize=(10, 6))
plt.boxplot(data_to_plot, labels=categories, patch_artist=True, showmeans=True)

plt.title('Box-Whisker Chart of Sentiment Categories', fontsize=16)
plt.ylabel('Value', fontsize=14)
plt.xlabel('Categories', fontsize=14)

output_path = 'box_whisker_chart.png'
plt.savefig(output_path, dpi=300)
plt.close()
