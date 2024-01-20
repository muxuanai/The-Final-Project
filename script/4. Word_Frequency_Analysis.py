import os
import pandas as pd
import jieba
import re
import emoji
from collections import Counter
from googletrans import Translator


def generate_word_cloud(text, stopwords, output_file):
    # Tokenize the text
    words = jieba.lcut(text, cut_all=False)

    # Calculate word frequencies
    word_freq = Counter([word for word in words if word not in stopwords])

    # Generate word cloud
    word_freq_df = pd.DataFrame(word_freq.most_common(), columns=['Word', 'Frequency'])

    # Remove rows with only one Chinese character or only numbers
    word_freq_df = word_freq_df[word_freq_df['Word'].apply(lambda x: len(re.findall(u'[\u4e00-\u9fa5]', x)) > 1 and not x.isdigit())]

    # Take the top 15 result
    top_15_words = word_freq_df.head(15)

    if os.path.exists(output_file):
        os.remove(output_file)
        print(f'Deleting existing file: {output_file}')

    top_15_words.to_csv(output_file, index=False, encoding='utf_8_sig')


def translate_text(text, target_language='en'):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text

def translate_csv(input_csv_path):
    df = pd.read_csv(input_csv_path)
    print('Translation in progress')

    df['Word Translation'] = df['Word'].apply(translate_text)
    df['Word Translation'] = df['Word Translation'].str.lower()

    # Save the translated data
    df.to_csv(input_csv_path, index=False, encoding='utf_8_sig')
    print('The process is accomplished.')

def generate_word_frequency(input_file, output_file, stopwords_file, additional_stopwords=None, custom_phrases=None):
    df = pd.read_csv(input_file)

    # Merge text content
    text = ' '.join(df['Contents'])

    # Remove punctuation, special characters, and emoji
    text = re.sub(r'[^\w\s]', '', text)
    text = emoji.demojize(text)
    text = re.sub(r':\S+:', '', text)

    # Set custom phrases
    if custom_phrases:
        for phrase in custom_phrases:
            jieba.add_word(phrase)

    #  Set stopwords
    my_stopwords = [line.strip() for line in open(stopwords_file, 'r', encoding='utf_8_sig').readlines()]
    if additional_stopwords:
        my_stopwords += additional_stopwords

    # Generate word cloud
    generate_word_cloud(text, my_stopwords, output_file)


additional_stopwords_articles = ['年轻人', '寺庙', '媒体', '不上', '现在', '不能', '一种', '不是', '知道', '没有', '很多', '上香']
generate_word_frequency('Wechat_Articles.csv', 'Frequency_Articles.csv', 'hit_stopwords.txt',
                        additional_stopwords_articles)
translate_csv('Frequency_articles.csv')


additional_stopwords_posts = ['年轻人', '寺庙', '没有', '一种', '不是', '很多', '现在', '觉得', '可能', '越来越', '已经', '北京', '人们', '真的', '不能', '媒体', '知道', '看到']
generate_word_frequency('Weibo_Posts.csv', 'Frequency_Posts.csv', 'hit_stopwords.txt',
                        additional_stopwords_posts)
translate_csv('Frequency_posts.csv')
