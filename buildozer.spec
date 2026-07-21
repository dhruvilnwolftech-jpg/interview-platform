[app]

# (str) Title of your application
title = Interview Platform - User

# (str) Package name
package.name = interview_user

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (source.dir) Source code directory where the main.py live
source.dir = ./user_app

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of excluded patterns, you must list all patterns you want to exclude
source.exclude_patterns = tests, bin, build, .git, dist, buildozer.spec

# (list) Garden requirements of the project
# Better to quote the garden package as str
garden_requirements = 

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Permissions
android.permissions = INTERNET,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
#android.ndk = 21b

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android app theme, default is ok for Kivy-based application
# android.theme = "@android:style/Theme.NoTitleBar"

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) Enable AndroidX support
android.enable_androidx = True

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should request the permission INTERNET
#android.uses_internet = False

# (bool) If the app uses WebView, add it!
#android.features = android.hardware.usb.host

# (list) Pattern to whitelist for the whole project
#android.whitelist = lib-dynload/termios.so

# (bool) If True, then skip trying to update binaries
android.skip_update = False

# (bool) If True, then automatically accept SDK license agreements
android.accept_sdk_license = True

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
#android.add_src = 

# (list) Pattern to whitelist (see buildozer file format)
#android.whitelist = lib-dynload/collections.so

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) The minimum supported Android SDK version (integer)
#android.api = 21

# (str) The minimum supported Android API, when using --requirements. If the value
# is higher than android.minapi, then android.api will be used.
# android.minsdk = 21

# (bool) Copy library instead of making a libpymodules.so (default True)
#android.copy_libs = 1

# (bool) Use the system Kivy bootstrap instead of downloading it.
#android.skip_update = False

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Copy the asset directory from desktop/source/android/files/assets to the
# <build>/src/main/assets, it is used by the Android app to store asset. If this
# is 1, it means you're trying to aggregate as many files as the proof of concept
# android.add_assets = 

# (str) Android add support for SimpleHTTP Server on port 6666
# android.add_http = True

# Python for android (p4a) specific lines

# (bool) Indicate if the bootstrap is using the setup.py file to parse
# requirements instead of using environment.yml for p4a recipes.
# android.p4a_bootstrap = True

# (list) python for android white-list
#p4a.whitelist = lib-dynload/termios.so

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
#p4a.port = 

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning of buildozer when it's deprecated python
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. where the built APK is put)
# bin_dir = ./bin
