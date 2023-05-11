from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.by import By
from selenium import webdriver
import dns.resolver
import pandas as pd
import re
import time


user_agent = 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44'
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("blink-settings=imagesEnabled=false")
chrome_options.add_argument("--disable-blink-features")
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument('log-level=3')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('ignore-certificate-errors')


def dns_available(url: str) -> bool:
    """
    检查域名是否可用
    :param url: str || 待处理数据
    :return: state: bool || 是否可用
    """
    try:
        dns.resolver.query(url, 'A')
        return True
    except:
        return False


def get_text(html: str) -> str:
    """
    获取网页文本
    :param html: str || 网页源码
    :return: text: str || 网页文本
    """
    return ''.join(re.findall(r'[\u4e00-\u9fa5]', str(html)))


def single_get_html_headless(url: str) -> str:
    """
    获取网页源码
    :param url: str || 待处理数据
    :return: html: str || 网页源码
    """
    if not dns_available(url):
        return ''
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.set_page_load_timeout(20)
    try:
        driver.get(('http://' + url) if 'http' not in url else url)
        html = get_text(driver.page_source)
    except:
        driver.quit()
        return ''
    time.sleep(3)
    if len(html) < 50:
        try:
            iframe = driver.find_element(By.TAG_NAME, "iframe")
            driver.switch_to.frame(iframe)
            html = get_text(driver.page_source)
        except:
            driver.quit()
            return ''
    if len(html) < 50:
        try:
            iframe = driver.find_element(By.TAG_NAME, "frame")
            driver.switch_to.frame(iframe)
            html = get_text(driver.page_source)
        except:
            driver.quit()
            return ''
    if len(html) < 30:
        driver.quit()
        return ''
    driver.quit()
    return html


def batch_get_html_headless(urls: pd.DataFrame) -> pd.DataFrame:
    """
    批量获取网页源码
    :param urls: pd.DataFrame || 待处理数据
    :return: urls: pd.DataFrame || 处理后数据
    """
    # TypeError list indices must be integers or slices, not str,fix it
    urls_list: list = urls['url'].tolist()
    htmls_list: list = []
    with ThreadPoolExecutor(max_workers=32) as executor:
        for html in executor.map(single_get_html_headless, urls_list):
            htmls_list.append(html)
    urls.loc[:, 'text'] = htmls_list
    return urls

