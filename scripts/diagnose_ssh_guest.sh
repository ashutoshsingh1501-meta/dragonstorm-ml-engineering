#!/usr/bin/env bash
# Intended for Azure Portal > VM > Run command > RunShellScript.
# Read-only checks. An active ssh.socket with inactive ssh.service can be valid.
set -u
echo "=== HOST ==="
hostname
uptime
echo "=== SSH SERVICE ==="
systemctl status ssh --no-pager -l || true
echo "=== SSH SOCKET ==="
systemctl status ssh.socket --no-pager -l || true
echo "=== PORT 22 LISTENERS ==="
ss -lntp | grep ':22' || true
echo "=== CONFIG CHECK ==="
/usr/sbin/sshd -t && echo "SSH CONFIG: VALID" || true
echo "=== RECENT LOGS ==="
journalctl -u ssh -n 30 --no-pager || true
echo "=== GUEST FIREWALL ==="
ufw status || true
echo "IMPORTANT: If the VM listens on port 22 but external SSH fails, check Azure NSG source-IP restriction and effective network path."
