from __future__ import annotations

import setuptools

with open('README.md', encoding='UTF-8') as f:
    long_description = f.read()

setuptools.setup(
    name="PTVRobot",

    version="1.1.0",

    author="Nikita (NIKDISSV)",
    author_email="nikdissv@proton.me",

    description="proxytv.ru IPTV Channels Parser and Robot",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/NIKDISSV-Forever/ProxyTVRobot",

    packages=setuptools.find_packages(),
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Multimedia :: Video',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Typing :: Typed',
    ],

    python_requires='>=3.8',
)
