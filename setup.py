from __future__ import annotations

import setuptools

with open('README.md', encoding='UTF-8') as f:
    long_description = f.read()

setuptools.setup(
    name='proxytv',

    version='1.0.1',

    author='Nikita (NIKDISSV)',
    author_email='nikdissv@proton.me',

    description='proxytv.ru IPTV Channels Parser and Robot (Like ProxyBot)',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/NIKDISSV-Forever/ProxyTVRobot',

    packages=setuptools.find_packages(),
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Video',
        'Topic :: Utilities',
        'Typing :: Typed'
    ],

    python_requires='>=3.8',
    keywords=['ProxyBot', 'IPTV', 'proxytv.ru', 'TV', 'free']
)
