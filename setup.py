#!/usr/bin/env python3
"""
Setup.py para Sistema de Finanzas SRI Ecuador
Instalación alternativa para Replit
"""

from setuptools import setup, find_packages

# Leer requirements.txt
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="finanzas-sri-ecuador",
    version="1.0.0",
    description="Sistema completo de finanzas personales para deducciones SRI Ecuador",
    author="Emilio Arauz",
    author_email="tu-email@example.com",
    url="https://github.com/earauzt/finanzas-sri-ecuador",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    entry_points={
        'console_scripts': [
            'finanzas-sri=main:main',
        ],
    },
    package_data={
        'finanzas_sri': [
            'templates/*.html',
            'static/css/*.css',
            'static/js/*.js',
        ],
    },
    zip_safe=False,
) 