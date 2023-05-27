from distutils.core import setup
from distutils.extension import Extension

setup(
    author="Andreas Mueller",
    author_email="t3kcit+wordcloud@gmail.com",
    name='wordcloud',
    version='1.2.1',
    url='https://github.com/amueller/word_cloud',
    description='A little word cloud generator',
    license='MIT',
    ext_modules=[Extension("wordcloud.query_integral_image",
                           ["wordcloud/query_integral_image.c"])],
    scripts=['wordcloud/wordcloud_cli.py'],
    packages=['wordcloud'],
    package_data={'wordcloud': ['stopwords', 'DroidSansMono.ttf']}
)
