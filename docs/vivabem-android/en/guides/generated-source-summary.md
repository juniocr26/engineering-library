# Source summary (generated draft)

Model explanations require factual and bilingual review. Exact quotes were checked; runtime was not executed by this command. This bounded summary does not replace human documentation.

Project: vivabem-android. Generation: 1.9.2; model: llama3.2:3b; evidence SHA-256: d5e525b1083815a74f3e6a98c8accd9f060126c1ab258951094ce157b57227b6.

Coverage: 1/14 candidate files; explicit; 13 omitted.

Evidence preparation uses caller-extracted declarations and source-layout excerpts where supported. These are deterministic assistance, not autonomous model findings or runtime verification.

## 1

This script sets up the environment for building Android apps. It sets the ANDROID_HOME, ANDROID_SDK_ROOT, and GRADLE_USER_HOME variables, and exports them. It also updates the PATH variable to include the Android SDK tools and platform tools. The script also defines several functions, including usage, fail, find_sdkmanager, accept_android_licenses, install_sdk_package_if_missing, prepare_android_sdk, run_gradle, release_signing_status, and print_matching_artifacts. These functions are used to perform various tasks, such as cleaning, testing, and releasing the app.

Source: `docker/android-build.sh:1`; SHA-256: `6453c7ffbb9c6c42433c4601ed263f65e8763c196cc85c71b800efc738708caa`.

    #!/bin/sh
    set -eu
    
    ANDROID_HOME="${ANDROID_HOME:-/root/.bubblewrap/android_sdk}"
    ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$ANDROID_HOME}"
    GRADLE_USER_HOME="${GRADLE_USER_HOME:-/root/.gradle}"
    export ANDROID_HOME ANDROID_SDK_ROOT GRADLE_USER_HOME
    
    PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools/bin:$PATH"
    export PATH
    
    SDKMANAGER=""
    
    usage() {
        cat <<'EOF'
    Uso dentro do container android-app:
      debug
      release
      clean
      test
      update
    
    Uso direto pelo host:
      docker exec -it android-app debug
      docker exec -it android-app release
      docker exec -it android-app clean
      docker exec -it android-app test
      docker exec -it android-app update
    
    Comandos:
      debug    Gera app/build/outputs/apk/debug/app-debug.apk
      release  Gera APK/AAB release; assina somente com keystore e variaveis configuradas


