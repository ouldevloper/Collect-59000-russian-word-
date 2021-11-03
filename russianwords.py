import contextlib
from logging import error
import urllib
import requests
from bs4 import BeautifulSoup,Comment
import selenium
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.support import select,events,color,ui
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as es
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from time import sleep
import urllib.request
from urllib.request import Request as request
import urllib.parse
import os
import sqlite3
#   = + _
class ScrapRussianWord(object):
    def __init__(self,url="https://en.openrussian.org/list/all",dbPath="db.db"):
        self.con = sqlite3.connect(f"{dbPath}")
        self.cur = self.con.cursor()
        self.apiUrl = "https://api.openrussian.org/read"
        self.drive  = webdriver.Firefox()
        self.drive.get(url)
        self.ruid = 1
        self.enid = 1
        self.run()

    def run(self):
            id  = 1
            while 1:
                #try:
                html = self.getContent()
                for data in self.parseHtml(html):
                    self.fillDatabase(data)
                    print(f"\r[*] {self.ruid} Done.")
                self.goNext()
                sleep(2)
                print("[*] Done.")
                #except Exception as er:
                #    print("[#] error line 39: ",er)
                    #break
    
    def getContent(self):
        try:
            element_present = es.presence_of_element_located((By.NAME, 'html'))
            WebDriverWait(self.drive, 10).until(element_present)
        except Exception as err:
            pass
        return self.drive.page_source
       
    def goNext(self):
        try:
            next =  self.drive.find_element_by_css_selector(".button.next")
            next.click()
        except Exception as er:
            raise er

    
    def downloadMp3(self,url,id):
        try:
            url = self.apiUrl+url
            with open(os.path.join("mp3/",f"word_{self.ruid}.mp3"),"wb") as file:
                content = urllib.request.urlopen(url.strip()).read()
                file.write(content)
            return True
        except Exception as er:
            raise er

    
    def parseHtml(self,html):
        #try:
        parse = BeautifulSoup(html,"html.parser")
        table = parse.find('table')
        WebDriverWait(self.drive,100).until(
            es.presence_of_all_elements_located((By.TAG_NAME,"table"))
        )
        tbody = table.find("tbody")
        WebDriverWait(self.drive,100).until(
            es.presence_of_all_elements_located((By.TAG_NAME,"tbody"))
        )
        WebDriverWait(self.drive,100).until(
            es.presence_of_all_elements_located((By.TAG_NAME,"a"))
        )
        WebDriverWait(self.drive,100).until(
            es.presence_of_all_elements_located((By.TAG_NAME,"p"))
        )
        for tr in tbody.find_all("tr"):
            data = []
            td = tr.find_all("td")[1:]
            data.append(td[0].a["href"])
            data.append(td[0].a.text)
            try:
                for p in td[1].find_all("p"):
                    data.append(p.text.strip("•"))
            except Exception as er:
                raise er
            yield data
        return True
        #except Exception as er:
        #    print("[#] error line 87: ",er)

    def fillDatabase(self,*data):
        sql1 = "insert into ruword values(?,?)"
        sql2 = "insert into enword values(?,?,?)"
        try:
            self.downloadMp3(data[0][0],self.ruid)
            self.cur.execute(sql1,(self.ruid,data[0][1]))
            self.con.commit()  
            for en in data[0][2:]:
                self.cur.execute(sql2,(self.enid,self.ruid,en))
                self.enid+=1
            self.con.commit()  
            self.ruid+=1
        except sqlite3.Error as er:
            self.con.rollback()
            raise er

        
ScrapRussianWord()


