#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import socket

import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import Adafruit_DHT
import particle_sensor

LOGGER = logging.getLogger(__name__)

HOST_NAME = socket.gethostname()

# BCM pin layout
SET_PIN = 27
RESET_PIN = 17

def make_message(name, value):
    return {'topic': "%s/plantower/%s" % (HOST_NAME, name),
            'payload': value,
            'retain': False,
            'qos': 0}


class MQTTPublisher:
    def __init__(self, hostname):
        self.hostname = hostname

    def handle_data(self, data):
        msgs = [
            make_message('PM_1_0', float(data['PM 1.0'])),
            make_message('PM_2_5', float(data['PM 2.5'])),
            make_message('PM_10', float(data['PM 10'])),
            make_message('DB_0_3', float(data['DB 0.3'])),
            make_message('DB_0_5', float(data['DB 0.5'])),
            make_message('DB_1_0', float(data['DB 1.0'])),
            make_message('DB_2_5', float(data['DB 2.5'])),
            make_message('DB_5_0', float(data['DB 5.0'])),
            make_message('DB_10_0', float(data['DB 10.0'])),
        ]

        humidity, temperature = Adafruit_DHT.read(Adafruit_DHT.DHT22, 22)
        if temperature:
            msgs.append(make_message('temperature', temperature))

        if humidity:
            msgs.append(make_message('humidity', humidity))

        LOGGER.info("Temperature: %0.1f \tHumidity: %0.1f\tPM 1.0: %s \tPM 2.5: %s \tPM 10: %s",
                    temperature or 0.0, humidity or 0.0, data['PM 1.0'], data['PM 2.5'], data['PM 10'])

        try:
            publish.multiple(msgs, hostname=self.hostname)
        except Exception as e:
            LOGGER.exception(e)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help="Increase verbosity (specify multiple times for more)")
    parser.add_argument(
        '--serial', action='store', default='/dev/ttyS0',
        help="The serial port to listen to data from the particle sensor on")
    parser.add_argument(
        '--hostname', action='store', required=True,
        help="The host to publish data to")

    args = parser.parse_args()

    log_level = logging.WARNING
    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(name)s %(levelname)s %(message)s')

    handler = MQTTPublisher(args.hostname)
    sensor = particle_sensor.PySerialCollector(
        args.serial,
        particle_sensor.SUPPORTED_SENSORS["plantower,pms7003"],
        handler.handle_data)

    try:
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(SET_PIN, GPIO.OUT)
        GPIO.output(SET_PIN, GPIO.HIGH)

        GPIO.setup(RESET_PIN, GPIO.OUT)
        GPIO.output(RESET_PIN, GPIO.HIGH)

        sensor.run()
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
