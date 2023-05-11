import pandas as pd
import csv
import re


def get_white_list(path: str) -> list:
    """
    获取白名单
    :param path: str || 白名单路径
    :return: result: list || 白名单
    """
    result = []
    csv.field_size_limit(500 * 1024 * 1024)
    with open(path, mode='r',encoding='UTF-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            first_column = row[0]
            result.append(first_column)
    file.close()
    return result


white_list = get_white_list('source/white_list.csv')


def single_white_list(url: str) -> bool:
    """
    单个url白名单过滤
    :param url: str || 待处理数据
    :return: result: bool || 是否过滤
    """
    suffixs = ['m4a','jpg','png','txt','wav','flv','mp3','local','node6','aa','mp4','mobi','gif','zip','xml','docx','xls','php','c']
    pattern = r':\d+$'
    if url[:5] == 'only-':
        return True
    spilt_url = url.split('.')
    if len(spilt_url[-1]) > 6 or len(spilt_url[-1]) == 1:
        return True
    if re.search(pattern, url):
        if url[-3:] == ':80' or url[-4:] == ':443':
            j = 0
            for white_word in white_list:
                if len(spilt_url) == 2:
                    if white_word == spilt_url[-2]:
                        j += 1
                elif len(spilt_url) > 2:
                    if white_word == spilt_url[-2] or white_word == spilt_url[-3]:
                        j += 1
            if j == 0:
                return False
            else:
                return True
        else:
            return True
    else:
        i = 0
        for suffix in suffixs:
            if suffix.upper() == spilt_url[-1].upper():
                i += 1
        if i == 0:
            j = 0
            for white_word in white_list:
                if len(spilt_url) == 2:
                    if white_word == spilt_url[-2]:
                        j += 1
                elif len(spilt_url) > 2:
                    if white_word == spilt_url[-2] or white_word == spilt_url[-3]:
                        j += 1
            if j == 0:
                return False
            else:
                return True
        else:
            return True


def batch_white_list(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    多个url白名单过滤
    :param df: pd.DataFrame || 待处理数据
    :return: tuple[pd.DataFrame, pd.DataFrame] || 过滤后的数据
    """
    dataframe:list = df['url'].tolist()
    suffixs = ['m4a','jpg','png','txt','wav','flv','mp3','local','node6','aa','mp4','mobi','gif','zip','xml','docx','xls','php','c']
    pattern = r':\d+$'
    filtered = []
    reserved = []
    for url in dataframe:
        i = 0
        if url[:5] == 'only-':
            filtered.append([url,'0'])
            continue
        spilt_url = url.split('.')
        if len(spilt_url[-1]) > 6 or len(spilt_url[-1]) == 1:#顶级域名长度大于6或者等于1的打上标签0，放入filtered中
            filtered.append([url,'0'])
            continue
        if re.search(pattern, url):#判断url是否带端口
            if url[-3:] == ':80' or url[-4:] == ':443':#判断端口是否为80或443
                j = 0
                for white_word in white_list:#判断二级域名是否在黑名单中，是j+1
                    if len(spilt_url) == 2:
                        if white_word == spilt_url[-2]:
                            j += 1
                    elif len(spilt_url) > 2:
                        if white_word == spilt_url[-2] or white_word == spilt_url[-3]:
                            j += 1
                if j == 0:#如果j为0，说明url不在黑名单中，加入到Reserved中
                    reserved.append([url,'0'])
                else:#如果j不为0，说明url在黑名单中，打上标签0，放入filtered中
                    filtered.append([url,'0'])
            else:#端口不是的话打上标签0，放入filtered中
                filtered.append([url,'0'])
        else:#不带端口的话进入这里
            for suffix in suffixs:#判断url是否以文件后缀结尾
                if suffix.upper() == spilt_url[-1].upper():#判断文件后缀是否在suffixs中，是i+1
                    i += 1
            if i == 0:#如果i为0，说明url不是以文件后缀结尾的，开始判断是否在黑名单中
                j = 0
                for white_word in white_list:#判断二级域名是否在黑名单中，是j+1
                    if len(spilt_url) == 2:
                        if white_word == spilt_url[-2]:
                            j += 1
                    elif len(spilt_url) > 2:
                        if white_word == spilt_url[-2] or white_word == spilt_url[-3]:
                            j += 1
                if j == 0:#如果j为0，说明url不在黑名单中，加入到Reserved中
                        reserved.append([url,'0'])
                else:#如果j不为0，说明url在黑名单中，打上标签0，放入filtered中
                    filtered.append([url,'0'])
            else:#如果i不为0，说明url是以文件后缀结尾的，打上标签0，放入filtered中
                filtered.append([url,'0'])
    filtered_df: pd.DataFrame = df[df['url'].isin([i[0] for i in filtered])]
    reserved_df: pd.DataFrame = df[df['url'].isin([i[0] for i in reserved])]
    return filtered_df, reserved_df


# 无法访问的黑名单
def black_list(text: str) -> bool:
    """
    判断是否为无法访问的黑名单
    :param text: str || 待判断文本
    :return: bool || 是否为无法访问的黑名单
    """
    ban = ['您无权使用所提供的凭据','该域名已过期','页面访问的地区不在服务范围','无法浏览网页','网站请求出错','域名可转让出售','您的节点套餐到期','网站维护中非常抱歉','网关错误','正在对内容进行审核','验证码安全验证','站点已暂停','无法访问此网站','进入官网浏览器寰宇浏览器','正在进入网站','站点维护','网站正在建设中','无法打开访问页面','拖动滑块','没有找到','一口价','购买此域名','域名即将停用','域名到期','域名已到期','域名已经到期','域名续费','域名转让','域名出售','域名正在出售','正在底价出售中','域名出租','此域名可以出售','域名不存在','域名未配置','域名未启用','端口未接入','端口未开放','端口未绑定','购买该域名','当前域名未绑定','资源不可用','检查您的连接安全性','恭喜站点创建成功','国家反诈中心工信部','站点创建成功','本页面由系统自动生成','域名不存在','浏览器打开隐藏显示信息','网络错误请求失败','域名可以转让','尚未进行备案','网站请求超时','您访问的页面不存在','网页暂时无法访问','网络测速温馨提示','下面的数字给它取消','夸克专用浏览器','腾讯云域名注册']
    for i in ban:
        if i in str(text):
            return True
    return False


# 词汇过滤器
def filter(text: str) -> str:
    """
    词汇过滤器
    :param text: str || 待过滤文本
    :return: str || 过滤后文本
    """
    ret:str = str(text)
    if '公司' in str(text):
        text_list = text.split('公司')
        for i in range(len(text_list)):
            text_list[i] = text_list[i][:-12] if i < len(text_list) - 1 else text_list[i]
        ret = ''.join(text_list)
    return ret


# 从dataframe中批量处理
def batch_preprocess(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """
    从dataframe中批量处理
    :param df: pd.DataFrame || 待处理的dataframe
    :return: tuple[pd.DataFrame, int] || 处理后的dataframe和无效的数据量
    """
    count:int = len(df)
    df['text'] = df['text'].apply(lambda x: '' if black_list(x) else x)
    df['text'] = df['text'].apply(filter)
    df['text'] = df['text'].apply(lambda x: '' if len(x) < 30 else x) 
    df = df[df['text'] != '']
    invalid:int = count - len(df)
    return df, invalid

