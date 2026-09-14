---
orphan: true
---

# Corpus Research: Unsafe Serialization, Archives, and Active Content (AI Generated)

Research snapshot: `galaxyproject/tools-iuc` reviews, **2026-07-23**.

> This is AI-generated research, not normative IUC policy. See the curated
> [Tool Security Checklist](../security) for current guidance.

## 1. One boundary, several file types

A file upload is not necessarily passive data. Some formats instruct a loader
to reconstruct objects, write paths, import code, or render active browser
content.

The review corpus exposes three related classes:

1. object serialization such as pickle, RData, and model checkpoints;
2. archive members whose names control filesystem writes;
3. HTML, SVG, or JavaScript interpreted by a browser.

Each crosses from bytes controlled by a user or remote service into behavior.

## 2. Pickle-like scientific formats

Python pickle can invoke arbitrary callables while loading. R workspace/RData
objects and machine-learning checkpoints can carry similar risks depending on
their loader and format.

[PR #3859](https://github.com/galaxyproject/tools-iuc/pull/3859#discussion_r700597777)
raised the question of whether IUC should accept uploaded RData inputs at all.
Reviewers described the format as both a security and reproducibility risk
comparable to pickle. The PR was not merged.

[PR #6037](https://github.com/galaxyproject/tools-iuc/pull/6037#discussion_r1631496051)
endorsed keeping a pickle internal to the tool rather than accepting an
arbitrary uploaded pickle.

The risk decision changes when:

- the file is created and consumed within one trusted job;
- the input can only come from a trusted tool output;
- the loader has a documented restricted mode;
- the deployment accepts only trusted users;
- the job is strongly isolated and has no useful credentials or writable shared
  resources.

These conditions can reduce risk, but should be explicit rather than inferred
from a file extension.

## 3. PyTorch and safer model exchange

[PR #7168](https://github.com/galaxyproject/tools-iuc/pull/7168#discussion_r2262907637)
identified uploaded `.pth` checkpoints as pickle-backed inputs that can execute
arbitrary code on public infrastructure.

The discussion progressed through two mitigations:

1. `torch.load(..., weights_only=True)` with a predefined trusted architecture,
   which narrows what the loader reconstructs;
2. migration to the non-pickle
   [safetensors format](https://github.com/galaxyproject/tools-iuc/pull/7168#discussion_r2326694430),
   which became the preferred final interface.

This is a useful policy pattern:

- prefer a format incapable of expressing executable objects;
- otherwise require a library safe-loading mode;
- separate model weights from executable model architecture;
- pin a minimum dependency version where the safe mode is actually enforced;
- add a Galaxy datatype so the safe artifact is distinguishable in workflows.

## 4. Archive extraction

[PR #4890](https://github.com/galaxyproject/tools-iuc/pull/4890) patched
CVE-2007-4559 in two data managers. The original code called
`tar.extractall()` on downloaded archives without proving that member paths
remained beneath the extraction root.

A safe extractor should account for:

- absolute paths;
- `..` components and canonical-path escapes;
- symbolic and hard links;
- device nodes and other special files;
- duplicate members and overwrite behavior;
- platform-specific separators;
- resource exhaustion from archive size or expansion ratio.

Checking only `member.name` as a string is not enough. Resolve the candidate
destination against a known root and verify containment. Links require their
own target policy. Prefer extracting only named members the tool needs.

Python's standard-library behavior changes over time, so a wrapper or helper
must also pin and document the minimum runtime whose extraction policy it
depends on.

## 5. Browser-active output

[PR #7810](https://github.com/galaxyproject/tools-iuc/pull/7810#discussion_r2971922247)
rejected shipping raw HTML because it was hard to review and carried security
concerns, recommending a repository-reviewed SVG asset and an inert PNG
preview instead.

Active content has multiple contexts with different escaping rules:

- HTML text;
- HTML attributes;
- URLs;
- CSS;
- JavaScript strings and programs;
- SVG elements, attributes, scripts, and remote references.

Escaping for one context is not safe for another. Sanitizing markup requires a
structural allowlist, not shell quoting or Galaxy's text-parameter character
map.

Review should determine:

1. whether the content is displayed inline or offered only as a download;
2. which values are user controlled;
3. which Galaxy datatype and rendering path serves it;
4. what browser origin and containment apply;
5. whether it can load remote content or communicate with its opener/parent;
6. whether a static image or Galaxy-native visualization is sufficient.

Galaxy's default deployment policy reflects this risk: HTML is sanitized unless
an administrator allowlists a tool, and XSS-prone SVG/XML-like MIME types are
served as plain text unless an administrator opts into active serving. Producing
active output therefore asks an administrator to extend trust to the wrapper;
it is not only a presentation choice.

## 6. Candidate static checks

High confidence:

- user-controlled pickle or unrestricted object deserialization;
- user-controlled RData/workspace loading without an explicit policy;
- archive `extractall` without member containment;
- user values emitted directly into HTML/JavaScript/SVG source.

Context dependent:

- PyTorch loading with `weights_only=True`;
- unsafe format used only for a same-job internal intermediate;
- active content emitted through an established isolated Galaxy datatype;
- trusted preinstalled models that users cannot replace;
- archive extraction using a runtime-provided safe filter whose minimum version
  is pinned.

## 7. Tests and negative fixtures

Serialization:

- verify the expected safe format is required;
- reject or safely fail on an object-bearing checkpoint;
- pin the safe-loader option and dependency version.

Archives:

- include `../escape`, absolute paths, nested traversal, and unsafe links;
- assert no file appears outside the extraction root;
- enforce file-count and expanded-size expectations where practical.

Active content:

- include markup delimiters, event attributes, script-like URLs, and closing
  tags in user values;
- verify the delivered datatype and rendering path;
- prefer a static expected artifact that can be inspected without executing it.
