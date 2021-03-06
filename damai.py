# -*- coding: utf-8 -*-

import os
import time
import pickle
import winsound
import configparser
from time import sleep
from selenium import webdriver

config = configparser.RawConfigParser()
config.read("config.ini", encoding="utf-8")
target_url = config.get("config", "url")
ticket_number = config.get("config", "number")

# 大麦网主页
damai_url = "https://www.damai.cn/"
# 登录页
login_url = "https://passport.damai.cn/login?ru=https%3A%2F%2Fwww.damai.cn%2F"

name = "unused"
phone = "unused"

class Concert(object):
    def __init__(self):

        self.status = 0
        self.login_method = 1

    def set_cookie(self):
        self.driver.get(damai_url)
        print("###请点击登录###")
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:
            sleep(1)
        print("###请扫码登录###")
        while self.driver.title == '大麦登录':
            sleep(1)
        print("###扫码成功###")
        pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
        print("###Cookie保存成功###")
        self.driver.get(target_url)

    def get_cookie(self):
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))  # 载入cookie
            for cookie in cookies:
                cookie_dict = {
                    'domain': '.damai.cn',
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    "expires": "",
                    'path': '/',
                    'httpOnly': False,
                    'HostOnly': False,
                    'Secure': False}
                self.driver.add_cookie(cookie_dict)
            print('###载入Cookie###')
        except Exception as e:
            print(e)

    def login(self):
        if self.login_method == 0:
            self.driver.get(login_url)
            print('###开始登录###')

        elif self.login_method == 1:
            if not os.path.exists('cookies.pkl'):
                self.set_cookie()
            else:
                self.driver.get(target_url)
                self.get_cookie()

    def enter_concert(self):
        print('###打开浏览器，进入大麦网###')
        self.driver = webdriver.Chrome()
        self.login()
        self.driver.refresh()
        self.status = 2
        print("###登录成功###")

    def choose_ticket(self):
        if self.status == 2:
            self.num = 1

            print("=" * 30)
            print("###开始进行日期及票价选择###")
            while self.driver.title.find('确认订单') == -1:
                buybutton = self.driver.find_element_by_class_name('buybtn').text
                if buybutton == "即将开抢":
                    self.status = 2
                    self.driver.get(target_url)
                    print('###抢票未开始，刷新等待开始###')
                    continue

                elif buybutton == "立即预定":
                    self.driver.find_element_by_class_name('buybtn').click()
                    self.status = 3
                    self.num = 1

                elif buybutton == "立即购买":
                    self.driver.find_element_by_class_name('buybtn').click()
                    self.status = 4

                elif buybutton == "选座购买":
                    self.driver.find_element_by_class_name('buybtn').click()
                    self.status = 5

                elif buybutton == "提交缺货登记":
                    print('###抢票失败，请手动提交缺货登记###')
                    break

                title = self.driver.title
                if title == "确认订单":
                    self.check_order()

                elif self.status == 5:
                    print("###请自行选择位置和票价###")
                    break

    def check_order(self):
        if self.status in [3, 4]:
            if(ticket_number == '1'):
                stat = self.driver.find_elements_by_xpath(
                            '//div[@id="confirmOrder_1"]/div[2]/div[2]/div[1]/div[1]/label/span/input')[
                            0]
                while(stat.get_attribute('aria-checked') == 'false'):
                    time.sleep(0.5)
                    stat = self.driver.find_elements_by_xpath(
                        '//div[@id="confirmOrder_1"]/div[2]/div[2]/div[1]/div[1]/label/span/input')[
                        0]
                    self.driver.find_elements_by_xpath(
                            '//div[@id="confirmOrder_1"]/div[2]/div[2]/div[1]/div[1]/label/span/input')[
                            0].click()
                    print(stat.get_attribute('aria-checked'))

            print('###不选择订单优惠###')
            print('###请在付款完成后下载大麦APP进入订单详情页申请开具###')

            time.sleep(1)
            self.driver.find_elements_by_xpath('//div[@class = "w1200"]//div[2]//div//div[9]//button[1]')[0].click()

    def finish(self):
        self.driver.quit()


if __name__ == '__main__':
    con = Concert()
    con.enter_concert()
    con.choose_ticket()

    duration = 10000
    freq = 600
    while(1):
        winsound.Beep(freq, duration)