# from setuptools import setup, find_packages

# setup(
#     name="blonde-cli",
#     version="0.1.0",
#     packages=find_packages(),
#     install_requires=[
#         "typer",
#         "openai",
#         "requests",
#     ],
#     entry_points={
#         "console_scripts": [
#             "blnd=cli:app",  # maps "blnd" command to cli.py app
#         ],
#     },
# )



from setuptools import setup, find_packages

setup(
    name="blonde-cli",
    version="0.1.0",
    packages=find_packages(),
    py_modules=["cli", "utils"],  # Explicitly include your modules
    install_requires=[
        "typer",
        "openai", 
        "requests",
        "pyyaml",   # <-- add this
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "blnd=cli:app",
        ],
    },
    package_data={
        "": ["*.py"],
    },
)