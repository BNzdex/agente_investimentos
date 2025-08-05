from setuptools import setup, find_packages

setup(
    name="agente-ia-investimentos",
    version="1.0.0",
    description="Agente de IA para análise de investimentos com web scraping",
    author="Time AI Investimentos",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "pandas>=1.5.0", 
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "beautifulsoup4>=4.11.0",
        "yfinance>=0.2.0",
        "plotly>=5.10.0",
        "textblob>=0.17.0",
        "aiohttp>=3.8.0",
        "lxml>=4.9.0",
        "scikit-learn>=1.1.0",
        "openpyxl>=3.0.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)