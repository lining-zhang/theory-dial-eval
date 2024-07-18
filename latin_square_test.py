# python latin_square_test.py

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import itertools
from itertools import chain
from value_lookup import group_lookup, comb_lookup, col_lookup

def index_generator():
    index_ls = []
    for i in range(4):
        index = "QS" + str(i+1)
        for j in range(4):
            index_ = index + "-" + str(j+1)
            for b in range(8):
                index_f = index_ + "-" + str(b+1)
                index_ls.append(index_f)
    return index_ls

def data_transform(index, data, df):
    group_num, round_num, block_num = index.split("-")[0], index.split("-")[1], index.split("-")[2]
    person = group_lookup[group_num][0]
    chatbot_topic = comb_lookup["round"+round_num][int(block_num)-1].split("-")
    chatbot, topic = chatbot_topic[0], chatbot_topic[1]

    insert_row = len(df)
    df.loc[insert_row, "index"] = index
    df.loc[insert_row, "person_id"] = person
    df.loc[insert_row, "chatbot_id"] = chatbot
    df.loc[insert_row, "topic_id"] = topic

    cols = list(itertools.chain.from_iterable(col_lookup[group_num]["block"+block_num]))
    cols = [col.split(".")[0] for col in cols]
    scores = data.loc[(data["person_id"] == person) & (data["chatbot_id"] == chatbot) & (data["topic_id"] == topic), cols]
    df.loc[insert_row, cols] = scores.values[0]
    return df

def corr_compare(df):
    plt.style.use("ggplot")
    fig = plt.figure(figsize=(30, 12))
    
    df_row_t4 = df[~df["index"].str.contains("5|6|7|8")]
    for i, df_ in enumerate([df, df_row_t4]):
        ax = fig.add_subplot(1, 2, i+1)
        corr = df_.corr()
        corr.fillna(0, inplace=True)

        sns.heatmap(corr, mask=np.triu(np.ones_like(corr, dtype=bool)), 
                    square=True, cmap="coolwarm", vmin=-1, vmax=1, linewidths=.1, ax=ax, 
                    annot=True, fmt=".2f", annot_kws={"fontsize":4})
        if i==0:
            ax.set_title("w/ all data", fontsize=8)
        else:
            ax.set_title("w/ top 4 rows", fontsize=8)
    
    plt.tight_layout()
    plt.savefig("./corr_compare_1.pdf")
    plt.show()

# data = pd.read_csv("./data/final_df_v1.csv", index_col=0)
# index_ls = index_generator()
# df = pd.DataFrame()

# for index in index_ls:
#     df = data_transform(index, data, df)
# df.to_csv("./data/transformed_df_v1.csv")
df = pd.read_csv("./data/transformed_df_v1.csv", index_col=0)

corr_compare(df)