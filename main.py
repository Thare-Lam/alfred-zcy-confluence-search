import sys
import json
import os
import requests
from bs4 import BeautifulSoup
from workflow import Workflow3, ICON_SYNC

reload(sys)
sys.setdefaultencoding('utf-8')

req_cache_key = 'zcy-confluence-search-req-key-20190102'
req_cache_timeout = 30 * 24 * 60 * 60
auth_file = '.zcy_alfred'

home_url = 'http://confluence.cai-inc.com'
login_url = home_url + '/dologin.action'
search_url = home_url + '/dosearchsite.action?cql=siteSearch+~+"{query}"+and+type+%3D+"page"&queryString={query}'
empty_result = 'No results found for {query}'


def main(wf):
    # get session request object from cache
    req = wf.cached_data(req_cache_key, get_auth_req, req_cache_timeout)

    query = ' '.join(wf.args)
    search_url_entity = search_url.format(query=query)

    resp = req.get(search_url_entity)

    # session invalid
    if not has_login(resp):
        wf.logger.debug('cached auth request object is not successful')
        req = get_auth_req()
        wf.cache_data(req_cache_key, req)
        resp = req.get(search_url_entity)
    else:
        wf.logger.debug('cached auth request object is successful')

    soup = BeautifulSoup(resp.content, 'html.parser')
    res_ol = soup.select('ol[class="search-results cql"]')
    if len(res_ol) == 0:
        wf.add_item(title=empty_result.format(query=query))
        wf.send_feedback()
    else:
        for _ in res_ol[0].children:
            info = _.select('a[class="search-result-link visitable"]')[0]
            wf.add_item(title=info.text,
                        subtitle=_.select('div[class="search-result-meta"]')[0].text + ' - ' + _.select('div[class="highlights"]')[0].text,
                        arg=home_url + '/' + info['href'],
                        valid=True)
        wf.send_feedback()


def get_auth_req():
    with open(os.path.join(os.environ['HOME'], auth_file), 'r') as r:
        jd = json.load(r)
        login_data = {
            'os_username': jd.get('username'),
            'os_password': jd.get('password')
        }
        req = requests.session()
        req.post(login_url, data=login_data)
        wf.logger.debug('login to fetch auth request object')
        return req


def has_login(resp):
    return 'os_password' not in resp.content


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
