"""
Module for visualization of confusion matrix, that is part of the report
produced by the pipeline.
"""
import itertools
from typing import List, Text

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np


def plot_confusion_matrix(cm: np.array,
                          target_names: List[Text],
                          title: Text = 'Confusion matrix',
                          cmap: matplotlib.colors.LinearSegmentedColormap = None,
                          normalize: bool = True) -> plt.figure:
    """Given a sklearn confusion matrix (cm), make a plot.

       Usage:
       plot_confusion_matrix(cm = cm, normalize = True, target_names = y_labels_vals, title = best_estimator_name)

        Citation:
        http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html

    Args:
        cm (np.array): confusion matrix from sklearn.metrics.confusion_matrix
        target_names (List[Text]): given classification classes such as [0, 1, 2] 
                                   the class names, for example: ['high', 'medium', 'low']
        title (Text, optional): the text to display at the top of the matrix. Defaults to 'Confusion matrix'.
        cmap (matplotlib.colors.LinearSegmentedColormap, optional): the gradient of the values displayed from matplotlib.pyplot.cm
                  see http://matplotlib.org/examples/color/colormaps_reference.html
                  plt.get_cmap('jet') or plt.cm.Blues. Defaults to None.
        normalize (bool, optional): If False, plot the raw numbers. If True, plot the proportions. Defaults to True.

    Returns:
        plt.gfc (plt.figure): plotted confusion matrix
    """
    accuracy = np.trace(cm) / float(np.sum(cm))
    misclass = 1 - accuracy

    if cmap is None:
        cmap = plt.get_cmap('Blues')

    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()

    if target_names is not None:
        tick_marks = np.arange(len(target_names))
        plt.xticks(tick_marks, target_names, rotation=45)
        plt.yticks(tick_marks, target_names)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    thresh = cm.max() / 1.5 if normalize else cm.max() / 2
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        if normalize:
            plt.text(j, i, "{:0.4f}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")
        else:
            plt.text(j, i, "{:,}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label\naccuracy={:0.4f}; misclass={:0.4f}'.format(
        accuracy, misclass))

    return plt.gcf()
