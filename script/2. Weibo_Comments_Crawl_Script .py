import os
import requests
import pandas as pd
import datetime
from time import sleep
import random
from fake_useragent import UserAgent
import re


def trans_time(v_str):
    """Convert GMT time to standard time"""
    gmt_format = '%a %b %d %H:%M:%S +0800 %Y'
    timearray = datetime.datetime.strptime(v_str, gmt_format)
    ret_time = timearray.strftime("%Y-%m-%d %H:%M:%S")
    return ret_time


def tran_gender(gender_tag):
    """Complete the words of gender"""
    if gender_tag == 'm':
        return 'male'
    elif gender_tag == 'f':
        return 'female'
    else:  # -1
        return 'unknown'


def get_comments(v_weibo_ids, v_comment_file, v_max_page):
    """
    acquire comments
    :param v_weibo_ids: a list consisting of weibo articles(id) I want to get comments on
    :param v_comment_file: a file consisting of weibo comments from different articles
    :param v_max_page: the maximum page
    :return: None
    """
    for weibo_id in v_weibo_ids:
        print('Crawling comments for Weibo ID: {}'.format(weibo_id))
        max_id = '0'
        max_id_type = '0'
        # start crawling comments
        for page in range(1, v_max_page + 1):
            wait_seconds = random.uniform(0, 1)  # # set the waiting time
            print('start waiting {} seconds'.format(wait_seconds))
            sleep(wait_seconds)
            print('start crawling the {} pages'.format(page))
            if page == 1:  # the first page without max_id
                url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type=0'.format(weibo_id, weibo_id)
            else:  # non-first page requires max_id
                if str(max_id) == '0':  # If max_id is 0, it means there is no next page
                    print('max_id is 0, break now')
                    break
                url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type={}&max_id={}'.format(weibo_id,
                                                                                                         weibo_id,
                                                                                                         max_id_type,
                                                                                                         max_id)
            # send requests
            ua = UserAgent()
            headers = {
                "user-agent": ua.random,
                "cookie": "WEIBOCN_FROM=1110006030; SUB=_2A25In9oODeRhGeBG7FYX-SvPzz-IHXVr1VPGrDV6PUJbkdANLWL7kW1NQez5q1-q315h2Sv1KhXTwnTxV3aNh6GJ; MLOGIN=1; _T_WM=11331743659; XSRF-TOKEN=7c087d; M_WEIBOCN_PARAMS=oid%3D4881800520536418%26luicode%3D20000061%26lfid%3D4881800520536418%26fid%3D102803%26uicode%3D10000011",
                "accept": "application/json, text/plain, */*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "zh-CN,zh; q=0.9,en-us; q=0.8,en; q=0.7",
                "referer": "https://m.weibo.cn/detail/{}".format(weibo_id),
                "x-requested-with": "XMLHttpRequest",
                "mweibo-pwa": "1"
            }
            r = requests.get(url, headers=headers)
            print(r.status_code)
            print(r.json())
            try:
                max_id = r.json()['data']['max_id']  # Get max_id for next page request
                max_id_type = r.json()['data']['max_id_type']
                datas = r.json()['data']['data']
            except Exception as e:
                print('excepted: ' + str(e))
                print(r.json())
                continue
            print('Comment Numbers:', len(datas))

            page_list = []  # comment pages
            id_list = []  # comment ID
            text_list = []  # comment contents
            time_list = []  # comment time
            like_count_list = []  # like number
            source_list = []  # IP location
            author_name_list = []  # commentator name
            author_id_list = []  # commentator ID
            author_gender_list = []  # commentator gender
            follow_count_list = []  # follow number
            followers_count_list = []  # followers number

            for data in datas:
                page_list.append(page)
                id_list.append(data['id'])
                dr = re.compile(r'<[^>]+>', re.S)  # clean data
                text2 = dr.sub('', data['text'])
                text_list.append(text2)
                time_list.append(trans_time(v_str=data['created_at']))
                like_count_list.append(data['like_count'])
                source_list.append(data['source'])
                author_name_list.append(data['user']['screen_name'])
                author_id_list.append(data['user']['id'])
                author_gender_list.append(tran_gender(data['user']['gender']))
                follow_count_list.append(data['user']['follow_count'])
                followers_count_list.append(data['user']['followers_count'])

            df = pd.DataFrame(
                {
                    'Max_id': max_id,
                    'Weibo ID': [weibo_id] * len(time_list),
                    'Comment Pages': page_list,
                    'Comment ID': id_list,
                    'Posting Time': time_list,
                    'Like Counts': like_count_list,
                    'IP Location': source_list,
                    'Author Name': author_name_list,
                    'Author ID': author_id_list,
                    'Author Gender': author_gender_list,
                    'Follow Counts': follow_count_list,
                    'Followers Counts': followers_count_list,
                    'Contents': text_list,
                })
            if os.path.exists(v_comment_file):  # If the file exists, no more headers are set
                header = False
            else:  # otherwise, set the csv file header
                header = True
            # save files
            df.to_csv(v_comment_file, mode='a+', index=False, header=header, encoding='utf_8_sig')
            print('The result is saved successfully: {}'.format(v_comment_file))


if __name__ == '__main__':
    weibo_id_list = ['4881800520536418', '4881672200262337', '4881713090791295', '4881753259640752', '4882155806919680',
                     '4881778361501658', '4881703447300725', '4881722925913216', '4881750327296526', '4881718631204137',
                     '4882135292577341', '4881831117718143']  # Specify the ID of Weibo to be crawled
    max_page = 30  # set pages
    comment_file = 'Weibo_Comments_Raw.csv'
    # If the file exists, delete it first
    if os.path.exists(comment_file):
        print('Deleting existing file: {}'.format(comment_file))
        os.remove(comment_file)
    # call the function
    get_comments(v_weibo_ids=weibo_id_list, v_comment_file=comment_file, v_max_page=max_page)