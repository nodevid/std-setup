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


def test_common_packages(host):
    packages = ["vim", "curl", "wget", "htop", "net-tools"]
    for pkg in packages:
        p = host.package(pkg)
        assert p.is_installed, f"Package {pkg} should be installed"


def test_fail2ban_installed(host):
    p = host.package("fail2ban")
    assert p.is_installed, "fail2ban should be installed"


def test_audit_package_installed(host):
    ansible_facts = host.ansible.get_facts()
    os_family = ansible_facts["os_family"]
    pkg = "auditd" if os_family == "Debian" else "audit"
    p = host.package(pkg)
    assert p.is_installed, f"{pkg} should be installed"


def test_admin_user_exists(host):
    user = host.user("admin")
    assert user.exists, "admin user should exist"


def test_admin_user_shell(host):
    user = host.user("admin")
    assert user.shell == "/bin/bash", "admin user shell should be /bin/bash"


def test_admin_ssh_dir(host):
    f = host.file("/home/admin/.ssh")
    assert f.exists, "admin .ssh directory should exist"
    assert f.is_directory, "admin .ssh should be a directory"
    assert f.user == "admin", "admin .ssh should be owned by admin"
    assert f.mode == 0o700, "admin .ssh should have mode 0700"


def test_admin_sudoers(host):
    f = host.file("/etc/sudoers.d/admin")
    assert f.exists, "admin sudoers file should exist"
    assert f.mode == 0o440, "admin sudoers should have mode 0440"


def test_sshd_config_exists(host):
    f = host.file("/etc/ssh/sshd_config")
    assert f.exists, "sshd_config should exist"
    assert f.mode == 0o600, "sshd_config should have mode 0600"


def test_ssh_port_config(host):
    f = host.file("/etc/ssh/sshd_config")
    assert f.exists
    assert "Port 2222" in f.content_string, "SSH port should be 2222"


def test_ssh_root_login_disabled(host):
    f = host.file("/etc/ssh/sshd_config")
    assert f.exists
    assert 'PermitRootLogin no' in f.content_string, "Root login should be disabled"


def test_ssh_password_auth_disabled(host):
    f = host.file("/etc/ssh/sshd_config")
    assert f.exists
    assert 'PasswordAuthentication no' in f.content_string, "Password auth should be disabled"


def test_ssh_x11_forwarding_disabled(host):
    f = host.file("/etc/ssh/sshd_config")
    assert f.exists
    assert 'X11Forwarding no' in f.content_string, "X11 forwarding should be disabled"


def test_ssh_banner_configured(host):
    f = host.file("/etc/ssh/sshd_config")
    assert f.exists
    assert "Banner /etc/issue.net" in f.content_string, "SSH banner should be configured"


def test_fail2ban_jail_exists(host):
    f = host.file("/etc/fail2ban/jail.local")
    assert f.exists, "fail2ban jail.local should exist"
    assert f.mode == 0o644, "fail2ban jail.local should have mode 0644"


def test_fail2ban_service_running(host):
    svc = host.service("fail2ban")
    assert svc.is_enabled, "fail2ban should be enabled"


def test_fail2ban_service_active(host):
    svc = host.service("fail2ban")
    assert svc.is_running, "fail2ban should be running"


def test_auditd_service_enabled(host):
    svc = host.service("auditd")
    assert svc.is_enabled, "auditd should be enabled"


def test_auditd_service_active(host):
    svc = host.service("auditd")
    assert svc.is_running, "auditd should be running"


def test_auditd_rules_exist(host):
    f = host.file("/etc/audit/rules.d/hardening.rules")
    assert f.exists, "auditd hardening rules should exist"
    assert f.mode == 0o600, "auditd rules should have mode 0600"


def test_ipv6_disabled_sysctl(host):
    ansible_facts = host.ansible.get_facts()
    os_family = ansible_facts["os_family"]
    if os_family == "Debian":
        sysctl = host.sysctl("net.ipv6.conf.all.disable_ipv6")
        assert sysctl == 1, "IPv6 should be disabled via sysctl"


def test_core_dumps_disabled(host):
    f = host.file("/etc/security/limits.conf")
    assert f.exists
    assert "* hard core 0" in f.content_string, "Core dumps should be disabled"


def test_core_dump_sysctl(host):
    sysctl = host.sysctl("fs.suid_dumpable")
    assert sysctl == 0, "Core dumps should be disabled via sysctl"


def test_usb_storage_disabled(host):
    f = host.file("/etc/modprobe.d/disable-usb-storage.conf")
    assert f.exists, "USB storage modprobe config should exist"
    assert f.mode == 0o600, "USB storage config should have mode 0600"


def test_unused_filesystems_disabled(host):
    f = host.file("/etc/modprobe.d/disable-filesystems.conf")
    assert f.exists, "Unused filesystems modprobe config should exist"
    assert f.mode == 0o600, "Filesystems config should have mode 0600"


def test_etc_issue_banner(host):
    f = host.file("/etc/issue")
    assert f.exists, "/etc/issue should exist"
    assert "AUTHORIZED ACCESS ONLY" in f.content_string, "Warning banner should exist"


def test_etc_issue_net_banner(host):
    f = host.file("/etc/issue.net")
    assert f.exists, "/etc/issue.net should exist"
    assert "AUTHORIZED ACCESS ONLY" in f.content_string, "SSH banner should exist"


def test_etc_passwd_permissions(host):
    f = host.file("/etc/passwd")
    assert f.exists
    assert f.mode == 0o644, "/etc/passwd should have mode 0644"


def test_etc_shadow_permissions(host):
    f = host.file("/etc/shadow")
    assert f.exists
    assert f.mode == 0o640, "/etc/shadow should have mode 0640"


def test_etc_group_permissions(host):
    f = host.file("/etc/group")
    assert f.exists
    assert f.mode == 0o644, "/etc/group should have mode 0644"


def test_etc_gshadow_permissions(host):
    f = host.file("/etc/gshadow")
    assert f.exists
    assert f.mode == 0o640, "/etc/gshadow should have mode 0640"


def test_sshd_service_running(host):
    ansible_facts = host.ansible.get_facts()
    os_family = ansible_facts["os_family"]
    service_name = "ssh" if os_family == "Debian" else "sshd"
    svc = host.service(service_name)
    assert svc.is_enabled, f"{service_name} should be enabled"
    assert svc.is_running, f"{service_name} should be running"


def test_firewall_service_running(host):
    ansible_facts = host.ansible.get_facts()
    os_family = ansible_facts["os_family"]
    if os_family == "Debian":
        svc = host.service("ufw")
        assert svc.is_enabled, "UFW should be enabled"
    else:
        svc = host.service("firewalld")
        assert svc.is_enabled, "firewalld should be enabled"


def test_autoupdate_debian(host):
    ansible_facts = host.ansible.get_facts()
    os_family = ansible_facts["os_family"]
    if os_family == "Debian":
        p = host.package("unattended-upgrades")
        assert p.is_installed, "unattended-upgrades should be installed"
        svc = host.service("unattended-upgrades")
        assert svc.is_enabled, "unattended-upgrades should be enabled"


def test_autoupdate_rhel(host):
    ansible_facts = host.ansible.get_facts()
    os_family = ansible_facts["os_family"]
    if os_family in ["RedHat", "Rocky"]:
        p = host.package("dnf-automatic")
        assert p.is_installed, "dnf-automatic should be installed"
