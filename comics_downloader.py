import requests
from urllib.parse import urlparse
from common import download_image

def get_comics_id(url):
    parser = urlparse(url)
    return parser.path.strip('/')

def get_comics_data(url):
    comics_id = get_comics_id(url)
    url_template = f'http://xkcd.com/{comics_id}/info.0.json'
    response = requests.get(url_template)
    return response.json()


def downoload_comics(url):
    img_url = get_comics_data(url)['img']
    filename = urlparse(img_url).path.split('/')[-1]
    download_image(img_url, filename)

def get_comment(url):
    comment = get_comics_data(url)['alt']
    return comment


if __name__ == '__main__':
    url = 'https://xkcd.com/353/'
    downoload_comics(url)
    print(get_comment(url))
