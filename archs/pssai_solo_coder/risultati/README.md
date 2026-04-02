# Riepilogo Risultati

Questo documento riassume le metriche principali estratte automaticamente dai file Excel presenti in questa cartella.

*NB: Le metriche sono state calcolate usando il tool [psandman](https://github.com/dessertlab/psandman).*

## Globale

_File sorgente: `report_global.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 40.01 |
| CrystalBleu | 0.15 |
| Meteor | 0.44 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.94 |
| syntax_comparative_accuracy | 0.96 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.79 | 0.85 | 0.88 | 0.74 |
| Sysmon | ATT&CK Tags | 0.81 | 0.88 | 0.91 | 0.34 |
| PWSH | Rule IDs | 0.24 | 0.61 | 0.71 | 2.42 |
| PWSH | ATT&CK Tags | 0.53 | 0.80 | 0.87 | 0.63 |

## Categoria Backdoor

_File sorgente: `report_backdoor.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 44.65 |
| CrystalBleu | 0.12 |
| Meteor | 0.48 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.70 | 0.79 | 0.84 | 0.70 |
| Sysmon | ATT&CK Tags | 0.70 | 0.83 | 0.88 | 0.40 |
| PWSH | Rule IDs | 0.33 | 0.71 | 0.80 | 1.33 |
| PWSH | ATT&CK Tags | 0.67 | 0.83 | 0.88 | 0.50 |

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
| Sysmon | Rule IDs | 0.89 | 0.94 | 0.96 | 0.21 |
| Sysmon | ATT&CK Tags | 0.89 | 0.93 | 0.94 | 0.32 |
| PWSH | Rule IDs | 0.17 | 0.56 | 0.69 | 1.83 |
| PWSH | ATT&CK Tags | 0.67 | 0.86 | 0.91 | 0.50 |

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
| Sysmon | Rule IDs | 0.50 | 0.64 | 0.70 | 2.00 |
| Sysmon | ATT&CK Tags | 0.62 | 0.77 | 0.83 | 0.62 |
| PWSH | Rule IDs | 0.00 | 0.59 | 0.71 | 2.57 |
| PWSH | ATT&CK Tags | 0.43 | 0.74 | 0.82 | 0.86 |

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
| PWSH | Rule IDs | 0.43 | 0.59 | 0.68 | 3.14 |
| PWSH | ATT&CK Tags | 0.57 | 0.86 | 0.91 | 0.43 |

## Categoria Long Code

_File sorgente: `report_long_code.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 37.44 |
| CrystalBleu | 0.12 |
| Meteor | 0.34 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.92 |
| syntax_comparative_accuracy | 0.96 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.78 | 0.83 | 0.86 | 1.09 |
| Sysmon | ATT&CK Tags | 0.83 | 0.88 | 0.91 | 0.39 |
| PWSH | Rule IDs | 0.33 | 0.60 | 0.70 | 2.83 |
| PWSH | ATT&CK Tags | 0.50 | 0.79 | 0.86 | 0.58 |

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
| Sysmon | Rule IDs | 0.80 | 0.84 | 0.87 | 1.10 |
| Sysmon | ATT&CK Tags | 0.80 | 0.86 | 0.89 | 0.50 |
| PWSH | Rule IDs | 0.43 | 0.68 | 0.75 | 2.14 |
| PWSH | ATT&CK Tags | 0.71 | 0.83 | 0.88 | 0.43 |

## Categoria Short Code

_File sorgente: `report_short_code.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 55.55 |
| CrystalBleu | 0.17 |
| Meteor | 0.54 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.96 |
| syntax_comparative_accuracy | 0.96 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.79 | 0.86 | 0.90 | 0.42 |
| Sysmon | ATT&CK Tags | 0.79 | 0.88 | 0.92 | 0.29 |
| PWSH | Rule IDs | 0.24 | 0.64 | 0.74 | 1.90 |
| PWSH | ATT&CK Tags | 0.67 | 0.84 | 0.89 | 0.52 |
