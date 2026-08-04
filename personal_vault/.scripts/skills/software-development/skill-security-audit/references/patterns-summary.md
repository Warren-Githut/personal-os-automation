# 64 vulnerability patterns — condensed

## 16 categories

### 1. Prompt Injection
P1 Instruction Override (HIGH)
P2 Hidden Instructions (HIGH)
P3 Exfiltration Commands (HIGH)
P4 Behavior Manipulation (MEDIUM)
P5 Harmful Content (CRITICAL)

### 2. Data Exfiltration
E1 External Transmission (MEDIUM)
E2 Env Variable Harvesting (HIGH)
E3 File System Enumeration (MEDIUM)
E4 Context Leakage (HIGH)

### 3. Privilege Escalation
PE1 Excessive Permissions (LOW)
PE2 Sudo/Root Execution (MEDIUM)
PE3 Credential Access (HIGH)

### 4. Supply Chain
SC1 Unpinned Dependencies (LOW)
SC2 External Script Fetching (HIGH)
SC3 Obfuscated Code (HIGH)
SC4 Known Vulnerable Deps — auto-queries OSV.dev (HIGH)
SC5 Abandoned Dependencies (MEDIUM)
SC6 Typosquatting (HIGH)

### 5. Excessive Agency
EA1 Unrestricted Tool Access (HIGH)
EA2 Autonomous Decision Making (HIGH)
EA3 Scope Creep (MEDIUM)
EA4 Unbounded Resource Access (MEDIUM)

### 6. Output Handling
OH1 Unvalidated Output Injection (HIGH)
OH2 Cross-Context Output (MEDIUM)
OH3 Unbounded Output (MEDIUM)

### 7. System Prompt Leakage
P6 Direct Leakage (HIGH)
P7 Indirect Extraction (MEDIUM)
P8 Debug Artifacts (LOW)

### 8. File System Tampering
F1 Unauthorized Writes (HIGH)
F2 Dangerous Permissions (MEDIUM)
F3 Archive Extraction Without Validation (HIGH)

### 9. Network Abuse
N1 Callback Allowed (HIGH)
N2 Downgrade Risk (MEDIUM)
N3 Hardcoded IP/Domain (MEDIUM)

### 10. Encryption/Crypto
C1 Weak Algorithm (HIGH)
C2 Hardcoded Keys (CRITICAL)
C3 Certificate Bypass (HIGH)

### 11. Authentication
AU1 Hardcoded Credentials (CRITICAL)
AU2 Session Token Leakage (HIGH)
AU3 Weak Auth Flow (MEDIUM)

### 12. Input Validation
IV1 Command Injection (CRITICAL)
IV2 Path Traversal (HIGH)
IV3 Unvalidated Deserialization (HIGH)

### 13. Logging/Side Channels
LG1 Sensitive Logging (HIGH)
LG2 Timing Side Channel (LOW)

### 14. Resource Abuse
RA1 Infinite Loop (MEDIUM)
RA2 Memory Bomb (MEDIUM)
RA3 Crypto Mining Pattern (CRITICAL)

### 15. Data Privacy
DP1 PII Collection (HIGH)
DP2 Unencrypted Storage (MEDIUM)
DP3 Data Retention Violation (LOW)

### 16. Tool Misuse
TM1 Tool Parameter Abuse (HIGH)
TM2 Chaining Abuse (HIGH)
TM3 Tool Impersonation (HIGH)
