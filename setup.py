# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    README = f.read()

with open('LICENSE') as f:
    LICENSE = f.read()

setup(
    name='environmental-sensor',
    version='0.1.0',
    description='An MQTT client which sends particle and temperature data.',
    long_description=README,
    author='Russell Sim',
    author_email='russell.sim@gmail.com',
    url='https://github.com/russell/environmental-sensor',
    license=LICENSE,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'paho-mqtt',
    ],
    entry_points={
        'console_scripts': [
            'es-mqtt = environmental_sensor.cli:main'
        ]
    },
)
