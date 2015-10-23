#!/usr/bin/env python
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
__version__ = '0.3.0'

MetaData = namedtuple('MetaData', ['group', 'artifact', 'version', 'aar'])
VersionCheck = namedtuple('VersionCheck', ['version', 'metadata'])

log = logging.getLogger('Mvn Update')


def get_versions_oss_nexus(group, artifact):
    url = 'http://repo1.maven.org/maven2/'+group.replace('.', '/')+'/'+artifact+'/maven-metadata.xml'

    r = requests.get(url)

    if r.status_code is not 200:
        log.debug('%s:%s Unexpected response: HTTP STATUS %s' % (group, artifact, r.status_code))
        log.debug(url)
        return None

    body = r.text
    body = body.encode('utf8')

    return get_versions_from_maven_metadata(body)


def get_versions_jcenter_bintray(group: str, artifact: str) -> list:
    url = 'http://jcenter.bintray.com/' + group.replace('.', '/')+'/'+artifact+'/maven-metadata.xml'
    r = requests.get(url)

    if r.status_code is not 200:
        log.debug('%s:%s Unexpected response: HTTP STATUS %s' % (group, artifact, r.status_code))
        log.debug(url)
        return None

    body = r.text
    body = body.encode('utf8')

    return get_versions_from_maven_metadata(body)


def get_versions_from_maven_metadata(metadata: str) -> list:
    """
    Returns the versions list from the contents of maven-metadata.xml
    :param metadata:
    :return: version list
    """
    doc = etree.fromstring(metadata)
    meta_versions = doc.find('versioning').find('versions').getchildren()

    versions = []
    for m in meta_versions:
        versions.append(m.text)

    return versions


def fix_semver(version: str) -> str:
    """
    Add patch version were absent
    :param version:
    :return:
    """
    if version.count('.') is 1:
        return version + '.0'
    return version


def get_latest_non_prerelease(versions: list) -> str:
    """
    Returns latest stable version
    :param versions: List of version strings stored ASC
    :return: stable version
    """
    versions.reverse()
    for v in versions:
        comp_ver = fix_semver(v)
        sem_version = semantic_version.Version(comp_ver)
        is_prerelease = len(sem_version.prerelease) > 0

        if not is_prerelease:
            return v

    return None


def find_oss_nexus(artifact: MetaData, get_prerelease: bool) -> str:
    """
    Query OSS Nexus for latest release of artifact
    If get_prerelease is false and there is no stable this will return None
    :param artifact:
    :param get_prerelease:
    :return:
    """
    versions = get_versions_oss_nexus(artifact.group, artifact.artifact)
    # pprint(versions)

    if versions is None:
        return None

    if get_prerelease:
        return versions[-1]
    else:
        return get_latest_non_prerelease(versions)


def find_jcenter_bintray(artifact: MetaData, get_prerelease: bool) -> str:
    versions = get_versions_jcenter_bintray(artifact.group, artifact.artifact)

    if versions is None:
        return None

    if get_prerelease:
        return versions[-1]
    else:
        return get_latest_non_prerelease(versions)


def find_latest_version(artifact: MetaData, get_prerelease: bool) -> str:
    """
    Check repos for version latest version of artifact
    :param artifact:
    :return:
    """

    version = find_oss_nexus(artifact, get_prerelease)

    if not version:
        version = find_jcenter_bintray(artifact, get_prerelease)

    return version


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
    parser.add_argument('-p', '--prerelease', help='Update to prerelease versions', action='store_true')

    args = parser.parse_args()

    log.debug(args.file)

    gradlefile = os.path.expanduser(args.file)
    if os.path.abspath(gradlefile):
        gradlefile = os.path.join(os.getcwd(), gradlefile)

    artifacts = parse_artifacts(gradlefile)

    new_versions = []
    for art in artifacts:
        if 'com.android.support' not in art.group and 'com.google.android.gms' not in art.group:
            latest_version = find_latest_version(art, args.prerelease)
            new_versions.append(VersionCheck(latest_version, art))
    log.debug(new_versions)

    for check in new_versions:
        meta = check.metadata
        try:
            if semantic_version.compare(meta.version, check.version) < 0:
                print('%s:%s %s -> %s' % (meta.group, meta.artifact, meta.version, check.version))
            else:
                print('%s:%s %s current' % (meta.group, meta.artifact, meta.version))

        except ValueError as e:
            print('%s for %s' % (e, meta))

    # actually rewrite the file, if one want
    if args.update:
        print("Rewriting build.gradle with updates..")
        rewrite(gradlefile, new_versions)


if __name__ == '__main__':
    main()
