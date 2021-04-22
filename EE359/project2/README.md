
## Community Detection

> 0.8都到不了，我是废物，我卷不动了 :sob::sob::sob:

In this lab, we implement the Louvain Method to perform community detection

### Environment Setup

Python 3.8 is used in this project. `pip install -r requirements.txt` can install the dependencies.

`python src/main.py` will run the Louvain algorithm given `data/edges.csv` and `data/ground_truth.csv`. By default the `verbose` mode is on, which means you can see the training process on the console, and every iteration / two phase a summary of the current training process will be printed.

### Notes

- The algorithm chooses the order of nodes to optimize randomly. As a result, the results/accuracy for every execution of the program may differ a little.
- Usually, the Louvain method will stop at around 10\~20 clusters, but since ground truth number is limited, some clusters may be unable to find its 0\~4 label. In our implementation, we will assign labels by voting on neighbors with known clusters

### Example

Here is an observation of running.

```
Round 0, (220377, 31136)
New Phase, modularity -7.710011723948257e-05
Iteration #1, 28226 vertices Moved, modularity: 0.12779494890510845, cluster#: 14630
Iteration #2, 20339 vertices Moved, modularity: 0.24348501427788533, cluster#: 9465
Iteration #3, 13478 vertices Moved, modularity: 0.28358660710193084, cluster#: 7117
Iteration #4, 9402 vertices Moved, modularity: 0.30252376036634593, cluster#: 5881
Iteration #5, 7235 vertices Moved, modularity: 0.3140151223316634, cluster#: 5101
Iteration #6, 5781 vertices Moved, modularity: 0.3220089201141691, cluster#: 4543
Iteration #7, 5222 vertices Moved, modularity: 0.3315460653897221, cluster#: 4052
Iteration #8, 5206 vertices Moved, modularity: 0.35440880734027014, cluster#: 3404
Iteration #9, 4331 vertices Moved, modularity: 0.3728249624481418, cluster#: 2947
Iteration #10, 3879 vertices Moved, modularity: 0.3874893810741575, cluster#: 2614
Iteration #11, 3365 vertices Moved, modularity: 0.40168816418981623, cluster#: 2406
Iteration #12, 2785 vertices Moved, modularity: 0.4094006043090651, cluster#: 2228
Iteration #13, 2557 vertices Moved, modularity: 0.4166809598333615, cluster#: 2032
Iteration #14, 2711 vertices Moved, modularity: 0.4285308689214767, cluster#: 1735
Iteration #15, 2411 vertices Moved, modularity: 0.4427313138162251, cluster#: 1431
Iteration #16, 2028 vertices Moved, modularity: 0.45416253345627217, cluster#: 1273
Iteration #17, 1462 vertices Moved, modularity: 0.4607245648216055, cluster#: 1208
Iteration #18, 1254 vertices Moved, modularity: 0.46532525228179183, cluster#: 1156
Iteration #19, 1041 vertices Moved, modularity: 0.468871221726079, cluster#: 1102
Iteration #20, 1006 vertices Moved, modularity: 0.47266965289077306, cluster#: 1023
Iteration #21, 961 vertices Moved, modularity: 0.47665231846684686, cluster#: 948
Iteration #22, 757 vertices Moved, modularity: 0.47966354381718646, cluster#: 909
Iteration #23, 641 vertices Moved, modularity: 0.4818691007951801, cluster#: 880
Iteration #24, 458 vertices Moved, modularity: 0.48319233537735945, cluster#: 860
Iteration #25, 322 vertices Moved, modularity: 0.4838189743044508, cluster#: 850
Iteration #26, 229 vertices Moved, modularity: 0.48411938357950374, cluster#: 840
Iteration #27, 176 vertices Moved, modularity: 0.48421061257676956, cluster#: 839
839 clusters
Round 1, (220377, 839)
New Phase, modularity 0.4842106125767697
Iteration #1, 748 vertices Moved, modularity: 0.49846425794762644, cluster#: 249
Iteration #2, 398 vertices Moved, modularity: 0.5001345802314738, cluster#: 121
Iteration #3, 204 vertices Moved, modularity: 0.5003452489984733, cluster#: 90
Iteration #4, 155 vertices Moved, modularity: 0.5003530520567308, cluster#: 73
73 clusters
Round 2, (220377, 73)
New Phase, modularity 0.5003530520567334
Iteration #1, 62 vertices Moved, modularity: 0.5038940316853142, cluster#: 23
Iteration #2, 30 vertices Moved, modularity: 0.5046557580297476, cluster#: 18
Iteration #3, 14 vertices Moved, modularity: 0.5047260267660041, cluster#: 16
16 clusters
Round 3, (220377, 16)
New Phase, modularity 0.5047260267660041
Iteration #1, 2 vertices Moved, modularity: 0.5047572136932755, cluster#: 14
Iteration #2, 0 vertices Moved, modularity: 0.5047572136932755, cluster#: 14
14 clusters
Round 4, (220377, 14)
New Phase, modularity 0.5047572136932756
Iteration #1, 0 vertices Moved, modularity: 0.5047572136932756, cluster#: 14
14 clusters
{11: {0: 1}, 1: {0: 2, 1: 9}, 10: {0: 1}, 4: {0: 1, 3: 10}, 9: {0: 1, 2: 1}, 2: {0: 2}, 5: {0: 1}, 6: {0: 1, 1: 1}, 3: {2: 9}, 0: {4: 10}}
{11: 0, 1: 1, 10: 0, 4: 3, 9: 2, 2: 0, 5: 0, 6: 1, 3: 2, 0: 4}
1746
```