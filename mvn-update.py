#!/usr/bin/env python3
# coding=utf-8
import os
import requests
import argparse
import re
import semantic_version
from lxml import etree
from collections import namedtuple
import logging

__author__ = 'Victor Häggqvist'
__version__ = '0.1.1'

MetaData = namedtuple('MetaData', ['group', 'artifact', 'version', 'aar'])
VersionCheck = namedtuple('VersionCheck', ['version', 'metadata'])

log = logging.getLogger('Mvn Update')


def search_oss_nexus(artifact: MetaData) -> str:
    """
    Query OSS Sonatype Nexus for artifact info
    :param artifact:
    :return version str:
    """
    headers = {'Accept': 'application/json'}
    url = 'https://oss.sonatype.org/service/local/artifact/maven/resolve?g=%s&a=%s&v=RELEASE&r=releases' % (artifact.group, artifact.artifact)
    if len(artifact.aar) > 0:
        url += '&p=aar'

    resp = requests.get(url, headers=headers)

    if resp.status_code is not 200:
        log.debug('%s:%s %s Unexpected response: HTTP STATUS %s' % (artifact.group, artifact.artifact, artifact.version, resp.status_code))
        log.debug(url)
        return None

    body = resp.json()
    return body['data']['version']


def search_jcenter_bintray(artifact: MetaData) -> str:
    """
    Query JCenter search for artifact info
    :param artifact:
    :return:
    """
    url = 'http://jcenter.bintray.com/' + artifact.group.replace('.', '/')+'/'+artifact.artifact+'/maven-metadata.xml'
    resp = requests.get(url)

    if resp.status_code is not 200:
        log.debug(url)
        return None

    body = resp.text
    body = body.encode('utf8')

    doc = etree.fromstring(body)
    return doc.find('version').text


def find_latest_version(artifact: MetaData) -> str:
    """
    Check repos for version
    :param artifact:
    :return:
    """
    verison = search_oss_nexus(artifact)

    if not verison:
        verison = search_jcenter_bintray(artifact)

    return verison


def parse_artifacts(gradlefile: str) -> list:
    """
    Hunt for compile lines in the gradle config
    :param gradlefile:
    :return list of artifacts:
    """
    pattern = re.compile(r"compile\s'([a-z-0-9.]{1,}):([a-z-0-9.]{1,}):([0-9.\-a-z]{1,})([@aar]*)'")

    print('Processing %s' % gradlefile)
    deps = []
    with open(gradlefile, 'r') as f:
        cont = f.read()
        for line in cont.split('\n'):
            m = pattern.search(line)
            if m:
                meta = MetaData(group=m.group(1), artifact=m.group(2), version=m.group(3), aar=m.group(4))
                deps.append(meta)

    return deps


def rewrite(gradlefile: str, new_versions: list):
    """
    Rewrite the build.gradle with updated version numbers
    :param gradlefile:
    :param new_versions:
    :return:
    """
    with open(gradlefile, 'r+') as f:
        cont = f.read()

        for news in new_versions:
            meta = news.metadata
            oldline = r'%s:%s:%s' % (meta.group, meta.artifact, meta.version)
            newline = r'%s:%s:%s' % (meta.group, meta.artifact, news.version)

            cont = re.sub(oldline, newline, cont, flags=re.MULTILINE)

        f.seek(0)
        f.write(cont)


def main():
    parser = argparse.ArgumentParser(description='Maven Update v'+__version__)
    parser.add_argument('file', help='gradle.build file')
    parser.add_argument('-u', '--update', help='Actually update the gradle.build file', action='store_true')
    parser.add_argument('--prerelease', help='Update to prerelease versions', action='store_true')

    args = parser.parse_args()

    log.debug(args.file)

    gradlefile = os.path.expanduser(args.file)
    if os.path.abspath(gradlefile):
        gradlefile = os.path.join(os.getcwd(), gradlefile)

    artifacts = parse_artifacts(gradlefile)

    new_versions = []
    for art in artifacts:
        if 'com.android.support' not in art.group and 'com.google.android.gms' not in art.group:
            latest_version = find_latest_version(art)
            new_versions.append(VersionCheck(latest_version, art))
    log.debug(new_versions)

    for check in new_versions:
        meta = check.metadata
        try:
            cv = semantic_version.Version(check.version)
            is_prerelease = len(cv.prerelease) > 0
            update_prerelease = args.prerelease and is_prerelease

            if semantic_version.compare(meta.version, check.version) < 0 and update_prerelease:
                print('%s:%s %s -> %s' % (meta.group, meta.artifact, meta.version, check.version))
            else:
                print('%s:%s %s current' % (meta.group, meta.artifact, meta.version))
        except ValueError as e:
            print('%s for %s' % (e, meta))

    if args.update:
        print("Rewriting build.gradle with updates..")
        rewrite(gradlefile, new_versions)


if __name__ == '__main__':
    main()
