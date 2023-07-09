from transformers import AutoTokenizer, BertForSequenceClassification
import torch
import torch.nn as nn
import pandas as pd
import os


"""
由于比赛限制提交文件大小，需将模型文件 pytorch_model.bin 改为线上存储，首次运行将自动下载至于model/bert文件夹
请检查model/bert文件夹的权限，确保可以写入文件
"""


if not os.path.exists('model/bert/pytorch_model.bin'):
    print("模型文件不存在，正在下载...(预计5-10分钟)")
    import requests
    url = "http://xxx.xxx.xxx.xxx/pytorch_model.bin"
    r = requests.get(url)
    with open('model/bert/pytorch_model.bin', 'wb') as f:
        f.write(r.content)
    print("模型文件下载成功，开始加载模型")


# 预加载模型
tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese", do_lower_case=False, cache_dir='cache')
model = BertForSequenceClassification.from_pretrained("bert-base-chinese", num_labels=13)
model.load_state_dict(torch.load('model/bert/pytorch_model.bin'))
model.eval()
print("加载模型成功")


class MyDataset(torch.utils.data.Dataset):
    """
    构建数据集
    """
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        return {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}, torch.tensor(self.labels[idx])

    def __len__(self):
        return len(self.labels)


def bert_prediction_single(text: str) -> tuple[str, list]:
    """
    单条预测
    :param text: str || 需要预测的文本
    :return:
        prediction: str || 预测结果
        tensor: list || 预测的tensor
    """
    # 分词
    test_encodings = tokenizer([text], truncation=True, max_length=512, padding="max_length")
    test_dataset = MyDataset(test_encodings, [0])
    # 加载数据
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1, shuffle=False)

    # 指定GPU
    device = torch.device('cuda')
    # 加载模型
    model.to(device)
    # 开始预测
    predictions: str = ''
    logits_list: list = []
    with torch.no_grad():
        for batch in test_loader:
            # 将数据放入GPU
            input_ids = batch[0]['input_ids'].to(device)
            # attention_mask
            attention_mask = batch[0]['attention_mask'].to(device)
            # 预测
            outputs = model(input_ids, attention_mask=attention_mask)
            # 获取预测结果
            logits = outputs.logits
            predictions = torch.argmax(logits, dim=1)
            logits = nn.functional.softmax(logits, dim=1)
            logits_list = logits.tolist()[0]
            # 保留小数点后五位，最小值为0.00001
            logits_list = [round(i, 5) for i in logits_list]

    return predictions.item(), logits_list


def bert_prediction_batch(df: pd.DataFrame) -> pd.DataFrame:
    """
    批量预测
    :param df: pd.DataFrame || 需要预测的数据集
    :return: df: pd.DataFrame || 预测结果
    """
    pd.set_option('mode.chained_assignment', None)
    # 分词
    test_encodings = tokenizer(df['text'].tolist(), truncation=True, max_length=512, padding="max_length")
    test_labels = df['label'].tolist()
    # 构建数据
    test_dataset = MyDataset(test_encodings, test_labels)
    # 加载数据
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1, shuffle=False)
    # 指定GPU
    device = torch.device('cuda')
    # 加载模型
    model.to(device)
    # 开始预测
    prediction_list: list = []
    with torch.no_grad():
        total:int = 0
        for batch in test_loader:
            # 将数据放入GPU
            input_ids = batch[0]['input_ids'].to(device)
            # attention mask
            attention_mask = batch[0]['attention_mask'].to(device)
            # 预测
            outputs = model(input_ids, attention_mask=attention_mask)
            # 获取预测结果
            logits = outputs.logits
            predictions:int = torch.argmax(logits, dim=1)
            # 保存预测结果
            prediction_list.append(predictions.item())
            total += 1

    df.loc[:, 'label'] = prediction_list

    return df

