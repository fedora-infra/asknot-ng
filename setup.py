from setuptools import setup

description = 'Ask not what $ORG can do for you, but what you can do for $ORG'

setup(
    name='asknot-ng',
    version='1.0',
    description=description,
    license='GPLv3+',
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    url='https://github.com/fedora-infra/asknot-ng',
    install_requires=[
        'mako',
        'PyYAML',
        ],
    extras_require={
        'tests': ['nose'],
        },
    packages=[],
    py_modules=['asknot_lib'],

    # This declares our special-case extractor to 'babel', a python l18n tool.
    entry_points="""
    [babel.extractors]
    asknot = asknot_lib:extract
    """,

    # This further declares that babel should use our extractor on yaml files
    # in the questions/ directory.
    message_extractors={
        "questions": [
            ('**.yml', 'asknot', None),
        ]
    }
)
