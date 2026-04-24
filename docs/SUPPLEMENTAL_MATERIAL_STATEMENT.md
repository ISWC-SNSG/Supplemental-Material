# Supplemental Material Statement Templates

## Anonymous Review Version

Use this version during double-blind review. Replace `<ANON_REPO_URL>` with the anonymous repository URL. If the submission system provides a ZIP rather than a repository URL, use the alternative ZIP wording below.

```latex
\paragraph*{Supplemental Material Statement:}
The anonymous supplemental repository accompanying this submission is available at \url{<ANON_REPO_URL>}. It provides the released benchmark files (\textbf{TechRisk-EventLogic-Bench}), fixed public-evaluation subset manifests, metric definitions, paper-aligned result artifacts, evaluation utilities, prompt templates, configuration files, reproduction notes, and reference baseline adapters used to document the benchmark-local comparison protocol. The adapters are independent protocol-level adaptations and are not official implementations of the cited baseline systems. Official third-party baseline code and full raw mirrors of public datasets are not redistributed. The repository is intended to support anonymous verification of the reported results and evaluation protocol during review; a permanent public release will be prepared after the review process.
```

## Anonymous Review Version When Uploaded as a ZIP

```latex
\paragraph*{Supplemental Material Statement:}
The supplemental ZIP file uploaded with this submission provides the released benchmark files (\textbf{TechRisk-EventLogic-Bench}), fixed public-evaluation subset manifests, metric definitions, paper-aligned result artifacts, evaluation utilities, prompt templates, configuration files, reproduction notes, and reference baseline adapters used to document the benchmark-local comparison protocol. The adapters are independent protocol-level adaptations and are not official implementations of the cited baseline systems. Official third-party baseline code and full raw mirrors of public datasets are not redistributed. The supplemental materials are intended to support anonymous verification of the reported results and evaluation protocol during review; a permanent public release will be prepared after the review process.
```

## URL Placement

Before submission, replace the placeholder in the anonymous-review version:

```latex
... is available at \url{<ANON_REPO_URL>}. It provides ...
                     ^^^^^^^^^^^^^^^^^^^^^
                     replace with the anonymous repository URL
```

## Camera-Ready / Post-Acceptance Version

Replace `<PUBLIC_REPO_URL>` with the final public repository URL.

```latex
\paragraph*{Supplemental Material Statement:}
The released benchmark files (\textbf{TechRisk-EventLogic-Bench}), fixed public-evaluation subset manifests, metric definitions, result artifacts, evaluation utilities, prompt templates, configuration files, reproduction notes, and reference baseline adapters are publicly available at \url{<PUBLIC_REPO_URL>}. The final public release also includes versioned documentation, schema descriptions, and citation metadata.
```
