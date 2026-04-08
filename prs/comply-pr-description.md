# PR: Replace vague control language in SOC2 policy templates

**Target repo:** strongdm/comply
**Branch:** `fix/vague-policy-language`
**Base:** `master`

---

## Title

Fix vague control language that triggers SOC2/SOX audit findings

## Body

SOC2 policy templates exist so companies can adopt them and pass audits. But several templates contain language that auditors will flag as insufficient under specific Trust Services Criteria.

I ran these templates through [Redline](https://github.com/BipinRimal314/redline), a deterministic compliance doc linter that traces every flag to a regulation paragraph. Four files produced findings:

**availability.md** -- "proper controls" appears 3 times. SOX Section 404 (AS 2201) requires control descriptions to be specific and testable. An auditor reading "proper controls" will ask: which controls? Reviewed how often? By whom? This language forces every adopter to rewrite it before their audit.

**application.md** -- Risk levels (High/Medium/Low) are used in the vulnerability section but reference OWASP externally without restating the criteria in-policy. SOC2 CC3.2 requires risk assessments with defined scoring criteria. Added inline criteria summary so the policy stands alone.

**encryption.md** -- "appropriate access control mechanisms" in the key protection clause. SOC2 CC6.1 requires documented access controls with defined authorization criteria. Replaced with specific mechanisms.

**confidentiality.md** -- "appropriate privileges" used without reference to a classification scheme. SOC2 C1.1 requires formal data classification. Added cross-reference to the Data Classification Policy already mentioned elsewhere in the repo.

Each change replaces a vague qualifier with specific, testable language. The templates remain generic enough for any organization to customize, but now they won't trigger the most common audit findings on first read.

These findings were identified using deterministic regex-based linting rules, each traceable to a regulation paragraph. No LLM was used in the analysis.

### Files changed

- `example/policies/availability.md`
- `example/policies/application.md`
- `example/policies/encryption.md`
- `example/policies/confidentiality.md`
