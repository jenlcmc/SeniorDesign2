import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn import svm



# Cross_val_score the three kernels with a 5-fold CV
def cross_val_for_kernel(kernel, C=1, random_state=42):
    clf = svm.SVC(kernel=kernel, C=C, random_state=random_state)
    scores = cross_val_score(clf, X, y, cv=5)
    return scores

svmAccuracies = {}

kernels = ['linear', 'poly', 'rbf']
for kernel in kernels:
    scores = cross_val_for_kernel(kernel)
    svmAccuracies[kernel.capitalize()] = scores