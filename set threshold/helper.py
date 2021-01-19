import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.cluster import KMeans
import optparse
import os

# parser = optparse.OptionParser(usage="usage: %prog [options]")
# parser.add_option('--csv_path', dest='csv_path', help='specify csv_path source of data file')

# (options, args) = parser.parse_args()

# if not options.csv_path:
#     parser.error('csv_path is not given')

# csv_path = options.csv_path

COUNTER = 0
LS = []
DF_ALL = []


def persebaran_volume(data):
    return data[['result','vol_cbm']].groupby('result').sum(), data[['result','vol_cbm']].groupby('result').sum().describe()

def persebaran_weight(data):
    return data[['result','weight_ton']].groupby('result').sum(), data[['result','weight_ton']].groupby('result').sum().describe()

def persebaran_order(data):
    return data[['result','origin']].groupby('result').count(), data[['result','origin']].groupby('result').count().describe()

def persebaran_distance(data):
    return data[['cluster','distance_km']].groupby('cluster').sum(), data[['cluster','distance_km']].groupby('cluster').sum().describe()

def clusterkeun(data):
    X = data[['partner_longitude','partner_latitude']].to_numpy()
    kmeans = KMeans(n_clusters=2, random_state=0).fit(X)
    res = kmeans.labels_
    data['result'] = res
    vhasil, vresume = persebaran_volume(data)
    whasil, wresume = persebaran_weight(data)
    return data, vhasil, whasil


### def class
class Node:

    def __init__(self, data):

        self.left = None
        self.right = None
        self.data = data

        if len(self.data) > 1:
            # print(len(self.data))
            self.branch, self.volem_branch, self.weight_branch = clusterkeun(data)
            self._insert(self.branch)
        else:
            pass
        

    # Insert method to create nodes
    def _insert(self, branch):
        # print('insert')
        # if self.volem_branch.vol_cbm[0] <=2.8 or self.volem_branch.vol_cbm[1] <=2.8:
        if max(self.volem_branch.vol_cbm[0],self.volem_branch.vol_cbm[1]) <= 2.8:
            pass
        else:
            if self.volem_branch.vol_cbm[0] <= 2.8:           
                pass
            else:
                self.left = Node(self.branch[branch['result']==0].reset_index(drop=True))
            if self.volem_branch.vol_cbm[1] <= 2.8:           
                pass
            else:
                self.right = Node(self.branch[branch['result']==1].reset_index(drop=True))


# Function to get the count of leaf nodes in binary tree 
def getLeafCount(node):
    global COUNTER
    global LS
    global DF_ALL
    try:
        if node.volem_branch.vol_cbm[0] <= 2.8: 
            # print(node.volem_branch.vol_cbm[0], node.volem_branch.vol_cbm[1])
            # print('cluster 0')
            COUNTER+=1
            LS.append(COUNTER)
            # print('cluster {}'.format(COUNTER))
            # print(node.branch[node.branch['result']==0].reset_index(drop=True))
            DF_ALL.append(node.branch[node.branch['result']==0].reset_index(drop=True))
        if node.volem_branch.vol_cbm[1] <= 2.8:
            # print(node.volem_branch.vol_cbm[0], node.volem_branch.vol_cbm[1])
            # print('cluster 1')
            COUNTER+=1
            LS.append(COUNTER)
            # print('cluster {}'.format(COUNTER))
            # print(node.branch[node.branch['result']==1].reset_index(drop=True))
            DF_ALL.append(node.branch[node.branch['result']==1].reset_index(drop=True))
    except:
        pass
    if node is None: 
        return 0 
    if(node.left is None and node.right is None): 
        return 1 
    else: 
        return getLeafCount(node.left) + getLeafCount(node.right) 

def flush_global():
    global COUNTER
    global LS
    global DF_ALL
    COUNTER = 0
    LS = []
    DF_ALL = []


def get_cluster(data):

    # read file
    # data = pd.read_csv(csv_path)

    lst = []
    for i in range(len(data)):
        if (data['vol_cbm'][i] >= 2.8) | (data['weight_ton'][i] > 2):
            a = 1
        else:
            a = 0
        lst.append(a)

    data['result'] = lst

    ##data besar masing2 1 cluster
    data_final = data[data['result']==1].reset_index(drop=True)
    data_final['result'] = data_final.index

    # data.result ==> a = 1 (final)
    # data.result ==> a = 0 (to cluster)

    head = data[data['result']==0].reset_index(drop=True)

    root = Node(head)
    # print(root)

    getLeafCount(root)

    for i in range(len(LS)): 
        DF_ALL[i]['result']=LS[i]

    df_baru = pd.DataFrame()

    for i in range(len(DF_ALL)): 
        df_baru = pd.concat([df_baru,DF_ALL[i]])

    if len(data_final) == 0:
    	maks = 0
    else:
    	maks = max(data_final['result'])

    df_baru['result'] = df_baru['result'] + maks

    df_baru = df_baru.reset_index(drop=True)

    data_final = pd.concat([data_final,df_baru]).reset_index(drop=True)
    
    flush_global()
    return data_final


