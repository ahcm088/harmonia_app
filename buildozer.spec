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

# FIX para evitar erro build-tools license
android.build_tools_version = 30.0.3

# Configurações adicionais recomendadas
android.arch = arm64-v8a
android.sdk = 24
android.ndk = 25b
android.api = 30
android.minapi = 21
android.gradle_dependencies = 'com.android.tools.build:gradle:7.2.2'

# Otimização para reduzir tamanho do APK
android.enable_shrink = True
android.enable_proguard = True

[buildozer]
# Configurações de build
log_level = 2
warn_on_root = 1
target = android