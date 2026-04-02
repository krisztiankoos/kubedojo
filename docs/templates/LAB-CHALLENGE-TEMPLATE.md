# [Template] Inquiry-Based Lab
<!-- Use for: Killercoda Scenarios, Challenge-based exercises -->

## The Scenario
*A broken, incomplete, or high-stakes production state.*
"Production is down. The frontend cannot reach the database. Your job is to restore connectivity."

---

## The Objective
*A clear, measurable goal.*
"Successfully resolve the DNS query from Pod A to Service B."

---

## The Challenge (No Steps)
"Use your understanding of the {{Component}} to identify the gap. You have access to `kubectl` and `dig`."

---

## Tiered Hints (JIT)
<details>
<summary>Hint 1: The Concept</summary>
"Remember how the Service uses a Label Selector to find Pods."
</details>

<details>
<summary>Hint 2: The Component</summary>
"Check the 'Endpoints' object for Service B. Is it empty?"
</details>

<details>
<summary>Hint 3: The Command</summary>
"Run \`kubectl get ep service-b\` and compare the labels."
</details>

---

## Verification
"Run the check script: \`check-connectivity.sh\`"

---

## Reflection (The "Why")
"Why did the IP address change even though the Service name stayed the same?"
