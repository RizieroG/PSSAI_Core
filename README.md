# PSSAI Core

Repository di ricerca per la generazione e validazione di script PowerShell con pipeline agentiche basate su CrewAI.

## Table of Contents

- [PSSAI Core](#pssai-core)
  - [Table of Contents](#table-of-contents)
  - [Stato Repository](#stato-repository)
  - [Struttura Repository](#struttura-repository)
  - [Architetture Attive (`archs/`)](#architetture-attive-archs)
  - [Prerequisiti Comuni](#prerequisiti-comuni)
  - [Quick Start](#quick-start)
    - [Esempio pipeline completa](#esempio-pipeline-completa)
    - [Esempio variante senza gate statico](#esempio-variante-senza-gate-statico)
    - [Esempio solo coder](#esempio-solo-coder)
  - [Risultati Sperimentali](#risultati-sperimentali)
  - [Campione Sperimentale](#campione-sperimentale)
  - [Metriche Utilizzate](#metriche-utilizzate)
    - [1) Code Similarity](#1-code-similarity)
    - [2) Analisi statica](#2-analisi-statica)
    - [3) Analisi dinamica](#3-analisi-dinamica)
  - [Componenti Deprecati](#componenti-deprecati)
  - [Tecniche utilizzate](#tecniche-utilizzate)
  - [Licenze](#licenze)
  - [Note](#note)

## Stato Repository

Ultimo aggiornamento:

- Le architetture attive sono organizzate sotto `archs/`.
- Le vecchie pipeline `pssai_full_automation_*` e il toolkit `evaluation_metrics` sono marcati come deprecati e mantenuti solo per storico/riproducibilita.

## Struttura Repository

- `archs/`
  - Contiene le varianti architetturali attive e i rispettivi risultati.
- `img/`
  - Diagrammi architetturali usati nella documentazione.
- `evaluation_metrics/` (deprecato)
  - Toolkit storico di metriche.
- `pssai_full_automation_dynamic_analysis/` (deprecato)
  - Pipeline storica full automation con focus dinamico.
- `pssai_full_automation_static_analysis/` (deprecato)
  - Pipeline storica full automation con focus statico.

## Architetture Attive (`archs/`)

| Architettura | Focus pipeline | Documentazione | Risultati |
| --- | --- | --- | --- |
| `pssai_solo_coder` | Solo Coder, single-pass | [code/README](archs/pssai_solo_coder/code/README.md) | [risultati/README](archs/pssai_solo_coder/risultati/README.md) |
| `pssai_coder_judger` | Coder + Aligner (judger) | [code/README](archs/pssai_coder_judger/code/README.md) | [risultati/README](archs/pssai_coder_judger/risultati/README.md) |
| `pssai_no_dynamic` | Planning + coding + gate statico + alignment | [code/README](archs/pssai_no_dynamic/code/README.md) | [risultati/README](archs/pssai_no_dynamic/risultati/README.md) |
| `pssai_no_static` | Planning + coding + gate dinamico + alignment | [code/README](archs/pssai_no_static/code/README.md) | [risultati/README](archs/pssai_no_static/risultati/README.md) |
| `pssai_no_judger` | Planning + statico + dinamico (senza aligner) | [code/README](archs/pssai_no_judger/code/README.md) | [risultati/README](archs/pssai_no_judger/risultati/README.md) |
| `pssai_complete` | Pipeline completa: statico + dinamico + alignment | [code/README](archs/pssai_complete/code/README.md) | [risultati/README](archs/pssai_complete/risultati/README.md) |
| `pssai_complete_nested` | Completa con restart innestato | [code/README](archs/pssai_complete_nested/code/README.md) | [risultati/README](archs/pssai_complete_nested/risultati/README.md) |
| `pssai_hitl` | Variante Human-in-the-Loop | [code/README](archs/pssai_hitl/code/README.md) | [risultati_statici](archs/pssai_hitl/risultati_statici/) |

## Prerequisiti Comuni

- Python 3.x
- Installazione dipendenze nella cartella `code` dell'architettura scelta: `pip install -r requirements.txt`
- Variabile ambiente `OPENAI_API_KEY` per le varianti OpenAI
- `PSScriptAnalyzer` richiesto dalle varianti con gate statico
- `psandman` richiesto dalle varianti con gate dinamico (`pssai_complete`, `pssai_complete_nested`, `pssai_no_static`, `pssai_no_judger`)

Nota: alcune varianti con analisi dinamica usano percorsi `psandman` hardcoded nei file Python. Verificare le costanti all'inizio dell'entrypoint prima dell'esecuzione.

## Quick Start

### Esempio pipeline completa

```bash
cd archs/pssai_complete/code
pip install -r requirements.txt
python multi_agent_architecture.py "Descrizione dello script da generare"
python multi_agent_architecture.py --ref path\to\reference.ps1 "Descrizione dello script da generare"
```

### Esempio variante senza gate statico

```bash
cd archs/pssai_no_static/code
pip install -r requirements.txt
python multi_agent_architecture_obs.py "Descrizione dello script da generare"
```

### Esempio solo coder

```bash
cd archs/pssai_solo_coder/code
pip install -r requirements.txt
python multi_agent_architecture.py "Descrizione dello script da generare"
```

## Risultati Sperimentali

- Per le varianti in `archs/*/risultati/` sono disponibili file `report_*.xlsx` per categoria e globale.
- Ogni cartella `risultati` include un `README.md` con sintesi metriche.
- Per `pssai_hitl` i risultati statici sono in `archs/pssai_hitl/risultati_statici/`.

## Campione Sperimentale

Il campione usato nell'analisi sperimentale è composto da 50 script PowerShell di riferimento (Ground Truth), distribuiti in 5 categorie malware:

- Backdoor: 10
- Downloader: 10
- Launcher Injection: 10
- Privilege Escalation: 10
- Credential Stealer: 10

Per la lunghezza del codice, il dataset è stato anche segmentato in:

- Script brevi: 28 (meno di 10 righe)
- Script lunghi: 22 (10 righe o piu)

Le analisi sono state condotte sia in forma aggregata (globale) sia disaggregata (per categoria e lunghezza), per evidenziare meglio punti di forza e criticita delle diverse architetture.

## Metriche Utilizzate

Le metriche seguono tre livelli complementari.

### 1) Code Similarity

- `CrystalBLEU`: variante di BLEU per code generation che riduce il peso degli n-grammi banali e valorizza quelli distintivi, migliorando la misura della similarita logico-strutturale.
- `METEOR / METEOR-L`: misura più flessibile del matching esatto; cattura meglio equivalenze funzionali anche con piccole variazioni lessicali o di forma.
- `chrF`: similarità a livello di carattere; utile per codice e naming tecnico, dove minime variazioni sintattiche possono alterare i token ma non sempre la vicinanza morfologica.

### 2) Analisi statica

- `Single Syntax Accuracy`: percentuale di script generati senza errori di parsing.
- `Comparative Syntax Accuracy`: accuratezza sintattica contestualizzata rispetto alla Ground Truth, considerando solo errori nuovi introdotti dal generato.

Queste metriche sono basate su `PSScriptAnalyzer` e si concentrano sui `ParseError`.

### 3) Analisi dinamica

La valutazione runtime confronta il comportamento atteso e osservato (regole Sigma e tag MITRE ATT&CK estratti dai log), con metriche multi-label:

- `Exact Match Ratio (EMR)`: quota di campioni con match perfetto tra set atteso e set osservato.
- `Mean Jaccard Index`: sovrapposizione media tra insiemi attesi e osservati.
- `Sorensen-Dice Coefficient`: similarita insiemistica che premia maggiormente l'intersezione.
- `Mean Symmetric Difference`: numero medio di differenze tra i due insiemi.

## Componenti Deprecati

> [!WARNING]
> I seguenti percorsi sono deprecati dal 22 marzo 2026 e non sono piu mantenuti.
> Usare solo per storico/riproducibilità.

- [evaluation_metrics/README.md](evaluation_metrics/README.md)
- [pssai_full_automation_dynamic_analysis/code/README.md](pssai_full_automation_dynamic_analysis/code/README.md)
- [pssai_full_automation_static_analysis/code/README.md](pssai_full_automation_static_analysis/code/README.md)

## Tecniche utilizzate

- **Multi-Agent** con ruoli distinti (Planner, Coder, Reviewer, Change Planner, Aligner).
- **Chain-of-Thought** per la pianificazione strutturata.
- **Self-Evaluation Loop** con gate di validazione e cicli iterativi di fix.
- **Ablation Study** per misurare il contributo dei singoli moduli (`no_static`, `no_dynamic`, `no_judger`).
- **Validazione comportamentale in sandbox** tramite `psandman` e analisi dei log runtime.
- **Valutazione multi-label** su regole Sigma e tag MITRE ATT&CK estratti dai log.
- **Analisi statica automatica** con `PSScriptAnalyzer` e metriche di correttezza sintattica.
- **Osservabilita del workflow** con tracciamento di transizioni, tempi e output (`observability_*.json`).
- **Human-in-the-Loop** per raffinamento manuale.

## Licenze

- Codice sorgente: [MIT License](LICENSE)

## Note

Progetto sviluppato per attivita di ricerca e sperimentazione accademica.
Non usare per generare o automatizzare codice malevolo.
