from urllib import parse
import posixpath
import logging

import github3
import semantic_version

log = logging.getLogger(__name__)


class GitHubRepos:
    def __init__(self, repos_url):
        self.repos_url = repos_url

        o = parse.urlparse(self.repos_url)
        # github.com/<owner>/<project>[.git]
        self.owner, self.project = posixpath.split(o.path[1:])
        if self.project.endswith('.git'):
            self.project = self.project[:-4]

    def __str__(self):
        return self.repos_url

    def find(self, version=None):
        tags = []
        log.info('looking for tags of {}/{}'.format(self.owner, self.project))
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

        if not tags:
            log.error('could not find a stable release')
            return None

        tags.sort()
        return tags[-1][1].zipball_url
