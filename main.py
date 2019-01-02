import sys
import json
import os
import requests
from bs4 import BeautifulSoup
from workflow import Workflow3, ICON_SYNC

reload(sys)
sys.setdefaultencoding('utf-8')

auth_file = '.zcy_alfred'

home_url = 'http://confluence.cai-inc.com'
login_url = home_url + '/dologin.action'
search_url = home_url + '/dosearchsite.action?cql=siteSearch+~+"{query}"+and+type+%3D+"page"&queryString={query}'
empty_result = 'No results found for {query}'


def main(wf):
    req = requests.session()
    req.post(login_url, data=get_login_data())
    query = ' '.join(wf.args)
    resp = req.get(search_url.format(query=query))
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


def get_login_data():
    with open(os.path.join(os.environ['HOME'], auth_file), 'r') as r:
        jd = json.load(r)
        return {
            'os_username': jd.get('username'),
            'os_password': jd.get('password')
        }


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
