from setuptools import setup

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

description = 'Ask not what $ORG can do for you, but what you can do for $ORG'

setup(
    name='asknot-ng',
    version='0.0',
    description=description,
    license='GPLv3+',
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    url='https://github.com/fedora-infra/asknot-ng',
    install_requires=requirements,
    packages=[],
    py_modules=['asknot_lib'],
    entry_points="""
    [babel.extractors]
    asknot = asknot_lib:extract
    """,
    message_extractors = {
        "questions": [
            ('**.yml', 'asknot', None),
        ]
    }
)
