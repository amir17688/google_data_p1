from setuptools import setup, find_packages

setup(
    name='django-db-tools',
    version='0.0.1',
    description='A read only mode tool for your database',
    long_description=open('README.rst').read(),
    # Get more strings from http://www.python.org/pypi?:action=list_classifiers
    author='Craig Kerstiens',
    author_email='craig.kerstiens@gmail.com',
    url='https://github.com/craigkerstiens/django-db-tools',
    download_url='https://github.com/craigkerstiens/django-db-tools/downloads',
    license='BSD',
    packages=find_packages(exclude=('tests', 'example')),
    tests_require=[
        'django>=1.3,<1.5',
    ],
    include_package_data=True,
    zip_safe=False,  # because we're including media that Django needs
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
