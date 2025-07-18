[app]
title = Harmonauta
package.name = harmonauta
package.domain = org.harmonauta
source.dir = .
source.include_exts = py,kv,png,jpg,ttf
version = 1.0
requirements = kivy==2.2.1,requests,beautifulsoup4
orientation = portrait
fullscreen = 1
osx.kivy_version = 2.2.1

# Imagens personalizadas
icon.filename = assets/harmonauta_logo.png
presplash.filename = assets/harmonauta_splash.png

# Inclui assets no APK
android.presplash_color = #FFFFFF
android.add_resource = assets

[buildozer]
log_level = 2
warn_on_root = 1
