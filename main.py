# -*- coding: utf-8 -*-
"""

Created on Thu Feb 20 23:12:25 2020

@author: Tim
"""
import requests
import bs4
import time
import datetime
import sqlite3


def isValidDate(theDate):  # 確認日期格式是否正確
    try:
        time.strptime(theDate, '%Y-%m-%d')
    except ValueError:
        return False
    else:
        return True


def checkDate():  # 檢查輸入日期範圍
    dateRange = input("輸入欲尋找貼文範圍日期  (ex:20200226-20200227):  ")
    while True:
        if not dateRange:
            dateRange = input('請重新輸入:')

        if dateRange and '-' not in dateRange:
            dateRange = input('日期格式須包含"-"，請重新輸入:')

        if len(dateRange.split('-')[0]) and len(dateRange.split('-')[1]) != 8:
            dateRange = input('日期輸入錯誤，請重新輸入:')

        elif len(dateRange.split('-')[0]) and len(dateRange.split('-')[1]) == 8:
            date1 = dateRange.split('-')[0]
            date2 = dateRange.split('-')[1]

            if not date1.isdigit() or not date2.isdigit():
                dateRange = input('日期格式非全數字，請重新輸入:')

            elif date1.isdigit() and date2.isdigit():
                date1_array = str(date1[0:4] + '-' + date1[4:6] + '-' + date1[6:8])
                date2_array = str(date2[0:4] + '-' + date2[4:6] + '-' + date2[6:8])

                if isValidDate(date1_array) and isValidDate(date2_array):
                    if (int(datetime.datetime.now().year) - 1 <= int(date1[0:4])) and (
                            int(datetime.datetime.now().year) - 1 <= int(date2[0:4])) and (
                            int(datetime.datetime.now().year) <= int(date2[0:4])):
                        date1_timeArray = time.strptime(date1_array, "%Y-%m-%d")
                        date2_timeArray = time.strptime(date2_array, "%Y-%m-%d")
                        date1_stamp = int(time.mktime(date1_timeArray))
                        date2_stamp = int(time.mktime(date2_timeArray))

                        if date1_stamp <= date2_stamp:
                            date2_stamp += 86400  # 當天日期也需搜尋
                            break
                        else:
                            dateRange = input('後面日期不得小於前面日期，請重新輸入:')
                    else:
                        dateRange = input('搜尋範圍最多一年內，請重新輸入:')
                else:
                    dateRange = input('日期 年、月、日 格式錯誤，請重新輸入:')
    return date1_stamp, date2_stamp


def setDatabase():  # 若需以多台機器同時爬蟲，則資料庫建議採用大型伺服器資料庫，如MySQL、Redis或MongoDB等...
    conn = sqlite3.connect("datafile.db")
    cursor = conn.cursor()   # 如果資料故不存在則建立TABLE
    cursor.execute("""create table if not exists pttdata
    (id integer primary key unique, 
    authorId text, 
    authorName text,
    title text,
    publishedTime,
    content text,
    canonicalUrl text,
    createdTime text,
    commentId text,
    commentContent text,
    commentTime text)""")
    return conn, cursor


def main():
    date1_stamp, date2_stamp = checkDate()  # 設定輸入範圍

    conn, cursor = setDatabase()  # 建立資料庫
    # 存取所有時間範圍內之url
    # 若需爬取整個ptt看板只需先爬過一次全看板URL再以迴圈進行即可，這邊先以Gossiping測試
    url = 'https://www.ptt.cc/bbs/Gossiping/index.html'
    ppthtml = requests.get(url, cookies={'over18': '1'})  # 設置 cookie用以進入大部分看板
    objSoup = bs4.BeautifulSoup(ppthtml.text, 'html.parser')
    pttdivs = objSoup.find_all('div', 'r-ent')  # 尋找本頁文章
    checkNum = 0  # 設置日期範圍確認數
    urls = []  # 創立矩陣存放範圍時間內文章url
    tempurls = []
    bbsname = 'https://www.ptt.cc'

    while True:  # 直至沒有欲抓取文章則跳出迴圈
        for p in pttdivs:
            if p.find('a'):
                tempdivs = p.find('div', 'date')
                dateArray = time.strptime(str(datetime.datetime.now().year) + '/' + tempdivs.text.strip(), "%Y/%m/%d")
                date_stamp = int(time.mktime(dateArray))

                if date1_stamp <= date_stamp <= date2_stamp:
                    href = bbsname + p.find('a')['href']  # 文章連結
                    tempUrl = cursor.execute("select * from pttdata where canonicalUrl like :url", {"url": href})  
                    if not tempUrl.fetchall():  # 遇已擷取過網址則跳過
                        tempurls.append(href)
                    checkNum += 1
        tempurls.reverse()
        urls.extend(tempurls)  # 確保文章最新順序

        if checkNum == 0:  # 確認已無範圍日期內文章
            break
        else:
            nextpage = objSoup.find('div', 'btn-group btn-group-paging')
            nexturl = bbsname + nextpage.find_all('a')[1]['href']

            time.sleep(2)  # ''' 避免requests過於頻繁 '''

            ppthtml = requests.get(nexturl, cookies={'over18': '1'})  # 設置 cookie
            objSoup = bs4.BeautifulSoup(ppthtml.text, 'html.parser')
            pttdivs = objSoup.find_all('div', 'r-ent')  # 尋找下頁文章

            print('下一頁URL:', nexturl, '  本頁URL抓取數:', checkNum)  # ''' 觀察目前爬蟲進度以及抓取文章數 '''

            checkNum = 0  # 設置日期範圍確認數(初始化)
            tempurls = []  # 暫存矩陣初始化

    print('時間範圍內所有文章URL存取完畢，解析中...\n')
    
    # 抓取urls內所有連結中所需資料
    articles = []  # 資料矩陣
    dataNum = 0  # 資料計數
    for eachURL in urls:

        time.sleep(2)  # ''' 避免requests過於頻繁 '''

        eachhtml = requests.get(eachURL, cookies={'over18': '1'})  # 設置 cookie
        eachSoup = bs4.BeautifulSoup(eachhtml.text, 'html.parser')
        eachdivs = eachSoup.find('div', id='main-container')
        items = eachdivs.find_all('div', 'article-metaline')
        if items:
            title = items[1].find('span', 'article-meta-value').text  # 標題
            authorId = items[0].find('span', 'article-meta-value').text.split('(')[0]  # 作者Id
            authorName = items[0].find('span', 'article-meta-value').text.split('(')[1].split(')')[0]  # 切割出作者暱稱
            canonicalUrl = eachURL  # 文章連結
            arttime = items[2].find('span', 'article-meta-value').text  # 文章發布日期
            publishedTime = eachURL.split('M.')[1].split('.A')[0]  # 文章發布時間
            content = eachdivs.text.split(arttime)[-1].split('--')[0]  # 切割出內文
            pttpush = eachdivs.find_all('div', 'push')  # PTT推文
            pushNum = 0
            for push_item in pttpush:
                if push_item.text != '檔案過大！部分文章無法顯示':  # 跳脫推文過多無法顯示問題
                    topiclist = list(push_item)
                    commentId = topiclist[1].text
                    commentContent = topiclist[2].text.split(':')[-1]
                    push_time = topiclist[3]
                    if len(push_time.text) > 13:  #  推文時間避免IP部分(包含\n共13個字元)
                        push_timeStr = arttime.split(' ')[-1].strip() + '-' + push_time.text[-13:].strip('\n').strip()
                    else:
                        push_timeStr = arttime.split(' ')[-1].strip() + '-' + push_time.text.strip('\n').strip()
                    push_timeArray = time.strptime(push_timeStr, "%Y-%m/%d %H:%M")
                    commentTime = int(time.mktime(push_timeArray))
                    createdTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                    # 寫入資料庫
                    cursor.execute("""insert into pttdata (authorId, authorName, title, publishedTime, content, 
                    canonicalUrl, createdTime, commentId, commentContent, commentTime)
                    values (?, ?, ?, ?, ?, ? ,? ,? ,? ,?)""",
                                   (authorId, authorName, title, publishedTime, content, canonicalUrl, createdTime,
                                    commentId, commentContent, commentTime))
                    conn.commit()
                    dataNum += 1
                    pushNum += 1
                    print('資料儲存成功!目前完成{}筆資料，其文章標題為{}，第{}則推文'.format(dataNum, title, pushNum))

                    articles.append({'authorId': authorId,
                                     'authorName': authorName,
                                     'title': title,
                                     'publishedTime': publishedTime,
                                     'content': content,
                                     'canonicalUrl': canonicalUrl,
                                     'createdTime': createdTime,
                                     'commentId': commentId,
                                     'commentContent': commentContent,
                                     'commentTime': commentTime})
    conn.close()  # 關閉資料庫連結

    print('資料全數完成...顯示中')
    print('總資料數量 = ', len(articles))

    count = 0
    for article in articles:
        count += 1
        print('資料編號:', count)
        print('文章作者:', article['authorId'])
        print('作者暱稱:', article['authorName'])
        print('文章標題:', article['title'])
        print('發布時間:', article['publishedTime'])
        print('內文:', article['content'])
        print('文章連結:', article['canonicalUrl'])
        print('建立時間:', article['createdTime'])
        print('推文者ID:', article['commentId'])
        print('完整推文:', article['commentContent'])
        print('推文時間:', article['commentTime'])
        print('\n')


if __name__ == '__main__':
    main()
