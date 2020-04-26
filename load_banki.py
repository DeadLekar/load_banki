import requests
import sqlite3 as lite
import time
import datetime
from paths import *

class NewsGetter:
    conn = None
    c = None
    CURR_YEAR = str(datetime.datetime.now().year)
    START_POS = 'widget__date margin-top-medium'
    END_POS = 'news-pagination'
    URL_MASK = 'https://www.banki.ru/news/lenta/page{}/'

    def __init__(self, _conn):
        self.conn = _conn
        self.c = self.conn.cursor()

    def get_html(self, url):
        r = requests.get(url)
        start_pos = r.text.find(self.START_POS)
        end_pos = r.text.find(self.END_POS)
        return r.text[start_pos:end_pos]

    def get_substr(self, text, text_before, text_after):
        start_pos = text.find(text_before) + len(text_before)
        end_pos = text.find(text_after, start_pos)
        return text[start_pos:end_pos]

    def get_news(self, month_num):
        if len(month_num) == 1:
            month_num = '0' + month_num

        cnt_pages = 1
        flg_finish = False
        while 1:
            text = self.get_html(self.URL_MASK.format(cnt_pages))
            days_list = text.split('<time>')
            days_list.remove(days_list[0])
            for day in days_list:
                if day[3:10] == month_num + '.' + self.CURR_YEAR:
                    pub_day = day[:10]
                    news = day.split('text-list-date')
                    news.remove(news[0])
                    for news_item in news:
                        news_item_data_list = news_item.split('class=')
                        link = 'https://www.banki.ru' + self.get_substr(news_item_data_list[0], '="', '"')
                        title = self.get_substr(news_item_data_list[1], '<span>', '</span>').strip()
                        pub_time = self.get_substr(news_item_data_list[0], '>', '<')
                        print('{};{};{};{}'.format(pub_day, pub_time, link, title))
                else:
                    flg_finish = True
                    break
            if flg_finish: break
            cnt_pages += 1


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

conn = lite.connect(db_path + DB_NAME)
# seeker = LinksSeeker(conn)
news_getter = NewsGetter(conn)
news_getter.get_news('04')





