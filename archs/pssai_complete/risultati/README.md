# Riepilogo Risultati

Questo documento riassume le metriche principali estratte automaticamente dai file Excel presenti in questa cartella.

*NB: Le metriche sono state calcolate usando il tool [psandman](https://github.com/dessertlab/psandman).*

## Globale

_File sorgente: `report_global.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 50.90 |
| CrystalBleu | 0.24 |
| Meteor | 0.64 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.87 |
| syntax_comparative_accuracy | 0.94 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.93 | 0.96 | 0.97 | 0.24 |
| Sysmon | ATT&CK Tags | 0.93 | 0.96 | 0.97 | 0.13 |
| PWSH | Rule IDs | 0.72 | 0.84 | 0.88 | 0.81 |
| PWSH | ATT&CK Tags | 0.78 | 0.90 | 0.93 | 0.31 |

## Categoria Backdoor

_File sorgente: `report_backdoor.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 59.43 |
| CrystalBleu | 0.29 |
| Meteor | 0.65 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.90 |
| syntax_comparative_accuracy | 0.90 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.96 | 0.98 | 0.99 | 0.04 |
| Sysmon | ATT&CK Tags | 0.96 | 0.98 | 0.99 | 0.04 |
| PWSH | Rule IDs | 0.90 | 0.91 | 0.92 | 0.90 |
| PWSH | ATT&CK Tags | 0.90 | 0.93 | 0.94 | 0.50 |

## Categoria Credential Stealer

_File sorgente: `report_credential_stealer.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 38.61 |
| CrystalBleu | 0.10 |
| Meteor | 0.49 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.96 | 0.98 | 0.99 | 0.14 |
| Sysmon | ATT&CK Tags | 0.96 | 0.98 | 0.99 | 0.04 |
| PWSH | Rule IDs | 0.50 | 0.72 | 0.80 | 1.17 |
| PWSH | ATT&CK Tags | 0.83 | 0.92 | 0.94 | 0.33 |

## Categoria Downloader

_File sorgente: `report_downloader.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 50.85 |
| CrystalBleu | 0.00 |
| Meteor | 0.41 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.88 | 0.94 | 0.96 | 0.12 |
| Sysmon | ATT&CK Tags | 0.88 | 0.94 | 0.96 | 0.12 |
| PWSH | Rule IDs | 0.57 | 0.77 | 0.84 | 2.00 |
| PWSH | ATT&CK Tags | 0.57 | 0.82 | 0.88 | 0.71 |

## Categoria Launcher Injection

_File sorgente: `report_launcher_injection.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 36.72 |
| CrystalBleu | 0.06 |
| Meteor | 0.41 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.78 |
| syntax_comparative_accuracy | 0.89 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.89 | 0.94 | 0.96 | 0.11 |
| Sysmon | ATT&CK Tags | 0.89 | 0.93 | 0.94 | 0.22 |
| PWSH | Rule IDs | 0.71 | 0.79 | 0.83 | 1.14 |
| PWSH | ATT&CK Tags | 0.71 | 0.86 | 0.90 | 0.43 |

## Categoria Long Code

_File sorgente: `report_long_code.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 47.25 |
| CrystalBleu | 0.20 |
| Meteor | 0.44 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.79 |
| syntax_comparative_accuracy | 0.88 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.91 | 0.94 | 0.95 | 0.43 |
| Sysmon | ATT&CK Tags | 0.91 | 0.94 | 0.95 | 0.22 |
| PWSH | Rule IDs | 0.75 | 0.82 | 0.86 | 1.00 |
| PWSH | ATT&CK Tags | 0.75 | 0.86 | 0.90 | 0.42 |

## Categoria Privilege Escalation

_File sorgente: `report_privilege_escalation.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 35.53 |
| CrystalBleu | 0.10 |
| Meteor | 0.38 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.90 |
| syntax_comparative_accuracy | 0.90 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.90 | 0.91 | 0.92 | 0.90 |
| Sysmon | ATT&CK Tags | 0.90 | 0.93 | 0.94 | 0.30 |
| PWSH | Rule IDs | 0.71 | 0.87 | 0.91 | 0.57 |
| PWSH | ATT&CK Tags | 0.71 | 0.88 | 0.92 | 0.29 |

## Categoria Short Code

_File sorgente: `report_short_code.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 76.92 |
| CrystalBleu | 0.32 |
| Meteor | 0.84 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.96 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.96 | 0.98 | 0.99 | 0.04 |
| Sysmon | ATT&CK Tags | 0.96 | 0.98 | 0.99 | 0.04 |
| PWSH | Rule IDs | 0.67 | 0.83 | 0.88 | 1.00 |
| PWSH | ATT&CK Tags | 0.76 | 0.91 | 0.94 | 0.33 |
