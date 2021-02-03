import datetime
import json
import os
from time import sleep

import numpy as np
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from argparse import ArgumentParser
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

FILENAME = "settings.json"


# オプションを受け取る
def get_option():
    parser = ArgumentParser()
    parser.add_argument('-d', '--date', type=str,
                        default='Today',
                        help='Date to post, (e.g. "Today", "2020/01/12")')
    parser.add_argument('-t', '--time', type=str,
                        default='both',
                        help='Time to post, (e.g. "am", "pm", and "both")')
    return parser.parse_args()


# 正規分布で体温を計算し閾値（最小・最大）外の場合は平均値に変更する
def calc_temp(l_f):
    logger.info('体温を計算します')
    t_f = round(np.random.normal(
        loc=l_f,
        scale=dev
    ), 1)

    if t_f < t_min or t_max < t_f:
        t_f = l_f

    logger.info(f'体温：{t_f}')
    return t_f


# ファイルがなければ作成し，csvファイルに体温と日付のログを残す
def save_log_to_csv(row):
    logger.info('csvファイルにログを追記します')
    log_filename = "log.csv"
    log_path = os.path.join(os.getcwd(), log_filename)

    if not os.path.isfile(log_path):
        with open(log_path, mode='x') as f:
            label = ["Date", "Time", "Temperature", "WriteTime"]
            writer = csv.writer(f)
            writer.writerow(label)

    with open(log_path, mode='a') as f:
        writer = csv.writer(f)
        writer.writerow(row)


def Chrome():
    options = Options()
    options.add_argument('--incognito')
    # options.add_argument('--headless')
    browser = webdriver.Chrome(options=options)
    # wait = WebDriverWait(browser, 10)  # ToDo 要素が見つかるまで待機を実装する
    browser.implicitly_wait(20)  # 暗黙的に20秒間まで待つ

    return browser


def sign_in(bsr):
    logger.info('サインインします')
    # メールアドレスを入力
    bsr.find_element(By.ID, 'i0116').send_keys(email)
    bsr.find_element(By.ID, 'idSIButton9').click()

    # パスワードを入力
    bsr.find_element(By.ID, 'i0118').send_keys(pwd)
    sleep(1)
    bsr.find_element(By.ID, 'idSIButton9').click()

    # サインイン状態を維持するか
    # browser.find_element(By.ID, 'idSIButton9').click()
    bsr.find_element(By.XPATH, "//input[@value='いいえ']").click()


if __name__ == '__main__':
    # 設定ファイルを読み込み
    json_path = os.path.join(os.path.dirname(__file__), FILENAME)
    with open(json_path) as f:
        s = f.read()
    settings_dict: dict = json.loads(s)

    usr = settings_dict.get('user', 'a00000')
    dmn = settings_dict.get('domain', 'ichinoseki.kosen-ac.jp')
    pwd = settings_dict.get('password', 'hoge-fuga-piyo')
    url = settings_dict.get('url', 'https://forms.office.com/Pages/ResponsePage.aspx?id=XYP-cpVeEkWK4KezivJfyEdEHwI'
                                   '-LNRNt_LtLgm8-zFUQzJOVEtKNzIwT0JFSVEyOVpEOTcwMktDNi4u')
    mng = settings_dict.get('morning_avg', 36.0)  # 朝の体温
    evg = settings_dict.get('evening_avg', 36.5)  # 夜の体温
    dev = settings_dict.get('deviation', 0.2)  # 標準偏差
    t_min = settings_dict.get('temp_min', 35.6)  # 最低体温
    t_max = settings_dict.get('temp_max', 37.2)  # 最高体温
    email = usr + '@' + dmn

    t_mng = calc_temp(mng)
    t_evg = calc_temp(evg)
    temps = (t_mng, t_evg)

    args = get_option()
    time = args.time
    date = args.date

    isComplete = False  # 入力完了かどうか  # ログに書き込むデータ [date, time, temp, write_time]

    for i, t in enumerate(temps):
        row_log = []

        if isComplete is False:
            browser = Chrome()
            browser.get(url)
            sign_in(browser)

            # 日付の選択
            logger.info('日付を入力します')
            if date == "Today":
                logger.info('-> 今日')
                browser.find_element(
                    By.XPATH, "//input[@value='今日']").click()
                dt_now = datetime.datetime.now()
                row_log.append(dt_now.strftime('%Y/%m/%d'))
            else:
                logger.info(f'-> その他: {date}')
                browser.find_element(
                    By.XPATH, "//input[@value='その他']").click()
                browser.find_element(By.XPATH,
                                     "//input[@class='office-form-question-textbox form-control "
                                     "office-form-theme-focus-border border-no-radius datepicker']").send_keys(date)
                # browser.find_element(
                #     By.XPATH, "//button[@class='picker__button--close']").click()
                row_log.append(date)

            # 登校前か帰宅後か指定して次へ
            logger.info('時間帯を選択します')
            try:
                if time == 'pm' or i == 1:
                    logger.info('-> 帰宅（帰寮）後')
                    browser.find_element(
                        By.XPATH, "//input[@value='帰宅（帰寮）後']").click()
                    row_log.append('pm')
                elif time == 'am' or i == 0:
                    logger.info('-> 登校前・休日朝')
                    browser.find_element(
                        By.XPATH, "//input[@value='登校前・休日朝']").click()
                    row_log.append('am')
            except Exception as e:
                logger.debug("Exception: {e}".format())
                logger.debug("時間帯の選択画面でエラーが生じました")

            browser.find_element(By.XPATH, "//button[@title='次へ']").click()

            # 体調を入力
            logger.info('体調を入力します')
            try:
                logger.info('-> 良好')
                browser.find_element(By.XPATH, "//input[@value='良好']").click()
            except Exception as e:
                logger.debug("Exception: {e}".format())
                logger.debug("体調の選択画面でエラーが生じました")

            # 体温を入力
            if time == 'am':
                t = temps[0]
                isComplete = True
            elif time == 'pm':
                t = temps[1]
                isComplete = True

            logger.info('体温を入力します')
            logger.info(f'-> {t}')
            browser.find_element(By.XPATH,
                                 "//input[@class='office-form-question-textbox office-form-textfield-input form-control "
                                 "office-form-theme-focus-border border-no-radius']").send_keys(str(t))
            row_log.append(t)
            sleep(1)

            # 部活動を入力
            if time == 'pm' or i == 1:
                logger.info('部活動を入力します')
                logger.info('-> 参加なし')
                browser.find_element(
                    By.CLASS_NAME, "select-placeholder").click()
                browser.find_element(By.XPATH, "//*[text()=\"参加なし\"]").click()

            # フォームを送信してタブを閉じる
            logger.info('フォームを送信します')
            browser.find_element(By.XPATH, "//button[@title='送信']").click()
            sleep(1)

            row_log.append(datetime.datetime.now())
            save_log_to_csv(row_log)
            sleep(1)

            logger.info('ブラウザを閉じます')
            browser.quit()
        else:
            break
