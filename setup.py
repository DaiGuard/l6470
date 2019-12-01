from setuptools import setup, find_packages

setup(
    name='l6470',
    version='1.0.0',
    description='STM L6470 stepping motor drvier control library',
    long_description='',
    author='DaiGuard',
    author_email='',
    url='https://github.com/DaiGuard/l6470',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        "Programing Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operation System :: Ubuntu 18.04"
    ],
    install_requires=[
        'spidev',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
    test_suite='sample_run.suite',
)