# Riepilogo Risultati

Questo documento riassume le metriche principali estratte automaticamente dai file Excel presenti in questa cartella.

*NB: Le metriche sono state calcolate usando il tool [psandman](https://github.com/dessertlab/psandman).*

## Globale

_File sorgente: `report_global.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 40.27 |
| CrystalBleu | 0.14 |
| Meteor | 0.46 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.96 |
| syntax_comparative_accuracy | 0.96 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.77 | 0.87 | 0.90 | 0.53 |
| Sysmon | ATT&CK Tags | 0.81 | 0.89 | 0.92 | 0.30 |
| PWSH | Rule IDs | 0.32 | 0.60 | 0.70 | 2.39 |
| PWSH | ATT&CK Tags | 0.53 | 0.79 | 0.86 | 0.71 |

## Categoria Backdoor

_File sorgente: `report_backdoor.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 49.03 |
| CrystalBleu | 0.15 |
| Meteor | 0.46 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.90 |
| syntax_comparative_accuracy | 0.90 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.70 | 0.79 | 0.84 | 0.70 |
| Sysmon | ATT&CK Tags | 0.70 | 0.83 | 0.88 | 0.40 |
| PWSH | Rule IDs | 0.33 | 0.78 | 0.86 | 1.17 |
| PWSH | ATT&CK Tags | 0.83 | 0.94 | 0.97 | 0.17 |

## Categoria Credential Stealer

_File sorgente: `report_credential_stealer.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 40.48 |
| CrystalBleu | 0.11 |
| Meteor | 0.50 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.93 | 0.96 | 0.97 | 0.24 |
| Sysmon | ATT&CK Tags | 0.93 | 0.96 | 0.97 | 0.13 |
| PWSH | Rule IDs | 0.33 | 0.65 | 0.75 | 1.50 |
| PWSH | ATT&CK Tags | 0.67 | 0.90 | 0.94 | 0.33 |

## Categoria Downloader

_File sorgente: `report_downloader.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 48.88 |
| CrystalBleu | 0.00 |
| Meteor | 0.49 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.88 |
| syntax_comparative_accuracy | 0.88 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.50 | 0.71 | 0.78 | 1.50 |
| Sysmon | ATT&CK Tags | 0.75 | 0.85 | 0.90 | 0.38 |
| PWSH | Rule IDs | 0.43 | 0.61 | 0.69 | 2.43 |
| PWSH | ATT&CK Tags | 0.43 | 0.67 | 0.76 | 1.14 |

## Categoria Launcher Injection

_File sorgente: `report_launcher_injection.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 37.82 |
| CrystalBleu | 0.06 |
| Meteor | 0.48 |

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
| PWSH | Rule IDs | 0.14 | 0.44 | 0.57 | 3.43 |
| PWSH | ATT&CK Tags | 0.43 | 0.74 | 0.82 | 0.86 |

## Categoria Long Code

_File sorgente: `report_long_code.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 36.89 |
| CrystalBleu | 0.11 |
| Meteor | 0.33 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 0.92 |
| syntax_comparative_accuracy | 0.92 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.74 | 0.86 | 0.90 | 0.70 |
| Sysmon | ATT&CK Tags | 0.83 | 0.90 | 0.93 | 0.30 |
| PWSH | Rule IDs | 0.33 | 0.58 | 0.67 | 2.92 |
| PWSH | ATT&CK Tags | 0.42 | 0.72 | 0.81 | 0.83 |

## Categoria Privilege Escalation

_File sorgente: `report_privilege_escalation.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 32.34 |
| CrystalBleu | 0.07 |
| Meteor | 0.38 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.70 | 0.86 | 0.91 | 0.50 |
| Sysmon | ATT&CK Tags | 0.70 | 0.84 | 0.89 | 0.50 |
| PWSH | Rule IDs | 0.57 | 0.71 | 0.78 | 1.86 |
| PWSH | ATT&CK Tags | 0.57 | 0.79 | 0.85 | 0.57 |

## Categoria Short Code

_File sorgente: `report_short_code.xlsx`_

### Risultati Similarita Semantica

| Metrica | Valore |
| --- | ---: |
| ChrF | 62.26 |
| CrystalBleu | 0.19 |
| Meteor | 0.60 |

### Risultati Analisi Statica

| Metrica | Valore |
| --- | ---: |
| syntax_single_accuracy | 1.00 |
| syntax_comparative_accuracy | 1.00 |

### Risultati Analisi Dinamica

| Contesto | Label Set | Exact Match Ratio | Jaccard Mean Index | Dice Index | Mean Symmetric Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| Sysmon | Rule IDs | 0.79 | 0.87 | 0.91 | 0.38 |
| Sysmon | ATT&CK Tags | 0.79 | 0.88 | 0.92 | 0.29 |
| PWSH | Rule IDs | 0.38 | 0.67 | 0.76 | 1.67 |
| PWSH | ATT&CK Tags | 0.67 | 0.85 | 0.89 | 0.52 |
