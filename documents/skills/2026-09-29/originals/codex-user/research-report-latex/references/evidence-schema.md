# Evidence JSONL schema

`init_report.py` 创建 `evidence/sources.jsonl` 和 `evidence/claims.jsonl`。每个非空行必须是一个完整 JSON 对象；不要添加 Markdown 围栏或注释。

## sources.jsonl

必需字段：

- `source_id`: 唯一 ID，格式 `S001`。
- `title`: 来源标题。
- `locator`: URL、本地路径或稳定内容 ID。
- `source_type`: 例如 `official_doc`、`source_code`、`paper`、`internal_doc`、`dataset`、`experiment_log`。
- `publisher_or_author`: 作者、机构或发布方；未知时写 `unknown`。
- `published_or_version`: 日期、版本或提交；未知时写 `unknown`。
- `accessed_at`: `YYYY-MM-DD`。
- `read_depth`: `full`、`partial`、`metadata_only` 或 `unreadable`。
- `evidence_scope`: 本次实际读取范围和可支持的判断。
- `limitations`: 版本、权限、截断、动态内容或其他限制；没有则为空字符串。

示例：

```json
{"source_id":"S001","title":"LaTeXmk manual","locator":"https://tug.ctan.org/support/latexmk/latexmk.pdf","source_type":"official_doc","publisher_or_author":"John Collins","published_or_version":"4.88","accessed_at":"2026-08-30","read_depth":"partial","evidence_scope":"自动多遍编译与命令行选项","limitations":"未审阅持续预览章节"}
```

## claims.jsonl

通用必需字段：

- `claim_id`: 唯一 ID，格式 `C001`。
- `claim`: 一条可判断真假的完整陈述。
- `kind`: `source_statement`、`experiment_observation`、`inference`、`hypothesis` 或 `insufficient_evidence`。
- `source_ids`: 支撑来源 ID 数组；无来源时使用空数组。
- `locators`: 与证据对应的页码、章节、行号或锚点数组。
- `confidence`: `high`、`medium`、`low` 或 `unknown`。
- `limitations`: 适用范围和缺口；没有则为空字符串。

条件字段：

- `experiment_observation` 需要 `observation_artifact`，指向日志、截图、代码或数据。
- `inference` 至少需要一个 `source_id` 或 `observation_artifact`。
- `hypothesis` 需要 `validation`，描述可证伪检查和成功/停止条件。
- `insufficient_evidence` 的 `limitations` 不能为空。

示例：

```json
{"claim_id":"C001","claim":"latexmk 会依据依赖变化调度生成 PDF 所需的多次命令。","kind":"source_statement","source_ids":["S001"],"locators":["CTAN package description; manual sections 2 and 5"],"confidence":"high","limitations":"不覆盖未知的自定义代码生成器"}
```

## 与 LaTeX 的连接

正文关键判断后使用 `\claimref{C001}`。`validate_evidence.py --require-claim-refs` 会检查：

- 引用的 Claim 是否存在；
- 每个 Claim 是否至少在主稿或 `\input` 文件中出现一次；
- Claim 是否引用存在且具有足够读取深度的来源；
- 未被任何 Claim 使用的来源会被列为警告，便于删除无关资料或补写用途。

结构校验不检查链接真实性、引用位置是否精确、Claim 是否忠实于原文。这三项必须由内容审查完成。

