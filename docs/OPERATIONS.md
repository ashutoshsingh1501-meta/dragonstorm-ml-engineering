# DragonStorm Lab — Operations and reproducibility notes

This document supports the public engineering journal. **No secrets, actual SSH private-key values, public VM IPs, subscription IDs or personal network addresses belong in GitHub.**

## Windows → Azure VM SSH

1. Start the personal VM using Azure Portal. Wait until provisioning/boot completes.
2. Confirm Azure Networking inbound TCP/22 rule permits **only** your *current* public client IP, not an old DHCP/ISP lease. Use **My IP Address** to refresh if the ISP changed it; do **not** open 22 to the world.
3. In Windows PowerShell (replace placeholders with local values; do not publish them):
   ```powershell
   ssh -i "$env:USERPROFILE\Downloads\<ssh-private-key>.pem" azureuser@<vm-public-ip>
   Test-NetConnection <vm-public-ip> -Port 22 -InformationLevel Detailed
   ```
4. If SSH fails, use Azure Portal **Run command → RunShellScript** with [guest diagnostic](../scripts/diagnose_ssh_guest.sh), or paste its contents into the portal. An inactive socket-activated service can be normal; don't misdiagnose it without checking ssh.socket and active listeners.
5. If needed, starting the service was tested with `sudo systemctl start ssh.service` and rechecking `systemctl is-active ssh.service`, `ss -lntp`, `sudo /usr/sbin/sshd -t`; in the Nov 12 incident this **did not fix** external SSH. Updating Azure NSG's old source IP **did**.

PowerShell 5.1 does not include a Unix-style `touch` command by default. The initial multiline `scp` paste was reversed; the single-line transfer below worked:

```powershell
scp -i "$env:USERPROFILE\Downloads\<ssh-private-key>.pem" azureuser@<vm-public-ip>:/home/azureuser/dragonstorm-lab/test-dog-annotated.jpg "$env:USERPROFILE\Downloads\test-dog-annotated.jpg"
```

## Check model readiness

Use [read-only VM diagnostic](../scripts/check_triton_lab.sh) and then, if Docker is active but retained Triton is stopped:

```bash
if [ "$(sudo docker inspect -f '{{.State.Running}}' triton-cpu 2>/dev/null)" != "true" ]; then
    sudo docker start triton-cpu
fi
for i in $(seq 1 30); do
    if curl -fsS http://127.0.0.1:8000/v2/models/ssd_mobilenet_v1_12/ready >/dev/null 2>&1; then
        echo 'TRITON MODEL: READY'; break
    fi
    sleep 2
done
curl -sS -o /dev/null -w 'Model HTTP Status: %{http_code}\n' \
    http://127.0.0.1:8000/v2/models/ssd_mobilenet_v1_12/ready
```

An HTTP 200 readiness probe verifies model status, **not** model correctness. Transient resets during startup were observed on Nov 7 and subsequently resolved by waiting for readiness.

## Experiment execution order

1. Verify local model asset and source checksum from [model notes](models/ssd-mobilenetv1-12-source-notes.md); source image and COCO label map are third-party assets stored on VM only.
2. Compile relevant scripts with `~/dragonstorm-lab/.venv-onnx-inspect/bin/python -m py_compile <path>` before first run.
3. Run [synthetic smoke](../scripts/first_triton_inference.py), [photo smoke](../scripts/real_photo_triton_inference.py), [annotation](../scripts/annotate_triton_detection.py).
4. Run [ONNX graph inspection](../scripts/inspect_onnx_preprocessing.py), [full-resolution](../scripts/original_resolution_inference.py), [A/B/C](../scripts/compare_preprocessing.py), then [benchmark](../scripts/benchmark_triton.py).
5. Keep `real_photo_triton_inference.py` in the same directory as dependent experiment scripts when running on the VM. Do not assume GitHub remotely updating files updates the VM-local copies; download new scripts explicitly.
6. Read [full Nov 12–13 journal](journal/2026-11-13-triton-preprocessing-benchmark.md) and [results transcription](experiments/2026-11-13-cpu-baseline.json). Benchmarks measure client HTTP wall-time, with only 24–30 samples/config.

## Shutdown and maintenance

1. Preserve measured results on VM and commit source/documentation separately. Never check in the downloaded ONNX binary, private credentials or sensitive logs.
2. Close SSH with `exit`.
3. In Azure Portal **Stop (deallocate)** and verify **Stopped (deallocated)**. SSH exit alone leaves billing compute active. November 13 end-state was **verified** by an Azure Portal screenshot showing **Stopped (deallocated)** after the user closed the SSH session; always repeat this verification after future sessions.
4. Restore a safe auto-shutdown policy if desired; original ADR proposed 20:00 IST but evidence shows it was turned off during bootstrap. No claim that it has been restored.
5. Ubuntu Nov 12 banner reported 14 available updates (12 standard security). Schedule controlled upgrade/reboot/health recheck rather than changing packages during timed benchmarking.
