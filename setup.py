from setuptools import setup, find_packages

setup(
    name="freelancer_export_script",
    version="1.0.0",
    py_modules=["main"],
    install_requires=[
        "discord.py",
        "colorlog",
    ],
    entry_points={
        "console_scripts": [
            "freelancer_export_script = main:main", 
        ],
    },
)