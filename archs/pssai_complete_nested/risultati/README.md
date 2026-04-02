# Riepilogo Risultati

Questo documento riassume le metriche principali estratte automaticamente dai file Excel presenti in questa cartella.

*NB: Le metriche sono state calcolate usando il tool [psandman](https://github.com/dessertlab/psandman).*

## Globale

_File sorgente: `report_global.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 41.43 |
| CrystalBleu | 0.15 |
| Meteor | 0.45 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.91 |
| syntax_comparative_accuracy | 0.91 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.78 | 0.88 | 0.91 | 0.45 |
| Sysmon | ATT&CK Tags | 0.83 | 0.90 | 0.93 | 0.26 |
| PWSH | Rule IDs | 0.39 | 0.65 | 0.74 | 1.97 |
| PWSH | ATT&CK Tags | 0.60 | 0.83 | 0.88 | 0.68 |

## Categoria Backdoor

_File sorgente: `report_backdoor.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 48.55 |
| CrystalBleu | 0.12 |
| Meteor | 0.46 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.90 |
| syntax_comparative_accuracy | 0.90 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.70 | 0.80 | 0.85 | 0.60 |
| Sysmon | ATT&CK Tags | 0.70 | 0.83 | 0.88 | 0.40 |
| PWSH | Rule IDs | 0.33 | 0.81 | 0.89 | 0.83 |
| PWSH | ATT&CK Tags | 0.83 | 0.94 | 0.97 | 0.17 |

## Categoria Credential Stealer

_File sorgente: `report_credential_stealer.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 43.47 |
| CrystalBleu | 0.13 |
| Meteor | 0.50 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.90 |
| syntax_comparative_accuracy | 0.90 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.93 | 0.96 | 0.97 | 0.24 |
| Sysmon | ATT&CK Tags | 0.93 | 0.96 | 0.97 | 0.13 |
| PWSH | Rule IDs | 0.83 | 0.89 | 0.92 | 0.67 |
| PWSH | ATT&CK Tags | 0.83 | 0.94 | 0.97 | 0.17 |

## Categoria Downloader

_File sorgente: `report_downloader.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 49.64 |
| CrystalBleu | 0.00 |
| Meteor | 0.44 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.88 |
| syntax_comparative_accuracy | 0.88 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.50 | 0.73 | 0.79 | 1.38 |
| Sysmon | ATT&CK Tags | 0.75 | 0.85 | 0.90 | 0.38 |
| PWSH | Rule IDs | 0.43 | 0.68 | 0.77 | 2.00 |
| PWSH | ATT&CK Tags | 0.57 | 0.74 | 0.81 | 1.00 |

## Categoria Launcher Injection

_File sorgente: `report_launcher_injection.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 38.17 |
| CrystalBleu | 0.09 |
| Meteor | 0.51 |

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
| PWSH | Rule IDs | 0.43 | 0.59 | 0.68 | 2.29 |
| PWSH | ATT&CK Tags | 0.57 | 0.81 | 0.87 | 0.57 |

## Categoria Long Code

_File sorgente: `report_long_code.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 38.16 |
| CrystalBleu | 0.11 |
| Meteor | 0.33 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.83 |
| syntax_comparative_accuracy | 0.83 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.78 | 0.90 | 0.92 | 0.52 |
| Sysmon | ATT&CK Tags | 0.87 | 0.93 | 0.95 | 0.22 |
| PWSH | Rule IDs | 0.33 | 0.61 | 0.70 | 2.33 |
| PWSH | ATT&CK Tags | 0.50 | 0.76 | 0.84 | 0.67 |


## Categoria Privilege Escalation

_File sorgente: `report_privilege_escalation.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 34.10 |
| CrystalBleu | 0.07 |
| Meteor | 0.36 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.80 | 0.92 | 0.94 | 0.30 |
| Sysmon | ATT&CK Tags | 0.80 | 0.91 | 0.94 | 0.30 |
| PWSH | Rule IDs | 0.29 | 0.56 | 0.67 | 2.14 |
| PWSH | ATT&CK Tags | 0.43 | 0.71 | 0.80 | 0.71 |

## Categoria Short Code

_File sorgente: `report_short_code.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 62.37 |
| CrystalBleu | 0.19 |
| Meteor | 0.59 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.79 | 0.87 | 0.90 | 0.38 |
| Sysmon | ATT&CK Tags | 0.79 | 0.88 | 0.92 | 0.29 |
| PWSH | Rule IDs | 0.52 | 0.75 | 0.82 | 1.24 |
| PWSH | ATT&CK Tags | 0.71 | 0.86 | 0.90 | 0.48 |
