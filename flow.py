import pandas as pd
from analysis import FlowConnectsAnalysis

config = {
    "topic_count": 20
}

def main():
    data = pd.read_csv("test.csv")
    analysis = FlowConnectsAnalysis(data, config)
    scored_data = analysis.detect()
    print scored_data

if __name__ == "__main__":
    main()
