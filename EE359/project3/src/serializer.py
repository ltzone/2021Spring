import pickle
import pandas as pd

def serialize_embedding(pik_dir, csv_dir):
    """
    Serialize the weights from a pickle file to a csv file
    """
    with open(pik_dir, "rb") as f:
        embedding = pickle.load(f)
    out_df = pd.concat([pd.DataFrame([embedding[i]], index=[i]) for i in sorted(embedding.keys())])
    out_df.to_csv(csv_dir)


if __name__ == '__main__':
    serialize_embedding("data/pretrained_embedding.pik", "data/embedding_result.csv")