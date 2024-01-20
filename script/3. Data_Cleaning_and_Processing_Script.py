import pandas as pd
import re
import os


def clean_and_process_data(input_file, output_file, id_column):
    df = pd.read_csv(input_file, encoding='utf_8_sig')

    # remove duplicate values
    existing_df = df.drop_duplicates(subset=[id_column], keep='first')

    # remove missing values
    df_cleaned = existing_df.dropna(subset=['Contents'])

    # Remove irrelevant content
    # Irrelevant contents include:
    # 'Repost', 'Headline Article', 'Weibo Video', '"Intelligent Ticket Booking Tool (Ad)',
    # 'Destiny In Marriage', 'Wish For Good Fortune (Ad)', 'Tarot', 'Stock Market Index', 'Training', 'House Rental',
    # 'Stocks', 'Investment', 'Bank', 'Natal Chart (Ad)', 'Daily Inspiration', 'Examination', 'YaYa (A panda's name)',
    # 'Car', 'Energy', 'Postal Service', 'Starbucks'
    keywords_to_exclude = ['转发微博', '头条文章', '微博视频', '网页链接', '智行抢票神器', '姻缘', '祈福', '塔罗', '大盘', '培训',
                           '租房', '股票', '投资', '银行', '星盘', '日签', '考试', '丫丫', '汽车', '能源', '驿马', '星巴克']

    exclude_pattern = '|'.join(keywords_to_exclude)
    df_filtered = df_cleaned[~df_cleaned['Contents'].str.contains(exclude_pattern)]

    # Handle the '@' symbol
    def process_contents(content):
        content = re.sub(r'@[\w]+', '', content)
        content = re.sub(r'#.*?#', '', content)
        return content

    df_filtered['Contents'] = df_filtered['Contents'].apply(process_contents)
    df_filtered['Contents'] = df_filtered['Contents'].str.strip()

    # Remove blank rows
    df_final = df_filtered[df_filtered['Contents'].str.strip() != '']

    # save
    df_final.to_csv(output_file, mode='a', index=False, encoding='utf_8_sig')
    print(f'The data cleaning of {input_file} is completed.')


# call the function
file_list = [
    {'input_file': 'Weibo_Comments_Raw.csv', 'output_file': 'Weibo_comments.csv', 'id_column': 'User ID'},
    {'input_file': 'Weibo_Posts_Raw.csv', 'output_file': 'Weibo_posts.csv', 'id_column': 'Weibo ID'}]

for file_info in file_list:
    input_file = file_info['input_file']
    output_file = file_info['output_file']

    if os.path.exists(input_file):
        if os.path.exists(output_file):
            print('Deleting existing file: {}'.format(output_file))
            os.remove(output_file)

        clean_and_process_data(input_file=input_file, output_file=output_file, id_column=file_info['id_column'])
