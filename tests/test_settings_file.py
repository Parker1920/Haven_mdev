import json
from pathlib import Path


def test_settings_file_exists_and_has_theme():
    root = Path(__file__).parent.parent
    settings_path = root / 'settings.json'
    assert settings_path.exists(), 'settings.json must exist at repository root'
    data = json.loads(settings_path.read_text(encoding='utf-8'))
    assert 'theme' in data, 'settings.json should contain a top-level theme key'
    theme = data['theme']
    for k in ('bg', 'text', 'card', 'primary'):
        assert k in theme, f"theme must contain {k}"
