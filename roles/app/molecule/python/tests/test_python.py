---
import os

molecule_directory = os.path.dirname(os.path.abspath(__file__))
role_directory = os.path.dirname(os.path.dirname(molecule_directory))

infra_files = [
    os.path.join(os.path.dirname(role_directory), "testinfra"),
    os.path.join(molecule_directory, "tests"),
]

infra_path = None
for fp in infra_files:
    if os.path.isdir(fp):
        infra_path = fp
        break

if infra_path is not None and infra_path not in os.environ.get("PYTHONPATH", ""):
    os.environ["PYTHONPATH"] = (
        f"{infra_path}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"
    )

import pytest
import testinfra

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def test_app_user_exists(host):
    user = host.user("app")
    assert user.exists, "app user should exist"


def test_app_user_system(host):
    user = host.user("app")
    assert user.system, "app user should be a system user"


def test_app_base_dir_exists(host):
    f = host.file("/opt/apps")
    assert f.exists, "/opt/apps should exist"
    assert f.is_directory, "/opt/apps should be a directory"
    assert f.user == "app", "/opt/apps should be owned by app"
    assert f.mode == 0o755, "/opt/apps should have mode 0755"


def test_python3_installed(host):
    p = host.package("python3")
    assert p.is_installed, "python3 should be installed"


def test_python3_pip_installed(host):
    p = host.package("python3-pip")
    assert p.is_installed, "python3-pip should be installed"


def test_python3_venv_installed(host):
    p = host.package("python3-venv")
    assert p.is_installed, "python3-venv should be installed"


def test_python3_command_works(host):
    result = host.run("python3 --version")
    assert result.rc == 0, "python3 command should work"


def test_requests_package_installed(host):
    result = host.run("pip3 show requests")
    assert result.rc == 0, "requests package should be installed"
