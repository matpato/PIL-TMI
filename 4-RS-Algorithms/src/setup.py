from os.path import join, dirname
from setuptools import setup

def read(fname):
    try:
        return open(join(dirname(__file__), fname)).read()
    except:
        return 'See https://github.com/matpato/PIL-TMI/blob/main/README.md'


setup(
    name='PIL-TMI',
    version='0.1',
    author='Matilde Pato, Renato Marcelo, Nuno Datia',
    author_email='matilde.pato@gmail.com',
    maintainer='Matilde Pato'
    description='Patient Information Leaflets for implicit feedback datasets',
    long_description=read('README.md'),
    license='MIT License',
    keywords=['recommendation system', 'implicit feedback', 'semantic similarity', 'ontologies'],
    url='https://github.com/matpato/PIL-TMI',
    # download_url='url here',
    install_requires=['numpy', 'scipy', 'pandas', 'ssmpy', 'mysql-connector-python==8.0.11', 'pymysql'],
    classifiers=['Development Status :: 1 - alpha',
                 'Natural Language :: English',
                 'Intended Audience :: Science/Research',
                 'Programming Language :: Python :: 3.11',
                 'License :: MIT License'
                 ],
    include_package_data=True
)