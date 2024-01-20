import os
import requests
import pandas as pd
import datetime
from time import sleep
import random
import re
from jsonpath import jsonpath

headers = {
	"User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36",
	"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	"accept-encoding": "gzip, deflate, br"
}


def trans_time(v_str):
	"""Transform GMT time to standard time"""
	gmt_format = '%a %b %d %H:%M:%S +0800 %Y'
	timearray = datetime.datetime.strptime(v_str, gmt_format)
	ret_time = timearray.strftime('%Y-%m-%d %H:%M:%S')
	return ret_time


def tran_gender(gender_tag):
	"""Complete the words of gender"""
	if gender_tag == 'm':
		return 'male'
	elif gender_tag == 'f':
		return 'female'
	else:  # -1
		return 'unknown'


def get_long_text(v_id):
	"""acquire long text of some weibo"""
	url = 'https://m.weibo.cn/statuses/extend?id=' + str(v_id)
	r = requests.get(url, headers=headers)
	json_data = r.json()
	long_text = json_data['data']['longTextContent']
	dr = re.compile(r'<[^>]+>', re.S)
	long_text2 = dr.sub('', long_text)
	return long_text2


def get_weibo_list(v_keyword, v_max_page, v_post_file):
	"""
	acquire Weibo lists
	:param v_keyword: search keyword
	:param v_max_page: the maximum page
	:param v_post_file: save post file
	:return None
	"""

	for page in range(2, v_max_page + 1):  # the first page contains advertisement
		wait_seconds = random.uniform(0, 1)  # set the waiting time
		print('start waiting {} seconds'.format(wait_seconds))
		sleep(wait_seconds)
		print('start crawling the {} pages'.format(page))
		url = 'https://m.weibo.cn/api/container/getIndex'
		params = {
			"containerid": "100103type=1&q={}".format(v_keyword),
			"page_type": "searchall",
			"page": page
		}
		# send requests
		r = requests.get(url, headers=headers, params=params)
		print(r.status_code)
		print(r.json())
		# parse data
		cards = r.json()["data"]["cards"]
		print(len(cards))
		status_province_list = []
		status_country_list = []

		for card in cards:
			# IP location: province
			try:
				status_province = card['card_group'][0]['mblog']['status_province']
				status_province_list.append(status_province)
			except:
				status_province_list.append('')
			# IP location: country
			try:
				status_country = card['card_group'][0]['mblog']['status_country']
				status_country_list.append(status_country)
			except:
				status_country_list.append('')

		# contents
		text_list = jsonpath(cards, '$..mblog.text')
		# data cleaning
		dr = re.compile(r'<[^>]+>', re.S)
		text2_list = []
		print('text_list is:')
		print(text_list)
		if text_list is False:  # If the Weibo content is not obtained, enter the next cycle
			break
		if type(text_list) == list and len(text_list) > 0:
			for text in text_list:
				text2 = dr.sub('', text)
				print(text2)
				text2_list.append(text2)

		# posting time
		time_list = jsonpath(cards, '$..mblog.created_at')
		time_list = [trans_time(v_str=i) for i in time_list]
		# author
		author_list = jsonpath(cards, '$..mblog.user.screen_name')
		# weibo ID
		id_list = jsonpath(cards, '$..mblog.id')
		# author gender
		gender_list = jsonpath(cards, '$..mblog.user.gender')
		gender_list = [tran_gender(gender_tag=i) for i in gender_list]
		# follow count
		follow_count = jsonpath(cards, '$..mblog.user.follow_count')
		# followers count
		followers_count = jsonpath(cards, '$..mblog.user.followers_count')

		# test whether long text exists
		islongtext_list = jsonpath(cards, '$..mblog.isLongText')
		idx = 0
		for i in islongtext_list:
			if i == True:
				long_text = get_long_text(v_id=id_list[idx])
				text2_list[idx] = long_text
			idx += 1

		# repost number
		reposts_count_list = jsonpath(cards, '$..mblog.reposts_count')
		# comment number
		comments_count_list = jsonpath(cards, '$..mblog.comments_count')
		# like number
		attitudes_count_list = jsonpath(cards, '$..mblog.attitudes_count')

		# save data
		print('id_list:', len(id_list))
		print(len(time_list))
		print(len(status_province_list))
		print(len(status_country_list))

		df = pd.DataFrame({
			'Keyword': [v_keyword] * len(id_list),
			'Pages': [page] * len(id_list),
			'Weibo ID': id_list,
			'Author Name': author_list,
			'Author Gender': gender_list,
			'Follow Counts': follow_count,
			'Followers Counts': followers_count,
			'Posting Time': time_list,
			'Repost Counts': reposts_count_list,
			'Comment Counts': comments_count_list,
			'Like Counts': attitudes_count_list,
			'IP location province': status_province_list,
			'IP location country': status_country_list,
			'Contents': text2_list
		})

		if os.path.exists(v_post_file):  # If the file exists, no more headers are set
			header = False
		else:  # otherwise, set the csv file header
			header = True
		# save files
		df.to_csv(v_post_file, mode='a+', index=False, header=header, encoding='utf_8_sig', errors='ignore')
		print('The result is saved successfully:{}'.format(v_post_file))


if __name__ == '__main__':
	# keywords list:
	# Young people don't go to class or don't work hard but only go to Buddhist temples to offer incense.
	# The media commented that young people don't go to class or don't work hard but only go to Buddhist temples to offer incense.
	# Why temple tourism suddenly became popular
	# Why do young people love to go to temples?
	# Why do young people love to visit temples?
	# Why are young people so keen on praying?
	# Why temple tourism is booming among Gen Z?
	keyword_list = ['年轻人不上学不上进只上香', '媒体评年轻人不上课不上进只上香', '为什么寺庙旅游突然火了',
	                '年轻人为什么爱去寺庙了', '年轻人为什么爱逛寺庙', '为什么年轻人热衷于祈福了',
	                '为何寺庙旅游在90后00后中爆火']
	max_search_page = 50  # set pages
	v_post_file = 'Weibo_Posts_Raw.csv'
	# If the file exists, delete it first
	if os.path.exists(v_post_file):
		os.remove(v_post_file)
		print('Deleting existing file: {}'.format(v_post_file))
	# Call the function
	for keyword in keyword_list:
		get_weibo_list(v_keyword=keyword, v_max_page=max_search_page, v_post_file=v_post_file)
