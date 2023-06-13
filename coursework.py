import datetime
import requests
import json
import os
from tqdm import tqdm

with open('token.txt', 'r') as file_object:
    token = file_object.read().strip()


class VK_Photo:
    def __init__(self, token, version):
        self.url = 'https://api.vk.com/method/'
        self.params = {
            'access_token': token,
            'v': version
        }

    def photos_get(self, id, al_id='profile'):
        photo_params = {
            'owner_id': id,
            'album_id': al_id,
            'extended': 1,
            'count': 5,
            'rev': 1
        }
        req = requests.get(self.url + 'photos.get', params={**self.params, **photo_params}).json()
        req = req['response']['items']
        return req

    def create_folder(self):
        BASE_PATH = os.getcwd()
        folder = 'VK-photo'
        path_repl = os.path.join(BASE_PATH, folder)
        if not os.path.exists(path_repl):
            os.mkdir(path_repl)
        return str(path_repl) + '/'

    def get_largest(self, size_dict):
        if size_dict['width'] >= size_dict['height']:
            return size_dict['width']
        else:
            return size_dict['height']

    def download_photo(self, url, filename):
        res = requests.get(url)
        path = self.create_folder()
        with open(path + filename + '.jpg', 'bw') as file:
            file.write(res.content)

    def save_photo(self, id, al_id='profile'):
        filename_lib = []
        sizes_photo = []
        res = self.photos_get(id, al_id)
        for photo in tqdm(res):
            sizes = photo['sizes']
            max_sizes_url = max(sizes, key=self.get_largest)['url']
            filename = str(photo['likes']['count'])
            filename_lib.append(filename)
            if filename_lib.count(filename) > 1:
                filename += ' likes ' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                self.download_photo(max_sizes_url, filename)
                sizes_photo.append(dict(width=max(sizes, key=self.get_largest)['width'],
                                        height=max(sizes, key=self.get_largest)['height'],
                                        filename=filename + '.jpg'))
            else:
                self.download_photo(max_sizes_url, filename)
                sizes_photo.append(dict(width=max(sizes, key=self.get_largest)['width'],
                                        height=max(sizes, key=self.get_largest)['height'],
                                        filename=filename + '.jpg'))

        with open("photo-size.json", "w") as write_file:
            json.dump(sizes_photo, write_file)


if __name__ == '__main__':
    vk_client = VK_Photo(token, '5.131')
    vk_client.save_photo()


with open('token-YD.txt', 'r') as file_object:
    tokenYD = file_object.read().strip()

PHOTO_DIR = 'VK-photo'
BASE_PATH = os.getcwd()
files_path = os.path.join(BASE_PATH, PHOTO_DIR)
files_in_folder = os.listdir(files_path)


class YaUploader:
    def __init__(self, token: str):
        self.token = token
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                        'Authorization': f'OAuth {self.token}'}

    def uploads_files(self):
        self.check_and_create_folder(PHOTO_DIR)
        for file in tqdm(files_in_folder):
            photo_path = os.path.join(PHOTO_DIR, file).replace('\\', '/')
            res = requests.get(f'{self.url}/upload?path={photo_path}', headers=self.headers).json()
            with open(photo_path, 'rb') as f:
                try:
                    requests.put(res['href'], files={'file': f})
                except KeyError:
                    print(res['message'])
        return print("Файлы успешно загружены.")

    def check_and_create_folder(self, name_folder):
        res = requests.get(f'{self.url}?path={name_folder}', headers=self.headers).json()
        try:
            if res['error'] == 'DiskNotFoundError':
                requests.put(f'{self.url}?path={name_folder}', headers=self.headers).json()
                return f'Папки {name_folder} нет на Я.Диске. Создаём.'
        except KeyError:
            return f'Папка {name_folder} есть на Я.Диске.'

    def del_folder(self, name_folder):
        '''
        Функция удаление папки на Я.Диске.
        '''
        res = requests.delete(f'{self.url}?path={name_folder}', headers=self.headers)
        return res


if __name__ == '__main__':
    uploader = YaUploader(tokenYD)
    result = uploader.uploads_files()
