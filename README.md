# slamtrader

A set of scripts to manage my portfolio

## Quickstart

### Requirements

Install pyenv

```
$ brew install pyenv
```

Add this to `.zshrc`

```
if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init -)"
fi
```

Reload zsh

Install python

```
$ pyenv install 3.8.2
$ pyenv local 3.8.3
$ python --version
Python 3.8.2
```

Install pipx

```
$ brew install pipx
$ pipx ensurepath
```

Install poetry

```
$ pipx install poetry
```

Install nox

```
$ pipx install nox
```

### Running

```
$ poetry install
$ poetry run mish
```

### Testing

Run the full test suite

```
$ nox
```
