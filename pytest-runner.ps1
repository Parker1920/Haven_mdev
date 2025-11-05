# Pytest Runner Script
# This script allows running pytest from the project root with proper configuration

# Find python executable
$pythonCmd = "python"

# Run pytest with config from config/pytest.ini
& $pythonCmd -m pytest --ini=config/pytest.ini @args

exit $LASTEXITCODE
