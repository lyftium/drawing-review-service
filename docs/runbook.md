# Runbook: the model or the service does not start

Work from the outside in, and change one thing at a time.

1. **State and events**
   `kubectl -n drawing-review get pods -o wide` then
   `kubectl -n drawing-review describe pod <pod>` and `kubectl -n drawing-review get events --sort-by=.lastTimestamp`.
   `Pending` with "Insufficient nvidia.com/gpu" is a scheduling problem, not an app bug.
   `ImagePullBackOff` is a registry or tag problem. `CrashLoopBackOff` means read the logs.
2. **Logs and config**
   `kubectl -n drawing-review logs <pod> --previous` for the crash before the restart.
   Check the ConfigMap the pod actually got: `kubectl -n drawing-review get cm drawing-review-config -o yaml`.
   A bad `DRW_*` value fails at startup with a pydantic error that names the field.
3. **Weights and volumes**
   Is the PVC `Bound`? Is the path in `DRW_YOLO_WEIGHTS` or `HF_HOME` really there?
   With `HF_HUB_OFFLINE=1`, a missing file is an error instead of a silent download.
4. **GPU and environment**
   `kubectl describe node <node>` shows allocatable `nvidia.com/gpu`. Inside the pod,
   `nvidia-smi` shows the driver and CUDA version; the image's CUDA must be supported
   by the node driver.
5. **Memory and model parameters**
   OOMKilled or a CUDA OOM in vLLM: lower `--max-model-len` or `--max-num-seqs`,
   lower `--gpu-memory-utilization`, or add tensor parallelism. For tensor parallel,
   check `/dev/shm` is mounted.
6. **Minimal case**
   Run the stub configuration (`DRW_DETECTOR=stub DRW_INTERPRETER=rules`) to confirm
   the service itself works, then switch one real backend back on at a time.

On OpenShift the same steps apply with `oc` instead of `kubectl`; the usual extra
cause is the restricted security context (random UID), which is why the image does
not depend on a fixed home directory or a writable root filesystem.
