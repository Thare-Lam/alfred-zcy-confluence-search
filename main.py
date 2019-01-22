import sys
import json
import os
from bs4 import BeautifulSoup
from workflow import Workflow3, ICON_SYNC, web

reload(sys)
sys.setdefaultencoding('utf-8')

cookie_cache_key = 'zcy-confluence-search-cookie-key-20190103'
cookie_cache_timeout = 30 * 24 * 60 * 60

auth_file = '.zcy_alfred'

home_url = 'http://confluence.cai-inc.com'
login_url = home_url + '/dologin.action'
search_url = home_url + '/dosearchsite.action'

auth_failed = {
    'title': 'Username or password auth failed',
    'subtitle': 'Please check auth file (~/{filename})'.format(filename=auth_file)
}
empty_result = 'No results found for {query}'


def main(wf):
    query = ' '.join(wf.args)
    resp = do_search(query, wf.cached_data(cookie_cache_key, get_cookie, cookie_cache_timeout))
    # session invalid
    if auth_success(resp):
        wf.logger.debug('cached cookie is valid')
    else:
        wf.logger.debug('cached cookie is invalid')
        cookie = get_cookie()
        wf.cache_data(cookie_cache_key, cookie)
        resp = do_search(query, cookie)
        if not auth_success(resp):
            wf.add_item(title=auth_failed['title'], subtitle=auth_failed['subtitle'])
            wf.send_feedback()
            return
    parse_content(query, resp.content)


def auth_success(resp):
    return 'os_password' not in resp.content


def do_search(query, cookie):
    resp = web.get(search_url, headers={'Cookie': cookie}, params={
        'cql': 'siteSearch ~ "{query}" and type = "page"'.format(query=query),
        'queryString': query
    })
    resp.raise_for_status()
    return resp


def get_cookie():
    with open(os.path.join(os.environ['HOME'], auth_file), 'r') as r:
        jd = json.load(r)
        login_data = {
            'os_username': jd.get('username'),
            'os_password': jd.get('password')
        }
        r = web.post(login_url, data=login_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        r.raise_for_status()
        wf.logger.debug('login to fetch auth request object')
        return r.headers.get('set-cookie')


def parse_content(query, content):
    soup = BeautifulSoup(content, 'html.parser')
    res_ol = soup.select('ol[class="search-results cql"]')
    if len(res_ol) == 0:
        wf.add_item(title=empty_result.format(query=query))
        wf.send_feedback()
    else:
        for _ in res_ol[0].children:
            info = _.select('a[class="search-result-link visitable"]')[0]
            wf.add_item(title=info.text,
                        subtitle=_.select('div[class="search-result-meta"]')[0].text + ' - ' +
                                 _.select('div[class="highlights"]')[0].text,
                        arg=home_url + '/' + info['href'],
                        valid=True)
        wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow3(help_url='https://github.com/Thare-Lam/alfred-zcy-confluence-search',
                   update_settings={
                       'github_slug': 'Thare-Lam/alfred-zcy-confluence-search',
                       'frequency': 1
                   })

    if wf.update_available:
        wf.add_item('New version available', 'Action this item to install the update',
                    autocomplete='workflow:update', icon=ICON_SYNC)

    sys.exit(wf.run(main))
