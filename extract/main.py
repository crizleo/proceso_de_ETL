
import re
import argparse
import logging
import datetime
import csv
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError 
import news_page_objects as news
from common import config
logging.basicConfig(level= logging.INFO)

logger = logging.getLogger(__name__)

is_well_formed_link = re.compile(r'^https?://.+/.+$')
is_root_path = re.compile(r'^/.+$')

def _news_scrapper(news_site_uid):
    host = config()['news_sites'][news_site_uid]['url']

    logger.info('Beginning Scraper for {}'.format(host))
    homepage = news.HomePage(host, news_site_uid)
    articles = list()
    for link in homepage.article_links:
        article = _fetch_article(news_site_uid, host, link)

        if article:
            logger.info('Article fetched!!')
            articles.append(article)
    
    _save_articles(news_site_uid, articles)
    

def _save_articles(news_site_uid, articles):
    #asi conseguimos la hora y fecha actual
    #con strftime le damos formato a la fecha
    now = datetime.datetime.now().strftime('%Y_%m_%d')
    out_file_name = f'{news_site_uid}_{now}_articles.csv'

    csv_headers = list(filter(lambda property: not property.startswith('_'), dir(articles[0])))
    
    with open(out_file_name, mode= 'w+', encoding= 'utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

        for article in articles:
            row = [str(getattr(article, prop))for prop in csv_headers]
            writer.writerow(row)


def _fetch_article(news_site_uid, host, link):
    logger.info("Start fetching article {}".format(link))

    article = None

    try:
        article = news.Article_page(_build_link(host, link),news_site_uid)
    except (HTTPError, MaxRetryError):
        # HTTPError: captura un error si la pagina no existe
        # MaxRetryError: elimina la posibilidad de que se convierta en un infinityloop
        logger.warning("Error while fetching the article", exc_info= False)

    if article and not article.body:
        logger.warning('Invalid articel. there is no body')
        return None
    return article

def _build_link(host, link):
    if is_well_formed_link.match(link):
        return link
    elif is_root_path.match(link):
        return '{}{}'.format(host,link)
    else:
        return '{host}/{uri}'.format(host=host, uri=link)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    #creamos una lista de las posibles llaves que podemos ingresar
    news_site_choices = list(config()['news_sites'].keys())

    parser.add_argument('news_site',
                        help= 'The news site that you want to scrape',
                        type= str,
                        choices= news_site_choices)
            
    args = parser.parse_args()
    _news_scrapper(args.news_site)