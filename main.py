import requests, os
from urllib.parse import urlparse
from dotenv import load_dotenv
from random import randrange

VK_API_TEMPLATE = 'https://api.vk.com/method'


def download_image(image_url, filename):
    response = requests.get(image_url)
    if not response.ok:
        return None
    with open(filename, 'wb') as image_file:
        image_file.write(response.content)


def get_comics_id(url):
    parser = urlparse(url)
    return parser.path.strip('/')


def get_comics_data(url):
    comics_id = get_comics_id(url)
    url_template = f'http://xkcd.com/{comics_id}/info.0.json'
    response = requests.get(url_template)
    return response.json()


def download_comics(url):
    img_url = get_comics_data(url)['img']
    filename = urlparse(img_url).path.split('/')[-1]
    download_image(img_url, filename)
    return filename


def get_comment(url):
    comment = get_comics_data(url)['alt']
    return comment


def get_upload_url(vk_required_params):
    response = requests.get(f'{VK_API_TEMPLATE}/photos.getWallUploadServer', params=vk_required_params)
    return response.json()['response']['upload_url']


def upload_to_server(photo, upload_url):
    with open(photo, 'rb') as file:
        files = {'photo': file}
        response = requests.post(upload_url, files=files)
    return response.json()


def save_to_album(photo, hash, server, vk_required_params):
    data = vk_required_params
    data['photo'] = photo,
    data['hash'] = hash,
    data['server'] = server
    response = requests.post(f'{VK_API_TEMPLATE}/photos.saveWallPhoto', data=data)
    return response.json()


def publish_photo(owner_id, message, attachments, params):
    data = params
    data['owner_id'] = owner_id
    data['message'] = message
    data['attachments'] = attachments
    response = requests.post(f'{VK_API_TEMPLATE}/wall.post', data=data)
    return response.json()


def get_random_comics():
    max_comics_num = requests.get('https://xkcd.com/info.0.json').json()['num']
    random_num = randrange(1, max_comics_num + 1)
    url = 'https://xkcd.com/' + str(random_num)
    return download_comics(url), get_comment(url)


if __name__ == '__main__':
    load_dotenv()
    TOKEN, API_VERSION, GROUP_ID = os.getenv('VK_ACCESS_TOKEN'), os.getenv('VK_API_VERSION'), os.getenv('GROUP_ID')
    vk_required_params = {
        'access_token': TOKEN,
        'v': API_VERSION,
        'group_id': GROUP_ID
    }

    random_comics = get_random_comics()
    comics_filename = random_comics[0]
    comics_message = random_comics[1]

    upload_url = get_upload_url(vk_required_params)
    server_data = upload_to_server(comics_filename, upload_url)
    hash = server_data['hash']
    photo = server_data['photo']
    server = server_data['server']
    photo_details = save_to_album(photo, hash, server, vk_required_params)['response'][0]
    owner_id = '-' + GROUP_ID
    message = comics_message
    attachments = 'photo' + str(photo_details['owner_id']) + '_' + str(photo_details['id'])

    publish_photo(owner_id, message, attachments, vk_required_params)
    print(f'photo {comics_filename} published')
    os.remove(os.path.join(comics_filename))
