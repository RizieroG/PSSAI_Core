# Riepilogo Risultati

Questo documento riassume le metriche principali estratte automaticamente dai file Excel presenti in questa cartella.

*NB: Le metriche sono state calcolate usando il tool [psandman](https://github.com/dessertlab/psandman).*

## Globale

_File sorgente: `report_global.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 38.10 |
| CrystalBleu | 0.11 |
| Meteor | 0.39 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.98 |
| syntax_comparative_accuracy | 0.98 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.77 | 0.85 | 0.88 | 0.72 |
| Sysmon | ATT&CK Tags | 0.81 | 0.88 | 0.91 | 0.36 |
| PWSH | Rule IDs | 0.26 | 0.57 | 0.68 | 2.53 |
| PWSH | ATT&CK Tags | 0.47 | 0.76 | 0.84 | 0.68 |

## Categoria Backdoor

_File sorgente: `report_backdoor.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 45.29 |
| CrystalBleu | 0.13 |
| Meteor | 0.37 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.70 | 0.78 | 0.82 | 0.90 |
| Sysmon | ATT&CK Tags | 0.70 | 0.83 | 0.88 | 0.40 |
| PWSH | Rule IDs | 0.00 | 0.53 | 0.67 | 2.17 |
| PWSH | ATT&CK Tags | 0.33 | 0.69 | 0.80 | 0.67 |

## Categoria Credential Stealer

_File sorgente: `report_credential_stealer.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 34.75 |
| CrystalBleu | 0.06 |
| Meteor | 0.46 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.93 | 0.96 | 0.97 | 0.28 |
| Sysmon | ATT&CK Tags | 0.93 | 0.96 | 0.97 | 0.15 |
| PWSH | Rule IDs | 0.67 | 0.76 | 0.82 | 1.17 |
| PWSH | ATT&CK Tags | 0.83 | 0.88 | 0.92 | 0.17 |

## Categoria Downloader

_File sorgente: `report_downloader.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 49.16 |
| CrystalBleu | 0.00 |
| Meteor | 0.44 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.50 | 0.75 | 0.81 | 1.25 |
| Sysmon | ATT&CK Tags | 0.75 | 0.85 | 0.90 | 0.38 |
| PWSH | Rule IDs | 0.29 | 0.65 | 0.76 | 1.86 |
| PWSH | ATT&CK Tags | 0.43 | 0.70 | 0.82 | 0.57 |

## Categoria Launcher Injection

_File sorgente: `report_launcher_injection.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 32.83 |
| CrystalBleu | 0.04 |
| Meteor | 0.37 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.89 |
| syntax_comparative_accuracy | 0.89 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.89 | 0.94 | 0.96 | 0.11 |
| Sysmon | ATT&CK Tags | 0.89 | 0.93 | 0.94 | 0.22 |
| PWSH | Rule IDs | 0.29 | 0.51 | 0.61 | 3.43 |
| PWSH | ATT&CK Tags | 0.43 | 0.71 | 0.80 | 0.86 |

## Categoria Long Code

_File sorgente: `report_long_code.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 35.51 |
| CrystalBleu | 0.08 |
| Meteor | 0.31 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.96 |
| syntax_comparative_accuracy | 0.96 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.70 | 0.81 | 0.84 | 1.13 |
| Sysmon | ATT&CK Tags | 0.78 | 0.86 | 0.89 | 0.48 |
| PWSH | Rule IDs | 0.17 | 0.49 | 0.60 | 3.42 |
| PWSH | ATT&CK Tags | 0.25 | 0.62 | 0.74 | 1.00 |

## Categoria Privilege Escalation

_File sorgente: `report_privilege_escalation.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 33.27 |
| CrystalBleu | 0.05 |
| Meteor | 0.33 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.70 | 0.77 | 0.81 | 1.40 |
| Sysmon | ATT&CK Tags | 0.70 | 0.78 | 0.83 | 0.80 |
| PWSH | Rule IDs | 0.29 | 0.53 | 0.64 | 3.00 |
| PWSH | ATT&CK Tags | 0.57 | 0.79 | 0.85 | 0.57 |

## Categoria Short Code

_File sorgente: `report_short_code.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 53.18 |
| CrystalBleu | 0.13 |
| Meteor | 0.48 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.83 | 0.89 | 0.92 | 0.33 |
| Sysmon | ATT&CK Tags | 0.83 | 0.90 | 0.93 | 0.25 |
| PWSH | Rule IDs | 0.38 | 0.66 | 0.75 | 1.76 |
| PWSH | ATT&CK Tags | 0.67 | 0.88 | 0.92 | 0.33 |
