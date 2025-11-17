from pathlib import Path
from src.Beta_VH_Map import main as map_main


def test_generate_map_cli_direct():
    # Ensure Haven-UI dist exists
    ui_root = Path('Haven-UI')
    (ui_root / 'dist').mkdir(parents=True, exist_ok=True)

    out_path = ui_root / 'dist' / 'VH-Map.html'
    data_file = ui_root / 'data' / 'haven_ui.db'
    # Run map generator directly (CLI-style) using the mapped DB
    argv = ["--no-open", "--out", str(out_path), "--data-file", str(data_file), "--limit", "5"]
    map_main(argv)

    assert out_path.exists(), "Map was not generated in Haven-UI/dist"
    content = out_path.read_text(encoding='utf-8')
    assert '<html' in content.lower()
