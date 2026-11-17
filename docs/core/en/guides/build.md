# Home Assistant Core — Python package requirements

Temporary reviewed partial model excerpt. Important contracts remain undocumented. Not approved for publication; source quotes and full review evidence are preserved separately.

Source revision: `67ec6a4b7dcaed80b59930be6744f4944b5073e3`.

## 1

The Home Assistant project requires setuptools==84.0.0 for its build system.

Source: `pyproject.toml:1`; SHA-256: `d64a5d5da6d8bfaa4b6add2d353c0dbabac0343cbf50962edb3290d6631bd27f`.

    [build-system]
    requires = ["setuptools==84.0.0"]
    build-backend = "setuptools.build_meta"
    
    [project]
    name = "homeassistant"
    version = "2026.12.0.dev0"
    license = "Apache-2.0"
    license-files = ["LICENSE*", "homeassistant/backports/LICENSE*"]
    description = "Open-source home automation platform running on Python 3."
    readme = "README.rst"
    authors = [
      { name = "The Home Assistant Authors", email = "hello@home-assistant.io" },
    ]


