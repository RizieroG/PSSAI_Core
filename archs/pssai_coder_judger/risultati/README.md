# Riepilogo Risultati

Questo documento riassume le metriche principali estratte automaticamente dai file Excel presenti in questa cartella.

*NB: Le metriche sono state calcolate usando il tool [psandman](https://github.com/dessertlab/psandman).*

## Globale

_File sorgente: `report_globale.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 40.71 |
| CrystalBleu | 0.13 |
| Meteor | 0.42 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.94 |
| syntax_comparative_accuracy | 0.94 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.79 | 10.86 | 0.89 | 0.60 |
| Sysmon | ATT&CK Tags | 0.81 | 0.88 | 0.91 | 0.36 |
| PWSH | Rule IDs | 0.39 | 0.67 | 0.77 | 1.84 |
| PWSH | ATT&CK Tags | 0.63 | 0.85 | 0.90 | 0.50 |

## Categoria Backdoor

_File sorgente: `report_backdoor.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 50.31 |
| CrystalBleu | 0.16 |
| Meteor | 0.46 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.80 |
| syntax_comparative_accuracy | 0.80 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.80 | 0.87 | 0.90 | 0.40 |
| Sysmon | ATT&CK Tags | 0.80 | 0.88 | 0.92 | 0.30 |
| PWSH | Rule IDs | 0.67 | 0.86 | 0.91 | 0.67 |
| PWSH | ATT&CK Tags | 0.83 | 0.94 | 0.97 | 0.17 |

## Categoria Credential Stealer

_File sorgente: `report_credential_stealer.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 37.87 |
| CrystalBleu | 0.06 |
| Meteor | 0.45 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.90 | 0.95 | 0.97 | 0.10 |
| Sysmon | ATT&CK Tags | 0.90 | 0.93 | 0.95 | 0.20 |
| PWSH | Rule IDs | 0.33 | 0.67 | 0.76 | 1.33 |
| PWSH | ATT&CK Tags | 0.67 | 0.90 | 0.94 | 0.33 |

## Categoria Downloader

_File sorgente: `report_downloader.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 52.79 |
| CrystalBleu | 0.00 |
| Meteor | 0.43 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.62 | 0.70 | 0.75 | 1.88 |
| Sysmon | ATT&CK Tags | 0.75 | 0.83 | 0.88 | 0.50 |
| PWSH | Rule IDs | 0.29 | 0.62 | 0.73 | 2.43 |
| PWSH | ATT&CK Tags | 0.43 | 0.71 | 0.80 | 0.86 |

## Categoria Launcher Injection

_File sorgente: `report_launcher_injection.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 32.93 |
| CrystalBleu | 0.07 |
| Meteor | 0.46 |

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
| PWSH | Rule IDs | 0.57 | 0.72 | 0.79 | 1.57 |
| PWSH | ATT&CK Tags | 0.71 | 0.90 | 0.94 | 0.29 |

## Categoria Long Code

_File sorgente: `report_long_code.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 37.02 |
| CrystalBleu | 0.09 |
| Meteor | 0.30 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.88 |
| syntax_comparative_accuracy | 0.88 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.74 | 0.83 | 0.87 | 0.91 |
| Sysmon | ATT&CK Tags | 0.78 | 0.87 | 0.90 | 0.43 |
| PWSH | Rule IDs | 0.50 | 0.67 | 0.75 | 2.25 |
| PWSH | ATT&CK Tags | 0.50 | 0.76 | 0.84 | 0.67 |

## Categoria Privilege Escalation

_File sorgente: `report_privilege_escalation.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 35.12 |
| CrystalBleu | 0.08 |
| Meteor | 0.31 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.70 | 0.84 | 0.88 | 0.70 |
| Sysmon | ATT&CK Tags | 0.70 | 0.83 | 0.88 | 0.60 |
| PWSH | Rule IDs | 0.29 | 0.61 | 0.71 | 2.14 |
| PWSH | ATT&CK Tags | 0.71 | 0.83 | 0.88 | 0.43 |

## Categoria Short Code

_File sorgente: `report_short_code.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 64.75 |
| CrystalBleu | 0.20 |
| Meteor | 0.54 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.83 | 0.90 | 0.92 | 0.29 |
| Sysmon | ATT&CK Tags | 0.83 | 0.90 | 0.92 | 0.29 |
| PWSH | Rule IDs | 0.38 | 0.71 | 0.80 | 1.33 |
| PWSH | ATT&CK Tags | 0.76 | 0.91 | 0.94 | 0.29 |
