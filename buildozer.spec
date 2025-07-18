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

# Atualize para usar android.archs em vez de android.arch (mais moderno)
android.archs = arm64-v8a, armeabi-v7a
android.api = 30
android.minapi = 21
android.sdk = 24  # Pode ser removido, é depreciado
android.ndk = 25b # Pode ser removido, é depreciado

# Configurações do Gradle
android.gradle_dependencies = 'com.android.tools.build:gradle:7.2.2'

# Otimizações
android.enable_shrink = True
android.enable_proguard = True
android.allow_backup = False
android.uses_clear_text_traffic = False

# Não é necessário especificar paths vazios (remova estas linhas)
# android.sdk_path = 
# android.ndk_path = 
# android.sdk_dir = 
# android.ndk_dir = 

[buildozer]
log_level = 2
warn_on_root = 1
target = android