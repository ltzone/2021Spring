
## Clustering

In this lab, we implement the K-Means (together with K-Means++, an efficient initial centroid selection strategy) for the clustering task.

### Environment Setup

Python 3.8 is used in this project. Either `pip install -r requirements.txt` or `conda env create --file=config.yaml` can install the dependencies.

`python src/main.py` will run the K-Means algorithm given `data/course1.csv`. By default the `verbose` mode is on, which means you can see the training process on the console, and every 10 iterations a summary of the current training result will be printed.

You may also change the config of training and declare the input/output directory by modifying the parameters in the `main` part of the script.



### Note for the running time

Since the data points show good clustering property, in most cases, a perfect sets of clusters, with 1e4 elements per category can be found by the K-Means algorithm.

```
Category 0       10000 elements,         radius 0.5139838182531288
Category 1       10000 elements,         radius 0.5253962807254343
Category 2       10000 elements,         radius 0.5373167555430318
Category 3       10000 elements,         radius 0.5644269467164871
Category 4       10000 elements,         radius 0.5973270731874429
```

However, a bad choice of initial points may slower the training process and generate unsatisfactory results, as the below example shows.

```
Category 0 	 10000 elements, 	 radius 0.5973270731874429
Category 1 	 10000 elements, 	 radius 0.5644269467164871
Category 2 	 20000 elements, 	 radius 0.9846924655771885
Category 3 	 5044 elements, 	 radius 0.4251494862778501
Category 4 	 4956 elements, 	 radius 0.5101945667319101
```

To resolve this issue, we implement the [K-Means++ algorithm](https://en.wikipedia.org/wiki/K-means%2B%2B), whose sampling of initial points follows a distribution w.r.t the data point's minimum distance to the chosen centriods.

Experiments show that K-Means++ will be more likely to avoid the latter case than naive K-Means. However, there can still be cases where bad initial points are selected in K-Means++. Users can observe the verbose information during the training process to determine whether they need to restart the training in order to get a better initial set of centriods.