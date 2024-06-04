# pwd -> /Users/lining_zhang/Desktop/dial_eval
# python data_preprocess.py

import pandas as pd
import itertools
from itertools import product
from itertools import chain
from value_lookup import path_lookup, col_lookup, comb_lookup, group_lookup # type: ignore


class data_dealer(object):
    def __init__(self, path_lookup, col_lookup, comb_lookup, group_lookup):
        self.path_lookup = path_lookup
        self.col_lookup = col_lookup
        self.comb_lookup = comb_lookup
        self.group_lookup = group_lookup

        self.final_df = self.create_final_df()

    def get_csv_info(self, group_num, round_num, person_id):
        file_path = self.path_lookup[group_num][round_num]
        df = pd.read_csv(file_path, header=0)
        df.drop([0, 1], inplace=True)

        df_person = df[df["fetid"]==person_id]
        for i in range(8):
            run_number = i+1
            df_block = df_person[df_person["run_number"]==str(run_number)]

            block_name = "block"+str(run_number)
            cols = list(itertools.chain.from_iterable(self.col_lookup[group_num][block_name]))
            scores = df_block.loc[:, cols]

            # fill scores
            self.fill_scores(scores, round_num, person_id, i)

    def fill_scores(self, scores, round_num, person_id, block_id):
        c_t_info = self.comb_lookup[round_num][block_id].split("-")
        c, t = c_t_info[0], c_t_info[1]
        col_names = list(scores.columns)
        # transform to original names
        col_names_ = [name.split(".")[0] if "." in name else name for name in col_names]

        self.final_df.loc[(self.final_df["chatbot_id"] == c) & 
                          (self.final_df["topic_id"] == t) & 
                          (self.final_df["person_id"] == person_id), col_names_] = scores.values
        
    def create_final_df(self):
        col_p = list(chain.from_iterable(self.group_lookup.values()))
        col_c = ["c"+str(i+1) for i in range(4)]
        col_t = ["t"+str(i+1) for i in range(4)]
        comb = list(product(col_p,col_c,col_t))

        final_df = pd.DataFrame(data=comb, columns=["person_id", "chatbot_id", "topic_id"])
        return final_df
    
    def fill_all_csv(self, save_path):
        for group_num in list(self.group_lookup.keys()):
            for person_id in self.group_lookup[group_num]:
                for round_num in list(self.path_lookup[group_num].keys()):
                    self.get_csv_info(group_num, round_num, person_id)
        
        self.final_df.to_csv(save_path) 
        # "./data/final_df_v1.csv"


def main():
    dealer = data_dealer(path_lookup, col_lookup, comb_lookup, group_lookup)
    dealer.fill_all_csv("./data/final_df_v1.csv")

if __name__ == "__main__":
	main()