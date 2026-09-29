# LaTeX 编写与 PDF 验收

## 1. 尊重现有工具链

先检查主文件、`\input`/`\include`、图片、`.bib`/`.bbl`、文档类、`.sty`、`.latexmkrc` 和魔术注释。用户模板或出版规范明确指定引擎、参考文献后端和页数时保持不变，不把新报告的默认值强加给旧项目。

新建报告的默认选择：

| 场景 | 引擎 | 说明 |
|---|---|---|
| 新中文或多语言报告 | LuaLaTeX | UTF-8、OpenType，适合作为新文档基线 |
| 现有 `xeCJK`、字体或模板依赖 | XeLaTeX | 兼容优先，完成字体和文本层验证 |
| 明确要求的旧出版模板 | pdfLaTeX | 只在模板要求或兼容性需要时使用 |

模板使用 CTeX 的固定 Fandol fontset，避免按操作系统静默选择不同字体。若用户改用系统字体或项目字体，记录字体名、来源和许可证；跨机器复现时固定字体文件或 TeX 发行版。

## 2. 初始化与正文规则

没有现有模板时用 `scripts/init_report.py`。模板是可删改的起点，不是强制章节清单。

- 保持 UTF-8。
- 标题、作者、日期和 PDF metadata 与正文一致。
- 表格优先 `tabularx`/`longtable`，长 URL 使用 `xurl`；不要靠极小字号掩盖溢出。
- 图片使用相对路径，保留来源和说明；位图分辨率不足时在交付中披露。
- 特殊字符 `% & $ # _ { } ~ ^ \` 在普通文本中正确转义；代码和路径用合适的 verbatim/URL 命令。
- 不把工具 token、占位引用、`TODO`、`[VERIFY]` 或 `\ReportPlaceholder` 留入最终稿。

## 3. 参考文献

新资料库默认使用 `biblatex` + Biber，以支持 UTF-8 和多语言数据。网页资料至少记录作者或机构、标题、日期或版本、URL 和访问日期。

若现有模板使用 BibTeX/natbib 或提供 `.bst`，保持其后端；不要在同一项目中混用两套体系。latexmk 负责依据 `.bcf`、`.aux` 和日志调度 Biber/BibTeX，不要硬编码“固定跑三遍”。

## 4. 编译边界

`compile_report.py` 要求已安装的 latexmk 和目标引擎，不负责安装。工具未进入 `PATH` 时使用：

```bash
export LATEX_BIN_DIR=/absolute/path/to/existing/tex/bin
```

或传 `--tex-bin`。不要把该路径写入 Skill、源码或可共享配置。

默认忽略系统、用户和项目 `.latexmkrc`，减少隐式状态。现有项目明确依赖其 rc 文件时，在审阅文件内容后使用 `--allow-latexmk-rc`，并在构建记录中说明。

编译默认传入 `-no-shell-escape`。只有可信项目确有需要时，才另行设计允许列表；当前脚本不提供自动开启开关。

编译、文本层、字体和渲染 QA 均先在 append-only run 目录中的候选 PDF 上执行。所有 Gate 通过后，脚本才校验候选哈希并原子替换 `--output`；后置 QA 失败时 `published` 必须为 `false`，既有目标文件的哈希必须保持不变。

## 5. 阻断错误与版式警告

严格模式的阻断项：

- latexmk、引擎或 Biber 非零退出；
- PDF 不存在、为空、加密或页数为 0；
- `LaTeX Error`、`Undefined control sequence`、`Emergency stop`；
- 未定义或重复引用/引文、待重跑 Biber/LaTeX；
- `Missing character`、缺失字体或文件；
- 文本层为空或缺少用户指定的哨兵文本；
- 任何字体未嵌入；
- 渲染页数与 PDF 物理页数不同。

`Overfull \hbox` 默认视为需修复；`Underfull` 和包级警告逐条检查，可在确认视觉无缺陷后作为非阻断项披露。不要只依赖退出码或 `latexmk -Werror`。

## 6. 机器与视觉 QA

最终构建至少记录：

- latexmk、引擎、Biber、CTeX/BibLaTeX 的可得版本；
- 主文件、命令、run 目录、退出码和最终日志；
- `pdfinfo` 页数、纸张、加密状态和 metadata；
- `pdffonts` 的嵌入和 Unicode 映射信息；
- `pdftotext -layout` 文本层、预期标题或哨兵文本；
- PDF SHA-256；
- `pdftoppm` 生成的所有页面图。

机器检查后逐页目视。重点检查封面、目录、长表、公式、图片、参考文献和所有机器警告对应页。若封面不编号，分别报告物理页数与显示页码口径。

`uni=no` 不单独判定文本层失败，应与实际 `pdftotext` 结果联合判断。普通报告只承诺“可搜索、字体嵌入、视觉核验”；PDF/A、PDF/UA 或字节级可复现需要独立 profile、兼容性和双构建验证。
