import requests
import sqlite3 as lite
import time
import datetime
from paths import *

class NewsGetter:
    conn = None
    c = None
    CURR_YEAR = str(datetime.date.year)


    def __init__(self, _conn):
        self.conn = _conn
        self.c = self.conn.cursor()

    def get_news(self, month_num):
        if len(month_num) == 1:
            month_num = '0' + month_num


        pass


class LinksSeeker:
    conn = None
    c = None

    def __init__(self, _conn):
        self.conn = _conn
        self.c = self.conn.cursor()

    def get_links(self):
        links_to_seek_rows = self.c.execute("SELECT link FROM links WHERE links_cnt ISNULL").fetchall()
        for row in links_to_seek_rows:
            link = row[0]
            r = requests.get(link)
            start_pos = r.text.find("article-text")
            end_pos = r.text.find("/article", start_pos)
            text = r.text[start_pos:end_pos]

            # look for links
            cnt_all_links = text.count("www.banki.ru")
            cnt_news = text.count("banki.ru/news")
            cnt_not_news = cnt_all_links - cnt_news

            # look for widgets
            cnt_widgets_new = text.count("header-widget")
            cnt_widgets_old = text.count("BankiruNewsBundle:Widget")

            # update db
            self.c.execute("UPDATE links SET links_cnt={} WHERE link='{}'".format(cnt_not_news, link))
            self.c.execute("UPDATE links SET new_widgets_cnt={} WHERE link='{}'".format(cnt_widgets_new, link))
            self.c.execute("UPDATE links SET old_widgets_cnt={} WHERE link='{}'".format(cnt_widgets_old, link))
            conn.commit()
            print(link, cnt_not_news, cnt_widgets_new, cnt_widgets_old)
            # time.sleep(1)


db_path = get_right_path(db_paths)
DB_NAME = 'banki.db'

conn = lite.connect(db_path)
# seeker = LinksSeeker(conn)
news_getter = NewsGetter(conn)
news_getter.get_news('04')





