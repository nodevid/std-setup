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


def test_app_user_shell(host):
    user = host.user("app")
    assert user.shell == "/bin/bash", "app user shell should be /bin/bash"


def test_app_base_dir_exists(host):
    f = host.file("/opt/apps")
    assert f.exists, "/opt/apps should exist"
    assert f.is_directory, "/opt/apps should be a directory"
    assert f.user == "app", "/opt/apps should be owned by app"
    assert f.mode == 0o755, "/opt/apps should have mode 0755"


def test_nodejs_installed(host):
    p = host.package("nodejs")
    assert p.is_installed, "nodejs should be installed"


def test_npm_installed(host):
    p = host.package("npm")
    assert p.is_installed, "npm should be installed"


def test_nodejs_version(host):
    result = host.run("node --version")
    assert result.rc == 0, "node command should work"
    assert "v18" in result.stdout, "Node.js version should be v18.x"


def test_testapp_dir_exists(host):
    f = host.file("/opt/apps/testapp")
    assert f.exists, "testapp directory should exist"
    assert f.is_directory, "testapp should be a directory"


def test_testapp_files(host):
    f = host.file("/opt/apps/testapp/app.js")
    assert f.exists, "testapp/app.js should exist"
    assert f.user == "app", "app.js should be owned by app"


def test_testapp_service_file(host):
    f = host.file("/etc/systemd/system/testapp.service")
    assert f.exists, "testapp systemd service file should exist"
    assert f.mode == 0o644, "testapp service should have mode 0644"


def test_testapp_service_config(host):
    f = host.file("/etc/systemd/system/testapp.service")
    assert f.exists
    assert "testapp" in f.content_string, "Service should reference testapp"
    assert "/opt/apps/testapp" in f.content_string, "Service should reference app directory"
    assert "NODE_ENV=production" in f.content_string, "Service should set NODE_ENV"
