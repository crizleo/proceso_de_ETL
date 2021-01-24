import argparse
import logging
import hashlib
import nltk
from nltk.corpus import stopwords
logging.basicConfig(level=logging.INFO)
from urllib.parse import urlparse

import pandas as pd

logger = logging.getLogger(__name__)

def main(filename):
    logger.info('Starting cleanig process')
    df = _read_data(filename)

    newspaper_uid = _extract_newspaper_uid(filename)
    logger.info(f'Newspaper_uid detected: {newspaper_uid}')

    df = _add_newspaper_uid_column(df, newspaper_uid)

    df = _extract_host(df)

    df = _missing_titles(df)

    df = _generate_uids_for_rows(df)

    df = _remove_new_lines_from_body(df)

    df = _tokenize_column(df, 'title')
    df = _tokenize_column(df, 'body')

    df = _remove_duplicate_entries(df, 'title')
    df = _drop_rows_with_missing_values(df)

    _save_data(df, filename)
    return df

def _read_data(filename):
    logger.info(f'Reading file {filename}')
    return pd.read_csv(filename, encoding='utf-8')

def _extract_newspaper_uid(filename):
    logger.info('Extracting newspaper_uid')
    return filename.split(sep='_')[0]

def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info(f'filling newspaper_uid column whit {newspaper_uid}')
    df['newspaper_uid'] = newspaper_uid
    return df

def _extract_host(df):
    logger.info('Extracting host from DataFrame')
    df['host'] = df['link'].apply(lambda link: urlparse(link).netloc)
    return df

def _missing_titles(df):
    logger.info('Filling missing titles')
    missing_titles_mask = df['title'].isna()

    missing_titles = (df[missing_titles_mask]['link']
                      .str.extract(r'(?P<missing_titles>[^/]+)$')
                      .apply(lambda missing_titles: missing_titles.replace('-', ' ')))

    df.loc[missing_titles_mask]['title'] = missing_titles.loc[:, 'missing_titles']
    return df

def _generate_uids_for_rows(df):
    logger.info('Generating uids for rows')
    uids = (df.apply(lambda row: hashlib.md5(bytes(row['link'].encode())), axis=1)
            .apply(lambda hash_object: hash_object.hexdigest())
            )

    df['uid'] = uids
    df.set_index('uid', inplace=True)
    return df

def _remove_new_lines_from_body(df):
    logger.info('Removing new lines from body')
    df['body'] = df['body'].apply(lambda row: row.replace('\n','').replace('\r',''))
    return df

def _tokenize_column(df, column_name):
    stop_words = set(stopwords.words('spanish'))

    df[f'n_tokenize_{column_name}'] = (df
           .dropna()
           .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1)
           .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens)))
           .apply(lambda tokens: list(map(lambda token: token.lower(), tokens)))
           .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list)))
           .apply(lambda valid_word_list: len(valid_word_list))
           )

    return df

def _remove_duplicate_entries(df, column):
    logger.info('Removing duplicate entries')
    df.drop_duplicates(subset=[column], keep='first', inplace=True)

    return df

def _drop_rows_with_missing_values(df):
    logger.info('Removing rows with missing values')
    return df.dropna()

def _save_data(df, filename):
    clean_filename = f'clean_{filename}'
    logger.info(f'Saving data at location: {clean_filename}')
    df.to_csv(clean_filename, encoding='utf-8', sep='|')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help= 'The path to the dirty data',
                        type= str)

    arg = parser.parse_args()

    df = main(arg.filename)

    print(df)