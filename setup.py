import setuptools

install_requires = ""

with open("requirements.txt") as f:
    content = f.read()
    install_requires = content.splitlines()

setuptools.setup(
    name="discord-ext-events",
    version="1.0a",
    author="Example Author",
    description="Discord.py extension that extends functionality for checks "
                "across events ",
    url="https://github.com/cyrus01337/events",
    license="Unlicense",
    python_requires=">=3.5.3",
    install_requires=install_requires,
    packages=["discord.ext.events"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Unlicense License",
        "Operating System :: OS Independent",
    ]
)
