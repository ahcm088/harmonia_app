[app]
# Informações gerais
title = Harmonauta
package.name = harmonauta
package.domain = org.harmonauta
version = 1.0

# Diretórios e arquivos
source.dir = .
source.include_exts = py,kv,png,jpg,ttf
icon.filename = assets/harmonauta_logo.png
presplash.filename = assets/harmonauta_splash.png
android.presplash_color = #FFFFFF
android.add_resource = assets
android.resource = assets

# Requisitos Python
requirements = python3,kivy==2.2.1,requests,certifi

# Configurações da aplicação
orientation = portrait
fullscreen = 1
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Build Android
android.api = 30
android.minapi = 21
android.build_tools_version = 30.0.3
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.copy_libs = True
android.skip_update = False
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk

# Compatibilidade adicional
android.add_compile_options = sourceCompatibility JavaVersion.VERSION_1_8, targetCompatibility JavaVersion.VERSION_1_8

[buildozer]
log_level = 2
warn_on_root = 1
target = android

# Configurações do python-for-android
p4a.branch = master
p4a.recommended_ndk_version = 25b
p4a.bootstrap = sdl2