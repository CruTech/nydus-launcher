#!/usr/bin/python3

import subprocess

mc_username = "Get from server"

mc_uuid = "Get from server"

mc_access_tok = "Get from server"

cpjars = "/home/crutech/.minecraft/libraries/com/github/oshi/oshi-core/6.4.10/oshi-core-6.4.10.jar:/home/crutech/.minecraft/libraries/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar:/home/crutech/.minecraft/libraries/com/google/guava/failureaccess/1.0.1/failureaccess-1.0.1.jar:/home/crutech/.minecraft/libraries/com/google/guava/guava/32.1.2-jre/guava-32.1.2-jre.jar:/home/crutech/.minecraft/libraries/com/ibm/icu/icu4j/73.2/icu4j-73.2.jar:/home/crutech/.minecraft/libraries/com/mojang/authlib/6.0.54/authlib-6.0.54.jar:/home/crutech/.minecraft/libraries/com/mojang/blocklist/1.0.10/blocklist-1.0.10.jar:/home/crutech/.minecraft/libraries/com/mojang/brigadier/1.2.9/brigadier-1.2.9.jar:/home/crutech/.minecraft/libraries/com/mojang/datafixerupper/7.0.14/datafixerupper-7.0.14.jar:/home/crutech/.minecraft/libraries/com/mojang/logging/1.2.7/logging-1.2.7.jar:/home/crutech/.minecraft/libraries/com/mojang/patchy/2.2.10/patchy-2.2.10.jar:/home/crutech/.minecraft/libraries/com/mojang/text2speech/1.17.9/text2speech-1.17.9.jar:/home/crutech/.minecraft/libraries/commons-codec/commons-codec/1.16.0/commons-codec-1.16.0.jar:/home/crutech/.minecraft/libraries/commons-io/commons-io/2.15.1/commons-io-2.15.1.jar:/home/crutech/.minecraft/libraries/commons-logging/commons-logging/1.2/commons-logging-1.2.jar:/home/crutech/.minecraft/libraries/io/netty/netty-buffer/4.1.97.Final/netty-buffer-4.1.97.Final.jar:/home/crutech/.minecraft/libraries/io/netty/netty-codec/4.1.97.Final/netty-codec-4.1.97.Final.jar:/home/crutech/.minecraft/libraries/io/netty/netty-common/4.1.97.Final/netty-common-4.1.97.Final.jar:/home/crutech/.minecraft/libraries/io/netty/netty-handler/4.1.97.Final/netty-handler-4.1.97.Final.jar:/home/crutech/.minecraft/libraries/io/netty/netty-resolver/4.1.97.Final/netty-resolver-4.1.97.Final.jar:/home/crutech/.minecraft/libraries/io/netty/netty-transport-classes-epoll/4.1.97.Final/netty-transport-classes-epoll-4.1.97.Final.jar:/home/crutech/.minecraft/libraries/io/netty/netty-transport-native-epoll/4.1.97.Final/netty-transport-native-epoll-4.1.97.Final-linux-aarch_64.jar:/home/crutech/.minecraft/libraries/io/netty/netty-transport-native-epoll/4.1.97.Final/netty-transport-native-epoll-4.1.97.Final-linux-x86_64.jar:/home/crutech/.minecraft/libraries/io/netty/netty-transport-native-unix-common/4.1.97.Final/netty-transport-native-unix-common-4.1.97.Final.jar:/home/crutech/.minecraft/libraries/io/netty/netty-transport/4.1.97.Final/netty-transport-4.1.97.Final.jar:/home/crutech/.minecraft/libraries/it/unimi/dsi/fastutil/8.5.12/fastutil-8.5.12.jar:/home/crutech/.minecraft/libraries/net/java/dev/jna/jna-platform/5.14.0/jna-platform-5.14.0.jar:/home/crutech/.minecraft/libraries/net/java/dev/jna/jna/5.14.0/jna-5.14.0.jar:/home/crutech/.minecraft/libraries/net/sf/jopt-simple/jopt-simple/5.0.4/jopt-simple-5.0.4.jar:/home/crutech/.minecraft/libraries/org/apache/commons/commons-compress/1.26.0/commons-compress-1.26.0.jar:/home/crutech/.minecraft/libraries/org/apache/commons/commons-lang3/3.14.0/commons-lang3-3.14.0.jar:/home/crutech/.minecraft/libraries/org/apache/httpcomponents/httpclient/4.5.13/httpclient-4.5.13.jar:/home/crutech/.minecraft/libraries/org/apache/httpcomponents/httpcore/4.4.16/httpcore-4.4.16.jar:/home/crutech/.minecraft/libraries/org/apache/logging/log4j/log4j-api/2.22.1/log4j-api-2.22.1.jar:/home/crutech/.minecraft/libraries/org/apache/logging/log4j/log4j-core/2.22.1/log4j-core-2.22.1.jar:/home/crutech/.minecraft/libraries/org/apache/logging/log4j/log4j-slf4j2-impl/2.22.1/log4j-slf4j2-impl-2.22.1.jar:/home/crutech/.minecraft/libraries/org/jcraft/jorbis/0.0.17/jorbis-0.0.17.jar:/home/crutech/.minecraft/libraries/org/joml/joml/1.10.5/joml-1.10.5.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl-freetype/3.3.3/lwjgl-freetype-3.3.3.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl-freetype/3.3.3/lwjgl-freetype-3.3.3-natives-linux.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl-glfw/3.3.3/lwjgl-glfw-3.3.3.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl-glfw/3.3.3/lwjgl-glfw-3.3.3-natives-linux.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl-jemalloc/3.3.3/lwjgl-jemalloc-3.3.3.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl-jemalloc/3.3.3/lwjgl-jemalloc-3.3.3-natives-linux.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl-openal/3.3.3/lwjgl-openal-3.3.3.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl-openal/3.3.3/lwjgl-openal-3.3.3-natives-linux.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl-opengl/3.3.3/lwjgl-opengl-3.3.3.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl-opengl/3.3.3/lwjgl-opengl-3.3.3-natives-linux.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl-stb/3.3.3/lwjgl-stb-3.3.3.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl-stb/3.3.3/lwjgl-stb-3.3.3-natives-linux.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl-tinyfd/3.3.3/lwjgl-tinyfd-3.3.3.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl-tinyfd/3.3.3/lwjgl-tinyfd-3.3.3-natives-linux.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl/3.3.3/lwjgl-3.3.3.jar:/home/crutech/.minecraft/libraries/org/lwjgl/lwjgl/3.3.3/lwjgl-3.3.3-natives-linux.jar:/home/crutech/.minecraft/libraries/org/lz4/lz4-java/1.8.0/lz4-java-1.8.0.jar:/home/crutech/.minecraft/libraries/org/slf4j/slf4j-api/2.0.9/slf4j-api-2.0.9.jar:/home/crutech/.minecraft/versions/1.20.6/1.20.6.jar"

# 1 cpjars 2 username 3 uuid 4 accessToken
mc_launch_command = "java -cp {} -Xmx2G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M -Dlog4j.configurationFile=/home/crutech/.minecraft/assets/log_configs/client-1.12.xml net.minecraft.client.main.Main --username {} --version 1.20.6 --gameDir /home/crutech/.minecraft --assetsDir /home/crutech/.minecraft/assets --assetIndex 16 --uuid {} --accessToken {} --clientId +M7pS1g4bzXopTzryGLaMdNhjVW6GGpAxEH0QrOsiP4ZNElf89tRFA/rsWP3a5Pm --xuid 2535427717368992 --userType msa --versionType release --quickPlayPath /home/crutech/.minecraft/quickPlay/java/1723272866743.json".format(cpjars, mc_username, mc_uuid, mc_access_tok)

mc_launch_command = mc_launch_command.split(" ")

subprocess.run(mc_launch_command)
