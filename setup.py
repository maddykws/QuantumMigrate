from setuptools import setup, find_packages

setup(
    name="quantum-migrate",
    version="0.1.0",
    description="Scan codebases for quantum-vulnerable cryptography and get NIST post-quantum migration guidance.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="QuantumMigrate Contributors",
    url="https://github.com/maddykws/QuantumMigrate",
    packages=find_packages(exclude=["tests*", "web*"]),
    python_requires=">=3.11",
    install_requires=[
        "anthropic>=0.40.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "gitpython>=3.1.40",
        "requests>=2.31.0",
    ],
    extras_require={
        "web": ["streamlit>=1.32.0"],
    },
    entry_points={
        "console_scripts": [
            "quantummigrate=quantum_migrate.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries",
    ],
    keywords="post-quantum cryptography security scanner nist pqc",
)
