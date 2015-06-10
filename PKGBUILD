# Maintainer: Victor Häggqvist <victor@snilius.com>
# vim: ft=sh

pkgname=mvn-update
pkgver=0.1.1
pkgrel=1
pkgdesc="Maven artifact version updater for build.gradle config files"
url="https://developer.getpebble.com/2/getting-started/"
arch=('any')
license=('MIT')
depends=('python-lxml' 'python-requests' 'python-semantic-version' 'python-argparse')
source=('mvn-update.py')
sha512sums=('1bcc89a569d799dcb0a4b4eb201ce8b1d8c228df319f02691665cda0e3cf10fed6bbbd9abf8492088de025e616bf76d94842d60320c95a4f8b0921ac9de9891e')

package() {
  install -dm755 "$pkgdir/opt/mvn-update"
  install -dm755 "$pkgdir/usr/bin"
  cp mvn-update.py "$pkgdir/opt/mvn-update"
  ln -s "/opt/mvn-update/mvn-update.py" "$pkgdir/usr/bin/mvn-update"
}

# vim:set ts=2 sw=2 et:

