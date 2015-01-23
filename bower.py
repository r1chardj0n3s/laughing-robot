'''

Bower Registry API_URL
https://docs.google.com/document/d/17Nzv7onwsFYQU2ompvzNI9cCBczVHntWMiAn4zDip1w

'''
import os
import subprocess
from urllib import parse
import posixpath
import zipfile
import tempfile
import shutil
import json

import requests
import semantic_version


# http://stackoverflow.com/questions/19069093/what-is-the-official-bower-registry-url
API_URL = "https://bower.herokuapp.com"


def locate_component_dir():
    component_dir = 'bower_components'
    if not os.path.exists(component_dir):
        os.makedirs(component_dir)
    return component_dir


class GitHubDownload:
    def __init__(self, repos_url, version_tag, semver):
        self.repos_url = repos_url
        self.version_tag = version_tag
        self.semver = semver

    def __str__(self):
        return '{} at {}'.format(self.version_tag, self.repos_url)

    def download_url(self):
        o = parse.urlparse(self.repos_url)
        print(o)
        # github.com/<user>/<project>.git
        user, project = posixpath.split(o.path)
        project = project[:-4]
        return 'https://github.com/{}/{}/archive/{}.zip'.format(
            user, project, self.version_tag)


class Project:
    def __init__(self, name):
        self.name = name

    def find(self, version=None):
        '''Fetch the remote metadata blob for the named package.
        '''
        result = requests.get(API_URL + '/packages/' + self.name).json()

        assert result['url'].startswith('git:/')

        print('found repository {}'.format(result['url']))

        command = 'git ls-remote --tags {}'.format(result['url'])
        tags = []
        for line in subprocess.getoutput(command).splitlines():
            try:
                hash, ref = line.strip().split()
            except ValueError as e:
                print('error {} parsing "{}"'.format(e, line))
            version_tag = ref[10:]
            # so far all tags appear to prepend "v" to version
            assert version_tag[0] == 'v'
            try:
                semver = semantic_version.Version(version_tag[1:])
            except ValueError:
                # bad semver, no cookie
                continue
            if version in (version_tag, version_tag[1:]):
                return GitHubDownload(result['url'], version_tag, semver)
            if semver.prerelease or semver.build:
                continue
            tags.append((semver, version_tag))

        tags.sort()
        semver, version_tag = tags[-1]
        return GitHubDownload(result['url'], version_tag, semver)

    def fetch(self, version=None):
        download = self.find(version)
        url = download.download_url()
        print('downloading from {}'.format(url))
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
            meta = json.loads(contents.read(contents.namelist()[0]
                                           + 'bower.json').decode('utf8'))
            for name in contents.namelist():
                if name[-1] == '/':
                    continue
                assert name[0] != '/'
                assert not name.startswith('..')
                dest_name = '/'.join(name.split('/')[1:])

                if any(os.path.commonprefix([dest_name, ignore_path])
                        for ignore_path in meta['ignore']):
                    continue

                source = contents.open(name)
                dest_name = os.path.join(dest_path, dest_name)
                if not os.path.exists(os.path.dirname(dest_name)):
                    os.makedirs(os.path.dirname(dest_name))
                target = open(dest_name, "wb")
                with source, target:
                    shutil.copyfileobj(source, target)

if __name__ == '__main__':
    import sys
    Project(sys.argv[1]).fetch()
