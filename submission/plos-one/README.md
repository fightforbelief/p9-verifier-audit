# PLOS ONE 初投稿件

稿件类型为 **Research Article**。以下四份文件对应初投系统的四个上传项。两位作者须先完成[作者确认清单](AUTHOR_CONFIRMATIONS.md)，再由通讯作者定稿。

| 系统上传项 | 文件 | 内容 |
| --- | --- | --- |
| Manuscript | [正文 PDF](Manuscript.pdf) | 15 页，含题名页、摘要、连续行号、4 张表、Fig 1 图注、15 条参考文献和 S1 说明。 |
| Cover Letter | [投稿信 PDF](CoverLetter.pdf) | 1 页，写明文章类型、最近工作、研究增量、负面结果及建议编辑。确认既往 PLOS 联系和回避情况后定稿。 |
| Figure | [Fig1.tif](Fig1.tif) | 独立 RGB TIFF，2040 × 1035 像素、300 dpi、LZW 压缩。图注位于正文首次引用之后。 |
| Supporting Information | [S1_file.zip](S1_file.zip) | 解包后从 README.txt 开始。含固定版本的分析代码及测试、协议、全部派生数值报告、逐题数据、绘图脚本和 Fig 1 的源数据。 |

两份可编辑源文件为 [Manuscript.tex](Manuscript.tex) 和 [CoverLetter.tex](CoverLetter.tex)。正文使用 PLOS LaTeX 模板 v3.8，所有表格、公式及参考文献均内置在单个源文件中。编辑后可在本目录分别运行 `tectonic Manuscript.tex` 和 `tectonic CoverLetter.tex`。分析数据冻结在 [1845d77](https://github.com/fightforbelief/p9-verifier-audit/tree/1845d771360fb34dfee2537d614103ea3d598bb3)。独立补充包由 `python3 support/pack.py` 从该版生成。

## 投稿系统字段

**Full title**

Certifying best-of-N verifier comparisons with fallible answer judgments

**Short title**

Auditing mathematical verifier comparisons

**Authors, in order**

Yunjie Guo; Hanqing Yang. Both authors are affiliated with Independent Researcher, Suzhou, China. Corresponding author: Hanqing Yang (hanqing.yang189@gmail.com).

**Abstract**

A comparison between two mathematical verifiers can depend on a small number of uncertain answer grades. On a fixed generation pool, each answer contributes its grade times the difference in its probabilities of selection. We use this established linear comparison to ask how to spend a budget when preliminary judgments can be wrong. Given an upper bound on their error count, we derive the smallest attainable worst-case interval width both before provisional grades arrive and after they are available for selective adjudication. We replay 1,390,800 eligible responses from two public archives. On AceMath MATH-500 at eight draws, 437 reliable answer checks establish a 1.21 percentage-point lead, but 13 adverse grade changes can erase it. In the Lightman full-pool comparison, assuming at most five errors in either of two automatic grading rules gives intervals that exclude the archived 5.8-point gap. After calibrating the error bound by probability sampling, all six primary intervals contain zero. At the same adjudication budget, directly sampling signed grading errors gives narrower median intervals in all six settings. The minimax design is useful when an error ceiling can be defended and a guarantee across all compatible grades is required. Estimating a ceiling can be costly when the aim is a statistical comparison.

**Data Availability Statement**

The complete derived numerical results, study protocol, analysis scripts, tests, and instructions for reproducing the comparisons are provided in S1 File. The original scored samples are publicly available from OpenAI and NVIDIA. The OpenAI file is scored-test-samples.jsonl. For NVIDIA AceMath-RewardBench we used revision 4dcc58ef82ddc5915be91f9b4f2c18c8b503a0e4. The supporting file specifies all input paths and checksums. [OpenAI data and evaluator](https://github.com/openai/prm800k) · [NVIDIA dataset revision](https://huggingface.co/datasets/nvidia/AceMath-RewardBench/tree/4dcc58ef82ddc5915be91f9b4f2c18c8b503a0e4)

**Funding**

The authors received no specific funding for this work.

**Competing interests**

The authors have declared that no competing interests exist.

**Study design**

Secondary computational analysis of publicly released mathematical problems, model scores, and archived final-answer grades. The study recruited no participants and collected no new human judgments.

**Supporting information caption**

S1 File. Analysis code, protocol and numerical results. The ZIP archive includes the analysis scripts and tests, per-question results, tie and review-unit sensitivity analyses, provisional-grader replay, all 32 sampling repetitions, and a guide to the files and units.

**Academic Editor suggestion**

Issa Ali Atoum. PLOS identifies his interests as machine learning evaluation and reproducible research artifacts. See the author checklist for the conflict check. [PLOS editor profile](https://everyone.plos.org/2026/01/19/editorial-spotlight-issa-ali-atoum/)

核对投稿说明使用了 PLOS 的[作者指南](https://journals.plos.org/plosone/s/submission-guidelines)、[LaTeX 指南](https://journals.plos.org/plosone/s/latex)、[图件要求](https://journals.plos.org/plosone/s/figures)、[补充材料说明](https://journals.plos.org/plosone/s/supporting-information)和 [AI 披露政策](https://journals.plos.org/plosone/s/ethical-publishing-practice)。
