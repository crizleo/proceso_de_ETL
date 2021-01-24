from common import config
import requests
import bs4


class NewsPage:

    def __init__(self, url, news_site_uid):
        self._config = config()['news_sites'][news_site_uid]
        self._queries = self._config['queries']
        self._html = None
        self._visit(url)

    def _select(self,  query_string):
        return self._html.select(query_string)

    def _visit(self, url):
        headers = {'Accept-Encoding': 'deflate'}
        response = requests.get(url, headers=headers, stream=True)
        response.encoding = 'utf-8'
        #este metodo nos lanza un error si la solicitud no se completa
        response.raise_for_status()

        self._html = bs4.BeautifulSoup(response.text, 'html.parser')


class HomePage(NewsPage):

    def __init__(self,host ,news_site_uid):
        super().__init__(host, news_site_uid)

    @property
    def article_links(self):
        link_list = []
        for link in self._select(self._queries['news_links']):
            if link and link.has_attr('href'):
                link_list.append(link)
        
        #asi evitamos que se repita algun link
        return set(link['href'] for link in link_list)



class Article_page(NewsPage):

    def __init__(self, host, news_site_uid):
        self._host = host
        super().__init__(host, news_site_uid)

    @property
    def title(self):
        result = self._select(self._queries['article_title'])
        return result[0].text if len(result) else ''

    @property
    def body(self):
        result = self._select(self._queries['article_body'])
        return result[0].text if len(result) else ''

    @property
    def link(self):
        return self._host