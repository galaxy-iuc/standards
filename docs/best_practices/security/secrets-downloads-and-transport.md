---
orphan: true
---

# Corpus Research: Secrets, Downloads, and Transport (AI Generated)

Research snapshot: `galaxyproject/tools-iuc` reviews and Galaxy's current
credential schema, **2026-07-23**.

> This is AI-generated research, not normative IUC policy. See the curated
> [Tool Security Checklist](../security) for current guidance.

## 1. Credential flow is a system property

Credential safety depends on all of:

```text
Galaxy credential storage
  → job-script injection
  → wrapper/helper behavior
  → upstream application's credential interface
  → runner process visibility and job retention
```

A wrapper cannot compensate completely for an upstream CLI that accepts a
password only as a command-line argument.

## 2. Galaxy credentials

Galaxy 25.1 introduced tool credential requirements:

```xml
<requirements>
    <credentials name="service" version="1.0"
                 label="Service credentials">
        <variable name="username" inject_as_env="SERVICE_USER"
                  label="Username" />
        <secret name="password" inject_as_env="SERVICE_PASSWORD"
                label="Password" />
    </credentials>
</requirements>
```

Variables and secrets are injected into the job environment. Credentials are
deliberately not Cheetah variables, because values inserted into `<command>`
would be stored in generated command metadata.

The
[Galaxy schema security considerations](https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-requirements-credentials)
also warn that:

- job scripts may be accessible to Galaxy administrators;
- expanding a secret environment variable onto argv exposes it in the process
  list;
- credential values are not sanitized for shell use;
- a helper can write an environment value to a credential file when the
  application supports file-based authentication.

That helper must run inside the job, read the environment directly, and create
the file with restrictive permissions. An ordinary templated Galaxy
`<configfile>` is not a secret mechanism: credentials are not available as
Cheetah variables, and normal generated config files are created for ordinary
job data rather than private credential storage.

Environment injection is secure only when the application reads the environment
itself. This is unsafe:

```shell
client --password "$SERVICE_PASSWORD"
```

The shell expands the value before executing `client`, placing it on argv.

## 3. The ENA Webin case

[PR #7605](https://github.com/galaxyproject/tools-iuc/pull/7605#discussion_r2711909991)
is the clearest corpus example. Review identified:

- username and password visible in the process list;
- code-injection risk because credentials are not ordinary sanitized text
  parameters;
- `echo`-based file creation as another exposure;
- upstream support for password-file or password-environment options;
- a minimum Galaxy profile required for the credential mechanism.

The thread's requested-changes state is informative: sometimes secure wrapper
design requires an upstream interface change or a newer Galaxy version rather
than another layer of quoting.

## 4. Secret review checklist

- No literal credentials in XML, macros, scripts, tests, or fixtures.
- No credential-bearing Cheetah parameters.
- No secret expansion into argv.
- No `echo`, command tracing, debug output, or error message containing a
  secret.
- Credential files have the narrowest practical permissions, live only in the
  job directory, and are not declared outputs.
- The wrapper declares a tool profile compatible with credentials.
- Tool help states meaningful residual exposure, including administrator access
  where relevant.
- Tests use fake credentials and assert they do not appear in command metadata
  or outputs.

## 5. TLS and certificate verification

[PR #6021](https://github.com/galaxyproject/tools-iuc/pull/6021#discussion_r1609468529)
challenged code that disabled both TLS hostname checking and certificate
validation.

Disabling either property permits a network attacker or compromised intermediary
to substitute content. Installing the appropriate CA bundle, fixing the server
certificate, or allowing an administrator-controlled trust store is preferable
to setting `verify=False` or an unverified SSL context in a wrapper.

Flag:

- `verify=False`;
- `check_hostname = False`;
- unverified SSL contexts;
- command options such as `--insecure`, `-k`, or `--no-check-certificate`;
- plain HTTP when the same authoritative service supports HTTPS.

## 6. Download integrity

TLS authenticates a service and protects transport. A checksum binds the
download to an expected artifact. They solve different problems and are both
useful.

[PR #7473](https://github.com/galaxyproject/tools-iuc/pull/7473#discussion_r3319364992)
is a representative data-manager discussion. Review moved from ad hoc checksum
logic toward storing an expected digest and using a standard verification
command or the downloader's built-in verification.

Prefer:

- versioned or content-addressed URLs;
- expected SHA-256 or a stronger signature from an independent trusted source;
- a downloader that fails closed on verification errors;
- source URL, version, and digest recorded in resulting provenance or data-table
  metadata;
- download before extraction or execution, verify, then consume.

Avoid:

- `latest`, branch-head, or mutable release URLs without an integrity binding;
- downloading and executing a script in one pipe;
- a checksum obtained from the same unauthenticated channel as the artifact;
- MD5 as an authenticity mechanism. It may still detect accidental corruption
  when it is the only digest an upstream archive service publishes, but it does
  not provide collision resistance.

## 7. User-controlled URLs

A text parameter containing an arbitrary URL can introduce:

- server-side request forgery to private network services;
- local-file or alternate-scheme access;
- credential leakage through URL components or redirects;
- unexpectedly large downloads;
- content-type confusion;
- reproducibility failures from mutable content.

When user-specified remote access is essential:

- constrain schemes and, where possible, hosts;
- reject embedded credentials;
- define redirect policy;
- cap time and size;
- treat the result according to its actual parser or extractor;
- record the final resolved source.

Galaxy's own URL-fetch implementation checks schemes and private/local
destinations, resolves all DNS results, and re-checks redirects against an
administrator allowlist. A wrapper that sends a free-text URL directly to
`curl`, `wget`, or `requests` bypasses those controls and needs to reproduce an
appropriate, reviewable policy.

## 8. Candidate static checks

High confidence:

- secret parameter or credential environment variable expanded onto argv;
- secret printed with `echo`, debug tracing, or logs;
- TLS verification disabled;
- remote script downloaded and immediately executed;
- mutable download used as executable code without integrity verification.

Medium confidence:

- arbitrary URL parameter;
- downloaded archive without a digest;
- Galaxy credential feature used with an incompatible tool profile;
- credential file written with uncertain permissions or exposed as an output.

Useful suppressions:

- application consumes the injected environment variable directly;
- credential file is created privately, never output, and removed with the job;
- authoritative downloader performs and fails on the expected digest;
- immutable, versioned artifact with independently verified signature.
