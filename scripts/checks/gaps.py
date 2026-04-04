"""Gap detection — find scaffolding gaps at three levels:

1. Within-module: term used without definition
2. Between-module: module N+1 assumes knowledge module N didn't teach
3. Between-track: the jump from one track to the next

Also detects:
- Missing prerequisites
- Broken "Next Module" links
- Complexity jumps (difficulty spikes)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .structural import CheckResult


# Technical terms that should be explained before use (per track)
# These are terms that a BEGINNER in that track might not know
TRACK_JARGON = {
    "prerequisites": {
        "cpu", "ram", "ssd", "hdd", "os", "kernel", "process", "thread",
        "port", "ip address", "dns", "tcp", "http", "ssh", "ssl", "tls",
        "container", "docker", "kubernetes", "yaml", "json", "api",
        "git", "repository", "branch", "commit", "cli", "gui", "shell",
        "bash", "terminal", "sudo", "root", "permissions", "firewall",
    },
    "linux": {
        "inode", "file descriptor", "syscall", "namespace", "cgroup",
        "iptables", "nftables", "systemd", "journald", "selinux",
        "apparmor", "seccomp", "overlay", "unionfs", "chroot",
    },
    "cloud": {
        "vpc", "subnet", "cidr", "igw", "nat gateway", "security group",
        "iam", "role", "policy", "arn", "region", "az", "ec2", "s3",
        "lambda", "ecs", "eks", "fargate", "rds", "cloudformation",
        "terraform", "load balancer", "auto scaling", "cdn",
    },
    "k8s": {
        "pod", "deployment", "service", "ingress", "namespace", "configmap",
        "secret", "pv", "pvc", "storageclass", "rbac", "role", "clusterrole",
        "daemonset", "statefulset", "job", "cronjob", "hpa", "vpa",
        "networkpolicy", "cni", "csi", "cri", "operator", "crd", "helm",
        "kustomize", "etcd", "api server", "scheduler", "controller manager",
        "kubelet", "kube-proxy", "cordon", "drain", "taint", "toleration",
        "affinity", "pdb", "priority class",
    },
}


@dataclass
class GapIssue:
    """A gap found between modules."""
    module_a: str  # source module (or "track-start" for first module)
    module_b: str  # target module with the gap
    gap_type: str  # CONCEPT_JUMP, MISSING_PREREQ, BROKEN_LINK, COMPLEXITY_JUMP
    severity: str  # ERROR, WARNING
    message: str

    def __str__(self):
        icon = "❌" if self.severity == "ERROR" else "⚠️"
        return f"  {icon} [{self.gap_type}] {self.module_a} → {self.module_b}: {self.message}"


def extract_complexity(content: str) -> str | None:
    """Extract complexity tag from module content."""
    match = re.search(r"\[([A-Z]+)\]", content[:500])
    return match.group(1) if match else None


COMPLEXITY_ORDER = {"BEGINNER": 1, "EASY": 1, "BASIC": 1,
                    "MEDIUM": 2, "INTERMEDIATE": 2,
                    "COMPLEX": 3, "ADVANCED": 3, "HARD": 3,
                    "EXPERT": 4}


def extract_prerequisites(content: str) -> list[str]:
    """Extract listed prerequisites from module content."""
    prereqs = []
    match = re.search(r"\*\*Prerequisites?\*\*:?\s*(.+?)(?:\n\n|\n>|\n---)", content, re.DOTALL)
    if match:
        text = match.group(1)
        # Find module references like "Module 1.2" or "Module 0.3 (Shell Mastery)"
        refs = re.findall(r"Module\s+(\d+\.\d+)", text, re.IGNORECASE)
        prereqs.extend(refs)
    return prereqs


def extract_next_module(content: str) -> str | None:
    """Extract the Next Module link target."""
    match = re.search(r"(?:Next Module|Наступний модуль|What's Next).*?\[.*?\]\(([^)]+)\)", content)
    if match:
        return match.group(1)
    return None


def find_first_use_of_terms(content: str, terms: set[str]) -> dict[str, int]:
    """Find the first line number where each term appears."""
    first_use = {}
    lines = content.lower().split("\n")
    for i, line in enumerate(lines, 1):
        for term in terms:
            if term not in first_use and term.lower() in line:
                first_use[term] = i
    return first_use


def detect_gaps_in_sequence(module_files: list[Path], track: str = "k8s") -> list[GapIssue]:
    """Detect scaffolding gaps across a sequence of modules.

    Args:
        module_files: Ordered list of module file paths
        track: Track name for jargon lookup (prerequisites, linux, cloud, k8s)
    """
    issues = []

    if not module_files:
        return issues

    jargon = TRACK_JARGON.get(track, set())

    # Track which concepts have been introduced
    introduced_terms: set[str] = set()
    prev_complexity = None
    prev_name = "track-start"

    for path in module_files:
        content = path.read_text()
        name = path.stem

        # 1. Check complexity jumps
        complexity = extract_complexity(content)
        if complexity and prev_complexity:
            curr_level = COMPLEXITY_ORDER.get(complexity, 2)
            prev_level = COMPLEXITY_ORDER.get(prev_complexity, 2)
            if curr_level - prev_level > 1:
                issues.append(GapIssue(
                    prev_name, name, "COMPLEXITY_JUMP", "WARNING",
                    f"Jumps from [{prev_complexity}] to [{complexity}] — "
                    f"consider adding a bridging module or reducing complexity"
                ))

        # 2. Check for jargon used before introduction
        terms_in_module = find_first_use_of_terms(content, jargon)
        new_terms_used = set(terms_in_module.keys()) - introduced_terms

        # Terms used in this module are now "introduced" for subsequent modules
        introduced_terms.update(terms_in_module.keys())

        # Check if any new terms are used without definition in this module
        # (Heuristic: if a term appears but isn't in a heading or bold definition, it might be a gap)
        body_start = content.find("---", content.find("---") + 3)
        if body_start > 0:
            body = content[body_start:]
            for term in new_terms_used:
                # Check if the term is defined (appears in bold or heading)
                definition_pattern = rf"(\*\*{re.escape(term)}\*\*|##.*{re.escape(term)})"
                if not re.search(definition_pattern, body, re.IGNORECASE):
                    # Term used but never defined — potential gap
                    issues.append(GapIssue(
                        prev_name, name, "CONCEPT_JUMP", "WARNING",
                        f"Term '{term}' used but not defined/explained in this module "
                        f"or any previous module in the sequence"
                    ))

        # 3. Check prerequisite references
        prereqs = extract_prerequisites(content)
        # We can't validate if prereqs exist without the full file list,
        # but we track them for the report

        # 4. Check Next Module links
        next_link = extract_next_module(content)
        if next_link:
            # Resolve relative link
            target_name = next_link.rstrip("/").split("/")[-1]
            # Check if target exists in the module list
            target_exists = any(target_name in f.stem for f in module_files)
            if not target_exists and not next_link.startswith("http"):
                issues.append(GapIssue(
                    name, target_name, "BROKEN_LINK", "ERROR",
                    f"Next Module links to '{next_link}' but target not found in this section"
                ))

        prev_complexity = complexity
        prev_name = name

    return issues


def _numeric_sort_key(path: Path) -> tuple:
    """Sort module files numerically (0.1, 0.2, ..., 0.10) not lexicographically."""
    match = re.search(r"module-(\d+)\.(\d+)", path.stem)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (999, 999)


def detect_gaps_in_directory(directory: Path, track: str = "k8s") -> list[GapIssue]:
    """Detect gaps across all modules in a directory, sorted by numeric order."""
    module_files = sorted(directory.glob("module-*.md"), key=_numeric_sort_key)
    if not module_files:
        return []
    return detect_gaps_in_sequence(module_files, track)


def run_track_gap_analysis(track_root: Path, track: str = "k8s") -> list[GapIssue]:
    """Run gap analysis across an entire track (all subdirectories in order)."""
    all_issues = []

    # Find all part/section directories
    sections = sorted([d for d in track_root.iterdir() if d.is_dir()])

    if not sections:
        # Flat directory (no parts)
        return detect_gaps_in_directory(track_root, track)

    for section in sections:
        issues = detect_gaps_in_directory(section, track)
        all_issues.extend(issues)

    return all_issues


# ---------------------------------------------------------------------------
# Full learning path — cross-track gap detection
# ---------------------------------------------------------------------------

# The recommended learning path (directories under src/content/docs/)
LEARNING_PATH = [
    ("prerequisites/zero-to-terminal", "prerequisites"),
    ("linux/foundations/everyday-use", "linux"),
    ("prerequisites/cloud-native-101", "prerequisites"),
    ("prerequisites/kubernetes-basics", "prerequisites"),
    ("prerequisites/philosophy-design", "prerequisites"),
    ("prerequisites/modern-devops", "prerequisites"),
]

# Extended paths branching from the fundamentals
CERT_PATHS = {
    "cka": [
        ("k8s/cka/part0-environment", "k8s"),
        ("k8s/cka/part1-cluster-architecture", "k8s"),
        ("k8s/cka/part2-workloads-scheduling", "k8s"),
        ("k8s/cka/part3-services-networking", "k8s"),
        ("k8s/cka/part4-storage", "k8s"),
        ("k8s/cka/part5-troubleshooting", "k8s"),
    ],
    "ckad": [
        ("k8s/ckad/part0-environment", "k8s"),
        ("k8s/ckad/part1-design-build", "k8s"),
        ("k8s/ckad/part2-deployment", "k8s"),
        ("k8s/ckad/part3-observability", "k8s"),
        ("k8s/ckad/part4-environment", "k8s"),
        ("k8s/ckad/part5-networking", "k8s"),
    ],
}


@dataclass
class TrackTransition:
    """A gap found at the boundary between two tracks/sections."""
    from_section: str
    to_section: str
    gap_type: str  # BRIDGE_MISSING, CONCEPT_CLIFF, COMPLEXITY_CLIFF
    severity: str
    message: str
    suggestion: str  # "expand" or "new_module" or "cross_reference"

    def __str__(self):
        icon = "❌" if self.severity == "ERROR" else "⚠️"
        action = {"expand": "EXPAND existing module", "new_module": "NEW bridging module needed",
                  "cross_reference": "ADD cross-reference"}
        return (f"  {icon} [{self.gap_type}] {self.from_section} → {self.to_section}\n"
                f"      {self.message}\n"
                f"      Fix: {action.get(self.suggestion, self.suggestion)}")


def _get_section_taught_concepts(directory: Path, content_root: Path) -> set[str]:
    """Get ALL concepts taught across ALL modules in a section (not just last)."""
    full_path = content_root / directory
    if not full_path.exists():
        return set()
    modules = sorted(full_path.glob("module-*.md"), key=_numeric_sort_key)

    defined = set()
    all_terms = set().union(*TRACK_JARGON.values())
    for mod in modules:
        content = mod.read_text().lower()
        for term in all_terms:
            # Broader detection: bold, heading, OR explained inline ("X is ...", "X means ...", "called X")
            patterns = [
                rf"\*\*{re.escape(term)}\*\*",
                rf"##.*{re.escape(term)}",
                rf"{re.escape(term)}\s+(is|means|stands for|refers to)",
                rf"called\s+{re.escape(term)}",
                rf"\({re.escape(term)}\)",  # parenthetical definition
            ]
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    defined.add(term)
                    break
    return defined


def _get_first_module_assumptions(directory: Path, content_root: Path, track: str) -> set[str]:
    """Get concepts assumed in the first 2 modules of a section.

    Only checks terms relevant to the TARGET track's jargon, not all tracks.
    """
    full_path = content_root / directory
    if not full_path.exists():
        return set()
    modules = sorted(full_path.glob("module-*.md"), key=_numeric_sort_key)
    if not modules:
        return set()

    # Check first 2 modules (the transition zone)
    check_modules = modules[:2]

    # Only check terms relevant to this track
    track_terms = TRACK_JARGON.get(track, set())
    # Also include terms from the "prerequisites" set (universal basics)
    track_terms = track_terms | TRACK_JARGON.get("prerequisites", set())

    assumed = set()
    for mod in check_modules:
        content = mod.read_text().lower()
        body_start = content.find("---", content.find("---") + 3)
        body = content[body_start:] if body_start > 0 else content

        for term in track_terms:
            if term in body:
                # Check if it's defined in this module
                patterns = [
                    rf"\*\*{re.escape(term)}\*\*",
                    rf"##.*{re.escape(term)}",
                    rf"{re.escape(term)}\s+(is|means|stands for|refers to)",
                    rf"called\s+{re.escape(term)}",
                    rf"\({re.escape(term)}\)",
                ]
                defined_here = any(re.search(p, body, re.IGNORECASE) for p in patterns)
                if not defined_here:
                    assumed.add(term)
    return assumed


def detect_cross_track_gaps(content_root: Path,
                            path: list[tuple[str, str]] | None = None) -> list[TrackTransition]:
    """Detect gaps at transitions between tracks/sections in the learning path."""
    learning_path = path or LEARNING_PATH
    issues = []

    for i in range(len(learning_path) - 1):
        from_dir, from_track = learning_path[i]
        to_dir, to_track = learning_path[i + 1]

        from_name = from_dir.split("/")[-1]
        to_name = to_dir.split("/")[-1]

        # Build cumulative knowledge from ALL prior sections
        cumulative_taught: set[str] = set()
        for j in range(i + 1):
            prior_dir = Path(learning_path[j][0])
            cumulative_taught |= _get_section_taught_concepts(prior_dir, content_root)

        # Get concepts assumed by the next section (using target track's jargon)
        assumed = _get_first_module_assumptions(Path(to_dir), content_root, to_track)

        real_gaps = assumed - cumulative_taught

        if real_gaps:
            # Categorize: small gaps → cross-reference, big gaps → new module
            if len(real_gaps) <= 3:
                suggestion = "cross_reference"
                severity = "WARNING"
            elif len(real_gaps) <= 8:
                suggestion = "expand"
                severity = "WARNING"
            else:
                suggestion = "new_module"
                severity = "ERROR"

            issues.append(TrackTransition(
                from_section=from_name,
                to_section=to_name,
                gap_type="CONCEPT_CLIFF" if len(real_gaps) > 5 else "BRIDGE_MISSING",
                severity=severity,
                message=f"{len(real_gaps)} concepts assumed but never taught: {', '.join(sorted(real_gaps)[:10])}{'...' if len(real_gaps) > 10 else ''}",
                suggestion=suggestion,
            ))

        # Check complexity transition
        from_path = content_root / Path(from_dir)
        to_path = content_root / Path(to_dir)
        if from_path.exists() and to_path.exists():
            from_modules = sorted(from_path.glob("module-*.md"), key=_numeric_sort_key)
            to_modules = sorted(to_path.glob("module-*.md"), key=_numeric_sort_key)
            if from_modules and to_modules:
                last_complexity = extract_complexity(from_modules[-1].read_text())
                first_complexity = extract_complexity(to_modules[0].read_text())
                if last_complexity and first_complexity:
                    last_level = COMPLEXITY_ORDER.get(last_complexity, 2)
                    first_level = COMPLEXITY_ORDER.get(first_complexity, 2)
                    if first_level - last_level > 1:
                        issues.append(TrackTransition(
                            from_section=from_name,
                            to_section=to_name,
                            gap_type="COMPLEXITY_CLIFF",
                            severity="WARNING",
                            message=f"Complexity jumps from [{last_complexity}] to [{first_complexity}]",
                            suggestion="expand",
                        ))

    return issues

    return all_issues
