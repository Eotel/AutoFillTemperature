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
    t_f = round(np.random.normal(
        loc=l_f,
        scale=dev
    ), 1)

    if t_f < t_min or t_max < t_f:
        t_f = l_f
    return t_f


# ファイルがなければ作成し，csvファイルに体温と日付のログを残す
def save_log_to_csv(row):
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

            # 本日の日付を入力
            browser.find_element(By.XPATH, "//input[@class='office-form-question-textbox form-control "
                                           "office-form-theme-focus-border border-no-radius "
                                           "datepicker']").click()
            if date == "Today":
                browser.find_element(By.CLASS_NAME, "picker__button--today").click()
                dt_now = datetime.datetime.now()
                row_log.append(dt_now.strftime('%Y/%m/%d'))
            else:
                browser.find_element(By.XPATH,
                                     "//input[@class='office-form-question-textbox form-control "
                                     "office-form-theme-focus-border border-no-radius datepicker']").send_keys(date)
                browser.find_element(By.XPATH, "//button[@class='picker__button--close']").click()
                row_log.append(date)

            # 登校前か帰宅後か指定して次へ
            if time == 'pm' or i == 1:
                browser.find_element(By.XPATH, "//input[@value='帰宅（帰寮）後']").click()
                row_log.append('pm')
            elif time == 'am' or i == 0:
                browser.find_element(By.XPATH, "//input[@value='登校前・休日朝']").click()
                row_log.append('am')
            browser.find_element(By.XPATH, "//button[@title='次へ']").click()

            # 体温を入力
            if time == 'am':
                t = temps[0]
                isComplete = True
            elif time == 'pm':
                t = temps[1]
                isComplete = True
            browser.find_element(By.XPATH,
                                 "//input[@class='office-form-question-textbox office-form-textfield-input form-control "
                                 "office-form-theme-focus-border border-no-radius']").send_keys(str(t))
            row_log.append(t)

            # 体調を入力
            browser.find_element(By.XPATH, "//input[@value='良好']").click()

            # 部活動を入力
            if time == 'pm' or i == 1:
                browser.find_element(By.CLASS_NAME, "select-placeholder").click()
                browser.find_element(By.XPATH, "//*[text()=\"参加なし\"]").click()

            # フォームを送信してタブを閉じる
            browser.find_element(By.XPATH, "//button[@title='送信']").click()
            sleep(1)

            row_log.append(datetime.datetime.now())
            save_log_to_csv(row_log)
            sleep(1)

            browser.quit()
        else:
            break

