"""Check the real console launcher without running the crew or using API credits."""
import os
import subprocess
import sys
import unittest


class ConsoleExitTest(unittest.TestCase):
    def test_completed_crew_exits_successfully(self):
        program = '''
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch
import engineering_team.main as main

with TemporaryDirectory() as directory:
    sandbox = Path(directory) / "sandbox"
    sandbox.mkdir()
    (sandbox / "pyproject.toml").write_text("[project]\\nname = 'sandbox'\\n")
    with patch.object(main, "SANDBOX_DIR", sandbox), patch.object(main, "EngineeringTeam") as team:
        team.return_value.crew.return_value.kickoff.return_value = object()
        runpy.run_path(str(Path(sys.executable).parent / "run_crew"), run_name="__main__")
'''
        result = subprocess.run(
            [sys.executable, '-B', '-c', program],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, 'OTEL_SDK_DISABLED': 'true',
                 'CREWAI_TELEMETRY_ENABLED': 'false'},
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
