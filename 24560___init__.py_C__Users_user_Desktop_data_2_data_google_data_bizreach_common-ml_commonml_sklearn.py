# coding: utf-8

from commonml.sklearn import estimator
ChainerEstimator=estimator.ChainerEstimator
from commonml.sklearn import rnn_estimator
RnnEstimator=rnn_estimator.RnnEstimator

from commonml.sklearn import regressor
MeanSquaredErrorRegressor=regressor.mean_squared_error_regressor

from commonml.sklearn import classifier
SoftmaxCrossEntropyClassifier=classifier.softmax_cross_entropy_classifier
SoftmaxClassifier=classifier.softmax_classifier
HingeClassifier=classifier.hinge_classifier
SigmoidClassifier=classifier.sigmoid_classifier
SigmoidCrossEntropyClassifier=classifier.sigmoid_cross_entropy_classifier
