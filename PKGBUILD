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
sha512sums=('ca78c2f8a227cfbb1a9642b6980fd2afb82b04f213c4f55d7f2a11dca2821ca2b3b8f3feea172ac31c91b28d5eba631213737dccd44a80fb4704ba9d2563cb5d')

package() {
  install -dm755 "$pkgdir/opt/mvn-update"
  install -dm755 "$pkgdir/usr/bin"
  cp mvn-update.py "$pkgdir/opt/mvn-update"
  ln -s "/opt/mvn-update/mvn-update.py" "$pkgdir/usr/bin/mvn-update"
}

# vim:set ts=2 sw=2 et:

