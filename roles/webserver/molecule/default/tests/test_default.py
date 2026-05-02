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


def test_nginx_installed(host):
    p = host.package("nginx")
    assert p.is_installed, "nginx should be installed"


def test_nginx_service_running(host):
    svc = host.service("nginx")
    assert svc.is_enabled, "nginx should be enabled"
    assert svc.is_running, "nginx should be running"


def test_default_site_removed(host):
    f = host.file("/etc/nginx/sites-enabled/default")
    assert not f.exists, "default nginx site should be removed"


def test_ssl_params_config(host):
    f = host.file("/etc/nginx/snippets/ssl-params.conf")
    assert f.exists, "ssl-params.conf should exist"
    assert f.mode == 0o644, "ssl-params.conf should have mode 0644"


def test_security_headers_config(host):
    f = host.file("/etc/nginx/snippets/security-headers.conf")
    assert f.exists, "security-headers.conf should exist"
    assert f.mode == 0o644, "security-headers.conf should have mode 0644"


def test_security_headers_content(host):
    f = host.file("/etc/nginx/snippets/security-headers.conf")
    assert f.exists
    assert "Strict-Transport-Security" in f.content_string, "HSTS header should be present"
    assert "X-Frame-Options" in f.content_string, "X-Frame-Options header should be present"
    assert "X-Content-Type-Options" in f.content_string, "X-Content-Type-Options header should be present"


def test_test_site_config(host):
    f = host.file("/etc/nginx/sites-available/test-site")
    assert f.exists, "test-site config should exist"
    assert f.mode == 0o644, "test-site config should have mode 0644"


def test_test_site_enabled(host):
    f = host.file("/etc/nginx/sites-enabled/test-site")
    assert f.exists, "test-site should be enabled (symlinked)"
    assert f.is_symlink, "test-site should be a symlink"


def test_ssl_protocols(host):
    f = host.file("/etc/nginx/snippets/ssl-params.conf")
    assert f.exists
    assert "TLSv1.2" in f.content_string, "TLSv1.2 should be configured"
    assert "TLSv1.3" in f.content_string, "TLSv1.3 should be configured"


def test_nginx_config_valid(host):
    result = host.run("nginx -t")
    assert result.rc == 0, "nginx configuration should be valid"
