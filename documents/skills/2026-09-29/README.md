# 通用高价值 Agent Skills · 2026-09-29

本次按用户选择归档 P01、P02、A01–A08，并补充已安装技能中的通用研究、写作、设计、开发协作与办公能力。共 **24 个技能包：23 个原文快照、1 个通用改写版**。不包含工作专用技能、运行记录、身份/认证配置或本机完整盘点表。

这是可追溯的技能资料档案，不是统一安装包。本次没有改变任何 agent 的安装配置，也没有执行训练、付费 API 或技能效果评测。

## 阅读与使用

- 研究入门：survey → paper-card → synthesis → hypothesis。
- 实验闭环：reproduction-plan / experiment-plan → run-diagnosis → critical-review / numbers-audit → reflection。
- 技能改进：对照阅读 Claude skill-creator 与 P01 通用协议。前者提供脚本实现，后者强调证据、匹配基线与独立测试边界。
- 数据训练：P02 必须放回兼容的 RSIBench-Data 项目环境使用；这里保留入口和必要阅读上下文。

## 技能目录

| 选择 | 技能 | 用途 | 形态 |
|---|---|---|---|
| 补充 | [frontend-design](originals/shared/frontend-design/SKILL.md) | 共享前端设计指导 | 原文快照 |
| 补充 | [skill-creator](originals/codex-system/skill-creator/SKILL.md) | Codex 技能结构、资源组织与校验 | 原文快照 |
| A08 | [archify](originals/codex-user/archify/SKILL.md) | 架构、流程、时序与数据流可视化 | 原文快照 |
| A06 | [research-critical-review](originals/codex-user/research-critical-review/SKILL.md) | 证据驱动的研究审查 | 原文快照 |
| A04 | [research-experiment-plan](originals/codex-user/research-experiment-plan/SKILL.md) | 主张驱动的实验设计 | 原文快照 |
| 补充 | [research-hypothesis](originals/codex-user/research-hypothesis/SKILL.md) | 可证伪研究假设 | 原文快照 |
| A07 | [research-numbers-audit](originals/codex-user/research-numbers-audit/SKILL.md) | 数字与结果来源核验 | 原文快照 |
| A02 | [research-paper-card](originals/codex-user/research-paper-card/SKILL.md) | 论文主张—证据—代码卡片 | 原文快照 |
| 补充 | [research-reflection](originals/codex-user/research-reflection/SKILL.md) | 基于新证据更新研究判断 | 原文快照 |
| 补充 | [research-report-latex](originals/codex-user/research-report-latex/SKILL.md) | 来源台账与 LaTeX 报告 | 原文快照 |
| A03 | [research-reproduction-plan](originals/codex-user/research-reproduction-plan/SKILL.md) | 分阶段复现与验收 | 原文快照 |
| A05 | [research-run-diagnosis](originals/codex-user/research-run-diagnosis/SKILL.md) | 实现、数据、优化、评测与假设排障 | 原文快照 |
| 补充 | [research-survey](originals/codex-user/research-survey/SKILL.md) | 文献检索与方向地图 | 原文快照 |
| 补充 | [research-synthesis](originals/codex-user/research-synthesis/SKILL.md) | 已有论文的机制与证据综合 | 原文快照 |
| 补充 | [resume-experience-refiner](originals/codex-user/resume-experience-refiner/SKILL.md) | 基于事实提炼经历贡献 | 原文快照 |
| 补充 | [documents](originals/openai-runtime/documents/SKILL.md) | Word 文档与渲染检查 | 原文快照 |
| 补充 | [pdf](originals/openai-runtime/pdf/SKILL.md) | PDF 读取、生成与视觉检查 | 原文快照 |
| 补充 | [Presentations](originals/openai-runtime/presentations/SKILL.md) | 演示文稿制作与检查 | 原文快照 |
| 补充 | [Spreadsheets](originals/openai-runtime/spreadsheets/SKILL.md) | 表格、公式与图表 | 原文快照 |
| A01 | [skill-creator](originals/claude-market/skill-creator/SKILL.md) | 技能对照评测、评审与描述优化 | 原文快照 |
| 补充 | [autopilot](originals/cursor-builtin/autopilot/SKILL.md) | PR 评论、冲突和 CI 维护 | 原文快照 |
| 补充 | [split-to-prs](originals/cursor-builtin/split-to-prs/SKILL.md) | 可审查的 PR 拆分 | 原文快照 |
| P02 | [rsibench-data-factory](originals/project/rsibench-data-factory/SKILL.md) | 数据生成、SFT 与独立评测流程 | 原文快照 |
| P01 通用改写 | [skill-evolution-orchestrator](adapted/portable/skill-evolution-orchestrator/SKILL.md) | 有证据约束的技能改进协议 | 通用改写 |

## 来源与改写

`originals/` 保留选定技能文件及必要资源的原始字节，排除了 Python 缓存等运行副产物。来源位置、逐文件 SHA-256、原始哈希、包归属及排除项见 [manifest.json](manifest.json)。同名的 Codex 与 Claude skill-creator 分目录保存，不互相覆盖。

P01 放在 `adapted/portable/skill-evolution-orchestrator/`。原版依赖特定平台控制器、runner、内部目标证明契约和历史运行状态；本版移除这些实现依赖，保留冻结样本、匹配基线、故障归因、盲评、预算、版本选择和晋升记录。还将固定候选数量改为按诊断需要选择，并明确验证集选择与最终测试的区别。它是新整理的方法协议，不声称保留原控制平面的可执行实现或已验证效果。原始四个文件的哈希保留用于追溯，原版平台文件未复制。

P02 原文保持不变。配套阅读材料保存在 [context/rsibench-data-factory](context/rsibench-data-factory/README.md)，包括项目 README、训练评测说明、Tinker cookbook 与沙箱评测说明。源项目为 [evolvent-ai/RSIBench-Data](https://github.com/evolvent-ai/RSIBench-Data)，本次观察到 HEAD 为 `4c807610243e7b481d382c5ed360c71c79a22f61`；文件哈希而非 HEAD 单独决定此次快照内容。完整 backend、runner、数据、模型和外部服务不在本技能档案中。

研究系列保留原文的 Dr. Pie 衍生说明；经历精修保留其设计来源；Archify 保留版本、MIT 许可与第三方声明。其他文件保留本地包自带的许可，不据缺少 LICENSE 推断可自由再分发。此档案不改变任何上游许可。

## 已知使用边界

- Claude skill-creator 是本地市场源码快照，不代表此前已安装。其描述优化脚本按 `test_passed` 选择版本，那个划分实际承担验证集用途；需要新的独立测试集才能报告最终泛化。原文件未修改。
- P01 通用版不提供 runner 程序；必须使用实际可用的执行器，并核验运行和技能加载证据。
- P02 固定 Tinker / Harbor / E2B 链路；保存文档不代表服务连通、凭据可用或模型结果已复现。
- research-numbers-audit 的数值相似匹配只产生人工复核候选，不证明语义来源或实验正确。
- Cursor split-to-prs 的示例 `git stash create` 不保存未跟踪文件；使用时应另行保护这些文件。
- OpenAI 办公包依赖其宿主工具、库及渲染环境；归档了技能支持资源，没有打包宿主运行时。
- research-report-latex 原文包含多文件编译流程；使用时应遵守实际宿主的 LaTeX 工具约束。
- 原文中的安装、发布、消息发送等步骤只是归档内容；实际执行仍由具体任务与授权决定。

## 验证记录

归档完整性及通用版结构检查见 [VALIDATION.md](VALIDATION.md)。逐文件 SHA-256 见 [SHA256SUMS](SHA256SUMS)。本次验证仅覆盖保存的字节、选定文件范围、结构与引用，不是技能质量 benchmark。
