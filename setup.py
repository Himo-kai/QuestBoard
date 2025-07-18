from setuptools import setup, find_packages

setup(
    name="questboard",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'Flask>=3.0.0',
        'Flask-SQLAlchemy>=3.1.1',
        'Flask-Login>=0.6.2',
        'Flask-Migrate>=4.0.5',
        'python-dotenv>=1.0.0',
    ],
)
