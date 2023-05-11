from fastapi import UploadFile
import pandas as pd
import time
from .spider import single_get_html_headless, batch_get_html_headless
from .preprocess import single_white_list, batch_white_list, black_list, filter, batch_preprocess
from .svm import svm_prediction_single, svm_prediction_batch
from .bert import bert_prediction_single, bert_prediction_batch
from .utils import df_divide, count_label, gen_uuid, file_check, file_creat, file_save, file_load, cuda_check


def file_upload(file: UploadFile) -> tuple[bool, str, str]:
    """
    保存上传的文件并生成uuid
    :param file: UploadFile || 上传的文件
    :return: 
        state: bool || 是否成功
        file_uuid: str || 文件uuid
        exception: str || 异常信息
    """
    file_uuid = gen_uuid()
    state:bool = file_creat(file, file_uuid)
    return (True, file_uuid, None) if state else (False, None, ('file upload failed'))


def file_download(file_uuid: str) -> tuple[bool, str]:
    """
    根据uuid下载预测后的文件
    :param file_uuid: str || 文件uuid
    :return: 
        state: bool || 是否成功
        exception: str || 异常信息
    """
    state:bool = file_check(file_uuid)
    return (True, None) if state else (False, ('file is not exist'))


def single_prediction(url: str) -> tuple[bool, str, str, list, str, str]:
    """
    单条预测
    :param url: str || 需要预测的url
    :return: 
        state: bool || 是否成功 
        text: str || 爬取的的文本
        prediction: str || 预测结果
        tensor: list, || 预测的tensor
        time: str, || 总耗时
        exception: str || 异常信息
    """
    # 计时开始
    start_time = time.time()
    # 检查cuda和文件可用性
    if not cuda_check() or not url:
        return False, None, None, None, None,('url is empty' if not url else 'cuda is not available')
    try:
        # url预处理
        if single_white_list(url):
            return True, 'None', '0', [1.0,0.0], '3.0', None
        # 爬取文本
        text:str = filter(single_get_html_headless(url))
        # 检查黑名单和文本可用性
        if black_list(text) or not text:
            return False, None, None, None, None, ('url is invalid')
        # svm预测
        svm_pridection: list = svm_prediction_single(text)
        # bert预测
        if svm_pridection[0] < 0.5:
            prediction, tensor = bert_prediction_single(text)
        else:
            prediction = '0'
            tensor = [svm_pridection[0], 1 - svm_pridection[0]]
    except Exception as e:
        return False, None, None, None, None, e.__str__()
    # 计时结束
    total_time = str(time.time() - start_time)
    # 保留小数点后两位
    total_time = total_time[:total_time.find('.') + 3]
    prediction = str(prediction)
    return True, text, prediction, tensor, total_time, None


def batch_prediction(file_uuid: str) -> tuple[bool, dict, int, str, str]:
    """
    批量预测
    :param file_uuid: str || 文件uuid
    :return:
        state: bool || 是否成功
        predicted: list || 预测类别统计
        invalid: int || 无效数
        time: str || 总耗时
        exception: str || 异常信息
    """
    # 计时开始
    start_time = time.time()
    # 检查cuda和文件可用性
    if not cuda_check() or not file_check(file_uuid):
        return False, None, None, None, ('file is not exist' if not file_check(file_uuid) else 'cuda is not available')
    try:
        # url预处理
        pre_df_0, pre_df_1 = batch_white_list(file_load(file_uuid))
        pre_df_0['label'] = 0
        # 爬取文本
        pre_df = batch_get_html_headless(pre_df_1)
        # 文本预处理
        text_df, invalid = batch_preprocess(pre_df)
        # svm预测
        svm_df: pd.DataFrame = svm_prediction_batch(text_df) if not text_df.empty else None
        # 分割数据
        svm_df_0, svm_df_1 = df_divide(svm_df) if svm_df is not None else [pd.DataFrame(), pd.DataFrame()] 
        # bert预测
        bert_df = bert_prediction_batch(svm_df_1) if not svm_df_1.empty else None
        # 合并预测结果
        df_fin = pd.concat([pre_df_0, svm_df_0, bert_df], axis=0)
        # 保存预测结果
        file_save(file_uuid, df_fin)
    except Exception as e:
        return False, None, None, None, e.__str__()
    # 预测类别统计
    predicted: dict = count_label(df_fin)
    # 计时结束
    total_time = str(time.time() - start_time)
    # 保留小数点后两位
    total_time = total_time[:total_time.find('.') + 3]
    return True, predicted, invalid, total_time, None

