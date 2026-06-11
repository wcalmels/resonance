# resonance (core)

Editor-agnostic Python package. Install:

```bash
pip install -e .
```

## CLI

```bash
resonance context file.py --mode tests --compare
resonance generate --bot TestBot --task "..." --file file.py --output out.py
resonance module --description "..." --output-dir output/feature
```

## Library

```python
from resonance import ContextSelector, run_bot, generate, ProjectSpec
```
