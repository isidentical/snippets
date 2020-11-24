import shelve
from collections import namedtuple
from urllib.request import urlopen, Request
from pyquery import PyQuery

IMDB_CAST_FORMAT = "https://www.imdb.com/title/tt{show_id}/fullcredits"
_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0"

Cast = namedtuple("Cast", "name character total_episodes episode_years image")

def fetch_page(url, force = False):
    def _fetch_page(url):
        request = Request(url, headers = {'User-Agent': _USER_AGENT})
        with urlopen(request) as page:
            return page.read().decode()

    with shelve.open(".page_cache") as page_cache:
        if url not in page_cache or force:
            page_cache[url] = _fetch_page(url)
        
        return page_cache[url]
    
def fetch_casts(show_id):
    page = fetch_page(IMDB_CAST_FORMAT.format(show_id = show_id))
    interface = PyQuery(page)
    [cast_list] = interface(".cast_list")
    for index, cast in enumerate(cast_list.getchildren()[1:]):
        if len(cast.getchildren()) != 4:
            continue
        info, _, _, character = cast.getchildren()
        cast_info = info.getchildren()[0].getchildren()[0].attrib
        play_info = character.getchildren() 
        if len(play_info) == 2:
            character_name = play_info.pop(0).text.strip()
        elif len(play_info) == 1 and 'episode' in play_info[0].text.strip():
            character_name = "unknown"
        else:
            continue
        episode_details = play_info[0].text.strip()
        try:
            total_episodes, *_, episode_years = episode_details.split()
        except ValueError:
            total_episodes = "0"
            episode_years = None
        
        yield Cast(cast_info["alt"], character_name, total_episodes, episode_years, cast_info["src"])

def compare_casts(show_id_1, show_id_2, /):
    series_1_casts = {cast.name: cast for cast in fetch_casts(show_id_1)}
    series_2_casts = {cast.name: cast for cast in fetch_casts(show_id_2)}
    for common_cast in series_1_casts.keys() & series_2_casts.keys():
        cast_1 = series_1_casts[common_cast]
        cast_2 = series_2_casts[common_cast]
        if cast_1.image == cast_2.image:
            print(common_cast, "played", cast_1.character, "at", cast_1.episode_years, "for", cast_1.total_episodes, "episodes")
            print(common_cast, "played", cast_2.character, "at", cast_2.episode_years, "for", cast_2.total_episodes, "episodes")
compare_casts("1839578", "0118480")
