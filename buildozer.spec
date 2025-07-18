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

# Configurações do Android
android.build_tools_version = 30.0.3
android.accept_sdk_license = True

# Arquiteturas
android.archs = arm64-v8a, armeabi-v7a
android.api = 30
android.minapi = 21

# Configurações do Gradle
android.gradle_dependencies = 'com.android.tools.build:gradle:7.2.2'

# Otimizações
android.enable_shrink = True
android.enable_proguard = True
android.allow_backup = False
android.uses_clear_text_traffic = False

# Forçar o uso do libffi pré-compilado
android.use_prebuilt_libffi = True

# Usar uma versão mais recente do NDK
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk

# Configurações adicionais para evitar problemas de compilação
android.p4a_dir = /home/runner/.local/lib/python3.9/site-packages/pythonforandroid