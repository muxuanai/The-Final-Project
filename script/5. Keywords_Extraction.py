import pandas as pd
import jieba
import jieba.analyse
import re
import emoji
import os
from wordcloud import STOPWORDS
from googletrans import Translator


def extract_keywords(text, output_file, top_k=31, remove_adverbs=True, remove_keywords=None):
    #  Extract keywords
    if remove_adverbs:
        tags = jieba.analyse.extract_tags(text, topK=top_k, withWeight=True,
                                          allowPOS=('n', 'nr', 'nz', 'ns', 'nt'))
    else:
        tags = jieba.analyse.extract_tags(text, topK=top_k, withWeight=True)

    # Filter out specified keywords to remove
    if remove_keywords:
        tags = [tag for tag in tags if tag[0] not in remove_keywords]

    keywords_df = pd.DataFrame(tags, columns=['Keyword', 'Weight'])

    if os.path.exists(output_file):
        os.remove(output_file)
        print('Deleting existing file: {}'.format(output_file))

    keywords_df.to_csv(output_file, index=False, encoding='utf_8_sig')
    print('Top {} keywords saved to CSV: {}'.format(top_k, output_file))


def translate_text(text, target_language='en'):
    # Translate the keywords
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text


def translate_csv(input_csv_path):
    df = pd.read_csv(input_csv_path)
    print('Translation in progress')

    df['Keyword Translation'] = df['Keyword'].apply(translate_text)
    df['Keyword Translation'] = df['Keyword Translation'].str.lower()

    # Save the translated data
    df.to_csv(input_csv_path, index=False, encoding='utf_8_sig')
    print('The process is accomplished.')


def process_and_visualize_data(input_file, stopwords_file, output_file, additional_stopwords=None, remove_keywords=None, custom_phrases=None):
    df = pd.read_csv(input_file)

    # Merge text content
    text = '\n'.join(df['Contents'])

    # Remove punctuation, special characters, and emoji
    text = re.sub(r'[^\w\s]', '', text)
    text = emoji.demojize(text)
    text = re.sub(r':\S+:', '', text)

    #  Set stopwords
    my_stopwords = [line.strip() for line in open(stopwords_file, 'r', encoding='utf-8').readlines()]
    if additional_stopwords:
        my_stopwords += additional_stopwords
    my_stopwords.append(' ')
    my_stopwords.append('\n')

    stopwords = STOPWORDS
    stopwords.update(my_stopwords)

    # Extract keywords
    extract_keywords(text, output_file, remove_keywords=remove_keywords)


additional_stopwords = ['年轻人', '寺庙', '媒体', '京报', '时候', '拜拜', '人们', '北京', '早安', '手串']
remove_keywords = ['年轻人', '寺庙', '媒体', '京报', '时候', '拜拜', '人们', '北京', '早安', '手串']

process_and_visualize_data('Wechat_articles.csv',
                            'hit_stopwords.txt',
                            'Keywords_Articles.csv',
                            additional_stopwords, remove_keywords)
translate_csv('Keywords_Articles.csv')


process_and_visualize_data('Weibo_Posts.csv',
                           'hit_stopwords.txt',
                           'Keywords_Posts.csv',
                           additional_stopwords, remove_keywords)
translate_csv('Keywords_Posts.csv')
