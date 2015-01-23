'''

Bower Registry API_URL
https://docs.google.com/document/d/17Nzv7onwsFYQU2ompvzNI9cCBczVHntWMiAn4zDip1w

'''
import os
import sys
import zipfile
import tempfile
import shutil
import json
import logging

import requests

from bowerlib.github import GitHubRepos

log = logging.getLogger(__name__)

# http://stackoverflow.com/questions/19069093/what-is-the-official-bower-registry-url
API_URL = "https://bower.herokuapp.com"


def locate_component_dir():
    component_dir = 'bower_components'
    if not os.path.exists(component_dir):
        os.makedirs(component_dir)
    return component_dir


class Project:
    def __init__(self, name):
        self.name = name

    def find(self, version=None):
        '''Fetch the remote metadata blob for the named package.
        '''
        response = requests.get(API_URL + '/packages/' + self.name)
        if response.status_code != 200:
            logging.error('could not find package %s', self.name)
            sys.exit(1)

        try:
            result = response.json()
        except ValueError:
            fn = '/tmp/bower-py-json.txt'
            with open(fn, 'wb') as f:
                f.write(response.raw.read())
            log.exception('error parsing JSON (see %s)', fn)
            sys.exit(1)

        log.info('found repository {}'.format(result['url']))
        assert result['url'].startswith('git://github.com')
        return GitHubRepos(result['url']).find(version)

    def fetch(self, version=None):
        url = self.find(version)
        if url is None:
            sys.exit(1)
        log.info('downloading from {}'.format(url))
        response = requests.get(url, stream=True)
        with tempfile.TemporaryFile() as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
            f.seek(0)
            component_dir = locate_component_dir()
            dest_path = os.path.join(component_dir, self.name)
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)

            contents = zipfile.ZipFile(f)
            bower_json = contents.namelist()[0] + 'bower.json'
            if bower_json in contents.namelist():
                meta = json.loads(contents.read(bower_json).decode('utf8'))
            else:
                meta = {}
            for name in contents.namelist():
                # ASSUMPTION: the zip files are created on Unix by github
                # thus paths are unix separated and follow consistent structure
                if name[-1] == '/':
                    continue
                assert name[0] != '/'
                assert not name.startswith('..')
                dest_name = '/'.join(name.split('/')[1:])

                if any(dest_name.split('/')[0] == ignore_path
                        for ignore_path in meta.get('ignore', [])):
                    continue

                source = contents.open(name)
                dest_name = os.path.join(dest_path, dest_name)
                if not os.path.exists(os.path.dirname(dest_name)):
                    os.makedirs(os.path.dirname(dest_name))
                target = open(dest_name, "wb")
                with source, target:
                    shutil.copyfileobj(source, target)


def main():
    logging.basicConfig()
    if sys.argv[1] == 'install':
        Project(sys.argv[2]).fetch(sys.argv[3] if len(sys.argv) > 3 else None)


if __name__ == '__main__':
    main()
