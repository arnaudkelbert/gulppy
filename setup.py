import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='gulppy',
    version='0.0.1',
    author='Arnaud Kelbert',
    author_email='arnaud.kelbert@gmail.com',
    description='A python plugin library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/arnaudkelbert/gulppy',
    project_urls = {
        "Bug Tracker": "https://github.com/arnaudkelbert/gulppy/issues"
    },
    license='BSD-3-Clause',
    packages=['gulppy', 'gulppy.core'],
    package_data={'gulppy': ['core/*json']},
    install_requires=['pyyaml', 'pandas'],
)