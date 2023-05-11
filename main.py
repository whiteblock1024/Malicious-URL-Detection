from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pipeline import single_prediction, file_upload, batch_prediction, file_download


index_page = open("./static/index.html", 'r', encoding='utf-8').read()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 首页
@app.get("/")
async def index(): 
    """
    首页
    :return: index_page: str || index.html
    """  
    return HTMLResponse(index_page)


# 单例预测
@app.post("/prediction/single/")
def post_single_prediction(url: str):
    """
    单例预测
    :param url: str || 需要预测的url
    :return:
        state: bool || 是否成功
        text: str || 爬取的的文本
        prediction: str || 预测结果
        tensor: list, || 预测的tensor
        time: str, || 总耗时
        exception: str || 异常信息
    """
    state, text, prediction, tensor, time, exception = single_prediction(url)
    return {"state": state, "text": text, "prediction": prediction, "tensor": tensor, "time": time} if state else {"state": state, "exception": exception}


# 数据集上传
@app.post("/prediction/batch/upload/")
def post_batch_prediction_upload(file: UploadFile):
    """
    保存上传的文件并生成uuid
    :param file: UploadFile || 上传的文件
    :return:
        state: bool || 是否成功
        file_uuid: str || 文件uuid
        exception: str || 异常信息
    """
    state, file_uuid, exception = file_upload(file)
    return {"state": state, "file_uuid": file_uuid} if state else {"state": state, "exception": exception}


# 批量预测
@app.post("/prediction/batch/predict/")
def post_batch_prediction_predict(file_uuid: str):
    """
    批量预测
    :param file_uuid: str || 文件uuid
    :return:
        state: bool || 是否成功
        predicted: list || 预测类别分布
        invalid: int || 无效url数量
        time: str || 总耗时
        exception: str || 异常信息
    """
    state, predicted, invalid, time, exception = batch_prediction(file_uuid)
    return {"state": state, "predicted": predicted, "invalid": invalid, "time": time} if state else {"state": state, "exception": exception}


# 数据集下载
@app.get("/prediction/batch/download/{file_uuid}")
def get_batch_prediction_download(file_uuid: str):
    """
    根据uuid下载预测后的文件
    :param file_uuid: str || 文件uuid
    :return:
        state: bool || 是否成功
        exception: str || 异常信息
    """
    state, exception = file_download(file_uuid)
    return FileResponse(f'file/{file_uuid}_prediction.csv', media_type="text/csv", filename=f"{file_uuid}_prediction.csv.csv") if state else {"state": state, "exception": exception}

