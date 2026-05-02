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


def test_postgresql_installed(host):
    p = host.package("postgresql-14")
    assert p.is_installed, "postgresql-14 should be installed"


def test_postgresql_contrib_installed(host):
    p = host.package("postgresql-contrib-14")
    assert p.is_installed, "postgresql-contrib-14 should be installed"


def test_postgresql_service_running(host):
    svc = host.service("postgresql")
    assert svc.is_enabled, "postgresql should be enabled"
    assert svc.is_running, "postgresql should be running"


def test_python3_psycopg2_installed(host):
    p = host.package("python3-psycopg2")
    assert p.is_installed, "python3-psycopg2 should be installed"


def test_postgresql_config_exists(host):
    f = host.file("/etc/postgresql/14/main/postgresql.conf")
    assert f.exists, "postgresql.conf should exist"


def test_postgresql_listen_address(host):
    f = host.file("/etc/postgresql/14/main/postgresql.conf")
    assert f.exists
    assert "listen_addresses" in f.content_string, "listen_addresses should be configured"
