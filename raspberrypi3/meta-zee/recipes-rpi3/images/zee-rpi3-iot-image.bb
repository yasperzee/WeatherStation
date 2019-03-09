#*******************************************************************************
#
# yasperzee v0.1    3'19    mosquitto: mqtt server
#
#*******************************************************************************
LICENSE  = "MIT"
require zee-rpi3-base-image.bb
export IMAGE_BASENAME = "zee-rpi3-iot-image"
SUMMARY = "32bit IoT / mosquitto image for Rpi3"
#*******************************************************************************
# PACKAGE_EXCLUDE = " "

MQTT = " \
    libmosquitto1 \
    libmosquittopp1 \
    mosquitto \
    mosquitto-dev \
    mosquitto-clients \
    python-paho-mqtt \
"

IMAGE_INSTALL += " \
    ${MQTT} \
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
