# Riepilogo Risultati

Questo documento riassume le metriche principali estratte automaticamente dai file Excel presenti in questa cartella.

*NB: Le metriche sono state calcolate usando il tool [psandman](https://github.com/dessertlab/psandman).*

## Globale

_File sorgente: `report_global.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 39.88 |
| CrystalBleu | 0.14 |
| Meteor | 0.51 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.96 |
| syntax_comparative_accuracy | 0.98 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.85 | 0.91 | 0.92 | 0.55 |
| Sysmon | ATT&CK Tags | 0.89 | 0.93 | 0.95 | 0.21 |
| PWSH | Rule IDs | 0.37 | 0.67 | 0.76 | 1.63 |
| PWSH | ATT&CK Tags | 0.63 | 0.83 | 0.89 | 0.47 |

## Categoria Backdoor

_File sorgente: `report_backdoor.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 48.16 |
| CrystalBleu | 0.13 |
| Meteor | 0.48 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.90 |
| syntax_comparative_accuracy | 0.90 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.96 | 0.98 | 0.99 | 0.05 |
| Sysmon | ATT&CK Tags | 0.96 | 0.98 | 0.99 | 0.10 |
| PWSH | Rule IDs | 0.50 | 0.88 | 0.93 | 0.50 |
| PWSH | ATT&CK Tags | 0.83 | 0.94 | 0.97 | 0.17 |

## Categoria Credential Stealer

_File sorgente: `report_credential_stealer.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 37.65 |
| CrystalBleu | 0.10 |
| Meteor | 0.56 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.90 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.96 | 0.98 | 0.99 | 0.14 |
| Sysmon | ATT&CK Tags | 0.96 | 0.98 | 0.99 | 0.16 |
| PWSH | Rule IDs | 0.67 | 0.81 | 0.86 | 0.50 |
| PWSH | ATT&CK Tags | 0.76 | 0.91 | 0.94 | 0.43 |

## Categoria Downloader

_File sorgente: `report_downloader.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 51.26 |
| CrystalBleu | 0.00 |
| Meteor | 0.48 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.50 | 0.71 | 0.76 | 1.75 |
| Sysmon | ATT&CK Tags | 0.75 | 0.85 | 0.90 | 0.38 |
| PWSH | Rule IDs | 0.29 | 0.65 | 0.75 | 1.86 |
| PWSH | ATT&CK Tags | 0.43 | 0.75 | 0.84 | 0.57 |

## Categoria Launcher Injection

_File sorgente: `report_launcher_injection.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 38.03 |
| CrystalBleu | 0.11 |
| Meteor | 0.68 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.89 | 0.94 | 0.96 | 0.11 |
| Sysmon | ATT&CK Tags | 0.89 | 0.93 | 0.94 | 0.22 |
| PWSH | Rule IDs | 0.43 | 0.60 | 0.69 | 1.71 |
| PWSH | ATT&CK Tags | 0.71 | 0.83 | 0.90 | 0.43 |

## Categoria Long Code

_File sorgente: `report_long_code.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 35.77 |
| CrystalBleu | 0.10 |
| Meteor | 0.33 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.96 |
| syntax_comparative_accuracy | 0.96 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.78 | 0.86 | 0.88 | 1.00 |
| Sysmon | ATT&CK Tags | 0.87 | 0.91 | 0.93 | 0.30 |
| PWSH | Rule IDs | 0.50 | 0.69 | 0.76 | 1.75 |
| PWSH | ATT&CK Tags | 0.58 | 0.78 | 0.84 | 0.58 |

## Categoria Privilege Escalation

_File sorgente: `report_privilege_escalation.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 32.38 |
| CrystalBleu | 0.07 |
| Meteor | 0.35 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.80 | 0.84 | 0.87 | 1.10 |
| Sysmon | ATT&CK Tags | 0.80 | 0.86 | 0.89 | 0.50 |
| PWSH | Rule IDs | 0.29 | 0.62 | 0.72 | 2.00 |
| PWSH | ATT&CK Tags | 0.57 | 0.79 | 0.85 | 0.57 |

## Categoria Short Code

_File sorgente: `report_short_code.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 67.30 |
| CrystalBleu | 0.23 |
| Meteor | 0.69 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.96 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.92 | 0.95 | 0.97 | 0.12 |
| Sysmon | ATT&CK Tags | 0.92 | 0.95 | 0.97 | 0.12 |
| PWSH | Rule IDs | 0.38 | 0.71 | 0.80 | 1.14 |
| PWSH | ATT&CK Tags | 0.76 | 0.91 | 0.94 | 0.24 |
