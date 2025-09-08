import os
import tempfile


class AuthFile:
    """
    Create a temporary file for --auth-user-pass with username/password.
    WARNING: this writes credentials in clear text. Use only for demos/tests.
    The file is deleted on .close() or garbage collection.
    """

    def __init__(self, username: str, password: str):
        fd, path = tempfile.mkstemp(text=True)
        with os.fdopen(fd, "w") as f:
            f.write((username or "") + "\n" + (password or "") + "\n")
        self.path = path

    def close(self):
        try:
            if self.path and os.path.exists(self.path):
                os.remove(self.path)
        finally:
            self.path = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

