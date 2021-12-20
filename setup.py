import setuptools

with open('README.md', encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="ProxyTVruAPI",

    version="0.0.3",

    author="Nikita (NIKDISSV)",
    author_email="nikdissv.forever@protonmail.com",

    description="proxytv.ru IPTV Channels Parser and Robot",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/NIKDISSV-Forever/ProxyTVRobot",

    packages=setuptools.find_packages(),

    classifiers=[
        'Programming Language :: Python :: 3.9.7',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

    python_requires='>=3.6',
)
