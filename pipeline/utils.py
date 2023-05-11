from fastapi import UploadFile
import pandas as pd
import torch
import uuid
import os


def df_divide(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    将数据集分为正负两部分
    :param df: pd.DataFrame || 需要分割的数据集
    :return: 
        df_0: pd.DataFrame || label为0的数据集
        df_1: pd.DataFrame || label为1的数据集
    """
    df_0 = df[df['label'] == 0].copy()
    df_1 = df[df['label'] == 1].copy()
    return df_0, df_1


def count_label(df: pd.DataFrame) -> dict:
    """
    统计数据集中各个label的数量
    :param df: pd.DataFrame || 需要统计的数据集
    :return: count: list || 各个label的数量
    """
    count = {
        '0': 0,
        '1': 0,
        '2': 0,
        '3': 0,
        '4': 0,
        '5': 0,
        '6': 0,
        '7': 0,
        '8': 0,
        '9': 0,
        '10': 0,
        '11': 0,
        '12': 0,
    }
    for i in df['label']:
        count[str(int(i))] += 1
    return count


def gen_uuid() -> str:
    """
    生成uuid
    :return: uuid: str || uuid
    """
    return str(uuid.uuid1())


def file_check(file_uuid: str) -> bool:
    """
    检查文件是否存在
    :param file_uuid: str || 文件uuid
    :return: state: bool || 是否存在
    """
    state:bool = os.path.exists(f'./file/{file_uuid}.csv')
    return state


def file_creat(file: UploadFile, file_uuid: str) -> bool:
    """
    保存上传的文件
    :param file: UploadFile || 上传的文件
    :param file_uuid: str || 文件uuid
    :return: state: bool || 是否成功
    """
    try:
        df = pd.read_csv(file.file, encoding='utf-8')
        df.to_csv(f'./file/{file_uuid}.csv', index=False, encoding='utf-8')
    except:
        return False
    return True


def file_load(file_uuid: str) -> pd.DataFrame:
    """
    读取文件
    :param file_uuid: str || 文件uuid
    :return: df: pd.DataFrame || 读取的数据
    """
    df = pd.read_csv(f'./file/{file_uuid}.csv', encoding='utf-8')
    # 检查是否有列标题
    if 'url' not in df.columns:
        df.columns = ['url']
        if 'label' not in df.columns:
            df.loc[:, 'label'] = None
        if 'text' not in df.columns:
            df.loc[:, 'text'] = None
    
    return df


def file_save(file_uuid: str, df: pd.DataFrame) -> bool:
    """
    保存预测后的文件
    :param file_uuid: str || 文件uuid
    :param df: pd.DataFrame || 需要保存的数据   
    :return:
        state: bool || 是否成功
        exception: str || 异常信息
    """
    try:
        df.to_csv(f'./file/{file_uuid}_prediction.csv', index=False, encoding='utf-8')
    except:
        return False
    return True


def cuda_check() -> bool:
    """
    检查cuda可用性
    :return: state: bool || 是否有cuda
    """
    return torch.cuda.is_available()

