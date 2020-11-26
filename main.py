import json
import os
from time import sleep

import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By

FILENAME = "settings.json"


# 正規分布で体温を計算し閾値（最小・最大）外の場合は平均値に変更する
def calc_temp(l_f):
    t_f = round(np.random.normal(
        loc=l_f,
        scale=dev
    ), 1)

    if t_f < t_min or t_max < t_f:
        t_f = l_f
    return t_f


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

    # 標準偏差の確認
    # plt.figure()
    # plt.hist(t_mng, bins=100, alpha=0.3, histtype='stepfilled', color='r')
    # plt.hist(t_evg, bins=100, alpha=0.3, histtype='stepfilled', color='b')
    # plt.show()

    for i, t in enumerate(temps):
        browser = webdriver.Chrome()

        # メールアドレスを入力
        browser.get(url)
        browser.find_element(By.ID, 'i0116').send_keys(email)
        browser.find_element(By.ID, 'idSIButton9').click()
        sleep(2)

        # パスワードを入力
        browser.find_element(By.ID, 'i0118').send_keys(pwd)
        browser.find_element(By.ID, 'idSIButton9').click()
        sleep(2)

        # サインイン状態を維持するか
        browser.find_element(By.ID, 'idSIButton9').click()
        sleep(2)

        # 本日の日付を入力
        browser.find_element(By.XPATH, "//input[@class='office-form-question-textbox form-control "
                                       "office-form-theme-focus-border border-no-radius "
                                       "datepicker']").click()
        browser.find_element(By.CLASS_NAME, "picker__button--today").click()

        # 登校前か帰宅後か指定して次へ
        if i == 0:
            browser.find_element(By.XPATH, "//input[@value='登校前']").click()
        else:
            browser.find_element(By.XPATH, "//input[@value='帰宅（帰寮）後']").click()
        browser.find_element(By.XPATH, "//button[@title='次へ']").click()
        sleep(2)

        browser.find_element(By.XPATH,
                             "//input[@class='office-form-question-textbox office-form-textfield-input form-control "
                             "office-form-theme-focus-border border-no-radius']").send_keys(str(t))

        # 体調を入力
        browser.find_element(By.XPATH, "//input[@value='良好']").click()

        # 部活動を入力
        if i == 1:
            browser.find_element(By.CLASS_NAME, "select-placeholder").click()
            browser.find_element(By.XPATH, "//*[text()=\"参加なし\"]").click()

        # フォームを送信してタブを閉じる
        browser.find_element(By.XPATH, "//button[@title='送信']").click()
        sleep(1)

        if i == 1:
            browser.close()
            browser.quit()
