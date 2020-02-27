
import setuptools


long_description = """
A academic resource crawler, including web of science, baidu scholar and etc . 
"""


setuptools.setup(
    name='tortoises',
    version='0.0.2',
    description='A toolkit for capturing network academic resources',
    long_description=long_description,
    author='dandanlemuria',
    author_email='18110980003@fudan.edu.cn',
    url='https://github.com/LemuriaChen/tortoise',
    license="MIT",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
      ],
    keywords='crawler, web of science, scholar',
    packages=setuptools.find_packages(),
    install_requires=[
        'selenium',
    ],
)
