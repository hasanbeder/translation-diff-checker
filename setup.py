from setuptools import setup, find_packages
import os

def read_version():
    version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
    with open(version_file, 'r') as f:
        return f.read().strip()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="translation-diff-checker",
    version=read_version(),
    author="Hasan Beder",
    description="A tool to compare and analyze translation files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hasanbeder/translation-diff-checker",
    project_urls={
        "X (Twitter)": "https://x.com/hasanbeder",
        "Bug Tracker": "https://github.com/hasanbeder/translation-diff-checker/issues"
    },
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Internationalization",
    ],
    python_requires='>=3.7',
    install_requires=[
        # Add dependencies from requirements.txt
    ],
    entry_points={
        'console_scripts': [
            'translation-diff-checker=translation_diff_checker:main',
        ],
    },
)
