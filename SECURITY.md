# Security Policy

## Reporting a Vulnerability

If you discover a security issue in KubeDojo's content (e.g., a command that could be harmful, credentials in examples, or a misconfigured exercise), please report it by:

1. Opening a [GitHub issue](https://github.com/kube-dojo/kube-dojo.github.io/issues) with the label "security"
2. Or emailing the maintainers directly

## Scope

KubeDojo is educational content (markdown files). There is no application code, backend, or user data. Security concerns are limited to:

- Commands or YAML examples that could be harmful if copy-pasted
- Accidental inclusion of real credentials or tokens in examples
- Links to malicious external resources

## Content Security

- All example credentials use placeholder values (`my-secret`, `changeme`, `example.com`)
- No real API keys, tokens, or passwords are included
- External links are reviewed for legitimacy
