
## Link Prediction

In this lab, we implement the Node2Vec random walk and Word2Vec CBOW model (with negative sampling) to perform link prediction

### Environment Setup

Python 3.8.8 is used in this project. `pip install -r requirements.txt` can install the dependencies.

### Usage
- `python src/cross_validation.py` splits the edges in the graph into 20% test set and use only 80% of the edges to calculate embedding. It then generates random false edges with the same size of the truth testing edges to compute AUC of the prediction based on the embedding result.
  > This code is only used for training, and does not involve `course3_test.csv`. You do not need to run this piece of code if you want to reproduce the result
- `python src/main.py` will run embedding and prediction algorithm on the whole graph and generate result in `data/submission.csv`, if `verbose` mode is on, the walking statistics will be stored in `walk_stat.pik` and the network weight of word2vec training will be stored as a tuple in `checkpoint_n.pik`
- `python src/main_fast.py` will not run the node2vec and word2vec algorithm. It will use the existing embedding result in the `data` folder yo generate the prediction result in `data/submission.csv`
- The embedding is stored in `pickle` format to save space, `python src/serializer.py` will decompress the pickle file and output the embedding vector into `data/embedding_result.csv`
- `Word2Vec.py` and `Node2Vec.py` are the core algorithm implementation. 

### Runtime

The major runtime of the algorithm falls on the `Word2Vec` training. Every epoch takes about 5 or 6 minutes on a 16GB RAM laptop. In fact, with only one epoch the model can already performs well on the train-test split. For the submission we train the model for four epoches. The detailed running time is as follows.

```
❯ python src/main.py     
Walk iteration 1/3
100%|█████████████████████████████| 16714/16714 [00:11<00:00, 1508.75it/s]
Walk iteration 2/3
100%|█████████████████████████████| 16714/16714 [00:11<00:00, 1457.09it/s]
Walk iteration 3/3
100%|█████████████████████████████| 16714/16714 [00:09<00:00, 1766.06it/s]
finish walking
16714 words have been loaded
100%|█████████████████████████████| 50142/50142 [06:32<00:00, 127.80it/s]
100%|█████████████████████████████| 50142/50142 [06:36<00:00, 126.32it/s]
100%|█████████████████████████████| 50142/50142 [05:55<00:00, 141.05it/s]
100%|█████████████████████████████| 50142/50142 [05:16<00:00, 158.37it/s]
finish training
```

totally 25m 1s


### Reference

1. Mikolov T, Sutskever I, Chen K, et al. Distributed representations of words and phrases and their compositionality\[J\]. arXiv preprint arXiv:1310.4546, 2013.
2. Grover A, Leskovec J. node2vec: Scalable feature learning for networks\[C\]//Proceedings of the 22nd ACM SIGKDD international conference on Knowledge discovery and data mining. 2016: 855-864.
3. Implementation notes about negative sampling for Word2Vec https://www.cnblogs.com/pinard/p/7249903.html
