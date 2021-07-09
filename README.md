# ciptools
Our standard library of functions.

## pyenv

It is recommended that you use [pyenv](https://github.com/pyenv/pyenv) to work with this library. These instructions
will show you how to install `pyenv` on macOS and then will assume that you have `pyenv` installed.

First, install HomeBrew:

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Then install `pyenv` and `pyenv-virtualenv`:

    brew install pyenv pyenv-virtualenv

Add this to your `.zprofile` to make it all work and then restart your terminal to get it all working again:

    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv virtualenv-init -)"

Now you're going to want to install some version of Python. This library aims to support Python 3.7 as that is the
default version of Python in Debian 10 (aka "buster"). When Debian 11 (aka "bullseye") becomes generally available
then this library will move to require Python 3.9.

    pyenv install 3.7.3
    pyenv install 3.9.2

In order to use these installed versions you have two options. The first is that you can put a file into the current
directory called `.python-version` and make it contain the version that you want to use when in that directory. The
second is that you can set a "global" version which will be used whenever a `.python-version` file is not found. We
will do both to set a global version and then to set a specific version for this project. 

    pyenv global 3.9.2
    echo "3.7.3" > .python-version

The only problem with the `.python-version` file is that IDEs like PyCharm and IntelliJ completely ignore it. So,
when you load this project in those IDEs you will have to manually choose the correct version of Python to use as the
project's SDK.

## poetry

This library uses [Python Poetry](https://python-poetry.org/) for builds, tests, and deployment. To install the `poetry`
command, after setting up `pyenv`, run these commands:

    # ensure that you are using pyenv by verifying that pip is coming from ~/.pyenv/shims/pip and that the python
    # version is the same as that specified either as global or in a ".python-version" file in the project directory.
    which pip
    pip --version 
    pip install poetry

To pull this project's dependencies down you can run this command:

    poetry install

To run lints and tests you can run this command:

    poetry run pytest

To update dependencies you can run this command:

    poetry update

Additionally, any time that you push to GitHub the tests will automatically run.

## Using in your program

If you want to add this to your project you should add our custom PyPi server to your configuration. If you are using
pip then pass `--extra-index-url https://uwcip.github.io/pypi/simple` or set the environment variable
`PIP_EXTRA_INDEX_URL==https://myorg.github.io/mypypi/simple`. Then you can install like this:

    pip install ciptools
    # or
    pip install ciptools --extra-index-url https://uwcip.github.io/pypi/simple

If you're using [poetry](https://python-poetry.org/) then simply add this to your `pyproject.toml` file:

```toml
[[tool.poetry.source]]
name = "uwcip"
url = "https://uwcip.github.io/pypi/simple/"
```

Then you can install like this:

    poetry add ciptools
