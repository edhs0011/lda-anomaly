import pandas as pd
from analysis import FlowConnectsAnalysis
from model import FlowSuspiciousConnectsModel

config = {
    "n_topics": 4,
    "n_iter": 20,
    "random_state": 1,
    "alpha": 1.02
}

def main():
    data = pd.read_csv("test.csv")
    model = FlowSuspiciousConnectsModel(data, config)
    model.train_new_model()

if __name__ == "__main__":
    main()
