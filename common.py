import requests, os


def get_file_extension(file_url):
    return os.path.splitext(file_url)[-1]


def download_image(image_url, filename):
    response = requests.get(image_url)
    if not response.ok:
        return None
    with open(filename, 'wb') as image_file:
        image_file.write(response.content)
