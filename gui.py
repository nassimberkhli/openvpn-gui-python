import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from vpn_controller import OpenVPNController


class OpenVPNGui(tk.Tk):
    """
    Tkinter GUI that uses OpenVPNController to start/stop OpenVPN.
    UI-only code lives here; no subprocess logic in the GUI layer.
    """

    def __init__(self):
        super().__init__()
        self.title("OpenVPN Client")
        self.geometry("760x520")

        self.ovpn_path = tk.StringVar(value="")
        self.username = tk.StringVar(value="")
        self.password = tk.StringVar(value="")
        self.status = tk.StringVar(value="Disconnected")

        self.ctrl = OpenVPNController(
            on_log=self._on_log_from_ctrl,
            on_connected=self._on_connected_from_ctrl,
            on_stopped=self._on_stopped_from_ctrl,
        )

        self._build_ui()
        self._log("Ready. Select a .ovpn file and click Connect.")

    def _build_ui(self):
        wrapper = ttk.Frame(self, padding=10)
        wrapper.pack(fill="both", expand=True)

        row1 = ttk.Frame(wrapper)
        row1.pack(fill="x", pady=4)
        ttk.Label(row1, text="OVPN file:", width=16).pack(side="left")
        ttk.Entry(row1, textvariable=self.ovpn_path).pack(side="left", fill="x", expand=True)
        ttk.Button(row1, text="Browse", command=self._browse_ovpn).pack(side="left", padx=6)

        row2 = ttk.Frame(wrapper)
        row2.pack(fill="x", pady=4)
        ttk.Label(row2, text="Username:", width=16).pack(side="left")
        ttk.Entry(row2, textvariable=self.username).pack(side="left", fill="x", expand=True)

        row3 = ttk.Frame(wrapper)
        row3.pack(fill="x", pady=4)
        ttk.Label(row3, text="Password:", width=16).pack(side="left")
        ttk.Entry(row3, textvariable=self.password, show="*").pack(side="left", fill="x", expand=True)

        row4 = ttk.Frame(wrapper)
        row4.pack(fill="x", pady=(6, 8))
        self.btn_connect = ttk.Button(row4, text="Connect", command=self._connect)
        self.btn_disconnect = ttk.Button(row4, text="Disconnect", command=self._disconnect, state="disabled")
        self.btn_connect.pack(side="left")
        ttk.Frame(row4, width=8).pack(side="left")
        self.btn_disconnect.pack(side="left")
        ttk.Label(row4, textvariable=self.status).pack(side="right")

        ttk.Label(wrapper, text="OpenVPN log:").pack(anchor="w", pady=(6, 2))
        self.txt = tk.Text(wrapper, height=20, wrap="none")
        self.txt.pack(fill="both", expand=True)

    def _browse_ovpn(self):
        path = filedialog.askopenfilename(
            title="Choose an .ovpn file",
            filetypes=[("OpenVPN config", "*.ovpn"), ("All files", "*.*")]
        )
        if path:
            self.ovpn_path.set(path)

    def _connect(self):
        """Validate inputs and start the controller."""
        cfg = self.ovpn_path.get().strip()
        if not cfg or not os.path.exists(cfg):
            messagebox.showerror("Error", "Please select a valid .ovpn file.")
            return

        self.status.set("Connecting…")
        self.btn_connect.configure(state="disabled")
        self.btn_disconnect.configure(state="normal")

        self.ctrl.start(config_path=cfg,
                        username=self.username.get(),
                        password=self.password.get())

        self._log(f"Starting OpenVPN with config: {cfg}")

    def _disconnect(self):
        """Ask controller to stop the VPN process."""
        self._log("Stopping VPN connection…")
        self.ctrl.stop()

    def _on_log_from_ctrl(self, line: str):
        self.after(0, lambda: self._log(line.rstrip()))

    def _on_connected_from_ctrl(self):
        self.after(0, lambda: self.status.set("Connected"))

    def _on_stopped_from_ctrl(self, graceful: bool):
        def _update():
            self.status.set("Disconnected")
            self.btn_connect.configure(state="normal")
            self.btn_disconnect.configure(state="disabled")
            if not graceful:
                self._log("Process ended unexpectedly.")
        self.after(0, _update)

    def _log(self, msg: str):
        self.txt.insert("end", msg + "\n")
        self.txt.see("end")

