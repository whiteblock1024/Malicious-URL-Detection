import pandas as pd
import numpy as np
import joblib
import jieba


# 预加载模型
vectorizer = joblib.load('model/svm/vectorizer.pkl')
clf = joblib.load('model/svm/svm_model.pkl')


# 分词
def cut_text(text_list: list) -> list:
    """
    jieba分词
    :param text_list: list || 需要分词的文本列表
    :return: list || 分词后的文本列表
    """
    return [' '.join(jieba.cut(text)) for text in text_list]


# 向量化
def vectorize_data(x_test:list) -> np.array:
    """
    向量化
    :param x_test: list || 需要向量化的文本列表
    :return: np.array || 向量化后的文本列表
    """
    x_test = cut_text(x_test)
    x_test = vectorizer.transform(x_test)
    return x_test


# 单例预测
def svm_prediction_single(text: str) -> list:
    """
    单例预测
    :param text: str || 需要预测的文本
    :return: list || 预测结果
    """
    x_test = vectorize_data([text])
    y_pred = clf.predict_proba(x_test)
    return y_pred[0]


# 批量预测
def svm_prediction_batch(test_data: pd.DataFrame) -> pd.DataFrame:
    """
    批量预测
    :param test_data: pd.DataFrame || 需要预测的数据
    :return: pd.DataFrame || 预测结果
    """
    x_test = test_data['text'].tolist()
    x_test = vectorize_data(x_test)
    y_pred = clf.predict(x_test)
    test_data.loc[:, 'label'] = y_pred
    return test_data


# 保存数据
def save_data(test_data: pd.DataFrame) -> None:
    """
    保存数据
    :param test_data: pd.DataFrame || 需要保存的数据
    :return: None
    """
    # 保留1类label
    # test_data = test_data[test_data['label'] == 1]
    test_data.to_csv('pipeline/test_p.csv', index=False, encoding='utf-8')

