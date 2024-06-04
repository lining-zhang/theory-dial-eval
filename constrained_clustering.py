# pwd -> /Users/lining_zhang/Desktop/dial_eval
# python ./constrained_clustering.py > ./results/result_v1.txt

import pandas as pd
from itertools import combinations
from scipy import stats


GM_PP_TM = ["GM1", "GM2", "GM3", "GM4", 
            "PP1", "PP2", "PP3", "PP4", "PP5", "PP6",
            "GM-TM1-1", "GM-TM1-2", "GM-TM1-3", "GM-TM1-4", "GM-TM1-5",
            "GM-TM2-1", "GM-TM2-2", "GM-TM2-3", "GM-TM2-4", "GM-TM2-5", "GM-TM2-6",
            "GM-TM3-1", "GM-TM3-2", "GM-TM3-3", "GM-TM3-4", "GM-TM3-5", "GM-TM3-6",
            "GM-TM4-1", "GM-TM4-2", "GM-TM4-3", "GM-TM4-4", "GM-TM4-5", "GM-TM4-6", "GM-TM4-7",
            "PP-TM1-1", "PP-TM1-2",
            "PP-TM2-1", "PP-TM2-2",
            "PP-TM3-1", "PP-TM3-2",
            "PP-TM4-1", "PP-TM4-2",
            "PP-TM5-1", "PP-TM5-2",
            "PP-TM6-1", "PP-TM6-2"
            ]


class constrained_clustering(object):
    def __init__(self, mapping_path, data_path):
        self.mapping_result = pd.read_csv(mapping_path)
        data = pd.read_csv(data_path, index_col=0)
        self.data = self.convert_numeric_data(data)
        self.ED_lookup = self.generate_ED_lookup()

    def generate_ED_lookup(self):
        ED_lookup = {}
        dim_name = list(self.mapping_result["Dimensions"])
        dim_idx = list(self.data.columns)[3:]

        for name, idx in zip(dim_name, dim_idx):
            ED_lookup[name] = idx
        return ED_lookup
    
    def convert_numeric_data(self, df):
        cols = list(df.columns)[3:]
        for col in cols:
            df[col] = pd.to_numeric(df[col])
        return df

    def EDS_filter(self, tm):
        """
        :param tm:
            For GM/PP level, just "GM1", "PP3", etc.
            For TM level, "GM-TM1-2" is the 2nd TM of GM1
        """
        df = self.mapping_result
        if tm in ["GM1", "GM2", "GM3", "GM4", 
                  "PP1", "PP2", "PP3", "PP4", "PP5", "PP6"]:
            EDS = list(df[df[tm]=="Y"]["Dimensions"])
        else:
            tm_info = tm.split("-")
            tm_col = tm_info[0]+tm_info[1][-1]+"-TMs"
            tm_name = tm_info[1]+"-"+tm_info[2]

            df_na = df[df[tm_col].notna()]
            EDS = list(df_na[df_na[tm_col].str.contains(tm_name)]["Dimensions"])
        return EDS

    def get_clustering(self, tm):
        EDS = self.EDS_filter(tm)
        # print(EDS)
        n = len(EDS)
        if n==0:
            print("There is no ED corresponding to {}".format(tm))
        elif n==1:
            print("There is only one ED ({}) corresponding to {}".format(EDS[0], tm))
        else:
            r = 0
            EDS_MAX = []
            for ED_pair in list(combinations(EDS, 2)):
                ED1, ED2 = ED_pair[0], ED_pair[1]
                res = stats.spearmanr(self.data[self.ED_lookup[ED1]], self.data[self.ED_lookup[ED2]])
                r0 = res.correlation

                if abs(r0) >= abs(r):
                    r = r0
                    EDS_MAX = [ED1, ED2]
            print("The highest Spearman's correlation is between {} and {}: {}".format(ED1, ED2, r))


def main():
    # print("hi")
    cluster_dealer = constrained_clustering("./results/GM-PP-mapping-result-Lining.csv",
                                            "./data/final_df_v1.csv")
    
    for tm in GM_PP_TM:
        print("For {}:".format(tm))
        cluster_dealer.get_clustering(tm)
        print("====================\n")

if __name__ == "__main__":
	main()