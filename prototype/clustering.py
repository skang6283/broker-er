import os 
import pandas as pd
import numpy as np
import constant 

from sklearn.preprocessing import StandardScaler
from k_means_constrained import KMeansConstrained

""" Clustering """
# Prepare Data
df = pd.read_csv(os.path.join(constant.DATA_DIR, "cluster_analysis.csv"))

X = df.drop(columns=["Ticker"]).values

scaler = StandardScaler()
X = scaler.fit_transform(X)

# Kmeans clustering with size constraints
clf = KMeansConstrained(n_clusters=50, size_min=5, size_max=10)

labels = clf.fit_predict(X)
# cluster_centers = scaler.inverse_transform(clf.cluster_centers_)

# Output dataframe
df["clusterId"] = labels
df.to_csv(os.path.join(constant.DATA_DIR, "cluster_result.csv"), index=False)

