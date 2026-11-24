# Config casting diagnostic — before revision

At `9b403a0c33f0e2eebba099e9e6aa1c1e9535daec`, the selected `Config._perform_cast` handler catches `TypeError` and `ValueError` from `cast(value)`. Its error message directly reads `cast.__name__`.

Evidence: `starlette/config.py:139–142`. This is a static description of the selected branch, without runtime execution.
