from setuptools import setup, find_packages

setup(
    name='pyMOOGi',
    version='1.0.0',
    url='https://github.com/madamow/pymoogi',
    license='MIT',
    author='Monika Adamow',
    author_email='madamow@icloud.com',
    description='Interactive MOOG wrapper',
    entry_points = {
        'console_scripts': ['pymoogi = pymoogi.__main__:main']
        },
    packages=find_packages()
)
