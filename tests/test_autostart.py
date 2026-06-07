from jarvis.autostart import launchd, manager, systemd_user, windows_task


def test_launch_command_runs_voice_mode():
    cmd = manager.launch_command()
    assert "-m jarvis voice" in cmd


def test_systemd_unit_includes_exec_and_install_target():
    unit = systemd_user.unit_text("/usr/bin/python -m jarvis voice")
    assert "ExecStart=/usr/bin/python -m jarvis voice" in unit
    assert "WantedBy=default.target" in unit
    assert "Restart=on-failure" in unit


def test_launchd_plist_includes_label_and_args():
    plist = launchd.plist_text("/usr/bin/python -m jarvis voice")
    assert "com.jarvis.assistant" in plist
    assert "<string>/usr/bin/python</string>" in plist
    assert "<string>voice</string>" in plist
    assert "<key>RunAtLoad</key>" in plist


def test_windows_task_command_is_onlogon():
    cmd = windows_task.create_command("python -m jarvis voice")
    assert cmd[:2] == ["schtasks", "/Create"]
    assert "ONLOGON" in cmd
    assert "JarvisAssistant" in cmd


def test_manager_rejects_unknown_action():
    assert "Unknown autostart action" in manager.run("frobnicate")
