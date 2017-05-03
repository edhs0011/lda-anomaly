class FlowSuspiciousConnectsModel:

    # def __init__(self, topic_count, ip_to_topic_mix, word_to_per_topic_prob, time_cuts, ibyt_cuts, ipkt_cuts):
    #     self.topic_count = topic_count
    #     self.ip_to_topic_mix = ip_to_topic_mix
    #     self.word_to_per_topic_prob = word_to_per_topic_prob
    #     self.time_cuts = time_cuts
    #     self.ibyt_cuts = ibyt_cuts
    #     self.ipkt_cuts = ipkt_cuts

    def __init__(self, data, config):
        self.data = data    # trhour,trminute,trsec,sip,dip,sport,dport,ipkt,ibyt
        self.config = config

    def _compute_deciles(self, df):
        return df.quantile([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

    def _compute_quantile(self, df):
        return df.quantile([0.2, 0.4, 0.6, 0.8, 1.0])

    def _quantile_bin(self, val, cuts):
        for i, v in enumerate(cuts):
            if val >= v:
                return i

    def _assemble_words(self, df):
        src = df["sport"]
        dst = df["dport"]
        time_bin = self._quantile_bin(df["time"], df["time_cuts"])
        ibyt_bin = self._quantile_bin(df["ibyt"], df["ibyt_cuts"])
        ipkt_bin = self._quantile_bin(df["ipkt_time"], df["ipkt_cuts"])
        port_word = None

        if src == 0 and dst == 0:
            port_word = "0"
        elif (src > 0 and dst == 0) or (src <= 1024 and dst > 1024):
            port_word = str(src)
        elif (src == 0 and dst > 0) or (src > 1024 and dst <= 1024):
            port_word = str(dst)
        elif src <= 1024 and dst <= 1024:
            port_word = "111111"
        else:
            port_word = "333333"

        src_word = "_".join(port_word, time_bin, ibyt_bin, ipkt_bin)
        dst_word = "_".join(port_word, time_bin, ibyt_bin, ipkt_bin)
        if src > dst:
            src_word = "_".join("-1", src_word)
        elif src < dst:
            dst_word = "_".join("-1", dst_word)
        return src_word, dst_word
            

    def test(self, x):
        print x["trhour"]
        # return x["trhour"]

    def train_new_model(self):
        self.data["time"] = self.data["trhour"] * 3600 + self.data["trminute"] * 60 + self.data["trsec"]
        print self.data["ibyt"]
        print self.data["ibyt"].quantile([0.5])
        self.data["time_cuts"] = self._compute_quantile(self.data["time"])
        print self.data["time_cuts"]
        self.data["ibyt_cuts"] = self._compute_deciles(self.data["ibyt"])
        print self.data["ibyt_cuts"]
        self.data["ipkt_cuts"] = self._compute_deciles(self.data["ipkt"])
        print self.data.apply(self._assemble_words, axis=1)
        
        # self.data["src_word"], self.data["dst_word"] = self._assemble_words()

    def score(self):
        pass