# Maintainer: Florian Bruhin (The Compiler) <archlinux.org@the-compiler.org>
# Adapted for dp1 version by Semyon Maryasin <simeon@maryasin.name>
# vim: ft=sh

pkgname=mvn-update
pkgver=0.1.0
pkgrel=1
pkgdesc="Maven artifact version updater for build.gradle config files"
url="https://developer.getpebble.com/2/getting-started/"
arch=('any')
license=('MIT')
depends=('python-lxml' 'python-requests' 'python-semantic-version' 'python-argparse')
source=('mvn-update.py')
sha256sums=('59064ee56b7099dc0cb5f6844c2b3c241815feadc98accd4426f949452799b96')

package() {
  install -dm755 "$pkgdir/opt/mvn-update"
  install -dm755 "$pkgdir/usr/bin"
  cp mvn-update.py "$pkgdir/opt/mvn-update"
  ln -s "/opt/mvn-update/mvn-update.py" "$pkgdir/usr/bin/mvn-update"
}

# vim:set ts=2 sw=2 et:

