# reconcile_traits ![Python application](https://github.com/rafelafrance/reconcile_traits/workflows/CI/badge.svg)

Reconcile traits from different sources: Traiter (LabelTraiter, etc.) and ChatGPT4.

_All happy families are alike; each unhappy family is unhappy in its own way._ - Tolstoy

Both the rule-base parsers in LabelTraiter and ChatGPT4 have issues, but each in their own way. The rule-based parsers excel at parsing short phrases with a defined vocabulary (like: colors, etc.) or fields with a known format (latitude, longitude, dates, etc.). What rule-based parsers are not good at, is more freeform text like localities, habitats, or names. Note that some fields use a jargon like dates written with a roman numeral for the month "1-IV-72" for "April 1, 1972". You can easily program that into the rules.

Conversely, ChatGPT4 does a better job at those longer wishy-washy fields, and, surprisingly to me, not very well at things like dates or colors. It proved hopeless at linking traits to plants or their parts. For example, it would struggle with linking "4-7 ft." back to the plant itself. Fortunately, this kind of linkage is needed more common in plant treatments than in herbarium sheet labels. ChatGPT4 also has a tendency to "hallucinate/confabulate" field labels (Darwin Core terms); less so with the text itself.

The idea of this repository is to see if we can reduce the overall errors by combining the output from both types of models, relying on each when it is strongest. What this entailed was comparing the output from both models and writing a bespoke reconciler for each field. Sometimes the rules are quite simple lke for "dwc:habitat" where we always use the ChatGPT4 output, or for "dwc:stateProvince" where we always use LabelTraiter's output.

Other times the reconciliation uses more rules to get the "best" output. See "dwc:recordNumber":
1. If the rule-based parser found a record number with a label like `No. 1234-56`, return that.
2. If the rule-based parser's record number value matches ChatGPT4's catalog number, then use that.
3. Else return whatever ChatGPT4 returned.

As you can see, each Darwin Core term requires its own ad hoc reconciler. Labor-intensive.

I have provided `example_data` in a directory. The zip file contains:
- Input: `dl_random_2023-09-14_typewritten_gpt4_clean` directory. It has JSON output files, one per label, that were data manually cleaned from ChatGPT4. The code for running this is in [traiter_llm](https://github.com/rafelafrance/traiter_llm) repository.
- Input: `dl_random_2023-09-14_typewritten_traiter` directory. It contains JSON output files from the [TraiterLabel](https://github.com/rafelafrance/LabelTraiter) `parse-labels` script. One per label.
- Input: `dl_random_2023-09-14_typewritten_ocr` directory with the OCRed text files (one file per label). It used scripts from the [ocr_ensemble](https://github.com/rafelafrance/ocr_ensemble) repository.
- Output: `dl_random_2023-09-14_typewritten_reconciled` directory. It contains the reconciled JSON output.

I also included the following data for reference. They are not needed to reconcile labels.
- Reference: `dl_random_2023-09-14_typewritten_gpt4` directory. Contains the uncleaned output from the ChatGPT4. It often had problems properly formatting JSON.
- Reference: `dl_random_2023-09-14_typewritten_sample_11.csv` and `dl_random_2023-09-14_typewritten_sample_11.ods` which were used to score the reconcilers. One row per label.

## Install

You will need to have Python3.11+ installed, as well as pip, a package manager for Python.
If you have `make` you can install the requirements into your python environment like so:

```bash
git clone https://github.com/rafelafrance/reconcile_traits.git
cd reconcile_traits
make install
```

## Running

On the off chance you want to try to run this yourself:

First unzip the file in the `sample_data` directory.

```bash
cd /to/reconcile_traits
source .venv/bin/activate
reconcile-traits @args/reconcile_example_data.args
```

It runs in seconds.
