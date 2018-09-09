"""Installation script."""
from os import path
from io import open
from setuptools import find_packages, setup

HERE = path.abspath(path.dirname(__file__))

def readme():
    with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
        return f.read().strip()


install_requires = [
    "sregistry[all]==0.0.69"
    ]

tests_require = [
    'pytest>=3.0.0'
    ]

setup(
    name='flow',
    version=0.1,
    description='Experiment pipeline',
    long_description=readme(),
    url='https://github.com/bouthilx/flow.git',
    author='Xavier Bouthillier',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=dict(test=tests_require),
    scripts=[
        'bin/flow-deploy',
        'bin/flow-execute'
        ],
    entry_points={
        'console_scripts': [
            'flow-submit = flow.bin.submit:main',
            'flow-compare = flow.bin.compare:main',
            'flow-analyze = flow.bin.analyze:main'
            ]
        },
    zip_safe=False
)
