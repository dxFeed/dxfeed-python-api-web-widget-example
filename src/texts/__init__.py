from pathlib import Path

TEXTS = dict()

paths = Path(__file__).parent.glob('*.md')
for path in paths:
    with open(path, 'r') as f:
        TEXTS.update({path.stem: f.read()})
