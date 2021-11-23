## Development Instructions

### Setup

Get the code!

```bash
git clone git@github.com:clarify/pyclarify.git
cd pyclarify
```

### Testing

Set up tests for all new functionality.

Initiate unit tests by running the following command from the root directory:

`python -m discover -s tests/`

### Documentation

Build html files of documentation locally by running

```bash
cd docs
make html
```

Documentation will be automatically generated from the numpy-style docstrings in the source code. It is then built and released when changes are merged into master.

### Release version conventions

See https://semver.org/
