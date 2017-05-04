import pandas as pd
import numpy as np
import lda

class FlowSuspiciousConnectsModel:

    def __init__(self, data, config):
        self.data = data    # trhour,trminute,trsec,sip,dip,sport,dport,ipkt,ibyt
        self.config = config

    def _compute_deciles(self, df):
        return df.quantile([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])

    def _compute_quantile(self, df):
        return df.quantile([0, 0.2, 0.4, 0.6, 0.8])

    def _assemble_words(self, df):
        src = df["sport"]
        dst = df["dport"]
        time_bin = df["time_bin"]
        ibyt_bin = df["ibyt_bin"]
        ipkt_bin = df["ipkt_bin"]

        if src == 0 and dst == 0:
            base = "_".join(["0", time_bin, ibyt_bin, ipkt_bin])
            return base, base

        elif src > 0 and dst == 0:
            base = "_".join([str(src), time_bin, ibyt_bin, ipkt_bin])
            return "-1_" + base, base

        elif src == 0 and dst > 0:
            base = "_".join([str(dst), time_bin, ibyt_bin, ipkt_bin])
            return base, "-1_" + base

        elif src <= 1024 and dst <= 1024:
            base = "_".join(["111111", time_bin, ibyt_bin, ipkt_bin])
            return base, base

        elif src <= 1024 and dst > 1024:
            base = "_".join([str(src), time_bin, ibyt_bin, ipkt_bin])
            return "-1_" + base, base

        elif src > 1024 and dst <= 1024:
            base = "_".join([str(dst), time_bin, ibyt_bin, ipkt_bin])
            return base, "-1_" + base

        else:
            base = "_".join(["333333", time_bin, ibyt_bin, ipkt_bin])
            return base, base

    def _compute_word_count_table(self):
        data = self.data
        data["time"] = data["trhour"] * 3600 + data["trminute"] * 60 + data["trsec"]
        time_cut = self._compute_quantile(data["time"])
        ibyt_cut = self._compute_deciles(data["ibyt"])
        ipkt_cut = self._compute_deciles(data["ipkt"])
        data["time_bin"] = np.digitize(data["time"], time_cut, right=True).astype(str)
        data["ibyt_bin"] = np.digitize(data["ibyt"], ibyt_cut, right=True).astype(str)
        data["ipkt_bin"] = np.digitize(data["ipkt"], ipkt_cut, right=True).astype(str)
        data["src_word"] = [w[0] for w in data.apply(self._assemble_words, axis=1)]
        data["dst_word"] = [w[1] for w in data.apply(self._assemble_words, axis=1)]
        s_word_count = data.groupby(["sip", "src_word"]).size()
        d_word_count = data.groupby(["dip", "dst_word"]).size()
        wc_table = pd.concat([s_word_count, d_word_count]).sum(level=[0, 1])
        wc_table.index.set_names(["ip", "word"], inplace=True)
        return wc_table

    def train_new_model(self):
        df_wc_table = self._compute_word_count_table()
        self.train(df_wc_table)
        self.predict(df_wc_table)
    
    def train(self, df):
        df = df.unstack().fillna(0).astype(int)
        X = df.as_matrix()
        self.model = lda.LDA(n_topics=self.config["topic_count"], n_iter=20, random_state=1)
        self.model.fit(X)

    def predict(self, df_ip_wc):
        df_topic_word = df_ip_wc.unstack().fillna(0).astype(int)
        X = df_topic_word.as_matrix()
        y = self.model.transform(X)
        vocal = df_topic_word.columns.values
        titles = df_topic_word.index.values
        ss_ip_topic = pd.Series(xrange(len(titles)), index=pd.Index(titles, name="ip"), name="ip_topic")
        ss_word_topic = pd.Series(xrange(len(vocal)), index=pd.Index(vocal, name="word"), name="word_topic")
        ix = df_ip_wc.to_frame().join(ss_ip_topic).join(ss_word_topic)
        topic_word = self.model.topic_word_
        print ix
        print topic_word
        prob = np.einsum('ij,ij->j', y[ix.ip_topic].T, topic_word[:, ix.word_topic])
        prob = pd.Series(prob, index=df_ip_wc.index, name="prob")
        df_prob = self.data[["sip", "src_word", "dip", "dst_word"]].join(prob, on=["sip", "src_word"]).join(prob, on=["dip", "dst_word"],
                                                                                                 lsuffix="s", rsuffix="d")
        ss_prob = df_prob[["probs", "probd"]].max(axis=1)
        ss_prob.name = "prob"
        print ss_prob