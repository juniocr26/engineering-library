# Home Assistant Core — Requisitos do pacote Python

Trecho parcial temporário do modelo, revisado. Contratos importantes continuam sem documentação. Sem aprovação de publicação; citações do código e evidências completas da revisão ficam preservadas separadamente.

Revisão de origem: `67ec6a4b7dcaed80b59930be6744f4944b5073e3`.

## 1

O projeto Home Assistant exige setuptools==84.0.0 para seu sistema de construção.

Fonte: `pyproject.toml:1`; SHA-256: `d64a5d5da6d8bfaa4b6add2d353c0dbabac0343cbf50962edb3290d6631bd27f`.

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


