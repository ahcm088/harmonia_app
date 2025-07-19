[app]
title = Harmonauta
package.name = harmonauta
package.domain = org.harmonauta
source.dir = .
source.include_exts = py,kv,png,jpg,ttf
version = 1.0
requirements = python3,kivy==2.2.1,requests,beautifulsoup4,typing_extensions,soupsieve,urllib3,pyopenssl,certifi,chardet,idna
orientation = portrait
fullscreen = 1

# Imagens personalizadas
icon.filename = assets/harmonauta_logo.png
presplash.filename = assets/harmonauta_splash.png

# Inclui assets no APK
android.presplash_color = #FFFFFF
android.add_resource = assets
android.resource = assets

# Configurações do Android
android.build_tools_version = 30.0.3
android.accept_sdk_license = True

# Arquiteturas
android.archs = arm64-v8a, armeabi-v7a
android.api = 30
android.minapi = 21

# Usar uma versão mais recente do NDK
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk

# Configurações para evitar problemas de compilação
android.skip_update = False
android.copy_libs = True

[buildozer]
log_level = 2
warn_on_root = 1
target = android

# Configurações específicas para p4a
p4a.branch = master
p4a.recommended_ndk_version = 25b
p4a.bootstrap = sdl2

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE
