#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ファイル名設定用
import configparser
import datetime
import os

# Seleniumのドライバ
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
# # Seleniumで要素の読み込みを待機するためのパッケージ類
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# BS4
from bs4 import BeautifulSoup
import codecs
import re
import requests


currentdirectory = os.path.dirname(os.path.abspath(__file__))
os.chdir(currentdirectory)
print(os.getcwd())

# 設定ファイル読み込み
inifile = configparser.ConfigParser()
inifile.read(os.path.join(currentdirectory, './setting.ini'), 'UTF-8')
togetterPageId = inifile.get('togetter', 'id')

# 定数
LOG_FILEPATH = os.path.join(currentdirectory, 'log'+datetime.datetime.now().strftime('%Y%m%d%H%M%S')+'.txt')

WAITING_TIME = 10000

togetterBaseUri = 'https://togetter.com/'
togetterPage = togetterBaseUri + 'li/' + togetterPageId + '?page='


# スクショ保存時のファイル名を生成
def get_filepath():
    now = datetime.datetime.now()
    filename = 'screen_{0:%Y%m%d%H%M%S}.png'.format(now)
    filepath = os.path.join(currentdirectory, filename)
    return filepath


def main():
    with open(LOG_FILEPATH, 'a', encoding='utf-8') as f:
        print('Start: {}'.format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=f)
        binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe')
        profile = FirefoxProfile(
            'C:\\Users\\y\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\hqterean.default')
        fox = webdriver.Firefox(firefox_profile=profile, firefox_binary=binary,
                                executable_path='C:\\geckodriver\\geckodriver.exe')
        fox.set_page_load_timeout(6000)
        try:
            fox.set_window_size(1280, 720)
            fox.get(togetterBaseUri)
        except:
            print('time out!')
            exit

        page = 0
        while True:
            page += 1
            uri = togetterPage + str(page)
            print('\tURI: {} {}'.format(uri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=f)

            ret = requests.get(uri)
            if ret.status_code == 302:
                exit
            # print('headers: ')
            # print(ret.headers)

            source = retrieve(fox, uri)
            bs = BeautifulSoup(source, 'lxml')
            for i in bs.find_all('div', class_='tweet'):
                text = i.getText()
                print(text)
                print('\t\tText\t{}'.format(text.replace('\n', '<br>')), file=f)

        # 終了時の後片付け
        fox.close()
        try:
            fox.quit()
        except:
            pass

        print('Done: {}'.format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=f)


# Seleniumを起動して認証を試行
def retrieve(fox, uri):

    # 末尾まで読み込む
    fox.get(uri)

    WebDriverWait(fox, WAITING_TIME).until(lambda fox:
        EC.presence_of_element_located((By.ID, 'more_tweet_btn')) or
        EC.presence_of_element_located((By.CLASS_NAME, 'pagenation')))

    try:
        pagenationDisplayed = fox.find_element_by_class_name('pagenation').is_displayed
    except:
        pagenationDisplayed = False

    if not pagenationDisplayed:
        WebDriverWait(fox, WAITING_TIME).until(
            EC.presence_of_element_located((By.ID, 'more_tweet_btn')))
        clickId(fox, 'more_tweet_btn')

    # ページネーションが表示されたらソースを返す
    WebDriverWait(fox, WAITING_TIME).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'pagenation')))
    # fox.save_screenshot(get_filepath())

    return fox.page_source


def clickClassName(fox, className):
    fox.find_element_by_class_name(className).click()


def clickId(fox, id):
    fox.find_element_by_id(id).click()


def clickLink(fox, text):
    fox.find_element_by_link_text(text).click()


def clickName(fox, name):
    fox.find_element_by_name(name).click()


def clickSelector(fox, selector):
    fox.find_elements_by_css_selector(selector).click()


def clickXpath(fox, xpath):
    fox.find_element_by_xpath(xpath).click()


def clearAndSendKeys(fox, name, text):
    fox.find_element_by_name(name).clear()
    fox.find_element_by_name(name).send_keys(text)


if __name__ == '__main__':
    main()

# Copyright (c) 2019 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.
