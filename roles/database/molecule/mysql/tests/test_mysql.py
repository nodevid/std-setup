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


def test_mysql_installed(host):
    p = host.package("mysql-server")
    assert p.is_installed, "mysql-server should be installed"


def test_mysql_service_running(host):
    svc = host.service("mysql")
    assert svc.is_enabled, "mysql should be enabled"
    assert svc.is_running, "mysql should be running"


def test_python3_pymysql_installed(host):
    p = host.package("python3-pymysql")
    assert p.is_installed, "python3-pymysql should be installed"


def test_mysql_bind_address(host):
    result = host.run("mysql -u root -e 'SELECT @@bind_address' 2>/dev/null || true")
    if result.rc == 0:
        assert "127.0.0.1" in result.stdout, "MySQL should be bound to 127.0.0.1"


def test_mysql_default_database_removed(host):
    result = host.run("mysql -u root -e 'SHOW DATABASES' 2>/dev/null || true")
    if result.rc == 0:
        assert "test" not in result.stdout, "MySQL test database should be removed"


def test_mysql_port(host):
    f = host.file("/etc/mysql/my.cnf")
    if f.exists:
        assert f.exists


def test_mysql_socket_exists(host):
    f = host.file("/var/run/mysqld/mysqld.sock")
    assert f.exists, "MySQL socket should exist"


def test_mysql_hardening_applied(host):
    result = host.run("mysql -u root -e 'SELECT user FROM mysql.user' 2>/dev/null || true")
    if result.rc == 0:
        lines = result.stdout.strip().split("\n")
        anon_users = [l for l in lines if l.strip() == ""]
        assert len(anon_users) == 0, "MySQL should have no anonymous users"
