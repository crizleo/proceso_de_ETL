import logging
logging.basicConfig(level=logging.INFO)
import subprocess

logger = logging.getLogger(__name__)

news_sites_uids = ['eluniversal', 'elpais']

def main():
    _extract()
    _transform()
    _load()

def _extract():
    logger.info('Starting extract procces')
    for news_site_uid in news_sites_uids:
        subprocess.run(['python', 'main.py', news_site_uid], cwd='./extract')
        subprocess.run(['find', '.', '-name', f'{news_site_uid}*',
                        '-exec', 'mv', '{}', f'../transform/{news_site_uid}.csv', ';'], cwd= './extract')


def _transform():
    logger.info('Starting transform process')
    for news_sites_uid in news_sites_uids:
        subprocess.run(['python', 'news_paper_recipe.py', f'{news_sites_uid}.csv'], cwd='./transform')
        subprocess.run(['rm', f'{news_sites_uid}.csv'])
        subprocess.run(['find', '.', '-name', f'clean_{news_sites_uid}.csv',
                        '-exec', 'mv', '{}', f'../load', ';'], cwd='./transform')



def _load():
    logger.info('Starting load procces')
    for news_sites_uid in news_sites_uids:
        subprocess.run(['python', 'main.py', f'clean_{news_sites_uid}.csv'], cwd='./load')
        subprocess.run(['rm', f'clean_{news_sites_uid}.csv'])




if __name__ == '__main__':
    main()





