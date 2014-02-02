from setuptools import setup

APP = ['starcheat.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': True, 'includes': ['sip'], 'iconfile': '../mac/icon.icns'}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
