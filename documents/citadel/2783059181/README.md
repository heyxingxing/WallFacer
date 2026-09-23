# 上下文工程(Context Engineering)调研

> 来源：[学城原文](https://km.sankuai.com/collabpage/2783059181) · 归档日期：2026-09-23 · 原文版本：`stepVersion=4`
>
> 本文为原文归档，未独立核实其中的技术判断与数据。内嵌 HTML 已保留原文件并提供图片预览；交互内容可下载 HTML 后打开，部分交互状态另附静态预览。
>
> [原始 Markdown 导出](source.md) · [原始 CitadelXML](source.xml) · [归档元信息](metadata.json) · [文档目录](../../README.md)

### 1. 概念定义与演进

#### 1.1 定义与起源

**上下文工程(Context Engineering)** 是一门构建动态系统的工程学科，其核心目标是：**为 LLM 的每次推理调用，提供正确的信息和工具，以正确的格式和优先级注入上下文窗口，使模型有可能完成任务** [论文5]。简而言之，上下文工程不是写一段好的提示词，而是构建一个能动态组装最优信息的系统。

> "Context Engineering is the art and science of building dynamic systems that provide the right information and tools, in the right format, so the LLM can plausibly accomplish the task." ， Harrison Chase (LangChain)
> "It is the delicate art and science of filling the context window with just the right information - task descriptions, few-shot examples, RAG, tools, state, and history - all compressed and composed in the right way." ， Andrej Karpathy

**概念演进时间线**：2025.6 Shopify CEO Tobi Lutke 公开表示 "I prefer Context Engineering over Prompt Engineering"，Karpathy 同期转发支持 → 2025.9 Anthropic 工程博客发布系统性阐述 → 2025.11 上海交大发表《Context Engineering 2.0》论文，提出 1.0→4.0 学术演进框架 → 2026.5 CMU 等发表 Agent Harness Engineering Survey → 2026.6 Loop Engineering 概念兴起（OpenClaw/Claude Code/Google Chrome 团队同周独立提出），标志着概念演进进入新阶段：**Prompt Engineering ⊂ Context Engineering ⊂ Harness Engineering ⊂ Loop Engineering**

#### 1.2 与 Prompt Engineering 的关系

上下文工程并非对提示词工程的简单替代，而是更高维度的范式升级：

| 维度 | Prompt Engineering | Context Engineering |
| --- | --- | --- |
| **信息来源** | 主要来自用户输入 | 绝大部分来自机器(工具)的输出 |
| **动态性** | 静态、一次性 | 高度动态，随 Agent 运行周期不断累积变化 |
| **范式** | "写一段好文字" | "构建一个组装信息的系统" |
| **关注点** | 措辞、格式、技巧 | 信息选择、结构设计、系统架构 |
| **核心挑战** | 如何表达清楚 | 如何在有限窗口内最大化信息密度 |

#### 1.3 为什么现在重要

三个关键驱动力使上下文工程成为 Agent 建设的核心课题：

1. **Agent 时代的到来**：从简单 ChatBot 到复杂多步骤 Agent，上下文不再是一段固定文本，而是一个持续膨胀、需要精心管理的动态信息流。
2. **上下文衰减的现实约束**：研究发现，上下文超过 32,000 个 token 后，模型正确性显著下降 [论文3]，远早于官方宣称的百万级 token 限制。"塞更多信息"不是解决方案，"选对信息"才是。
3. **生产级复杂度**：业务系统 Agent 需要对接大量工具、处理复杂状态、跨多轮对话工作，这些都需要系统性的上下文管理，而非手工编写 prompt 能解决。

### 2. 上下文的组成要素

一个 Agent 的上下文窗口由以下七大要素组成，每个要素都需要独立的管理策略：

<!-- HTML 内容 -->
![上下文工程策略图](../../../assets/citadel/2783059181/diagram-01.png)

[原始 HTML（下载后可交互）](../../../assets/citadel/2783059181/diagram-01.html)


| **要素** | **定义** | **关键考量** | **典型占比** |
| --- | --- | --- | --- |
| **系统提示词** (System Prompt) | Agent 的"基本人格"和行为规范，定义了 Agent 是谁、做什么、怎么做 | 生产级系统由十几层逻辑模块动态组装，而非一段静态文字；用 XML/Markdown 结构化组织 | 5-15% |
| **工具定义** (Tools) | Agent 可调用的工具集合及参数说明，定义了 Agent 与操作空间的契约 | 每个工具的 schema 都会占据 token（全量可达 77K+）；避免一次性加载全部工具，按需加载 | 10-20% |
| **外部数据** (RAG/MCP) | 通过检索增强生成(RAG)或模型上下文协议(MCP)从外部数据源获取的信息 | 检索质量直接决定上下文质量；需要权衡召回率与精确率；检索结果需适当截断和格式化 | 10-20% |
| **消息历史** (Message History) | 用户与 Agent 之间的对话历史，包括用户输入和 Agent 响应 | 随对话轮次增加持续消耗 token；第 15 轮开始忘记输出格式，第 20 轮开始用错工具，这是上下文架构问题 | 30-40% |
| **记忆系统** (Memory) | 跨会话持久化的信息存储，包括用户偏好、历史决策、学到的知识等 | 短期记忆(当前会话) vs 长期记忆(跨会话)；LightMem [论文19]：三阶段记忆架构，Token 降低 38x | 5-10% |
| **示例** (Few-shot) | 向模型展示期望的输入-输出格式和行为模式的参考样例 | 对 LLM 来说，示例是"一图胜千言"，比纯文字描述更有效；需权衡数量与 token 消耗 | 5-10% |
| **任务状态** (State) | Agent 当前任务的执行状态，包括进度、中间结果、待处理项 | 状态信息随任务推进不断变化；需要决定哪些状态值得保留在上下文中 | 5-10% |

> 📌 **预留空间**：以上各要素合计应控制在总窗口的 70-80%，至少预留 20-30% 给模型生成。超过预算时按优先级触发裁剪。

### 3. 核心策略框架

LangChain 创始人 Harrison Chase 提出四大操作策略（Write / Select / Compress / Isolate），构成上下文工程的完整方法论。四大策略协同配合，不是互斥的。

| **策略** | **核心思想** | **典型应用** | **2026 前沿进展** |
| --- | --- | --- | --- |
| **Write 写入** | 将信息持久化到窗口之外的存储，需要时再读取 | 关键决策写入笔记；用户偏好写入长期记忆；推理结果固化为工作流蓝图 [论文14]（token 成本降低 99%+） | MCP Workflow Engine：Agent 推理产出声明式 JSON 蓝图，后续执行只消耗一次 token |
| **Select 选择** | 从海量信息中选取最相关的部分注入上下文 | RAG 语义检索；Tool Search 按需加载工具；条件加载上下文模块 | Stable-RAG [论文16]：消除排列偏差幻觉；Predictive Prefetching [论文17]：预测性预取降低延迟 |
| **Compress 压缩** | 对已有上下文进行压缩，保留关键信息的同时减少 token 消耗 | 对话摘要；工具输出截断；冗余清除；渐进式摘要 | ContextCurator [论文13]：RL 训练轻量策略模型主动修剪噪声，WebArena 成功率 41.2%，token 减少 8.8% |
| **Isolate 隔离** | 将不同任务的上下文隔离到不同 Agent/窗口，避免上下文污染 | 子 Agent 架构（干净窗口）；多窗口管理；任务隔离（子 Agent 仅返回浓缩摘要） | Agent-Radar [论文20]：时空衰减注意力引导，无需训练即可让每个 Agent 聚焦相关上下文 |

**策略 × 要素交叉矩阵**（快速定位最佳实践）：

| 要素 ╲ 策略 | Write | Select | Compress | Isolate |
| --- | --- | --- | --- | --- |
| **系统提示词** | 动态组装模块化指令 | 按任务阶段条件加载 | 精简措辞，避免冗余规则 | 子 Agent 各自独立 System Prompt |
| **工具定义** | 推理结果固化为工作流蓝图 | Tool Search 按需加载 | 精简 schema 描述 | 不同子 Agent 加载不同工具集 |
| **消息历史** | 关键决策写入笔记持久化 | 滑动窗口保留近 N 轮 | 渐进式摘要 + 工具调用清除 | 子任务对话不回流主 Agent |
| **记忆系统** | 三阶段记忆架构(LightMem) | 语义检索相关记忆条目 | 离线整合，在线推理分离 | 用户/会话/Agent 三级隔离 |

当你面对某个具体的上下文要素（比如工具定义太大、消息历史太长），可以快速查表找到对应的操作手段。例如："工具定义"占 token 太多 → 查表发现可以用 **Select**（按需加载）+ **Compress**（精简 schema）+ **Isolate**（不同子 Agent 各自加载自己的工具集）

### 4. 关键技术实践

#### 4.1 即时上下文(JIT Context) vs 预加载

两种加载模式各有取舍，最佳实践是**混合策略**：

| **维度** | **预加载 (Eager Loading)** | **即时上下文 (JIT / Lazy Loading)** |
| --- | --- | --- |
| **机制** | Agent 启动时一次性将所有可能需要的信息加载到上下文 | 维护轻量标识符（文件路径、ID），运行时通过工具按需获取完整内容 |
| **优点** | 实现简单，信息随时可用，无额外延迟 | 节省 token，信息时效性高，上下文信噪比高 |
| **适用场景** | 少量核心信息（Agent 身份定义、基础规则） | 大规模知识库、工具集、文档库 |

**生产实践参考**：

- Claude Code 预加载 `CLAUDE.md`（~2k tokens），文件树索引作为 Layer 1，具体文件内容通过 `Read` 工具按需加载；
- Skill 架构以 `SKILL.md` 作为路由层预加载，`references/` 目录下的详细文档按需 `read_file` 加载。

#### 4.2 渐进式披露

**核心思想**：不一次性暴露所有信息，而是根据任务进展逐步披露，逐步缩小 LLM 每次决策时需要"看到"的上下文范围。

**实现方式**：① 分层信息架构，将信息分为"概览层"和"详情层"，先给概览，需要时再加载详情；② 条件触发，根据用户意图或任务阶段，决定披露哪些信息模块；③ 工具分页，对大型工具返回值实施分页，先返回摘要，Agent 可请求更多详情。

**生产实践参考**：

- Claude Code 预加载文件目录结构（`tree` 输出），具体文件内容通过 `Read` 工具按需加载；
- OpenClaw Skill 系统采用"名称+描述"预加载 → 匹配后读取完整 `SKILL.md` → 按需加载 `references/` 子文档的三级渐进披露。

#### 4.3 结构化笔记与持久化记忆

**核心思想**：Agent 定期将关键信息写入上下文窗口之外的持久化存储，稍后重新读取。关键在于"结构化"，不是随意记录，而是有组织、可检索、可更新的信息管理。

**实现模式**：① 待办事项列表，Agent 维护任务清单，完成一项划掉一项；② 战略笔记，记录高层架构决策、设计原则；③ 错误日志，记录已尝试但失败的方案，避免重复犯错；④ 会话摘要，每次会话结束时生成摘要，下次会话启动时加载。

**生产实践参考**：

- Claude Code 以 `CLAUDE.md` 作为长期记忆文件，每次会话启动时预加载；
- OpenClaw 采用"记忆即文件"设计，三级存储架构：`memory/YYYY-MM-DD.md`（每日记忆）+ `MEMORY.md`（长期记忆）+ 向量库（语义检索）；
- 飞象 Dumbo，CatCalw 等 以 `IDENTITY.md` / `SOUL.md` / `USER.md` 分别存储 Agent 身份、行为契约、用户偏好，`memory_write` / `memory_search` 工具支持短期和长期记忆的写入与检索。

#### 4.4 上下文隔离（子 Agent 架构）

**核心思想**：使用专门的子 Agent 处理特定任务，每个子 Agent 拥有干净的上下文窗口，互不干扰。

**关键设计原则**：① 主 Agent 负责高层协调（理解意图、分解任务、整合结果）；② 子 Agent 拥有独立上下文，不受主 Agent 历史对话的污染；③ 子 Agent 返回浓缩摘要，不将全部工作过程注入主 Agent 的上下文；④ 子 Agent 的失败不会污染主 Agent 的上下文。

**生产实践参考**：

- Claude Code Sub-agent 机制为每个子任务启动独立 ReAct 循环，支持独立无继承模式和 Fork 复制模式，搭配 `--worktree` 隔离可并行修改代码；
- 供商助手 MainAgent + 多 SubAgent 按业务域隔离（酒店、平台方向、定时任务各有独立 SubAgent），Skill 和 Context 相互隔离，各方向可独立迭代。

#### 4.5 对话历史管理

对话历史是上下文膨胀的主要来源之一。三种策略按轻量→重量排列，生产中通常组合使用：

| **策略** | **机制** | **优点** | **缺点** |
| --- | --- | --- | --- |
| **工具调用清除** | 清除已完成的工具调用 request+response，仅保留结论性一句话 | 最轻量，零额外推理成本 | 仅适用于工具密集型对话 |
| **滑动窗口** | 只保留最近 N 轮对话，被滑出的部分可生成摘要保留 | 实现简单，token 消耗可控 | 可能丢失早期关键信息 |
| **对话摘要** | 将历史对话压缩为结构化摘要（保留：决策、未解决问题、偏好） | 压缩比高（约 5:1），保留关键语义 | 摘要本身消耗推理预算 |

**生产实践参考**：

- Claude Code 五层压缩引擎（MicroCompact→Collapse→Session Memory→AutoCompact→Context Reset），在 95% 窗口时自动触发；
- 供商助手 Context Pruning + Compaction 分级降级，Compaction 触发从 ~30 轮推迟到 ~55 轮（+83%），群聊启动固定注入从 ~20,500 tokens 降至 ~9,400 tokens（-54%）。

#### 4.6 工具返回值优化

工具返回值是 Agent 系统中最容易被忽视但影响巨大的上下文消耗源。优化策略：

| **优化策略** | **具体做法** | **生产实践** |
| --- | --- | --- |
| Schema 瘦身 | 工具 description 控制在 50 词以内；用 enum 替代自由文本 | 供商助手 watson-cli 118 命令 AI Ready 改造：bizCode 免查、CLI help 丰富化，消除 LLM 幻觉推断参数问题 |
| 分级返回 | 工具支持 detail_level=summary\|full，默认返回摘要 | Dumbo 学城文档工具返回超长文档时自动输出简化版 Markdown 而非完整 XML |
| 流式分页 | 列表类工具默认返回有限条数 + has_more + cursor | Claude Code grep/glob 工具通过 limit 参数控制单次返回条数 |
| 结构化截断 | 保留前 N 行 + 末尾 M 行 + 中间省略标记 | OpenClaw Context Pruning 对旧工具输出做临时裁剪，每次会话节省 10k~30k tokens |

---

### 5. 实践落地：供商 AI 运维助手的上下文工程

以供商 AI 运维助手（华生 Watson）为案例，展示上下文工程如何在真实业务系统中落地。该助手基于 CatClaw 群助理形态，覆盖值班问题排查、每日巡检、告警分析、WBR 周报等场景。

#### 5.1 业务背景与挑战

| 挑战维度 | 具体问题 | 对上下文工程的要求 |
| --- | --- | --- |
| 场景分散 | TT 值班、巡检（20+ 服务）、告警（日均 100+）、WBR 周报 | 需要精准的 Skill 路由，避免上下文中塞入无关场景的规则 |
| 工具链庞大 | 118 个 CLI 命令、50+ 代码仓库、多个知识库 | 工具描述不能全量注入，需要分层选择（Select） |
| 排查链路长 | 单个 TT 需串联 Raptor → 日志 → traceId → 代码定位 | 需要工具返回值裁剪（Compress）和上下文生命周期管理 |
| 多方向并行 | 酒店 B 端、C 端、平台方向各有独立 Skill 和知识库 | 需要子 Agent 隔离（Isolate），各方向 Context 互不干扰 |

#### 5.2 上下文工程技术拆解

| 关键技术（第 4 章） | 在平台方向的落地方式 | 效果/收益（来源） |
| --- | --- | --- |
| **渐进式披露** | **4 层 Skill 智能路由演进**：V1 全量注入→V2 Skill Map 结构化索引→V3 SubAgent 分层隔离→V4 语义召回（BM25+Embedding，138 Skill/1,026 功能点） | 主 Agent Skill 路由准确率 42%→92%；子 Agent pass⁵ 33%→87% |
| **持久化记忆** | **知识冷启动三步法**：① 存量蒸馏，将已有排查经验批量转化为结构化知识；② 增量采集，AI 无法解决的问题，人给 AI 输入解决思路后沉淀为 Skill/知识库；③ 教学投喂，管理员主动写入规则与 SOP | "越用越聪明"正循环：新问题解决后知识库自动扩充 |
| **子 Agent 隔离** | MainAgent + 多 SubAgent 分层：酒店、平台方向、定时任务各有独立 SubAgent，Skill 和 Context 相互隔离 | 解决"子 Agent 专用 Skill 挂在主 Agent 上导致路由干扰"问题 |
| **对话历史管理** | **Context Pruning + Compaction 分级降级**：① Pruning 临时裁剪过期工具输出；② Compaction 永久压缩为摘要；③ Bootstrap 文件结构重排，高优先级规则前置；④ 内容瘦身，目录型内容迁移到独立文件 | Compaction 触发从 ~30 轮推迟到 ~55 轮（+83%）；固定注入 20,500→9,400 tokens（-54%）；关键规则覆盖率 100% |
| **工具返回值优化** | **watson-cli 118 命令 AI Ready 改造**：bizCode 免查优化、CLI help 丰富化、返回值结构化精简 | 消除 LLM 幻觉推断参数值问题；工具调用复杂度大幅降低 |

#### 5.3 量化效果

| 度量维度 | 优化前 | 优化后 | 对应技术 |
| --- | --- | --- | --- |
| Skill 路由准确率 | 42%（107+ Skill desc 被截断） | 92%（SubAgent 分层后+智能路由） | 渐进式披露 + 子 Agent 隔离 |
| pass⁵ 通过率 | 33% | 87% | 综合优化 |
| 上下文压缩触发 | ~30 轮后 | ~55 轮后（+83%） | Context Pruning + 对话历史管理 |
| 群聊启动固定注入 | ~20,500 tokens | ~9,400 tokens（-54%） | Bootstrap 结构重排 + 内容瘦身 |
| 平台 TT 完全解决率 | — | 27%（25/91） | 全链路综合效果 |
| 平台 TT AI 参与解决率 | — | 70.3%（64/91） | 全链路综合效果 |

#### 5.4 关键经验

- **上下文工程是 Agent 从"能用"到"好用"的分水岭**：同样的模型和工具集，仅通过上下文工程优化（分层隔离、Pruning、结构重排），路由准确率提升明显。
- **渐进式披露是解决 Skill 膨胀的核心策略**：4 层路由演进的本质是逐步缩小 LLM 的决策范围，从全量注入到结构化索引再到分层隔离，每一步都在减少无关信息。
- **Token 节省直接转化为能力提升**：固定注入减少 54% 意味着更多 token 预算留给实际排查，Agent 能完成更长链路推理而不触发压缩。
- **持续运营机制是上下文质量的保障**：通过"问题上报→打标→TODO→验收"闭环，持续发现 AI 能力缺口并补充对应 Skill/知识，驱动上下文质量螺旋上升。
- **不是所有技术都需要强行落地**：选择适合自身场景的技术组合比追求全覆盖更重要。

---

### 6. 总结与展望

#### 6.1 核心结论

| **核心结论** | **要点** | **支撑依据** |
| --- | --- | --- |
| 上下文工程是 Agent 成败的关键 | Gartner 预测 40%+ Agentic AI 项目将失败，根因之一是缺乏系统性上下文管理 | [报告11] Gartner 2025；[报告12] MIT NANDA |
| 更长窗口不能替代更好的工程 | 超过 32K token 后正确性显著下降；位置效应导致中间信息被忽略。精选和编排才是关键 | [论文3] Context Rot；[论文21] Lost in the Middle |
| 四大策略构成完整方法论 | Write/Select/Compress/Isolate 的组合可覆盖所有上下文管理问题 | [报告10] LangChain；[报告9] Anthropic |
| 概念层次仍在快速演进 | PE → CE → Harness Engineering → Loop Engineering，每层解决更大时间尺度的问题 | [论文15] Harness Engineering Survey |
| 可观测性是持续优化的前提 | 89% 的组织已实现某种可观测性，但只有 52% 在做离线评估。上下文组装延迟、token 利用率、缓存命中率是三个核心指标 | LangChain 2026 State of AI Agents |

#### 6.2 未来方向

- **自适应上下文系统**：Agent 自主学习何时压缩、何时检索、何时遗忘，从"人工编排"走向"自动编排"
- **缓存感知的上下文管理**：TokenPilot [论文22] 开创了将 KV Cache 命中率纳入上下文决策的范式
- **多 Agent 协作中的上下文共享**：上下文的隔离与共享边界如何设计是开放问题
- **上下文安全与对抗鲁棒性**：Agent 从更多外部源拉取上下文，上下文注入攻击的防御将成为必修课
- **端到端评估体系**：从"评估模型输出"到"评估上下文质量"，需要建立独立评估标准

### 附录：参考文献

#### A.1 学术论文

**[论文1]** [Context Engineering 2.0: The Context of Context Engineering](http://arxiv.org/abs/2510.26493) — 上海交大 (2025.11)，首次系统化定义上下文工程的学术演进框架(1.0→4.0)

**[论文2]** [Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models](http://arxiv.org/abs/2510.04618) — Stanford/MIT (2025)，提出 ACE 框架，将上下文视为可演化的"作战手册"

**[论文3]** Context Rot: How Adding Input Tokens Degrades LLM Performance — 证明上下文超过 32K token 后模型正确性显著下降

**[论文5]** Context Engineering: A Survey for Systematic Optimization of Information Load in LLMs — 综述论文，系统分析 1400+ 篇论文，将上下文工程形式化为数学优化问题

**[论文6]** [Memory in the Age of AI Agents: A Survey](http://arxiv.org/abs/2512.13564) — NUS/人大/复旦/北大联合 (2025)，提出 Forms-Functions-Dynamics 三维统一分析框架

**[论文13]** [Escaping the Context Bottleneck: Active Context Curation for LLM Agents via RL](http://arxiv.org/abs/2604.11462) — (2026.4)，ContextCurator + TaskExecutor 共生框架，WebArena 成功率 41.2%，token 减少 8.8%

**[论文14]** [Separating Intelligence from Execution: A Workflow Engine for the Model Context Protocol](http://arxiv.org/abs/2605.00827) — (2026.3)，推理与执行解耦，单次执行 token 成本降低 99%+

**[论文15]** [Agent Harness for Large Language Model Agents: A Survey](http://openreview.net/pdf?id=eONq7FdiHa) — CMU/Yale/JHU/Amazon (2026.4)，提出 ETCLOVG 七层 Harness 架构，仅调整 Harness 即可获 10× 性能差异

**[论文16]** [Stable-RAG: Mitigating Retrieval-Permutation-Induced Hallucinations in RAG](http://arxiv.org/abs/2601.02993) — ACL 2026，发现 RAG 检索结果排列顺序显著影响生成准确性

**[论文17]** [Predictive Prefetching for Retrieval-Augmented Generation](http://arxiv.org/abs/2605.17989) — ICML 2026，预测性预取机制大幅降低端到端延迟

**[论文19]** [LightMem: Lightweight and Efficient Memory-Augmented Generation](http://arxiv.org/abs/2510.18866) — 浙江大学，ICLR 2026，三阶段记忆架构，Token 降低 38x，QA 准确率提升 29.3%

**[论文20]** [Agent-Radar: Enhancing Multi-Agent Communication through Attention Steering](http://arxiv.org/abs/2605.30136) — (2026.05)，时空衰减注意力引导，5 个 benchmark SOTA

**[论文21]** [Lost in the Middle: How Language Models Use Long Contexts](http://arxiv.org/abs/2307.03172) — TACL 2024，验证 LLM 位置偏差"U 形"注意力分布

**[论文22]** [TokenPilot: Cache-Efficient Context Management for LLM Agents](http://arxiv.org/abs/2606.17016) — (2026.06)，缓存友好的 Agent 上下文管理框架，60%+ 成本降低

#### A.2 行业报告与文章

**[报告9]** [Anthropic: Effective Context Engineering for AI Agents](http://anthropic.com/engineering/effective-context-engineering-for-ai-agents) — (2025.9)，系统性实践指南

**[报告10]** [LangChain: Context Engineering for Agents](http://blog.langchain.com/context-engineering-for-agents) — Harrison Chase 提出 Write/Select/Compress/Isolate 四大策略框架

**[报告11]** [Gartner 预测报告](http://gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-more-than-40-percent-of-agentic-ai-projects-will-be-cancelled-by-end-of-2027) — (2025.6)，超过 40% 的 Agentic AI 项目将在 2027 年前被取消

**[报告12]** MIT 2025 年商业 AI 现状报告 (Project NANDA) — 95% 的 AI 试点未能产生可衡量的 P&L 影响

---

**注释：**

- 4 层 Skill 智能路由演进：[https://km.sankuai.com/collabpage/2773773240](https://km.sankuai.com/collabpage/2773773240)
- "越用越聪明"正循环：新问题解决后知识库自动扩充：[https://km.sankuai.com/collabpage/2774647408](https://km.sankuai.com/collabpage/2774647408)
- Compaction 触发从 ~30 轮推迟到 ~55 轮（+83%）；固定注入 20,500→9,400 tokens（-54%）；关键规则覆盖率 100%：[https://km.sankuai.com/collabpage/2769420283](https://km.sankuai.com/collabpage/2769420283)
