import os
import subprocess
import threading
import signal
from typing import Callable, Optional
from auth_file import AuthFile


class OpenVPNController:
    """
    Process/controller layer for OpenVPN.
    - Builds the command line
    - Starts/stops the subprocess
    - Streams logs line-by-line to a callback
    The GUI should only call start()/stop() and listen to callbacks.
    """

    def __init__(
        self,
        on_log: Callable[[str], None],
        on_connected: Callable[[], None],
        on_stopped: Callable[[bool], None],
        openvpn_exe: Optional[str] = None,
        verbosity: str = "3",
    ):
        self.on_log = on_log
        self.on_connected = on_connected
        self.on_stopped = on_stopped
        self.openvpn_exe = openvpn_exe or ("openvpn.exe" if os.name == "nt" else "openvpn")
        self.verbosity = verbosity

        self._proc: Optional[subprocess.Popen] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._auth: Optional[AuthFile] = None

    def start(self, config_path: str, username: str = "", password: str = ""):
        """Start OpenVPN with provided config and optional credentials."""
        if self._proc:
            return

        self._auth = AuthFile(username=username, password=password) if (username or password) else None

        cmd = self._build_cmd(config_path, self._auth.path if self._auth else None)
        self.on_log(f"Command: {' '.join(cmd)}")

        try:
            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True
            )
        except FileNotFoundError:
            self.on_log("ERROR: 'openvpn' binary not found in PATH.")
            self._cleanup()
            self.on_stopped(False)
            return

        self._reader_thread = threading.Thread(target=self._read_stdout, daemon=True)
        self._reader_thread.start()

    def stop(self):
        """Stop the OpenVPN process if running."""
        if not self._proc:
            return
        try:
            if os.name == "nt":
                self._proc.terminate()
            else:
                self._proc.send_signal(signal.SIGINT)
            self._proc.wait(timeout=10)
        except Exception as e:
            self.on_log(f"ERROR while stopping: {e}")
        finally:
            self._cleanup()
            self.on_stopped(True)

    # ---- Internals ----
    def _build_cmd(self, config_path: str, auth_path: Optional[str]):
        cmd = [self.openvpn_exe, "--config", config_path, "--verb", self.verbosity]
        if auth_path:
            cmd += ["--auth-user-pass", auth_path]
        return cmd

    def _read_stdout(self):
        """Read stdout and push lines to on_log(). Detect connection state."""
        graceful = True
        try:
            assert self._proc and self._proc.stdout
            for line in self._proc.stdout:
                self.on_log(line.rstrip())
                if "Initialization Sequence Completed" in line:
                    self.on_connected()
        except Exception as e:
            graceful = False
            self.on_log(f"[reader] {e}")
        finally:
            self._cleanup()
            self.on_stopped(graceful)

    def _cleanup(self):
        """Reset state and remove temp files."""
        if self._proc:
            try:
                if self._proc.poll() is None:
                    self._proc.kill()
            except Exception:
                pass
        self._proc = None

        if self._auth:
            self._auth.close()
        self._auth = None
        self._reader_thread = None

