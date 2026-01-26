# Multi-Agent System for PowerShell Code Generation <!-- omit in toc -->

## Table of Contents <!-- omit in toc -->
<!-- TOC -->
- [Overview](#overview)
- [Struttura della repository](#struttura-della-repository)
- [Architetture](#architetture)
  - [Visione generale del sistema (HitL)](#visione-generale-del-sistema-hitl)
  - [Solo analisi statica](#solo-analisi-statica)
  - [Analisi statica + dinamica](#analisi-statica--dinamica)
- [Pipeline e workflow](#pipeline-e-workflow)
  - [Static analysis (full automation)](#static-analysis-full-automation)
  - [Dynamic analysis (full automation)](#dynamic-analysis-full-automation)
  - [Human-in-the-loop](#human-in-the-loop)
- [Risultati e metriche ottenute](#risultati-e-metriche-ottenute)
  - [Report statici (PSScriptAnalyzer)](#report-statici-psscriptanalyzer)
  - [Metriche testuali (ottenute)](#metriche-testuali-ottenute)
  - [Risultati dinamici (psandman)](#risultati-dinamici-psandman)
  - [Esempi di metriche dinamiche](#esempi-di-metriche-dinamiche)
    - [Backdoor - example\_92](#backdoor---example_92)
    - [Privilege Escalation - example\_351](#privilege-escalation---example_351)
- [Tecniche utilizzate](#tecniche-utilizzate)
- [Note](#note)
<!-- /TOC -->

## Overview

Questo repository raccoglie un sistema agentico multi-ruolo basato su CrewAI per generare,
valutare e correggere automaticamente codice PowerShell. Sono presenti tre varianti operative:

- **Full automation con analisi statica** (PSScriptAnalyzer).
- **Full automation con analisi statica + dinamica** (psandman).
- **Human-in-the-Loop** con gate utente per revisioni mirate.

Ogni variante ha una cartella dedicata con codice, README specifici e risultati generati.

## Struttura della repository

- `pssai_full_automation_static_analysis/`
  - `code/`: entrypoint OpenAI/Ollama + README d'uso.
  - `risultati_statici/`: report PSScriptAnalyzer e metriche testuali (CSV/XLSX).
  - `risultati_dinamici/`: log e report di esecuzione (per categoria).
- `pssai_full_automation_dynamic_analysis/`
  - `code/`: entrypoint OpenAI per pipeline dinamica + README d'uso.
  - `risultati_statici/`: report PSScriptAnalyzer + metriche testuali (XLSX).
  - `risultati_dinamici/`: log psandman ed evidenze runtime (XML/EVTX/XLSX).
- `pssai_hitl/`
  - `code/`: variante con interazione utente (HITL) + README d'uso.
  - `risultati_statici/`: report statici e metriche (XLSX).
- `evaluation_metrics/`
  - toolkit per tokenizzazione e calcolo metriche (BLEU/ROUGE/METEOR/EditDistance/chrF) + README.
- `img/`
  - diagrammi architetturali del sistema.
- `README.md`
  - questo documento (panoramica completa della repository).

## Architetture

### Visione generale del sistema (HitL)
![Architettura del sistema](./img/architettura_sistema.png)

### Solo analisi statica
![Architettura del sistema - solo analisi statica](./img/architettura_sistema_solo_analisi_statica.png)

### Analisi statica + dinamica
![Architettura del sistema - analisi statica e dinamica](./img/architettura_sistema_analisi_statica_e_dinamica.png)

## Pipeline e workflow

### Static analysis (full automation)
1. **Planning**: il Planner genera un piano in 6-9 bullet.
2. **Coding**: il Coder produce lo script PowerShell.
3. **Static analysis**: PSScriptAnalyzer valida lo script.
4. **Review + fix loop**: il Reviewer emette fix notes; il Coder rigenera lo script (fino a `max_auto_fix_iters`).
5. **Alignment opzionale**: con `--ref`, l'Aligner propone fix notes per avvicinare lo script al reference.

### Dynamic analysis (full automation)
1. **Planning + Coding**: come nel flusso statico.
2. **Esecuzione sandbox**: psandman esegue lo script in VM e produce XML/EVTX.
3. **Dynamic review**: un reviewer valuta la coerenza tra piano e log runtime.
4. **Fix loop dinamico**: se fallisce, il Change Planner genera fix notes; il Coder rigenera lo script.
5. **Alignment + gate statico**: se usi `--ref`, l'Aligner propone fix notes e si esegue PSScriptAnalyzer post-allineamento.

### Human-in-the-loop
1. **Planning + Coding + Static analysis**: identico alla pipeline statica.
2. **Gate utente**: l'utente puo accettare, visualizzare o richiedere modifiche.
3. **Change Planner**: le richieste umane diventano fix notes per il Coder.
4. **Output finale**: lo script viene salvato dopo approvazione.

## Risultati e metriche ottenute

### Report statici (PSScriptAnalyzer)
I risultati statici sono salvati in CSV/XLSX, ad esempio:
- `pssai_full_automation_static_analysis/risultati_statici/pssa_results.csv`
  - colonne: errori/warning/info per reference e candidato, differenze e regole comuni/uniche.
- `pssai_full_automation_dynamic_analysis/risultati_statici/pssa_results_readble.xlsx`
- `pssai_hitl/risultati_statici/pssa_results_readble.xlsx`

### Metriche testuali (ottenute)
Le metriche di similarita tra script candidato e riferimento sono calcolate con il toolkit
in `evaluation_metrics/` e salvate in:
- `pssai_full_automation_static_analysis/risultati_statici/results_eval_complete_readable.xlsx`
- `pssai_full_automation_dynamic_analysis/risultati_statici/results_eval_complete_percentage.xlsx`
- `pssai_hitl/risultati_statici/results_eval_percentages.xlsx`

Metriche presenti nei report:
- **BLEU-1 / BLEU-2 / BLEU-4**
- **ROUGE-L** (Precision/Recall/F1)
- **METEOR**
- **Edit Distance** (raw/normalized)
- **chrF**

### Risultati dinamici (psandman)
Le evidenze runtime sono organizzate per categoria e codice, ad esempio:
- `pssai_full_automation_dynamic_analysis/risultati_dinamici/<Categoria>/code_*_train/`
- `pssai_full_automation_static_analysis/risultati_dinamici/<Categoria>/code_*/`

Categorie presenti:
- Backdoor
- Credential Stealer
- Downloader
- Launcher Injection
- Privilege Escalation

Tipicamente ogni cartella contiene:
- log XML/EVTX generati da psandman
- `report.xlsx` con sintesi dell'esecuzione
- (quando presente) `evaluation-suite-metriche.txt` con metriche aggregate

### Esempi di metriche dinamiche

Confronto tra:
- **Static**: full automation con sola analisi statica
- **Dynamic**: full automation con analisi statica + dinamica

#### Backdoor - example_92

| Blocco                           | Metrica  | Static | Dynamic |
|----------------------------------|----------|--------|---------|
| Semantic - ATT&CK Tags           | Micro-F1 | 0.91   | 0.88    |
| Semantic - ATT&CK Tags           | Macro-F1 | 0.83   | 0.79    |
| Semantic - ATT&CK Tags           | Jaccard  | 0.83   | 0.79    |
| Semantic - ATT&CK Tags           | Hamming  | 0.17   | 0.21    |
| Semantic - Triggered Rules       | Micro-F1 | 0.75   | 0.33    |
| Semantic - Triggered Rules       | Macro-F1 | 0.60   | 0.20    |
| Semantic - Triggered Rules       | Jaccard  | 0.60   | 0.20    |
| Semantic - Triggered Rules       | Hamming  | 0.40   | 0.80    |
| Dynamic Sysmon - ATT&CK Tags     | Micro-F1 | 1.00   | 1.00    |
| Dynamic Sysmon - ATT&CK Tags     | Macro-F1 | 1.00   | 1.00    |
| Dynamic Sysmon - ATT&CK Tags     | Jaccard  | 1.00   | 1.00    |
| Dynamic Sysmon - ATT&CK Tags     | Hamming  | 0.00   | 0.00    |
| Dynamic Sysmon - Triggered Rules | Micro-F1 | 1.00   | 1.00    |
| Dynamic Sysmon - Triggered Rules | Macro-F1 | 1.00   | 1.00    |
| Dynamic Sysmon - Triggered Rules | Jaccard  | 1.00   | 1.00    |
| Dynamic Sysmon - Triggered Rules | Hamming  | 0.00   | 0.00    |
| Dynamic PWSH - ATT&CK Tags       | Micro-F1 | 1.00   | 0.27    |
| Dynamic PWSH - ATT&CK Tags       | Macro-F1 | 1.00   | 0.15    |
| Dynamic PWSH - ATT&CK Tags       | Jaccard  | 1.00   | 0.15    |
| Dynamic PWSH - ATT&CK Tags       | Hamming  | 0.00   | 0.85    |
| Dynamic PWSH - Triggered Rules   | Micro-F1 | 1.00   | 0.50    |
| Dynamic PWSH - Triggered Rules   | Macro-F1 | 1.00   | 0.50    |
| Dynamic PWSH - Triggered Rules   | Jaccard  | 1.00   | 0.33    |
| Dynamic PWSH - Triggered Rules   | Hamming  | 0.00   | 0.67    |

#### Privilege Escalation - example_351

| Blocco                           | Metrica  | Static | Dynamic |
|----------------------------------|----------|--------|---------|
| Semantic - ATT&CK Tags           | Micro-F1 | 0.00   | 0.92    |
| Semantic - ATT&CK Tags           | Macro-F1 | 0.00   | 0.86    |
| Semantic - ATT&CK Tags           | Jaccard  | 0.00   | 0.86    |
| Semantic - ATT&CK Tags           | Hamming  | 1.00   | 0.14    |
| Semantic - Triggered Rules       | Micro-F1 | 0.00   | 0.67    |
| Semantic - Triggered Rules       | Macro-F1 | 0.00   | 0.50    |
| Semantic - Triggered Rules       | Jaccard  | 0.00   | 0.50    |
| Semantic - Triggered Rules       | Hamming  | 1.00   | 0.50    |
| Dynamic Sysmon - ATT&CK Tags     | Micro-F1 | 0.50   | 1.00    |
| Dynamic Sysmon - ATT&CK Tags     | Macro-F1 | 0.33   | 1.00    |
| Dynamic Sysmon - ATT&CK Tags     | Jaccard  | 0.33   | 1.00    |
| Dynamic Sysmon - ATT&CK Tags     | Hamming  | 0.67   | 0.00    |
| Dynamic Sysmon - Triggered Rules | Micro-F1 | 0.40   | 1.00    |
| Dynamic Sysmon - Triggered Rules | Macro-F1 | 0.25   | 1.00    |
| Dynamic Sysmon - Triggered Rules | Jaccard  | 0.25   | 1.00    |
| Dynamic Sysmon - Triggered Rules | Hamming  | 0.75   | 0.00    |
| Dynamic PWSH - ATT&CK Tags       | Micro-F1 | 0.33   | 0.92    |
| Dynamic PWSH - ATT&CK Tags       | Macro-F1 | 0.20   | 0.86    |
| Dynamic PWSH - ATT&CK Tags       | Jaccard  | 0.20   | 0.86    |
| Dynamic PWSH - ATT&CK Tags       | Hamming  | 0.80   | 0.14    |
| Dynamic PWSH - Triggered Rules   | Micro-F1 | 0.40   | 0.60    |
| Dynamic PWSH - Triggered Rules   | Macro-F1 | 0.25   | 0.43    |
| Dynamic PWSH - Triggered Rules   | Jaccard  | 0.25   | 0.43    |
| Dynamic PWSH - Triggered Rules   | Hamming  | 0.75   | 0.57    |

## Tecniche utilizzate

- **Multi-Agent** con ruoli distinti (Planner, Coder, Reviewer, Change Planner, Aligner).
- **Chain-of-Thought** per la pianificazione strutturata.
- **Self-Evaluation Loop** con PSScriptAnalyzer e PSandman (Dynamic Analysis)
- **Human-in-the-Loop** per raffinamento manuale.
- **Metriche di qualita** per confronto quantitativo tra codice reale e generato.

## Note

Questo progetto e rilasciato per scopi di ricerca e sperimentazione accademica.
Non utilizzare per la generazione automatica di codice malevolo o potenzialmente pericoloso.
