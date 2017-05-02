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

    def train_new_model(self):
        df_time = self.data["trhour"] * 3600 + self.data["trminute"] * 60 + self.data["trsec"]
        self.time_cuts = self._compute_quantile(df_time)
        self.ibyt_cuts = self._compute_deciles(data["ibyt"])
        self.ipkt_cuts = self._compute_deciles(data["ipkt_cuts"])

    def score(self):
        pass