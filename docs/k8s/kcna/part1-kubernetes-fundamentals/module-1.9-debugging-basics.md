# Module 1.9: Debugging Basics (Theory)

> **Complexity**: `[QUICK]` - Fast triage mindset
>
> **Time to Complete**: 15-20 minutes
>
> **Prerequisites**: Modules 1.1–1.8 (K8s fundamentals)

---

## Outline
- How to read pod state quickly
- Core commands for first-response debugging
- Common failure patterns and what they imply
- Mental model: detective with a three-step checklist (state → events → logs)
- Mini-scenario: “My app is down, I have 3 minutes—what do I check first?”

---

## Read the Signals (Clue Board)
- **Pod phase**: `Pending`, `Running`, `Succeeded`, `Failed`, `Unknown`.
- **Restart counts**: High restarts usually mean crash loops or OOM kills.
- **Events**: Scheduler or kubelet reasons often explain Pending/Failed states.
- **Container status**: `Waiting` (ImagePullBackOff, ErrImagePull), `Terminated` (ExitCode, OOMKilled).

```bash
kubectl get pods -A
kubectl describe pod <name> -n <ns>    # events + container status
kubectl logs <name> -n <ns>            # default: first container
kubectl logs <name> -n <ns> -c <c>     # multi-container pods
kubectl logs -p <name> -n <ns>         # previous instance (crash loops)
```

## Common Failure Patterns
- **ImagePullBackOff / ErrImagePull**: Bad image name/tag, registry auth, or network path.
- **CrashLoopBackOff**: App exits quickly; check logs, probes, config/secret mounts, entrypoint args.
- **Pending**: No nodes match (taints/affinity), insufficient CPU/memory, PVC binding issues.
- **OOMKilled**: Container exceeded memory; check limits/requests and app memory profile.
- **Probe failures**: Liveness keeps restarting the pod; readiness keeps it out of Service Endpoints.

## Fast Checks (Order of Operations)
1) `kubectl get pods -o wide` (phase/node).  
2) `kubectl describe pod` (events, reasons).  
3) `kubectl logs` (and `-p` if restarting).  
4) `kubectl get events --sort-by=.lastTimestamp | tail` (cluster-wide clues).  
5) If node-related: `kubectl get nodes -o wide` and check taints/conditions.

> **Exam mindset**: Know where to look first. KCNA expects awareness of these signals, not deep troubleshooting scripts.

> **Mental model**: Triage like an ER: vitals (phase/restarts), chart notes (events), then patient story (logs). Don't jump to surgery (config changes) before vitals.

```
CLUE MAP
[Vitals]   kubectl get pods
[Notes]    kubectl describe pod
[Story]    kubectl logs (-p)
[Scene]    kubectl get events --sort-by=.lastTimestamp | tail
```

> **Pitfall radar**: Re-running `kubectl apply` rarely fixes a bad image, missing secret, or failing probe—find the clue first.
