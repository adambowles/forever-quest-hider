"""Exercise the actual publication shell block without publishing anything."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ReleaseTests(unittest.TestCase):
    def publish(self, existing, upload_fails=False):
        text = (ROOT / '.github/workflows/release.yml').read_text()
        block = text.split('      - name: Publish installable addon\n', 1)[1].split('        run: |\n', 1)[1]
        script = '\n'.join(line[10:] for line in block.splitlines())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'dist').mkdir()
            (root / 'dist/addon.zip').touch()
            gh = root / 'gh'
            gh.write_text('''#!/bin/bash
printf '%s\\n' "$*" >> "$CALLS"
case "$2" in
  view) exit "$VIEW_STATUS" ;;
  upload) exit "$UPLOAD_STATUS" ;;
esac
''')
            gh.chmod(0o755)
            env = dict(os.environ, PATH=directory + ':' + os.environ['PATH'],
                       CALLS=str(root / 'calls'), VIEW_STATUS='0' if existing else '1',
                       UPLOAD_STATUS='1' if upload_fails else '0', RELEASE_TAG='v0.1.0')
            result = subprocess.run(['bash', '-e', '-c', script], cwd=root, env=env, capture_output=True)
            return result.returncode, (root / 'calls').read_text().splitlines()

    def test_existing_release_uploads_without_recreating(self):
        code, calls = self.publish(True)
        self.assertEqual(code, 0)
        self.assertEqual(calls, ['release view v0.1.0', 'release upload v0.1.0 dist/addon.zip --clobber'])

    def test_new_release_creates_then_uploads(self):
        code, calls = self.publish(False)
        self.assertEqual(code, 0)
        self.assertIn('release create v0.1.0 --verify-tag', calls[1])
        self.assertIn('release upload', calls[2])

    def test_upload_failure_is_not_reported_as_success(self):
        code, _ = self.publish(True, True)
        self.assertNotEqual(code, 0)
