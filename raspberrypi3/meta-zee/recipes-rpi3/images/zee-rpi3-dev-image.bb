#*******************************************************************************
#
# yasperzee v0.1    3'19   c/c++ development tools
#
#*******************************************************************************
require zee-rpi3-base-image.bb
export IMAGE_BASENAME = "zee-rpi3-dev-image"
SUMMARY = "32bit development image for Rpi3"
#*******************************************************************************
# PACKAGE_EXCLUDE = " "

DEV_SDK_INSTALL = " \
    binutils \
    binutils-symlinks \
    coreutils \
    cpp \
    cpp-symlinks \
    diffutils \
    elfutils \
    elfutils-binutils \
    file \
    g++ \
    g++-symlinks \
    gcc \
    gcc-symlinks \
    gdb \
    gdbserver \
    gettext \
    git \
    ldd \
    libstdc++ \
    libstdc++-dev \
    libtool \
    ltrace \
    make \
    pkgconfig \
    strace \
"

IMAGE_INSTALL += " \
    ${DEV_SDK_INSTALL} \
"
#
#disable_unused_services() {
#    rm ${IMAGE_ROOTFS}/etc/rc5.d/S15mountnfs.sh
#}
#
#ROOTFS_POSTPROCESS_COMMAND += " \
#    disable_unused_services ; \
# "
#
