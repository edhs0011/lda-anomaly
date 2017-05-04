import pandas as pd
from analysis import FlowConnectsAnalysis
from model import FlowSuspiciousConnectsModel

config = {
    "topic_count": 20
}

def main():
    data = pd.read_csv("test.csv")
    model = FlowSuspiciousConnectsModel(data, config)
    model.train_new_model()

if __name__ == "__main__":
    main()
