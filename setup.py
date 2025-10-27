

# # In setup.py
# from setuptools import setup, find_packages

# setup(
#     name="blonde-cli",
#     version="0.1.3",
#     packages=find_packages(),
#     py_modules=["cli", "utils"],
#     install_requires=[
#         "typer",
#         "rich",
#         "pyyaml",
#         "tenacity",
#         "python-dotenv",
#         "tree-sitter",
#         "tree-sitter-languages",
#         "openai",
#         "requests",
#         "python-magic",
#     ],
#     entry_points={
#         "console_scripts": [
#             "blnd=cli:app",
#         ],
#     },
#     package_data={
#         "": ["*.py"],
#     },
# )


from setuptools import setup, find_packages

setup(
    name="blonde-cli",
    version="0.1.3",
    author="Amardeep",
    author_email="amarbavi12345@gmail.com",
    description="AI-powered code assistant CLI",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_GITHUB/blonde-cli",
    packages=find_packages(exclude=("tests",)),
    py_modules=["cli", "utils", "model_selector", "memory", "tools", "server", "agentic_tools"],
    python_requires=">=3.10",
    install_requires=[
        "typer>=0.9.0",
        "rich",
        "pyyaml",
        "tenacity",
        "python-dotenv",
        "tree-sitter",
        "tree-sitter-languages",
        "openai",
        "requests",
        "python-magic",
    ],
    entry_points={
        "console_scripts": [
            "blnd=cli:app",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
