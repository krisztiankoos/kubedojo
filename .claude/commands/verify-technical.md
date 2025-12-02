---
description: Verify technical accuracy of commands and YAML in a module
---

# Technical Accuracy Verification

You are verifying the technical accuracy of a KubeDojo module. Focus on commands, YAML, and technical claims.

## Module to Verify

Verify the file: $ARGUMENTS

## Verification Checklist

### 1. kubectl Commands
For each kubectl command in the module:
- [ ] Syntax is correct
- [ ] Flags exist and are spelled correctly
- [ ] Short flags match long flags (`-n` = `--namespace`)
- [ ] Output expectations are realistic

### 2. YAML Manifests
For each YAML example:
- [ ] Valid YAML syntax (indentation, colons, dashes)
- [ ] Correct apiVersion for resource type
- [ ] Required fields present
- [ ] Field names spelled correctly
- [ ] Values are appropriate types (string vs int)

### 3. Technical Claims
For each technical statement:
- [ ] Accurate for Kubernetes 1.31+
- [ ] Aligns with CKA 2025 curriculum
- [ ] No outdated information (deprecated APIs, old practices)
- [ ] Consistent with kubernetes.io documentation

### 4. Versions & Compatibility
- [ ] Kubernetes version references are current (1.31+)
- [ ] Tool versions mentioned are compatible
- [ ] No deprecated commands or flags

### 5. URLs & References
- [ ] All URLs are valid and accessible
- [ ] Documentation links point to current versions
- [ ] No broken internal links

## Output Format

```
## Technical Verification: [Module Name]

### Commands Verified
| Command | Line | Status | Issue |
|---------|------|--------|-------|
| `kubectl get pods -A` | 45 | ✅ | - |
| `kubectl apply -f pod.yaml` | 67 | ✅ | - |
| `kubectl expose svc ...` | 89 | ❌ | Wrong syntax |

### YAML Verified
| Resource | Line | Status | Issue |
|----------|------|--------|-------|
| Pod nginx | 52-65 | ✅ | - |
| NetworkPolicy | 120-145 | ❌ | Wrong apiVersion |

### Technical Accuracy Issues
1. **Line X**: [Issue description]
   - Current: `[what it says]`
   - Should be: `[correct version]`
   - Reason: [why it's wrong]

2. ...

### Deprecated Content Found
- [ ] Line X: [deprecated item] - Use [modern alternative]
- ...

### Links Verified
| URL | Status |
|-----|--------|
| kubernetes.io/docs/... | ✅ |
| ... | ... |

### Summary
- Commands checked: X
- Commands with issues: X
- YAML blocks checked: X
- YAML with issues: X
- Technical claims verified: X
- Issues found: X

### Verdict
✅ PASS - No technical issues found
⚠️ WARN - Minor issues, module usable
❌ FAIL - Critical issues, needs fixes before use
```

## Critical Issues (Auto-Fail)

These issues require immediate fix:
- Wrong apiVersion (would fail when applied)
- Non-existent kubectl flags
- YAML syntax errors
- Fundamentally incorrect technical claims
- Deprecated APIs marked as current

## Common Gotchas to Check

1. `kubectl run` behavior changed - creates Pod, not Deployment
2. `kubectl expose` requires correct selectors
3. NetworkPolicy `apiVersion: networking.k8s.io/v1` (not extensions)
4. Ingress `apiVersion: networking.k8s.io/v1` (not extensions/v1beta1)
5. PodSecurityPolicy is REMOVED (use Pod Security Admission)
6. `kubectl get cs` (componentstatuses) is deprecated
