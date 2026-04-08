# Comply PR: Specific Line Changes

Each change below maps to a Redline finding with a regulation trace.

---

## 1. `example/policies/availability.md`

### Finding: SOXVagueControls (SOX Section 404, AS 2201)

"proper controls" appears 3 times. SOX Section 404 requires specific, testable control descriptions with defined procedures, frequencies, and responsible parties.

### Change 1a: Purpose and Scope, section a (first paragraph)

**Before:**
```
a. The purpose of this policy is to define requirements for proper controls to protect
the availability of the organization's information systems.
```

**After:**
```
a. The purpose of this policy is to define requirements for availability controls --
including redundancy, failover, backup, and business continuity measures -- to protect
the availability of the organization's information systems.
```

**Rationale:** Replaces "proper controls" with the four specific control categories that the policy itself defines in later sections. Now the purpose statement is traceable to the policy body.

### Change 1b: Policy, section b

**Before:**
```
a. Information systems must have a defined availability classification, with appropriate
controls enabled and incorporated into development and production processes based on
this classification.
```

**After:**
```
a. Information systems must have a defined availability classification (see Table 3),
with controls matching that classification -- including redundancy, monitoring, and
failover mechanisms -- enabled and incorporated into development and production
processes.
```

**Rationale:** "appropriate controls" is subjective. Linking to Table 3 (which already exists in the document) and naming the control types makes this testable. An auditor can verify: does the High-classification system have redundancy, monitoring, and failover? Yes or no.

---

## 2. `example/policies/application.md`

### Finding: SOC2MissingRiskCriteria (CC3.2)

Risk levels (High/Medium/Low) are used in section e to classify vulnerabilities, but the criteria for each level are defined only by external reference to OWASP. SOC2 CC3.2 requires risk assessments with defined methodologies and scoring criteria within the policy context.

### Change 2a: Policy, section e (before the subsections)

**Before:**
```
a. Vulnerabilities that are discovered during application assessments must be mitigated
based upon the following risk levels, which are based on the Open Web Application
Security Project (OWASP) Risk Rating Methodology (reference (b)):
```

**After:**
```
a. Vulnerabilities that are discovered during application assessments must be mitigated
based upon the following risk levels. Risk ratings are derived from the Open Web
Application Security Project (OWASP) Risk Rating Methodology (reference (b)),
combining likelihood and technical impact:

    - High: Likely to be discovered and exploited; causes severe data loss, full system
      compromise, or significant business impact.
    - Medium: Moderate likelihood of discovery; causes limited data exposure or partial
      system compromise.
    - Low: Unlikely to be discovered or exploited; causes minimal data exposure with
      limited business impact.

    Specific mitigation requirements for each level:
```

**Rationale:** The policy previously used High/Medium/Low as labels without defining what each level means. Companies adopting this template would face CC3.2 findings because the risk criteria aren't self-contained. The added definitions make the policy standalone -- an auditor doesn't need to open the OWASP reference to understand the rating scale.

---

## 3. `example/policies/encryption.md`

### Finding: SOC2VagueAccessControls (CC6.1)

"appropriate access control mechanisms" in section c. SOC2 CC6.1 requires documented logical and physical access controls with defined authorization criteria.

### Change 3a: Policy, section c

**Before:**
```
c. Cryptographic keys must be protected against loss, change or destruction by applying
appropriate access control mechanisms to prevent unauthorized use and backing up keys
on a regular basis.
```

**After:**
```
c. Cryptographic keys must be protected against loss, change or destruction by applying
access controls that include role-based permissions, separation of duties between key
administrators and key users, and audit logging of all key access events. Keys must be
backed up at least as frequently as the key rotation schedule defined in section f.
```

**Rationale:** "appropriate access control mechanisms" gives an auditor nothing to test against. The replacement names three specific, verifiable controls (RBAC, separation of duties, audit logging) and cross-references the backup frequency to the rotation schedule already defined later in the document.

---

## 4. `example/policies/confidentiality.md`

### Finding: SOC2VagueDataClassification (C1.1) + SOC2VagueAccessControls (CC6.1)

"appropriate privileges" in Policy section a.vi is used without cross-reference to a defined classification scheme. SOC2 C1.1 requires formal data classification with explicit handling requirements. The term "confidential information" is defined in the Background section, but access levels are not mapped to that classification.

### Change 4a: Policy, section a.vi

**Before:**
```
    i. Do not disclose confidential information to anyone outside the company or to
    anyone within the company who does not have appropriate privileges
```

**After:**
```
    i. Do not disclose confidential information to anyone outside the company or to
    anyone within the company who has not been granted access in accordance with the
    Data Classification Policy and whose access has not been approved by the
    information owner
```

**Rationale:** "appropriate privileges" is subjective. The replacement ties access decisions to two concrete checks: (1) alignment with the Data Classification Policy (which the application.md already cross-references), and (2) explicit approval from the information owner. Both are auditable.

### Change 4b: Confidentiality Measures, section c.i.2

**Before:**
```
        1. Encrypt electronic information and implement appropriate technical measures
        to safeguard databases
```

**After:**
```
        1. Encrypt electronic information at rest and in transit, implement database
        access controls including role-based permissions, and maintain audit logs of
        database access events
```

**Rationale:** "appropriate technical measures" is the kind of language that costs companies weeks of back-and-forth with auditors. The replacement names the specific measures (encryption scope, RBAC, audit logging) that a SOC2 auditor will look for.

---

## Summary of findings

| File | Finding | Rule | Regulation | Severity |
|---|---|---|---|---|
| availability.md | "proper controls" x3 | SOXVagueControls | SOX Section 404, AS 2201 | error |
| application.md | Undefined risk criteria | SOC2MissingRiskCriteria | SOC2 CC3.2 | error |
| encryption.md | "appropriate access control mechanisms" | SOC2VagueAccessControls | SOC2 CC6.1 | error |
| confidentiality.md | "appropriate privileges" | SOC2VagueAccessControls | SOC2 CC6.1 | error |
| confidentiality.md | "appropriate technical measures" | SOC2VagueAccessControls | SOC2 CC6.1 | error |

All findings identified by [Redline](https://github.com/BipinRimal314/redline) -- deterministic compliance doc linter with regulation-traceable rules.
