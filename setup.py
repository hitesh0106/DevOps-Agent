"""DevOps Agent — AI-Powered Infrastructure Automation"""

from setuptools import setup, find_packages

setup(
    name="devops-agent",
    version="1.0.0",
    description="AI-powered DevOps automation agent with ReAct reasoning",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="DevOps Agent Team",
    python_requires=">=3.11",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "langchain>=0.2.0",
        "langchain-anthropic>=0.1.0",
        "fastapi>=0.111.0",
        "uvicorn[standard]>=0.30.0",
        "sqlalchemy>=2.0.30",
        "redis>=5.0.0",
        "chromadb>=0.5.0",
        "pydantic-settings>=2.3.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.27.0",
        "structlog>=24.1.0",
        "rich>=13.7.0",
        "click>=8.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.2.0",
            "pytest-cov>=5.0.0",
            "pytest-asyncio>=0.23.0",
        ],
        "docker": ["docker>=7.1.0"],
        "kubernetes": ["kubernetes>=29.0.0"],
        "all": [
            "docker>=7.1.0",
            "kubernetes>=29.0.0",
            "PyGithub>=2.3.0",
            "slack-sdk>=3.27.0",
            "prometheus-api-client>=0.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "devops-agent=agent.core:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
)
