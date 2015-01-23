'''

Bower Registry API_URL
https://docs.google.com/document/d/17Nzv7onwsFYQU2ompvzNI9cCBczVHntWMiAn4zDip1w

'''
import os
from urllib import parse
import posixpath
import zipfile
import tempfile
import shutil
import json

import github3
import requests
import semantic_version


# http://stackoverflow.com/questions/19069093/what-is-the-official-bower-registry-url
API_URL = "https://bower.herokuapp.com"


def locate_component_dir():
    component_dir = 'bower_components'
    if not os.path.exists(component_dir):
        os.makedirs(component_dir)
    return component_dir


class GitHubRepos:
    def __init__(self, repos_url):
        self.repos_url = repos_url

        o = parse.urlparse(self.repos_url)
        # github.com/<owner>/<project>.git
        self.owner, self.project = posixpath.split(o.path[1:])
        self.project = self.project[:-4]

    def __str__(self):
        return self.repos_url

    def find(self, version=None):
        tags = []
        repos = github3.GitHub().repository(self.owner, self.project)
        for tag in repos.iter_tags():
            version_tag = tag.name
            # so far all tags appear to prepend "v" to version
            if version_tag[0] == 'v':
                actual_version = version_tag[1:]
            else:
                actual_version = version_tag
            try:
                semver = semantic_version.Version(actual_version)
            except ValueError:
                # bad semver, no cookie
                continue
            if version in (version_tag, actual_version):
                return tag.zipball_url
            if semver.prerelease or semver.build:
                continue
            tags.append((semver, tag))

        tags.sort()
        return tags[-1][1].zipball_url


class Project:
    def __init__(self, name):
        self.name = name

    def find(self, version=None):
        '''Fetch the remote metadata blob for the named package.
        '''
        result = requests.get(API_URL + '/packages/' + self.name).json()
        print('found repository {}'.format(result['url']))

        assert result['url'].startswith('git://github.com')
        return GitHubRepos(result['url']).find(version)

    def fetch(self, version=None):
        url = self.find(version)
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
            bower_json = contents.namelist()[0] + 'bower.json'
            if bower_json in contents.namelist():
                meta = json.loads(contents.read(bower_json).decode('utf8'))
            else:
                meta = {'ignore': []}
            for name in contents.namelist():
                # ASSUMPTION: the zip files are created on Unix by github
                # thus paths are unix separated and follow consistent structure
                if name[-1] == '/':
                    continue
                assert name[0] != '/'
                assert not name.startswith('..')
                dest_name = '/'.join(name.split('/')[1:])

                if any(dest_name.split('/')[0] == ignore_path
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
    if sys.argv[1] == 'install':
        Project(sys.argv[2]).fetch(sys.argv[3] if len(sys.argv) > 3 else None)
