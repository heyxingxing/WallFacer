> ⚠️ **注意（仅供阅读）**：此内容为简化版 Markdown，仅供阅读和总结，
> **不可直接用于 createDocument --content 或 updateDocumentByXml**。
> 如需编辑文档，请使用 `getDocumentXml` 获取完整格式后再通过 `updateDocumentByXml` 回传。
> 直接用此内容编辑会丢失样式宏、合并表格、NodeID 等关键信息，导致文档数据损坏。

---

# knowledge-flow —— Agent知识管理方案与实践

> **ℹ️ 信息：引言**
>
> 本文面向希望在自己的 AI 工作流中引入知识管理能力的同学 —— 无论是个人使用 AI 助手时希望给它注入持续积累的领域知识，还是团队在构建 Agent 工作流时需要一个可维护的知识层，或者是 AI 产品开发者希望在产品中嵌入知识管理能力。通过本文可以了解：knowledge-flow 的**整体设计理念**、**知识全生命周期各个环节的功能设计**以及几类典型**落地场景的具体实践。**SKILL 已发布至 Friday SKILL 广场 [🔗 链接卡片](https://friday.sankuai.com/skills/skill-detail?activeTab=overview&from=/skills-market?deepseek=false%26keyword=bml-knowledge-retriever%26mainView=skill%26orderByDownloadCount=all%26orderByTotalCallCount=all%26orderByTotalCallerCount=all%26page=1%26pageSize=30%26securityScanStatus=all%26spaceKeyword=%26spaceSortOrder=default%26spaceTypeFilter=org,project%26spaceVerifiedFilter=all%26tag=%26verifiedType=all%26viewMode=card%26visibility=all&id=17472)使用手册 [https://km.sankuai.com/collabpage/2767367827](https://km.sankuai.com/collabpage/2767367827)

> 应用实践
> 9.1.1 工程 Agent 全托管需求迭代 @孙润来
> 9.1.2 算法 Agent 需求托管开发 @常远
> 9.2 SKILL 闭环迭代 @曹先帅
> 9.3 群答疑助手 @张亮
> 9.4 CASE自主排查 @纪邵华

> 📑 **文档目录**

### 1. knowledge-flow 定位

knowledge-flow 是一套**以 Skill 为载体的全生命周期知识管理插件**，**既可以面向个人也可以面向团队，**涵盖知识的入库、结构化存储、检索与运营管理，为 AI Agent 提供完整的知识运维能力。其核心架构采用文件系统目录索引设计，以分级目录树的形式对知识进行结构化组织，Agent 可按需逐层检索，实现精准召回。该插件可以灵活嵌入 CatPaw、CatDesk、CatClaw（个人虾 & 群虾）、Claude Code 等 AI 产品。

> **💡 提示：**
>
> **尤其适用于：**知识体量适中（独立文档数量 < 500 篇）、领域边界清晰、需要知识的高质量检索、期望隐性知识和经验不断沉淀、且有知识库长期运营和维护需求的场景。

### 2. 功能板块详览

图中五个板块对应后续各章节的展开顺序（点击切换板块）。

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>knowledge-flow 功能板块详览</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: #ffffff;
    color: #1a1a2e;
    margin: 0; padding: 0;
  }
  .page {
    width: 858px;
    padding: 18px 22px 22px;
    display: flex;
    flex-direction: column;
    gap: 9px;
  }
  .page-header {
    text-align: center;
    padding: 9px 0 4px;
  }
  .page-header h1 {
    font-size: 16.5px;
    font-weight: 700;
    color: #1a1a2e;
    letter-spacing: 0.5px;
  }
  .page-header p {
    font-size: 12px;
    color: #64748b;
    margin-top: 3px;
  }
  .page-hint {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 5px;
  }

  /* 统计条 */
  .stats-bar {
    display: flex;
    gap: 0;
    background: #f8fafc;
    border-radius: 8px;
    border: 1.5px solid #e2e8f0;
    overflow: hidden;
  }
  .stat-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 10px 8px;
    gap: 3px;
    border-right: 1px solid #e2e8f0;
  }
  .stat-item:last-child { border-right: none; }
  .stat-num {
    font-size: 24px;
    font-weight: 800;
    line-height: 1;
  }
  .stat-label {
    font-size: 11px;
    color: #64748b;
    text-align: center;
    line-height: 1.4;
  }

  /* Tab 颜色主题（每个 tab 一套主色） */
  :root {
    --c0: #2563eb; --c0-bg: #eff6ff; --c0-light: #dbeafe;
    --c1: #7c3aed; --c1-bg: #f5f3ff; --c1-light: #ede9fe;
    --c2: #0891b2; --c2-bg: #ecfeff; --c2-light: #cffafe;
    --c3: #059669; --c3-bg: #ecfdf5; --c3-light: #d1fae5;
    --c4: #d97706; --c4-bg: #fffbeb; --c4-light: #fde68a;
  }

  /* Tab 导航 */
  .tab-nav {
    display: flex;
    gap: 6px;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0;
    align-items: flex-end;
  }
  .tab-nav-hint {
    margin-left: auto;
    font-size: 11px;
    color: #94a3b8;
    padding-bottom: 8px;
    white-space: nowrap;
  }
  .tab-btn {
    padding: 8px 18px;
    font-size: 14px;
    font-weight: 600;
    border: none;
    background: none;
    cursor: pointer;
    color: #64748b;
    border-bottom: 2.5px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s;
    border-radius: 4px 4px 0 0;
  }
  .tab-btn:hover { color: #334155; background: #f1f5f9; }

  .tab-btn[data-tab="0"].active { color: var(--c0); border-bottom-color: var(--c0); background: var(--c0-bg); }
  .tab-btn[data-tab="1"].active { color: var(--c1); border-bottom-color: var(--c1); background: var(--c1-bg); }
  .tab-btn[data-tab="2"].active { color: var(--c2); border-bottom-color: var(--c2); background: var(--c2-bg); }
  .tab-btn[data-tab="3"].active { color: var(--c3); border-bottom-color: var(--c3); background: var(--c3-bg); }
  .tab-btn[data-tab="4"].active { color: var(--c4); border-bottom-color: var(--c4); background: var(--c4-bg); }

  /* Tab 内容区 */
  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* 能力卡片网格 */
  .cap-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 9px;
    padding: 9px 0;
  }

  /* 分组标题行 */
  .group-header {
    grid-column: 1 / -1;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 2px 2px;
    margin-top: 4px;
  }
  .group-header:first-child { margin-top: 0; }
  .group-title {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }
  .group-line { flex: 1; height: 1px; background: #e2e8f0; }

  /* 能力卡片 */
  .cap-card {
    background: #f8fafc;
    border-radius: 8px;
    padding: 11px 13px;
    border: 1.5px solid #e2e8f0;
    transition: box-shadow 0.2s, transform 0.2s, border-color 0.2s;
    cursor: default;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .cap-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    transform: translateY(-2px);
  }

  /* 卡片左侧色条 */
  .cap-card { border-left-width: 3px; }

  .tab-content[data-tab="0"] .cap-card { border-left-color: var(--c0); }
  .tab-content[data-tab="0"] .cap-card:hover { border-color: var(--c0); border-left-width: 3px; background: var(--c0-bg); }
  .tab-content[data-tab="1"] .cap-card { border-left-color: var(--c1); }
  .tab-content[data-tab="1"] .cap-card:hover { border-color: var(--c1); border-left-width: 3px; background: var(--c1-bg); }
  .tab-content[data-tab="2"] .cap-card { border-left-color: var(--c2); }
  .tab-content[data-tab="2"] .cap-card:hover { border-color: var(--c2); border-left-width: 3px; background: var(--c2-bg); }
  .tab-content[data-tab="3"] .cap-card { border-left-color: var(--c3); }
  .tab-content[data-tab="3"] .cap-card:hover { border-color: var(--c3); border-left-width: 3px; background: var(--c3-bg); }
  .tab-content[data-tab="4"] .cap-card { border-left-color: var(--c4); }
  .tab-content[data-tab="4"] .cap-card:hover { border-color: var(--c4); border-left-width: 3px; background: var(--c4-bg); }

  .cap-name {
    font-size: 14px;
    font-weight: 700;
    color: #1e293b;
  }
  .cap-desc {
    font-size: 12px;
    color: #64748b;
    line-height: 1.55;
    flex: 1;
  }
  .cap-tag {
    display: inline-block;
    font-size: 11px;
    color: #94a3b8;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 1px 5px;
    align-self: flex-start;
  }
</style>
</head>
<body>
<div class="page">
  <div class="page-header">
    <h1>knowledge-flow 功能板块详览</h1>
    <p>覆盖知识抽取 · 入库 · 检索 · 管理全生命周期</p>
  </div>

  <!-- 统计条 -->
  <div class="stats-bar" id="stats-bar"></div>

  <!-- Tab 导航 -->
  <div class="tab-nav" id="tab-nav"></div>

  <!-- Tab 内容占位，由 JS 动态生成 -->
  <div id="tab-container"></div>
</div>

<script>
(function() {
  var TABS = [
    { icon: '🔍', label: '知识检索' },
    { icon: '🧩', label: '知识抽取' },
    { icon: '📥', label: '知识入库' },
    { icon: '⚙️', label: '知识管理' },
    { icon: '🛠', label: '其他' }
  ];

  var DATA = [
    // ── 知识抽取（tab 0）──
    {
      tab: 1,
      name: '代码库知识提取',
      desc: '扫描服务代码，自动识别系统架构、核心业务流程、配置依赖关系，将隐藏在代码里的知识变成可检索的文档。',
      tag: '代码 → 知识'
    },
    {
      tab: 1,
      name: 'XT ETL 任务提取',
      desc: '从数据平台的 ETL 任务中读取业务含义、数据血缘和调度规则，让"数据从哪来、往哪去"变得一目了然。',
      tag: 'ETL → 知识'
    },
    {
      tab: 1,
      name: 'TT 工单知识提取',
      desc: '从历史工单中识别高频问题类型、排查路径和解决方案，将散落在工单系统里的经验聚合成可复用的知识条目。',
      tag: '工单 → 知识'
    },
    {
      tab: 1,
      name: 'Agent 自主知识沉淀',
      desc: 'AI 助手在日常工作中，主动识别哪些经验值得留存（成功排查的案例、反复用到的规律），无需人工触发即自动入库。',
      tag: '会话 → 知识'
    },
    // ── 知识入库（tab 1）──
    {
      tab: 2,
      name: '学城链接入库',
      desc: '提供一个或几个学城文档链接，AI 自动读取内容、生成摘要和关键词，完成入库。适合零散文档的快速收录。',
      tag: '单文档 / 少量'
    },
    {
      tab: 2,
      name: '父目录批量入库',
      desc: '提供一个学城目录，AI 自动扫描其下所有文档，逐一评估质量和时效性，按推荐结果完成批量入库，支持百篇以上规模。',
      tag: '批量 100+'
    },
    {
      tab: 2,
      name: '代码知识入库',
      desc: '将代码库知识提取的产出物批量写入知识库，支持断点续传，适合大型服务代码库的一次性知识建档。',
      tag: '代码知识 · 本地文件'
    },
    {
      tab: 2,
      name: 'XT 任务入库',
      desc: '将 ETL 任务的业务语义和血缘信息写入知识库，让数据链路的来龙去脉在检索时随时可查。',
      tag: 'ETL 任务'
    },
    {
      tab: 2,
      name: '会话日志入库',
      desc: '对当前对话或历史日志文件中的知识进行提炼和整理，写入知识库指定目录，沉淀每次解决问题的经验。',
      tag: '会话沉淀'
    },
    {
      tab: 2,
      name: '批量工单入库',
      desc: '将经过分类整理的工单语料批量转化为学城文档并收录入库，适合一次性导入大量历史工单经验的场景。',
      tag: '批量工单'
    },
    {
      tab: 2,
      name: '知识库冷启入库',
      desc: '扫描大型父目录、生成目录模板、逐文档质量精判，帮助新领域知识库从零快速建档。',
      tag: '冷启动'
    },
    // ── 知识检索（tab 2）──
    {
      tab: 0,
      name: '核心检索',
      desc: 'Agent 像翻目录一样逐层浏览知识库的分类结构，找到最相关的那篇文档后完整读取。精准可溯源，是整个检索体系的主力。',
      tag: '三层检索 · 第一层'
    },
    {
      tab: 0,
      name: '辅助检索',
      desc: '维护一份关键词到目录的快速索引，让 Agent 不用从根目录一层层翻，直接跳到候选分类，大幅缩短检索路径。',
      tag: '三层检索 · 第二层'
    },
    {
      tab: 0,
      name: '兜底检索',
      desc: '当本地知识库找不到答案时，自动扩展到学城全站搜索，确保不因知识库覆盖不足而漏掉有用信息。',
      tag: '三层检索 · 第三层'
    },
    {
      tab: 0,
      name: '检索日志 & 质量追踪',
      desc: '记录每次检索走过的路径、命中了哪些节点、最终是否找到答案，为后续分析哪些知识缺口最频繁提供数据依据。',
      tag: '可观测性'
    },
    // ── 知识管理 · 结构治理（tab 3）──
    {
      tab: 3,
      group: { label: '结构治理', isFirst: true },
      name: '目录结构优化',
      desc: '随着入库文档增多，AI 自动分析哪些目录需要拆分、合并或重命名，通过交互确认后执行，保持知识库结构合理。',
      tag: '目录骨架'
    },
    {
      tab: 3,
      group: null,
      name: '容器节点优化',
      desc: '检测知识库中间目录的描述是否缺失、过短或使用了模板占位文字，由 AI 基于子目录内容重写，提升检索导航准确性。',
      tag: '描述质量'
    },
    // ── 知识管理 · 知识质量（tab 3）──
    {
      tab: 3,
      group: { label: '知识质量', isFirst: false },
      name: '知识更新',
      desc: '当源文档发生变化时，主动识别知识库里已过期的内容并完成替换，修复动作轻量、即时生效；同时定期扫描重复、混乱、失准等内部失修，让知识库长期保持健康。',
      tag: '更新替换'
    },
    {
      tab: 3,
      group: null,
      name: '矛盾检测',
      desc: '扫描知识库中的重复条目和互相矛盾的说法，由 Agent 进行语义判断，帮助发现并消除知识库里的”自相矛盾”。',
      tag: '质量门控'
    },
    {
      tab: 3,
      group: null,
      name: '评测集构建',
      desc: '扫描知识库中的文档，自动生成标准问答测试用例（cases.jsonl），覆盖各目录的典型检索意图，为后续持续评测奠定数据基础。',
      tag: '质量度量'
    },
    {
      tab: 3,
      group: null,
      name: '知识库评测',
      desc: '基于评测集对知识库检索质量进行系统性测量，生成准确率报告，定位哪些目录或问题类型命中率偏低，驱动知识库针对性改进。',
      tag: '质量度量'
    },
    // ── 知识管理 · 运营洞察（tab 3）──
    {
      tab: 3,
      group: { label: '运营洞察', isFirst: false },
      name: '知识库可视化',
      desc: '生成一张可交互的知识库全景图，直观展示目录树、各领域的文档数量和覆盖深度，让使用者清楚"我的知识库里有什么、哪里还是空白"。',
      tag: '全景感知'
    },
    {
      tab: 3,
      group: null,
      name: '版本管理 & 团队共享',
      desc: '将知识库托管在 Git 仓库，支持多人协同维护、版本回溯和冲突合并，让团队知识库像代码一样可管理。',
      tag: '团队协作'
    },
    // ── 其他（tab 4）──
    {
      tab: 4,
      name: '一键初始化配置',
      desc: '新用户只需运行一个命令，即可完成所有必要配置（权限、路径、依赖工具），几分钟内开箱即用。',
      tag: '初次使用'
    },
    {
      tab: 4,
      name: '能力速查手册',
      desc: '通过自然语言提问（如"你能做什么"）或帮助命令，随时查看当前具备哪些能力及对应的使用方式。',
      tag: '使用引导'
    },
    {
      tab: 4,
      name: '多知识库管理 & 切换',
      desc: '维护一个知识库注册表，支持注册多个知识库（各有独立路径和 Git 远端），一键切换当前激活项，自动同步所有相关配置字段，无需手动修改配置文件。',
      tag: '多库场景'
    },
    {
      tab: 4,
      name: '知识库目录模板（冷启）',
      desc: '在新领域或新团队刚开始建设知识库时，提供一套预设的目录骨架，避免从零设计结构，降低冷启动门槛。',
      tag: '冷启动'
    }
  ];

  // 按 tab 分组统计
  var tabCounts = TABS.map(function() { return 0; });
  DATA.forEach(function(d) { tabCounts[d.tab]++; });
  var total = DATA.length;

  // 渲染统计条
  var statsBar = document.getElementById('stats-bar');
  var statDefs = [
    { num: total, label: '能力项总计', color: '#1e293b' },
    { num: tabCounts[0], label: '知识检索', color: 'var(--c0)' },
    { num: tabCounts[1], label: '知识抽取', color: 'var(--c1)' },
    { num: tabCounts[2], label: '知识入库', color: 'var(--c2)' },
    { num: tabCounts[3], label: '知识管理', color: 'var(--c3)' },
    { num: tabCounts[4], label: '其他', color: 'var(--c4)' }
  ];
  statDefs.forEach(function(s) {
    var item = document.createElement('div');
    item.className = 'stat-item';
    item.innerHTML =
      '<span class="stat-num" style="color:' + s.color + '">' + s.num + '</span>' +
      '<span class="stat-label">' + s.label.replace('\n', '<br>') + '</span>';
    statsBar.appendChild(item);
  });

  // 渲染 Tab 导航
  var tabNav = document.getElementById('tab-nav');
  var tabContainer = document.getElementById('tab-container');

  TABS.forEach(function(t, i) {
    var btn = document.createElement('button');
    btn.className = 'tab-btn' + (i === 0 ? ' active' : '');
    btn.dataset.tab = i;
    btn.textContent = t.icon + ' ' + t.label;
    tabNav.appendChild(btn);
    if (i === TABS.length - 1) {
      var hint = document.createElement('span');
      hint.className = 'tab-nav-hint';
      hint.textContent = '← 点击切换板块';
      tabNav.appendChild(hint);
    }

    var content = document.createElement('div');
    content.className = 'tab-content' + (i === 0 ? ' active' : '');
    content.id = 'tab-' + i;
    content.dataset.tab = i;
    var grid = document.createElement('div');
    grid.className = 'cap-grid';
    grid.id = 'grid-' + i;
    content.appendChild(grid);
    tabContainer.appendChild(content);
  });

  // 渲染卡片
  DATA.forEach(function(d) {
    var grid = document.getElementById('grid-' + d.tab);
    if (!grid) return;

    if (d.group && d.group.label) {
      var tabColor = ['var(--c0)','var(--c1)','var(--c2)','var(--c3)','var(--c4)'][d.tab];
      var gh = document.createElement('div');
      gh.className = 'group-header';
      gh.innerHTML =
        '<span class="group-title" style="color:' + tabColor + '">' + d.group.label + '</span>' +
        '<div class="group-line"></div>';
      grid.appendChild(gh);
    }

    var card = document.createElement('div');
    card.className = 'cap-card';
    card.innerHTML =
      '<div class="cap-name">' + d.name + '</div>' +
      '<div class="cap-desc">' + d.desc + '</div>' +
      '<span class="cap-tag">' + d.tag + '</span>';
    grid.appendChild(card);
  });

  // Tab 切换
  var tabBtns = document.querySelectorAll('.tab-btn');
  var tabContents = document.querySelectorAll('.tab-content');
  tabBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
      tabBtns.forEach(function(b) { b.classList.remove('active'); });
      tabContents.forEach(function(c) { c.classList.remove('active'); });
      btn.classList.add('active');
      document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    });
  });
})();
</script>
</body>
</html>


### 3. 知识库的组织形式

整个知识库是一棵目录树。每个目录下都有一个 `data_structure.md` 文件，但它在不同位置扮演的角色不同：

- **中间层目录（容器节点）**的 `data_structure``.md` 是一份“导览牌”，每个子目录对应一段描述，告诉 Agent 这个方向收录的是什么类型的内容。Agent 读到这里，只需判断“我的问题是不是这个方向的”，然后决定是否继续深入。这一层不存放任何文档链接，职责只有一个 —— 帮 Agent 做路由。

- **最底层目录（叶子节点）**的 `data_structure.md`才是真正的文档索引。每篇收录的文档对应一个条目，包含标题、简介、内容纲要、关键词和原始链接。Agent 走到这一层，说明已经确认这里有相关内容，接下来会读取具体文档做深度理解。

根目录下还有一份 `keyword_index.json`。它**由脚本扫描整颗目录树的关键词字段自动生成**（无需消耗Token），作用是在 Agent 开始逐层导航之前，先给出一个“候选入口目录”的提示，省去从根目录一层层遍历的时间。索引只负责加速，不能替代导航——命中索引后，Agent 仍然会走完完整的导航流程再读取文档，确保内容是经过验证的，而不只是关键词匹配。

（点击知识库文件结构查看详情）

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>knowledge-flow · 知识库组织形式</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b; font-size: 13px;
}
.page { width: 858px; padding: 18px 20px 24px; }

.page-header { text-align: center; margin-bottom: 12px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }

/* ── 主体双栏 ── */
.explorer {
  display: flex; gap: 0;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  overflow: hidden; height: 420px;
  box-shadow: 0 2px 12px rgba(0,0,0,.06);
}

/* ── 左侧文件树 ── */
.tree-panel {
  width: 252px; flex-shrink: 0;
  background: #f8fafc; border-right: 1.5px solid #e2e8f0;
  display: flex; flex-direction: column; overflow: hidden;
}
.tree-title {
  padding: 9px 12px 8px; font-size: 10px; font-weight: 700;
  letter-spacing: 1px; text-transform: uppercase; color: #94a3b8;
  border-bottom: 1px solid #e2e8f0; flex-shrink: 0;
}
.tree-scroll { flex: 1; overflow-y: auto; padding: 6px 0; }

.tree-item {
  display: flex; align-items: center; gap: 5px;
  padding: 4px 10px; cursor: pointer; user-select: none;
  border-radius: 0; transition: background .12s;
  white-space: nowrap; overflow: hidden;
}
.tree-item:hover { background: #e2e8f0; }
.tree-item.selected { background: #dbeafe; }
.tree-item.selected .item-name { color: #1d4ed8; font-weight: 600; }

.toggle { width: 14px; height: 14px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 9px; color: #94a3b8; transition: transform .15s; }
.toggle.open { transform: rotate(90deg); }
.toggle.empty { visibility: hidden; }

.item-icon { flex-shrink: 0; font-size: 13px; }
.item-name { font-size: 12px; color: #334155; overflow: hidden; text-overflow: ellipsis; }
.item-name.dir { color: #1e293b; font-weight: 500; }

.tree-children { overflow: hidden; transition: height .15s; }

/* ── 右侧内容面板 ── */
.content-panel {
  flex: 1; display: flex; flex-direction: column; min-width: 0; background: #fff;
}
.content-header {
  padding: 8px 14px; border-bottom: 1.5px solid #e2e8f0;
  display: flex; align-items: center; gap: 8px; flex-shrink: 0;
}
.breadcrumb { font-size: 11px; color: #94a3b8; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.breadcrumb span { color: #64748b; }
.breadcrumb .last { color: #334155; font-weight: 600; }
.node-badge {
  flex-shrink: 0; font-size: 9.5px; font-weight: 700; padding: 2px 7px;
  border-radius: 10px; letter-spacing: .3px;
}
.badge-container { background: #ede9fe; color: #6d28d9; }
.badge-leaf      { background: #d1fae5; color: #065f46; }
.badge-index     { background: #fef3c7; color: #92400e; }
.badge-root      { background: #e0f2fe; color: #0369a1; }

.content-body {
  flex: 1; overflow-y: auto; padding: 14px 16px;
  font-size: 12px; line-height: 1.8;
}

/* 内容渲染：标题、字段、分割线 */
.c-h2    { font-size: 13.5px; font-weight: 700; color: #0f172a; margin: 12px 0 6px; padding-bottom: 4px; border-bottom: 1px solid #e2e8f0; }
.c-h2:first-child { margin-top: 0; }
.c-h3    { font-size: 12.5px; font-weight: 700; color: #1e40af; margin: 10px 0 4px; }
.c-field { margin: 3px 0; }
.c-key   { font-weight: 700; color: #475569; }
.c-val   { color: #334155; }
.c-val a { color: #2563eb; text-decoration: none; }
.c-val a:hover { text-decoration: underline; }
.c-outline li { margin-left: 18px; color: #64748b; font-size: 11.5px; }
.c-kw    { display: inline-block; background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 4px; padding: 0 5px; font-size: 10.5px; color: #475569; margin: 1px 3px 1px 0; }
.c-hr    { border: none; border-top: 1.5px dashed #e2e8f0; margin: 10px 0; }
.c-desc  { color: #64748b; margin: 4px 0 8px; font-size: 12px; }
.c-pre   { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 12px; font-family: 'SF Mono','Fira Code',monospace; font-size: 11px; color: #334155; overflow-x: auto; white-space: pre; }

/* 空状态 */
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #94a3b8; gap: 8px; }
.empty-state .icon { font-size: 32px; }
.empty-state p { font-size: 12px; }

/* ── 说明文字 ── */
.notes { margin-top: 12px; display: flex; flex-direction: column; gap: 7px; }
.note-item {
  display: flex; gap: 10px; align-items: flex-start;
  background: #f8fafc; border-radius: 8px; border: 1.5px solid #e2e8f0;
  padding: 9px 12px;
}
.note-badge {
  flex-shrink: 0; font-size: 9.5px; font-weight: 700; padding: 2px 8px;
  border-radius: 10px; margin-top: 1px;
}
.nb-purple { background: #ede9fe; color: #6d28d9; }
.nb-green  { background: #d1fae5; color: #065f46; }
.nb-amber  { background: #fef3c7; color: #92400e; }
.note-text { font-size: 12px; color: #475569; line-height: 1.7; }
.note-text strong { color: #1e293b; }
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>knowledge-flow · 知识库组织形式</h1>
    <p>点击左侧目录或文件，查看各节点的内容结构</p>
  </div>

  <div class="explorer">
    <div class="tree-panel">
      <div class="tree-title">知识库文件结构</div>
      <div class="tree-scroll" id="tree-root"></div>
    </div>
    <div class="content-panel">
      <div class="content-header" id="content-header" style="display:none">
        <div class="breadcrumb" id="breadcrumb"></div>
        <span class="node-badge" id="node-badge"></span>
      </div>
      <div class="content-body" id="content-body">
        <div class="empty-state">
          <span class="icon">📂</span>
          <p>点击左侧文件查看内容</p>
        </div>
      </div>
    </div>
  </div>

  <div class="notes">
    <div class="note-item">
      <span class="note-badge nb-purple">容器节点</span>
      <div class="note-text">目录下还有子目录时，<code style="background:#e2e8f0;padding:1px 4px;border-radius:3px;font-size:10.5px">data_structure.md</code> 扮演"导览牌"角色——每个子目录对应一个 <code style="background:#e2e8f0;padding:1px 4px;border-radius:3px;font-size:10.5px">### 子目录名/</code> 小节，附带 100-300 字的范围描述。Agent 在树状导航时读取这份描述，判断问题应该往哪个方向深入。</div>
    </div>
    <div class="note-item">
      <span class="note-badge nb-green">叶子节点</span>
      <div class="note-text">最底层目录的 <code style="background:#e2e8f0;padding:1px 4px;border-radius:3px;font-size:10.5px">data_structure.md</code> 才是真正的<strong>文档索引</strong>——每篇文档对应一个 <code style="background:#e2e8f0;padding:1px 4px;border-radius:3px;font-size:10.5px">## 标题</code> 条目，包含简介、纲要、关键词和原始链接。检索命中后，Agent 用链接读取完整文档内容。</div>
    </div>
    <div class="note-item">
      <span class="note-badge nb-amber">索引文件</span>
      <div class="note-text"><code style="background:#e2e8f0;padding:1px 4px;border-radius:3px;font-size:10.5px">keyword_index.json</code> 是从整颗目录树的关键词字段提取后构建的快速查找表，将关键词直接映射到对应目录路径，供 Layer 2 辅助检索使用，加快 Agent 的定位速度。</div>
    </div>
  </div>

</div>

<script>
// ── 树形数据定义 ──
const TREE = [
  {
    id: 'root', name: 'knowledge/', type: 'dir', open: true,
    children: [
      { id: 'root-idx', name: 'keyword_index.json', type: 'file', fileType: 'json' },
      { id: 'root-md',  name: 'data_structure.md',  type: 'file', fileType: 'md', nodeType: 'root' },
      {
        id: 'dir-sys', name: '系统架构/', type: 'dir', open: false,
        children: [
          { id: 'dir-sys-md', name: 'data_structure.md', type: 'file', fileType: 'md', nodeType: 'container' },
          {
            id: 'dir-svc', name: '服务架构/', type: 'dir', open: false,
            children: [
              { id: 'dir-svc-md', name: 'data_structure.md', type: 'file', fileType: 'md', nodeType: 'leaf' }
            ]
          },
          {
            id: 'dir-flow', name: '核心流程/', type: 'dir', open: false,
            children: [
              { id: 'dir-flow-md', name: 'data_structure.md', type: 'file', fileType: 'md', nodeType: 'leaf' }
            ]
          }
        ]
      },
      {
        id: 'dir-exp', name: '实验沉淀/', type: 'dir', open: false,
        children: [
          { id: 'dir-exp-md', name: 'data_structure.md', type: 'file', fileType: 'md', nodeType: 'container' },
          {
            id: 'dir-train', name: '模型训练/', type: 'dir', open: false,
            children: [
              { id: 'dir-train-md', name: 'data_structure.md', type: 'file', fileType: 'md', nodeType: 'leaf' }
            ]
          }
        ]
      }
    ]
  }
];

// ── 内容数据 ──
const CONTENT = {
  'root-md': {
    badge: '根节点', badgeClass: 'badge-root',
    path: 'knowledge/data_structure.md',
    html: `
      <div class="c-desc">知识库根目录的 data_structure.md 描述所有顶级领域的范围和内容方向，是 Agent 树状导航的第一站。</div>
      <div class="c-h3">### 系统架构/</div>
      <p style="color:#475569;font-size:12px;margin:4px 0 10px;line-height:1.7">收录系统整体设计、服务拓扑和核心业务流程相关文档。包含架构图、服务依赖关系、关键数据流程等内容，适合需要了解系统全貌时检索。</p>
      <div class="c-h3">### 实验沉淀/</div>
      <p style="color:#475569;font-size:12px;margin:4px 0 10px;line-height:1.7">记录各类离线实验的方案设计与结果分析。包含模型训练实验、策略调优对比等，是回溯历史实验决策依据的主要来源。</p>
    `
  },
  'dir-sys-md': {
    badge: '容器节点', badgeClass: 'badge-container',
    path: 'knowledge/系统架构/data_structure.md',
    html: `
      <div class="c-desc">当前目录下还有子目录，此文件描述各子目录的内容边界，供 Agent 选择继续深入的方向。</div>
      <div class="c-h3">### 服务架构/</div>
      <p style="color:#475569;font-size:12px;margin:4px 0 10px;line-height:1.7">服务级别的架构设计文档，包含服务拓扑图、上下游依赖关系、部署方式及容量规划相关内容。</p>
      <div class="c-h3">### 核心流程/</div>
      <p style="color:#475569;font-size:12px;margin:4px 0 10px;line-height:1.7">核心业务流程的详细说明，包含完整请求链路、数据处理各阶段逻辑及关键决策点的描述。</p>
    `
  },
  'dir-svc-md': {
    badge: '叶子节点', badgeClass: 'badge-leaf',
    path: 'knowledge/系统架构/服务架构/data_structure.md',
    html: `
      <div class="c-desc">最底层目录，此文件存放实际文档条目，每个 <strong>## 标题</strong> 对应一篇学城文档。</div>
      <div class="c-h2">整体服务架构设计</div>
      <div class="c-field"><span class="c-key">**文档简介**：</span><span class="c-val">描述系统整体服务拓扑，包含主要服务模块、调用关系和数据流向。</span></div>
      <div class="c-field" style="margin-top:4px"><span class="c-key">**内容纲要**：</span></div>
      <ul class="c-outline"><li>服务模块划分与职责</li><li>上下游依赖关系</li><li>关键数据流向说明</li></ul>
      <div class="c-field" style="margin-top:5px"><span class="c-key">**关键词**：</span><span class="c-kw">服务架构</span><span class="c-kw">服务拓扑</span><span class="c-kw">模块划分</span><span class="c-kw">调用关系</span></div>
      <div class="c-field"><span class="c-key">**文档链接**：</span><span class="c-val"><a href="#">https://km.sankuai.com/collabpage/xxxxxxx</a></span></div>
      <div class="c-field"><span class="c-key">**更新时间**：</span><span class="c-val">2026-03-15</span></div>
      <hr class="c-hr">
      <div class="c-h2">服务容量与扩缩容策略</div>
      <div class="c-field"><span class="c-key">**文档简介**：</span><span class="c-val">介绍服务容量规划方法和自动扩缩容触发策略。</span></div>
      <div class="c-field" style="margin-top:4px"><span class="c-key">**内容纲要**：</span></div>
      <ul class="c-outline"><li>容量评估指标</li><li>扩缩容阈值设定</li><li>历次容量问题复盘</li></ul>
      <div class="c-field" style="margin-top:5px"><span class="c-key">**关键词**：</span><span class="c-kw">容量规划</span><span class="c-kw">扩缩容</span><span class="c-kw">QPS</span><span class="c-kw">资源利用率</span></div>
      <div class="c-field"><span class="c-key">**文档链接**：</span><span class="c-val"><a href="#">https://km.sankuai.com/collabpage/xxxxxxx</a></span></div>
      <div class="c-field"><span class="c-key">**更新时间**：</span><span class="c-val">2026-04-01</span></div>
      <hr class="c-hr">
    `
  },
  'dir-flow-md': {
    badge: '叶子节点', badgeClass: 'badge-leaf',
    path: 'knowledge/系统架构/核心流程/data_structure.md',
    html: `
      <div class="c-desc">最底层目录，此文件存放实际文档条目。</div>
      <div class="c-h2">请求处理全链路说明</div>
      <div class="c-field"><span class="c-key">**文档简介**：</span><span class="c-val">从用户请求进入系统到最终响应，完整描述各处理阶段的逻辑和关键决策点。</span></div>
      <div class="c-field" style="margin-top:4px"><span class="c-key">**内容纲要**：</span></div>
      <ul class="c-outline"><li>请求接入与参数解析</li><li>核心处理阶段划分</li><li>结果组装与返回逻辑</li></ul>
      <div class="c-field" style="margin-top:5px"><span class="c-key">**关键词**：</span><span class="c-kw">请求链路</span><span class="c-kw">数据流</span><span class="c-kw">处理阶段</span><span class="c-kw">关键节点</span></div>
      <div class="c-field"><span class="c-key">**文档链接**：</span><span class="c-val"><a href="#">https://km.sankuai.com/collabpage/xxxxxxx</a></span></div>
      <div class="c-field"><span class="c-key">**更新时间**：</span><span class="c-val">2026-02-20</span></div>
      <hr class="c-hr">
    `
  },
  'dir-exp-md': {
    badge: '容器节点', badgeClass: 'badge-container',
    path: 'knowledge/实验沉淀/data_structure.md',
    html: `
      <div class="c-desc">当前目录下还有子目录，此文件描述各子目录的内容边界。</div>
      <div class="c-h3">### 模型训练/</div>
      <p style="color:#475569;font-size:12px;margin:4px 0 10px;line-height:1.7">各类模型训练实验的记录，包含实验方案、关键参数、离线评测结果和上线决策背景，是回溯历史实验的主要来源。</p>
    `
  },
  'dir-train-md': {
    badge: '叶子节点', badgeClass: 'badge-leaf',
    path: 'knowledge/实验沉淀/模型训练/data_structure.md',
    html: `
      <div class="c-desc">最底层目录，此文件存放实际文档条目。</div>
      <div class="c-h2">基线模型训练实验</div>
      <div class="c-field"><span class="c-key">**文档简介**：</span><span class="c-val">记录基线模型的训练方案、数据构成和离线评测结果。</span></div>
      <div class="c-field" style="margin-top:4px"><span class="c-key">**内容纲要**：</span></div>
      <ul class="c-outline"><li>训练数据来源与规模</li><li>模型结构与超参数设定</li><li>离线指标与基线对比</li></ul>
      <div class="c-field" style="margin-top:5px"><span class="c-key">**关键词**：</span><span class="c-kw">模型训练</span><span class="c-kw">基线</span><span class="c-kw">离线评测</span><span class="c-kw">实验记录</span></div>
      <div class="c-field"><span class="c-key">**文档链接**：</span><span class="c-val"><a href="#">https://km.sankuai.com/collabpage/xxxxxxx</a></span></div>
      <div class="c-field"><span class="c-key">**更新时间**：</span><span class="c-val">2026-03-15</span></div>
      <hr class="c-hr">
      <div class="c-h2">改进方案 A 实验对比</div>
      <div class="c-field"><span class="c-key">**文档简介**：</span><span class="c-val">在基线基础上验证方案 A（特征工程改进）的效果。</span></div>
      <div class="c-field" style="margin-top:4px"><span class="c-key">**内容纲要**：</span></div>
      <ul class="c-outline"><li>改进方案设计思路</li><li>与基线的指标对比</li><li>结论与后续迭代方向</li></ul>
      <div class="c-field" style="margin-top:5px"><span class="c-key">**关键词**：</span><span class="c-kw">实验对比</span><span class="c-kw">特征工程</span><span class="c-kw">效果验证</span><span class="c-kw">迭代方向</span></div>
      <div class="c-field"><span class="c-key">**文档链接**：</span><span class="c-val"><a href="#">https://km.sankuai.com/collabpage/xxxxxxx</a></span></div>
      <div class="c-field"><span class="c-key">**更新时间**：</span><span class="c-val">2026-04-01</span></div>
      <hr class="c-hr">
    `
  },
  'root-idx': {
    badge: '索引文件', badgeClass: 'badge-index',
    path: 'knowledge/keyword_index.json',
    html: `
      <div class="c-desc" style="margin-bottom:10px">由脚本扫描整颗目录树的关键词字段自动生成，将关键词直接映射到所在目录路径，供 Layer 2 辅助检索使用。</div>
      <pre class="c-pre">{
  "服务架构":   ["系统架构/服务架构"],
  "服务拓扑":   ["系统架构/服务架构"],
  "模块划分":   ["系统架构/服务架构"],
  "调用关系":   ["系统架构/服务架构"],
  "容量规划":   ["系统架构/服务架构"],
  "QPS":        ["系统架构/服务架构"],
  "请求链路":   ["系统架构/核心流程"],
  "数据流":     ["系统架构/核心流程"],
  "处理阶段":   ["系统架构/核心流程"],
  "模型训练":   ["实验沉淀/模型训练"],
  "基线":       ["实验沉淀/模型训练"],
  "离线评测":   ["实验沉淀/模型训练"],
  "实验记录":   ["实验沉淀/模型训练"],
  "特征工程":   ["实验沉淀/模型训练"],
  ...
}</pre>
    `
  }
};

// ── 渲染树 ──
let selectedId = null;

function getIcon(node) {
  if (node.type === 'dir') return node.open ? '📂' : '📁';
  if (node.fileType === 'json') return '📋';
  if (node.nodeType === 'leaf') return '📄';
  if (node.nodeType === 'root') return '📄';
  return '📝';
}

function renderTree(nodes, depth, container) {
  nodes.forEach(node => {
    const item = document.createElement('div');
    item.className = 'tree-item' + (node.id === selectedId ? ' selected' : '');
    item.style.paddingLeft = (10 + depth * 16) + 'px';
    item.dataset.id = node.id;

    const toggle = document.createElement('span');
    toggle.className = 'toggle' + (node.type === 'dir' ? (node.children.length ? (node.open ? ' open' : '') : ' empty') : ' empty');
    toggle.textContent = '▶';

    const icon = document.createElement('span');
    icon.className = 'item-icon';
    icon.textContent = getIcon(node);

    const name = document.createElement('span');
    name.className = 'item-name' + (node.type === 'dir' ? ' dir' : '');
    name.textContent = node.name;

    item.appendChild(toggle);
    item.appendChild(icon);
    item.appendChild(name);
    container.appendChild(item);

    if (node.type === 'dir' && node.children) {
      const childWrap = document.createElement('div');
      childWrap.className = 'tree-children';
      childWrap.id = 'children-' + node.id;
      childWrap.style.display = node.open ? 'block' : 'none';
      container.appendChild(childWrap);
      renderTree(node.children, depth + 1, childWrap);
    }

    item.addEventListener('click', (e) => {
      e.stopPropagation();
      if (node.type === 'dir' && node.children) {
        node.open = !node.open;
        toggle.className = 'toggle' + (node.children.length ? (node.open ? ' open' : '') : ' empty');
        icon.textContent = getIcon(node);
        const cw = document.getElementById('children-' + node.id);
        if (cw) cw.style.display = node.open ? 'block' : 'none';
      }
      if (node.type === 'file') {
        selectedId = node.id;
        document.querySelectorAll('.tree-item').forEach(el => el.classList.remove('selected'));
        item.classList.add('selected');
        name.parentElement.querySelector('.item-name').style.color = '';
        showContent(node.id);
      }
    });
  });
}

function showContent(id) {
  const data = CONTENT[id];
  if (!data) return;

  const header = document.getElementById('content-header');
  const breadcrumb = document.getElementById('breadcrumb');
  const badge = document.getElementById('node-badge');
  const body = document.getElementById('content-body');

  header.style.display = 'flex';

  const parts = data.path.split('/');
  breadcrumb.innerHTML = parts.map((p, i) =>
    i === parts.length - 1
      ? `<span class="last">${p}</span>`
      : `<span>${p}</span> <span style="color:#cbd5e1;margin:0 3px">/</span>`
  ).join('');

  badge.textContent = data.badge;
  badge.className = 'node-badge ' + data.badgeClass;
  body.innerHTML = data.html;
}

// ── 初始化 ──
const treeRoot = document.getElementById('tree-root');
renderTree(TREE, 0, treeRoot);
</script>
</body>
</html>


### 4. 知识检索

#### 4.1 三层检索架构

**第一层：核心检索（Core Retrieval）**

第一层是 knowledge-flow 检索体系的主力。它通过树状导航的方式，逐层读取 `data_structure.md`，定位到相关的文档链接或本地路径，然后通过学城工具调用（citadel）或本地文件读取（Read）按需加载内容。这种方式精准、可溯源，适合处理领域专业知识。想象一下在图书馆里查资料，你先找到相关的书架（根目录），再找到具体的分类（子目录），最后找到目标书籍（文档链接）—— 核心检索就是这样的导航过程。为避免过度展开，文档读取上限为 5 次。

**第二层：辅助检索（Assisted Retrieval）**

第二层通过`keyword_index.json` 提供关键词索引，帮助第一层快速定位候选目录。这里有个重要约束：关键词索引只用于加速定位，命中后必须回到树状导航继续验证，不能直接触发文档读取。就像图书馆的索引卡片，它能告诉你“关于这个话题的内容可能在某个分类下”，但你还是要去书架上确认，而不是直接从卡片上读内容。索引为扫描生成，每次知识库更新后自动重建（基于脚本，无需消耗Token）。

**第三层：兜底检索（Fallback Retrieval）**

当本地知识库无法提供相关内容时，系统会自动触发学城全局搜索。触发条件分三种：① 本地 0 次文档命中时强制触发；② 本地信息不足以回答时可选触发；③ 本地知识库已充分回答时禁止触发。这一层的覆盖面广，对搜索结果按关键词命中数打分排序，取前 3-5 篇精读，并在返回答案时清晰标注来源，让用户明确区分知识边界。

> 📊 **流程图（Drawio）**：https://km.sankuai.com/api/file/cdn/2783426698/253581748603?isNewContent=false&contentType=0&isNewContent=false

#### 4.2 检索日志 & 质量追踪

每次检索结束后，knowledge-flow 会自动把这次检索的完整过程写入本地的 `retrieval.jsonl`——走了哪些目录、最终读取了哪些文档、有没有触发兜底搜索。这份日志不需要人工维护，也不影响正常使用，但它是了解知识库健康状况的第一手数据来源。

例如，以下几类现象，出现时通常对应明确的改进方向：

**反复触发兜底搜索**。如果某类问题的日志里 `fallback_triggered` 持续为 true，说明本地知识库对这个方向的覆盖是空白的 —— Agent 在本地没有找到任何相关内容，只好去学城全站搜索。这是知识库入库优先级最直接的信号，对应的问题方向就是下一步应该补充的文档。

**每次检索都读满了文档数量上限才停下**。说明某个目录下积累的文档太多、主题混杂，Agent 需要把所有文档翻一遍才能找到答案，甚至翻完了还没找到。这类信号对应目录结构优化里的拆分操作。

> **📂 折叠块（默认折叠）：检索日志 示例**
>
> {
> "session_id": "20260506_111625_3vv",
> "timestamp": "2026-05-06T11:16:25",
> "question": "什么是ccwhat?",
> "knowledge_base": "knowledge-self-used",
> "nav_paths": [
> "数据与指标/监控告警",
> "系统链路与数据口径"
> ],
> "recalled_docs": [],
> "km_calls_used": 0,
> "local_reads_used": 0,
> "fallback_triggered": true,
> "fallback_docs": [
> {
> "title": "CCWhat（See See What）：开箱即用的 Claude Code 可视化智能分析工具",
> "link": "[CCWhat（See See What）：开箱即用的 Agent 可视化智能分析工具](https://km.sankuai.com/collabpage/2757288182)",
> "type": "fallback",
> "source_dir": "fallback_search"
> }
> ],
> "outcome": "unknown"
> }

### 5. 知识抽取

- **代码库知识：**代码库知识的提取工作由外部 skill（knowledge-extractor）负责，它扫描服务代码、识别系统架构、业务流程和配置依赖，产出结构化的 .md 和 .txt 文件。knowledge-flow 接收这批产出物后完成本地入库，支持断点续做。

- **XT ETL 任务：**从数据平台读取 ETL 任务的 SQL、调度配置与下游血缘关系，由 Agent 提炼出数据链路语义（上游输入表、直接下游表、调度周期、核心逻辑）后写入知识库，让“数据从哪来、往哪去”随时可查。同样采用状态机模式，Agent 逐任务分析后写入，支持断点续做。

- **Agent 知识沉淀：**对话结束后，Agent 识别有价值的内容（排查思路、决策依据、踩坑经验、规律总结），提炼为结构化条目写入知识库。支持两种触发方式：在上下文中主动触发，或提供本地历史日志文件由 Agent 读取分析。写入时根据情况选择三种模式之一：① 首次入库时新建写入；② 已有同名条目时可选择覆盖替换，③或在已有条目末尾追加补充记录，适合对同一问题的后续补录。

- **TT 工单：**从原始工单导出文件（聊天记录形式）出发，经 Agent 知识抽取解析工单结构和关键词，再对内容进行整理、分类和合并——按问题类型归组，将散落的历史工单经验聚合成更有结构的知识单元。之后批量创建学城文档（支持断点续传），最后按分类更新知识库索引。

> **ℹ️ 信息：**
>
> 知识抽取是入库的前置环节，本节列举的几类处理形式覆盖了常见场景，**实际使用时可根据自身的知识来源灵活选择更合适的提取方式。**knowledge-flow 的核心设计重心在于知识的组织结构、检索方式和运营管理，抽取环节本身保持开放。

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>knowledge-flow · 知识抽取</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 24px; }
.page-header { text-align: center; margin-bottom: 12px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }

/* ── 来源面板 ── */
.sp {
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  overflow: hidden; margin-bottom: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.sp:last-child { margin-bottom: 0; }

.sp-head {
  display: flex; align-items: center; gap: 9px;
  padding: 9px 14px; border-bottom: 1.5px solid #e2e8f0;
}
.sp-icon { font-size: 15px; flex-shrink: 0; }
.sp-name { font-size: 13px; font-weight: 700; color: #0f172a; }
.sp-tag  {
  font-size: 9.5px; font-weight: 700; padding: 2px 7px;
  border-radius: 10px; margin-left: 2px;
}
.sp-desc {
  font-size: 11px; color: #64748b; flex: 1;
  padding-left: 10px; border-left: 1px solid #e2e8f0;
  margin-left: 4px; line-height: 1.6;
}
.sp-body { padding: 11px 14px; }

.sp-blue   { border-color: #bfdbfe; }
.sp-blue   .sp-head { background: #eff6ff; border-bottom-color: #bfdbfe; }
.sp-purple { border-color: #ddd6fe; }
.sp-purple .sp-head { background: #f5f3ff; border-bottom-color: #ddd6fe; }
.sp-indigo { border-color: #c7d2fe; }
.sp-indigo .sp-head { background: #eef2ff; border-bottom-color: #c7d2fe; }
.sp-amber  { border-color: #fde68a; }
.sp-amber  .sp-head { background: #fffbeb; border-bottom-color: #fde68a; }

/* ── 流程节点 ── */
.flow-row { display: flex; align-items: center; gap: 0; flex-wrap: nowrap; }

.fn {
  flex-shrink: 0; border-radius: 7px; border: 1.5px solid;
  background: #fff; padding: 7px 8px; text-align: center; min-width: 86px;
}
.fn-main { font-size: 10.5px; font-weight: 600; color: #1e293b; line-height: 1.3; }
.fn-sub  { font-size: 9px;   color: #94a3b8; margin-top: 2px; line-height: 1.3; }
.fn-result .fn-main { font-weight: 700; }

.fa { flex-shrink: 0; display: flex; align-items: center; padding: 0 3px; }

.c-blue   { border-color: #93c5fd; }
.c-blue.fn-result   { background: #eff6ff; border-color: #3b82f6; }
.c-blue.fn-result .fn-main { color: #1d4ed8; }
.c-purple { border-color: #c4b5fd; }
.c-purple.fn-result { background: #f5f3ff; border-color: #7c3aed; }
.c-purple.fn-result .fn-main { color: #6d28d9; }
.c-indigo { border-color: #a5b4fc; }
.c-indigo.fn-result { background: #eef2ff; border-color: #4f46e5; }
.c-indigo.fn-result .fn-main { color: #3730a3; }
.c-amber  { border-color: #fcd34d; }
.c-amber.fn-result  { background: #fffbeb; border-color: #f59e0b; }
.c-amber.fn-result .fn-main { color: #92400e; }

.wf-new { border-color: #86efac; background: #f0fdf4; }
.wf-new .fn-main { color: #065f46; }
.wf-rep { border-color: #93c5fd; background: #eff6ff; }
.wf-rep .fn-main { color: #1e40af; }
.wf-app { border-color: #c4b5fd; background: #f5f3ff; }
.wf-app .fn-main { color: #6d28d9; }

.note { font-size: 10.5px; color: #94a3b8; margin-top: 9px; line-height: 1.6; }
.note strong { color: #64748b; }
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>knowledge-flow · 知识抽取</h1>
    <p>四类来源 · 各有完整的提取与入库流程</p>
  </div>

  <!-- ══ 代码库知识 ══ -->
  <div class="sp sp-blue">
    <div class="sp-head">
      <span class="sp-icon">💻</span>
      <span class="sp-name">代码库知识</span>
      <span class="sp-tag" style="background:#dbeafe;color:#1e40af">代码 → 知识</span>
      <span class="sp-desc">提取由外部 skill（knowledge-extractor）完成；knowledge-flow 接收结构化产出物，完成本地入库。</span>
    </div>
    <div class="sp-body">
      <div class="flow-row">
        <div class="fn c-blue" style="min-width:100px"><div class="fn-main">knowledge-extractor</div><div class="fn-sub">外部 skill 扫描代码</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#93c5fd" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#93c5fd"/></svg></div>
        <div class="fn c-blue"><div class="fn-main">结构化产出物</div><div class="fn-sub">.md / .txt 文件</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#93c5fd" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#93c5fd"/></svg></div>
        <div class="fn c-blue"><div class="fn-main">扫描文件队列</div><div class="fn-sub">逐文件处理</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#93c5fd" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#93c5fd"/></svg></div>
        <div class="fn c-blue"><div class="fn-main">Agent 生成元数据</div><div class="fn-sub">简介/纲要/关键词</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#93c5fd" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#93c5fd"/></svg></div>
        <div class="fn c-blue"><div class="fn-main">写入目标目录</div><div class="fn-sub">data_structure.md</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#3b82f6" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#3b82f6"/></svg></div>
        <div class="fn c-blue fn-result"><div class="fn-main">✓ 入库完成</div><div class="fn-sub">重建关键词索引</div></div>
      </div>
      <div class="note">⚡ <strong>.txt 文件</strong>（配置/表依赖）正则自动处理；<strong>.md 文件</strong>由 Agent 阅读后生成元数据。支持断点续做。</div>
    </div>
  </div>

  <!-- ══ XT ETL 任务 ══ -->
  <div class="sp sp-purple">
    <div class="sp-head">
      <span class="sp-icon">🔄</span>
      <span class="sp-name">XT ETL 任务</span>
      <span class="sp-tag" style="background:#ede9fe;color:#6d28d9">数据表 → 知识</span>
      <span class="sp-desc">从数据平台读取 ETL 任务的 SQL、调度配置与下游血缘，由 Agent 提炼数据链路语义后入库。</span>
    </div>
    <div class="sp-body">
      <div class="flow-row">
        <div class="fn c-purple"><div class="fn-main">指定任务列表</div><div class="fn-sub">task_a, task_b…</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#c4b5fd" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#c4b5fd"/></svg></div>
        <div class="fn c-purple"><div class="fn-main">读取任务内容</div><div class="fn-sub">SQL / 配置 / 血缘</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#c4b5fd" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#c4b5fd"/></svg></div>
        <div class="fn c-purple"><div class="fn-main">Agent 提炼语义</div><div class="fn-sub">摘要/纲要/关键词</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#c4b5fd" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#c4b5fd"/></svg></div>
        <div class="fn c-purple"><div class="fn-main">生成元数据条目</div><div class="fn-sub">写入目标目录</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#7c3aed" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#7c3aed"/></svg></div>
        <div class="fn c-purple fn-result"><div class="fn-main">✓ 入库完成</div><div class="fn-sub">重建关键词索引</div></div>
      </div>
      <div class="note">⚡ 状态机模式：脚本管理队列，Agent 逐任务分析后写入，支持断点续做。</div>
    </div>
  </div>

  <!-- ══ Agent 自主知识沉淀 ══ -->
  <div class="sp sp-indigo">
    <div class="sp-head">
      <span class="sp-icon">🤖</span>
      <span class="sp-name">Agent 自主知识沉淀</span>
      <span class="sp-tag" style="background:#e0e7ff;color:#3730a3">会话 → 知识</span>
      <span class="sp-desc">对话结束后，Agent 主动识别有价值的内容，自动提炼为结构化条目写入知识库。支持当前对话触发或读取本地历史日志文件。</span>
    </div>
    <div class="sp-body">
      <div class="flow-row">
        <!-- 两种来源 fork -->
        <div style="display:flex;flex-direction:column;gap:6px;flex-shrink:0">
          <div class="fn c-indigo" style="min-width:104px"><div class="fn-main">当前对话上下文</div><div class="fn-sub">会话结束时触发</div></div>
          <div class="fn c-indigo" style="min-width:104px"><div class="fn-main">本地历史日志文件</div><div class="fn-sub">.txt / .md</div></div>
        </div>
        <div style="display:flex;align-items:center;flex-shrink:0">
          <div style="display:flex;flex-direction:column">
            <div style="width:13px;height:33px;border-right:1.5px solid #a5b4fc;border-top:1.5px solid #a5b4fc;border-radius:0 4px 0 0"></div>
            <div style="width:13px;height:33px;border-right:1.5px solid #a5b4fc;border-bottom:1.5px solid #a5b4fc;border-radius:0 0 4px 0"></div>
          </div>
          <div style="width:6px;height:1.5px;background:#a5b4fc"></div>
        </div>
        <div class="fa"><svg width="16" height="10"><line x1="0" y1="5" x2="8" y2="5" stroke="#a5b4fc" stroke-width="1.5"/><polygon points="8,2 16,5 8,8" fill="#a5b4fc"/></svg></div>
        <div class="fn c-indigo"><div class="fn-main">识别有价值内容</div><div class="fn-sub">排查/决策/规律</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#a5b4fc" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#a5b4fc"/></svg></div>
        <div class="fn c-indigo"><div class="fn-main">生成结构化条目</div><div class="fn-sub">标题/简介/纲要/关键词</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#a5b4fc" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#a5b4fc"/></svg></div>
        <!-- 写入三叉 -->
        <div style="display:flex;align-items:center;flex-shrink:0">
          <div style="width:1.5px;height:82px;background:#a5b4fc"></div>
          <div style="display:flex;flex-direction:column;justify-content:space-between;height:82px">
            <div style="width:9px;height:1.5px;background:#a5b4fc;margin-top:11px"></div>
            <div style="width:9px;height:1.5px;background:#a5b4fc"></div>
            <div style="width:9px;height:1.5px;background:#a5b4fc;margin-bottom:11px"></div>
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:6px;flex-shrink:0">
          <div class="fn wf-new" style="min-width:82px"><div class="fn-main">新建写入</div><div class="fn-sub">首次入库</div></div>
          <div class="fn wf-rep" style="min-width:82px"><div class="fn-main">替换更新</div><div class="fn-sub">覆盖已有条目</div></div>
          <div class="fn wf-app" style="min-width:82px"><div class="fn-main">追加补充</div><div class="fn-sub">追加至已有条目</div></div>
        </div>
        <div class="fa" style="margin-left:3px"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#4f46e5" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#4f46e5"/></svg></div>
        <div class="fn c-indigo fn-result"><div class="fn-main">✓ 入库完成</div><div class="fn-sub">重建关键词索引</div></div>
      </div>
      <div class="note">⚡ <strong>追加补充</strong>在已有 .md 文件末尾新增「## 补充记录（日期）」段落，并同步更新索引条目的时间字段，适合对同一问题的后续补录。</div>
    </div>
  </div>

  <!-- ══ TT 工单 ══ -->
  <div class="sp sp-amber">
    <div class="sp-head">
      <span class="sp-icon">🎫</span>
      <span class="sp-name">TT 工单</span>
      <span class="sp-tag" style="background:#fef3c7;color:#92400e">工单 → 知识</span>
      <span class="sp-desc">原始工单导出后，经 Agent 知识抽取、整理分类合并，批量写入学城文档并更新知识库索引。</span>
    </div>
    <div class="sp-body">
      <div class="flow-row">
        <div class="fn c-amber"><div class="fn-main">原始工单导出</div><div class="fn-sub">聊天记录形式</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#fcd34d" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#fcd34d"/></svg></div>
        <div class="fn c-amber"><div class="fn-main">Agent 知识抽取</div><div class="fn-sub">解析工单结构/关键词</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#fcd34d" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#fcd34d"/></svg></div>
        <div class="fn c-amber"><div class="fn-main">整理 / 分类 / 合并</div><div class="fn-sub">按问题类型归组</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#fcd34d" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#fcd34d"/></svg></div>
        <div class="fn c-amber"><div class="fn-main">写入学城文档</div><div class="fn-sub">批量创建 · 断点续传</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#f59e0b" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#f59e0b"/></svg></div>
        <div class="fn c-amber fn-result"><div class="fn-main">✓ 更新知识库索引</div><div class="fn-sub">按分类写入</div></div>
      </div>
    </div>
  </div>

</div>
</body>
</html>


### 6. 知识入库

知识入库是将各类来源的知识写入本地知识库的过程。根据知识的存储形式，**分为两条渠道：**学城文档入库和本地文件入库。

#### 6.1 学城文档入库

学城文档入库的核心动作是：读取文档原文 → Agent 生成摘要和关键词 → 写入 data_structure.md 条目，条目中保存文档链接而非全文。检索命中时，Agent 再通过链接读取最新原文。

根据入库规模和场景，提供三种模式：

- **学城链接入库（少量文档）：**适合手里有明确目标的场景——提供几篇到十几篇文档链接，逐篇读取入库。每完成一篇才解锁下一篇（节奏闸门设计），队列持久化到磁盘，中断后可从断点继续。

- **父目录批量入库（大量文档）：**适合“知道某个目录下有大量文档、但不确定哪些值得入库”的场景。系统先扫描父目录下的全部文档，再由 Agent 逐篇评估（可跳过）——给出推荐/不推荐的判断，以及建议放入的目标目录。两个决策同时完成，过滤后的推荐项才进入实际入库流程。支持百篇以上规模，可随时中断恢复。

- **知识库冷启入库（冷启）：**适合面对全新领域从零开始建档的场景。流程分为四个阶段：首先扫描大型父目录并按文档时间和活跃度粗筛；然后由 Agent 基于文档结构生成目录模板，确定领域的知识分类骨架；再对每篇文档进行高/中/低三档质量精判，同时给出建议入库目录；最后生成结构化报告，可直接发布到学城作为领域建档进度的记录。

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>knowledge-flow · 学城文档入库</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 24px; }
.page-header { text-align: center; margin-bottom: 12px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }

/* ── 对比条 ── */
.compare-strip {
  display: flex; gap: 8px; margin-bottom: 14px;
}
.cs-item {
  flex: 1; border-radius: 9px; border: 1.5px solid;
  padding: 11px 13px; display: flex; flex-direction: column; gap: 5px;
}
.cs-head { display: flex; align-items: center; gap: 6px; }
.cs-icon { font-size: 15px; }
.cs-name { font-size: 12.5px; font-weight: 700; }
.cs-scale {
  font-size: 10px; font-weight: 700; padding: 1px 7px;
  border-radius: 8px; align-self: flex-start;
}
.cs-when { font-size: 11px; color: #64748b; line-height: 1.5; }

.cs-blue   { border-color: #bfdbfe; background: #eff6ff; }
.cs-blue   .cs-name  { color: #1e40af; }
.cs-blue   .cs-scale { background: #dbeafe; color: #1e40af; }
.cs-green  { border-color: #bbf7d0; background: #ecfdf5; }
.cs-green  .cs-name  { color: #065f46; }
.cs-green  .cs-scale { background: #d1fae5; color: #065f46; }
.cs-purple { border-color: #ddd6fe; background: #f5f3ff; }
.cs-purple .cs-name  { color: #6d28d9; }
.cs-purple .cs-scale { background: #ede9fe; color: #6d28d9; }

/* ── 流程面板 ── */
.sp {
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  overflow: hidden; margin-bottom: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.sp:last-child { margin-bottom: 0; }
.sp-head {
  display: flex; align-items: center; gap: 9px;
  padding: 9px 14px; border-bottom: 1.5px solid #e2e8f0;
}
.sp-icon { font-size: 15px; flex-shrink: 0; }
.sp-name { font-size: 13px; font-weight: 700; color: #0f172a; }
.sp-tag  { font-size: 9.5px; font-weight: 700; padding: 2px 7px; border-radius: 10px; margin-left: 2px; }
.sp-desc { font-size: 11px; color: #64748b; flex: 1; padding-left: 10px; border-left: 1px solid #e2e8f0; margin-left: 4px; line-height: 1.6; }
.sp-body { padding: 11px 14px; }

.sp-blue   { border-color: #bfdbfe; }
.sp-blue   .sp-head { background: #eff6ff; border-bottom-color: #bfdbfe; }
.sp-green  { border-color: #bbf7d0; }
.sp-green  .sp-head { background: #ecfdf5; border-bottom-color: #bbf7d0; }
.sp-purple { border-color: #ddd6fe; }
.sp-purple .sp-head { background: #f5f3ff; border-bottom-color: #ddd6fe; }

/* ── 流程节点 ── */
.flow-row { display: flex; align-items: center; gap: 0; flex-wrap: nowrap; }
.fn {
  flex-shrink: 0; border-radius: 7px; border: 1.5px solid;
  background: #fff; padding: 7px 8px; text-align: center; min-width: 88px;
}
.fn-main { font-size: 10.5px; font-weight: 600; color: #1e293b; line-height: 1.3; }
.fn-sub  { font-size: 9px; color: #94a3b8; margin-top: 2px; line-height: 1.3; }
.fn-result .fn-main { font-weight: 700; }

.fa { flex-shrink: 0; display: flex; align-items: center; padding: 0 3px; }

.c-blue   { border-color: #93c5fd; }
.c-blue.fn-result   { background: #eff6ff; border-color: #3b82f6; }
.c-blue.fn-result .fn-main { color: #1d4ed8; }
.c-green  { border-color: #6ee7b7; }
.c-green.fn-result  { background: #ecfdf5; border-color: #059669; }
.c-green.fn-result .fn-main { color: #065f46; }
.c-purple { border-color: #c4b5fd; }
.c-purple.fn-result { background: #f5f3ff; border-color: #7c3aed; }
.c-purple.fn-result .fn-main { color: #6d28d9; }

/* 高亮步骤（独特核心步骤） */
.fn-key { border-width: 2px; }
.c-blue.fn-key   { border-color: #3b82f6; background: #eff6ff; }
.c-blue.fn-key .fn-main { color: #1e40af; }
.c-green.fn-key  { border-color: #059669; background: #ecfdf5; }
.c-green.fn-key .fn-main { color: #065f46; }
.c-purple.fn-key { border-color: #7c3aed; background: #f5f3ff; }
.c-purple.fn-key .fn-main { color: #6d28d9; }

/* 质量三档 badge 组 */
.quality-badges { display: flex; flex-direction: column; gap: 3px; justify-content: center; }
.qb { font-size: 9.5px; font-weight: 700; padding: 1px 7px; border-radius: 6px; text-align: center; white-space: nowrap; }
.qb-high { background: #d1fae5; color: #065f46; }
.qb-mid  { background: #fef3c7; color: #92400e; }
.qb-low  { background: #fee2e2; color: #991b1b; }

/* 评估结果 badge 组 */
.eval-badges { display: flex; flex-direction: column; gap: 3px; justify-content: center; }
.eb { font-size: 9.5px; font-weight: 700; padding: 1px 7px; border-radius: 6px; text-align: center; white-space: nowrap; }
.eb-yes { background: #d1fae5; color: #065f46; }
.eb-no  { background: #f1f5f9; color: #64748b; }

/* 阶段标注 */
.stage-wrap { display: flex; flex-direction: column; gap: 8px; }
.stage-row  { display: flex; align-items: center; gap: 6px; }
.stage-lbl  {
  flex-shrink: 0; font-size: 9px; font-weight: 700; color: #94a3b8;
  letter-spacing: .5px; writing-mode: horizontal-tb;
  width: 24px; text-align: right;
}

.note { font-size: 10.5px; color: #94a3b8; margin-top: 9px; line-height: 1.6; }
.note strong { color: #64748b; }
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>knowledge-flow · 学城文档入库</h1>
    <p>三种模式覆盖从少量精选到大规模冷启的不同场景</p>
  </div>

  <!-- ── 对比条 ── -->
  <div class="compare-strip">
    <div class="cs-item cs-blue">
      <div class="cs-head"><span class="cs-icon">🔗</span><span class="cs-name">学城链接入库</span></div>
      <span class="cs-scale">少量 · 精选</span>
      <div class="cs-when">手里有几篇到几十篇文档链接，直接指定入库，适合零散的按需收录。</div>
    </div>
    <div class="cs-item cs-green">
      <div class="cs-head"><span class="cs-icon">📂</span><span class="cs-name">父目录批量入库</span></div>
      <span class="cs-scale">百篇级 · 筛选后入</span>
      <div class="cs-when">知道某个学城目录下有大量文档，希望系统扫描后由 Agent 评估哪些值得入库。</div>
    </div>
    <div class="cs-item cs-purple">
      <div class="cs-head"><span class="cs-icon">🏗️</span><span class="cs-name">知识库冷启入库</span></div>
      <span class="cs-scale">新领域 · 从零建档</span>
      <div class="cs-when">面对一个全新领域，需要先设计目录结构，再按质量判断批量建档入库。</div>
    </div>
  </div>

  <!-- ══ 学城链接入库 ══ -->
  <div class="sp sp-blue">
    <div class="sp-head">
      <span class="sp-icon">🔗</span>
      <span class="sp-name">学城链接入库</span>
      <span class="sp-tag" style="background:#dbeafe;color:#1e40af">逐篇处理</span>
      <span class="sp-desc">提供一个或多个学城文档链接，Agent 逐篇读取、生成元数据并写入知识库。适合精选收录，每篇质量有保证。</span>
    </div>
    <div class="sp-body">
      <div class="flow-row">
        <div class="fn c-blue"><div class="fn-main">提供链接列表</div><div class="fn-sub">逗号或文件分隔</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#93c5fd" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#93c5fd"/></svg></div>
        <div class="fn c-blue"><div class="fn-main">初始化队列</div><div class="fn-sub">持久化到磁盘</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#93c5fd" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#93c5fd"/></svg></div>
        <div class="fn c-blue"><div class="fn-main">读取文档内容</div><div class="fn-sub">km CLI</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#93c5fd" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#93c5fd"/></svg></div>
        <div class="fn c-blue"><div class="fn-main">Agent 生成元数据</div><div class="fn-sub">简介/纲要/关键词</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#93c5fd" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#93c5fd"/></svg></div>
        <div class="fn c-blue fn-key"><div class="fn-main">mark-done 写入</div><div class="fn-sub">解锁下一篇</div></div>
        <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#3b82f6" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#3b82f6"/></svg></div>
        <div class="fn c-blue fn-result"><div class="fn-main">✓ 入库完成</div><div class="fn-sub">重建关键词索引</div></div>
      </div>
      <div class="note">⚡ <strong>mark-done 是节奏闸门</strong>：必须标记当前篇完成后才能看到下一篇。队列持久化到磁盘，上下文压缩或中断后可从断点继续，不依赖对话记忆。</div>
    </div>
  </div>

  <!-- ══ 父目录批量入库 ══ -->
  <div class="sp sp-green">
    <div class="sp-head">
      <span class="sp-icon">📂</span>
      <span class="sp-name">父目录批量入库</span>
      <span class="sp-tag" style="background:#d1fae5;color:#065f46">四阶段流水线</span>
      <span class="sp-desc">提供一个学城父目录链接，系统扫描其下所有文档，由 Agent 逐篇评估并推荐，支持百篇以上规模。</span>
    </div>
    <div class="sp-body">
      <div class="stage-wrap">

        <div class="stage-row">
          <span class="stage-lbl">扫描</span>
          <div class="flow-row">
            <div class="fn c-green"><div class="fn-main">父目录 URL</div><div class="fn-sub">学城链接</div></div>
            <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#6ee7b7" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#6ee7b7"/></svg></div>
            <div class="fn c-green"><div class="fn-main">遍历文档树</div><div class="fn-sub">获取全部子文档</div></div>
          </div>
        </div>

        <div class="stage-row">
          <span class="stage-lbl">评估</span>
          <div class="flow-row">
            <div class="fn c-green fn-key" style="min-width:110px"><div class="fn-main">Agent 逐篇阅读评估</div><div class="fn-sub">推荐/不推荐 + 目标目录</div></div>
            <div class="fa" style="padding:0 6px">
              <div class="eval-badges">
                <span class="eb eb-yes">✓ 推荐入库</span>
                <span class="eb eb-no">✗ 不推荐</span>
              </div>
            </div>
            <div class="fn c-green"><div class="fn-main">生成入库候选列表</div><div class="fn-sub">过滤后的推荐项</div></div>
          </div>
        </div>

        <div class="stage-row">
          <span class="stage-lbl">入库</span>
          <div class="flow-row">
            <div class="fn c-green"><div class="fn-main">逐篇执行入库</div><div class="fn-sub">含元数据生成</div></div>
            <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#059669" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#059669"/></svg></div>
            <div class="fn c-green fn-result"><div class="fn-main">✓ 批量入库完成</div><div class="fn-sub">重建关键词索引</div></div>
          </div>
        </div>

      </div>
      <div class="note">⚡ <strong>评估阶段</strong>是核心——Agent 每篇都给出"推荐/不推荐"和"建议放入哪个目录"，两个决策同时完成，不合格的文档在这一步就被过滤掉。支持随时中断、恢复执行。</div>
    </div>
  </div>

  <!-- ══ 知识库冷启入库 ══ -->
  <div class="sp sp-purple">
    <div class="sp-head">
      <span class="sp-icon">🏗️</span>
      <span class="sp-name">知识库冷启入库</span>
      <span class="sp-tag" style="background:#ede9fe;color:#6d28d9">五阶段 · 从零建档</span>
      <span class="sp-desc">面对全新领域从零开始时使用。先建目录结构，再对文档做质量精判，最终生成结构化报告辅助决策。</span>
    </div>
    <div class="sp-body">
      <div class="stage-wrap">

        <div class="stage-row">
          <span class="stage-lbl">粗筛</span>
          <div class="flow-row">
            <div class="fn c-purple"><div class="fn-main">大型父目录 URL</div><div class="fn-sub">新领域入口</div></div>
            <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#c4b5fd" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#c4b5fd"/></svg></div>
            <div class="fn c-purple"><div class="fn-main">扫描 + 元数据粗筛</div><div class="fn-sub">按时间/活跃度过滤</div></div>
          </div>
        </div>

        <div class="stage-row">
          <span class="stage-lbl">建档</span>
          <div class="flow-row">
            <div class="fn c-purple fn-key" style="min-width:110px"><div class="fn-main">Agent 生成目录模板</div><div class="fn-sub">设计分类骨架</div></div>
          </div>
        </div>

        <div class="stage-row">
          <span class="stage-lbl">精判</span>
          <div class="flow-row">
            <div class="fn c-purple fn-key" style="min-width:110px"><div class="fn-main">逐篇质量精判</div><div class="fn-sub">+ 建议入库目录</div></div>
            <div class="fa" style="padding:0 6px">
              <div class="quality-badges">
                <span class="qb qb-high">高质量</span>
                <span class="qb qb-mid">一般</span>
                <span class="qb qb-low">时效性低</span>
              </div>
            </div>
          </div>
        </div>

        <div class="stage-row">
          <span class="stage-lbl">报告</span>
          <div class="flow-row">
            <div class="fn c-purple"><div class="fn-main">生成结构化报告</div><div class="fn-sub">可发布到学城</div></div>
            <div class="fa"><svg width="18" height="10"><line x1="0" y1="5" x2="10" y2="5" stroke="#7c3aed" stroke-width="1.5"/><polygon points="10,2 18,5 10,8" fill="#7c3aed"/></svg></div>
            <div class="fn c-purple fn-result"><div class="fn-main">✓ 选择性入库</div><div class="fn-sub">优先高质量文档</div></div>
          </div>
        </div>

      </div>
      <div class="note">⚡ <strong>粗筛</strong>用文档更新时间和活跃度快速过滤一批明显失效的文档；<strong>精判</strong>才是重头，三档质量标注 + 目标目录建议，为入库决策提供依据。报告可直接发布到学城，作为领域知识建档进度的记录。</div>
    </div>
  </div>

</div>
</body>
</html>


#### 6.2 本地文件入库

与学城文档入库（存摘要+链接）不同，本地文件入库将完整内容存储到知识库目录下，检索命中时直接读取本地文件，无需额外工具调用请求。

目前支持的本地文件形式包括：代码库知识提取产出的 .md 架构和流程文档、Agent 会话沉淀产出的 .md 经验文件、XT ETL 任务提取产出的 .txt 配置和数据表索引、TT 工单整理后的 .md 工单经验文件，以及其他任何可被 Agent 理解并转化为结构化条目的本地文本内容。

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>knowledge-flow · 本地文件入库</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 24px; }
.page-header { text-align: center; margin-bottom: 12px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }

/* ── 主体 ── */
.main {
  display: flex; align-items: center; gap: 0;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  background: #f8fafc; padding: 18px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
  position: relative;
}
#svg-arrows {
  position: absolute; top: 0; left: 0;
  width: 100%; height: 100%;
  pointer-events: none; z-index: 1;
}

/* ── 文件卡片列 ── */
.cards-col { display: flex; flex-direction: column; gap: 8px; flex: 0 0 380px; z-index: 2; }

.fc {
  background: #fff; border-radius: 8px; border: 1.5px solid #e2e8f0;
  padding: 9px 12px; display: flex; align-items: center; gap: 10px;
  transition: box-shadow .15s;
}
.fc:hover { box-shadow: 0 2px 10px rgba(0,0,0,.08); }
.fc.fc-more { border-style: dashed; background: #f8fafc; }

.fc-icon { font-size: 16px; flex-shrink: 0; }
.fc-body { flex: 1; min-width: 0; }
.fc-name { font-size: 11.5px; font-weight: 700; color: #1e293b; }
.fc-desc { font-size: 10px; color: #94a3b8; margin-top: 1px; line-height: 1.4; }
.fc-fmt  {
  flex-shrink: 0; font-size: 9.5px; font-weight: 700;
  padding: 2px 7px; border-radius: 6px;
  font-family: 'SF Mono','Fira Code',monospace;
}

/* 格式 tag 颜色 */
.fmt-md   { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
.fmt-txt  { background: #f5f3ff; color: #6d28d9; border: 1px solid #ddd6fe; }
.fmt-more { background: #f1f5f9; color: #64748b; border: 1px dashed #cbd5e1; }

/* ── 知识库目标 ── */
.kb-box {
  flex: 0 0 130px; margin-left: auto; z-index: 2;
  border: 2px solid #059669; border-radius: 10px;
  background: #ecfdf5; padding: 20px 12px;
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  text-align: center;
}
.kb-icon { font-size: 24px; }
.kb-name { font-size: 12px; font-weight: 700; color: #065f46; line-height: 1.4; }

/* ── 知识库内容说明条 ── */
.kb-detail {
  margin-top: 10px;
  border: 1.5px solid #e2e8f0; border-radius: 8px;
  background: #f8fafc; padding: 10px 14px;
  display: flex; gap: 18px; align-items: flex-start;
}
.kd-label {
  font-size: 9.5px; font-weight: 700; letter-spacing: .6px;
  text-transform: uppercase; color: #94a3b8;
  flex-shrink: 0; margin-top: 1px; width: 72px;
}
.kd-body { flex: 1; display: flex; gap: 6px; flex-wrap: wrap; }
.kd-chip {
  font-size: 10.5px; padding: 2px 9px; border-radius: 6px;
  border: 1.5px solid #e2e8f0; background: #fff; color: #334155;
}

/* ── 注释 ── */
.note { font-size: 10.5px; color: #94a3b8; margin-top: 10px; line-height: 1.6; }
.note strong { color: #64748b; }
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>knowledge-flow · 本地文件入库</h1>
    <p>多种本地文件形式 · 统一写入知识库目录</p>
  </div>

  <div class="main" id="main-wrap">
    <svg id="svg-arrows" xmlns="http://www.w3.org/2000/svg"></svg>

    <div class="cards-col">

      <div class="fc" id="fc-code">
        <span class="fc-icon">💻</span>
        <div class="fc-body">
          <div class="fc-name">代码库知识</div>
          <div class="fc-desc">系统架构、核心流程、服务依赖关系</div>
        </div>
        <span class="fc-fmt fmt-md">.md</span>
      </div>

      <div class="fc" id="fc-session">
        <span class="fc-icon">🤖</span>
        <div class="fc-body">
          <div class="fc-name">会话沉淀</div>
          <div class="fc-desc">排查经验、决策依据、踩坑记录</div>
        </div>
        <span class="fc-fmt fmt-md">.md</span>
      </div>

      <div class="fc" id="fc-config">
        <span class="fc-icon">🗂️</span>
        <div class="fc-body">
          <div class="fc-name">配置 & 数据表索引</div>
          <div class="fc-desc">配置依赖关系、数据血缘（XT 任务产出）</div>
        </div>
        <span class="fc-fmt fmt-txt">.txt</span>
      </div>

      <div class="fc" id="fc-tt">
        <span class="fc-icon">🎫</span>
        <div class="fc-body">
          <div class="fc-name">工单经验</div>
          <div class="fc-desc">历史 TT 工单整理后的问题类型与解决路径</div>
        </div>
        <span class="fc-fmt fmt-md">.md</span>
      </div>

      <div class="fc fc-more" id="fc-more">
        <span class="fc-icon">📄</span>
        <div class="fc-body">
          <div class="fc-name" style="color:#64748b">其他本地文档</div>
          <div class="fc-desc">任何可被 Agent 理解并转化为结构化条目的文本内容</div>
        </div>
        <span class="fc-fmt fmt-more">…</span>
      </div>

    </div>

    <div class="kb-box" id="kb-box">
      <span class="kb-icon">📚</span>
      <span class="kb-name">本地<br>知识库</span>
    </div>
  </div>

  <div class="kb-detail">
    <span class="kd-label">知识库内存储</span>
    <div class="kd-body">
      <span class="kd-chip">data_structure.md 条目索引</span>
      <span class="kd-chip">本地 .md 全文文件</span>
      <span class="kd-chip">.txt 索引文件</span>
      <span class="kd-chip">keyword_index.json 快查索引</span>
    </div>
  </div>

  <div class="note">⚡ 本地文件入库是学城文档入库之外的另一条渠道。与学城文档（存链接 + 摘要）不同，本地文件会将<strong>完整内容</strong>存储到知识库目录，检索命中时直接 Read 本地文件，无需额外的工具调用请求。</div>

</div>

<script>
(function () {
  function rect(id) {
    const el = document.getElementById(id);
    const wrap = document.getElementById('main-wrap');
    if (!el || !wrap) return null;
    const er = el.getBoundingClientRect();
    const wr = wrap.getBoundingClientRect();
    return { r: er.right - wr.left, cy: (er.top + er.bottom) / 2 - wr.top };
  }

  function draw() {
    const svg = document.getElementById('svg-arrows');
    const wrap = document.getElementById('main-wrap');
    svg.innerHTML = '';
    svg.setAttribute('width', wrap.offsetWidth);
    svg.setAttribute('height', wrap.offsetHeight);

    const kb = document.getElementById('kb-box');
    const wr = wrap.getBoundingClientRect();
    const kr = kb.getBoundingClientRect();
    const kbX = kr.left - wr.left;
    const kbCY = (kr.top + kr.bottom) / 2 - wr.top;

    const cards = ['fc-code','fc-session','fc-config','fc-tt','fc-more'];
    cards.forEach((id, i) => {
      const r = rect(id);
      if (!r) return;
      const x1 = r.r + 2, y1 = r.cy;
      const x2 = kbX - 2, y2 = kbCY;
      const mx = (x1 + x2) / 2;
      const isDashed = id === 'fc-more';
      const opacity = id === 'fc-more' ? '0.4' : '0.65';

      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', `M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}`);
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke', '#94a3b8');
      path.setAttribute('stroke-width', '1.5');
      path.setAttribute('opacity', opacity);
      if (isDashed) path.setAttribute('stroke-dasharray', '5 3');
      svg.appendChild(path);

      if (!isDashed) {
        const AH = 6, AW = 3;
        const poly = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        poly.setAttribute('points', `${x2},${y2} ${x2-AH},${y2-AW} ${x2-AH},${y2+AW}`);
        poly.setAttribute('fill', '#94a3b8');
        poly.setAttribute('opacity', opacity);
        svg.appendChild(poly);
      }
    });
  }

  window.addEventListener('load', draw);
  window.addEventListener('resize', draw);
})();
</script>
</body>
</html>


### 7. 知识管理

#### 7.1 结构治理

- **目录结构优化：**知识库的目录结构在建立初期往往是合理的，但随着文档持续写入，失衡几乎是必然的结果。某个方向的文档越积越多，原本清晰的分类开始显得混杂；另一些目录因为业务调整变得空旷；有时两个独立建立的目录在内容上出现大量重叠，检索时需要分别进入才能确认没有遗漏。这类问题如果不定期处理，知识库的可导航性会随规模增长而悄悄下滑。
> **📂 折叠块（默认折叠）：支持的操作类型**
>
> | 操作 | 适用场景 |
> | --- | --- |
> | rename_category | 目录名称与实际收录内容存在偏差 |
> | split_category | 单个目录文档过于密集，主题混杂 |
> | merge_categories | 多个目录内容高度重叠，造成冗余 |
> | move_category | 某个目录放错了层级或父目录 |
> | create_category | 某类内容缺少对应的目录容器 |
> | move_document | 单篇文档归错了目录 |
- **容器节点优化：**容器节点的描述质量是检索效果的隐性前提。Agent 在树状导航时，读取的正是各层容器节点的描述来判断“问题该往哪个方向深入” —— 如果一个中间目录的描述缺失、过短、或者停留在“待补充”之类的占位文字，Agent 在这里就失去了判断依据，只能盲目进入每个子目录逐一探索，导航效率大幅下降。
> **📂 折叠块（默认折叠）：描述质量检测规则**
>
> | 规则 | 判定标准 |
> | --- | --- |
> | 描述缺失 | 无任何描述文字 |
> | 描述过短 | 字符数低于 100 字 |
> | 模板占位文字 | 包含"待补充"等占位词 |
> | 子目录列表不一致 | 描述中提及的目录名与实际子目录不符 |

（点击橙/黄标签查看详情）

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>knowledge-flow · 知识库结构治理</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 24px; }

.page-header { text-align: center; margin-bottom: 10px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }

/* ── 图例条 ── */
.legend-bar {
  display: flex; align-items: center; gap: 16px;
  background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 8px;
  padding: 8px 14px; margin-bottom: 10px; flex-wrap: wrap;
}
.legend-bar .hint { font-size: 11px; color: #94a3b8; margin-left: auto; }
.leg { display: flex; align-items: center; gap: 6px; font-size: 11.5px; font-weight: 600; }
.leg-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.leg-o { background: #f97316; }
.leg-y { background: #ca8a04; }
.leg-g { background: #94a3b8; }

/* ── 主体双栏 ── */
.explorer {
  display: flex; gap: 0;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  overflow: hidden; min-height: 420px;
  box-shadow: 0 2px 12px rgba(0,0,0,.06);
}

/* ── 左侧文件树 ── */
.tree-panel {
  width: 262px; flex-shrink: 0;
  background: #f8fafc; border-right: 1.5px solid #e2e8f0;
  display: flex; flex-direction: column;
}
.tree-title {
  padding: 9px 12px 8px; font-size: 10px; font-weight: 700;
  letter-spacing: 1px; text-transform: uppercase; color: #94a3b8;
  border-bottom: 1px solid #e2e8f0; flex-shrink: 0;
}
.tree-scroll { flex: 1; overflow-y: auto; padding: 6px 0 12px; }

.ti {
  display: flex; align-items: center; gap: 5px;
  padding: 4px 10px; user-select: none;
  white-space: nowrap; overflow: hidden;
  transition: background .12s;
}
.ti.clickable { cursor: pointer; }
.ti.clickable:hover { background: #e8ecf0; }
.ti.selected { background: #dbeafe; }
.ti.selected .iname { color: #1d4ed8 !important; font-weight: 700; }

.toggle { width: 13px; font-size: 9px; color: #94a3b8; transition: transform .15s; flex-shrink: 0; text-align: center; }
.toggle.open { transform: rotate(90deg); }
.toggle.empty { visibility: hidden; }
.iicon { flex-shrink: 0; font-size: 12px; }
.iname { font-size: 12px; color: #334155; overflow: hidden; text-overflow: ellipsis; }
.iname.dir { font-weight: 500; color: #1e293b; }

/* 问题标签 */
.prob-tag {
  flex-shrink: 0; font-size: 9px; font-weight: 700;
  padding: 1px 6px; border-radius: 8px; margin-left: 4px;
  cursor: pointer;
}
.pt-o { background: #fed7aa; color: #c2410c; }
.pt-y { background: #fef08a; color: #92400e; }

.tree-children { overflow: hidden; }

/* ── 右侧内容面板 ── */
.content-panel {
  flex: 1; display: flex; flex-direction: column; min-width: 0;
}
.cp-header {
  padding: 10px 14px 9px; border-bottom: 1.5px solid #e2e8f0;
  display: flex; align-items: center; gap: 8px; flex-shrink: 0;
}
.cp-title { font-size: 13px; font-weight: 700; color: #0f172a; flex: 1; }
.feat-badge {
  font-size: 9.5px; font-weight: 700; padding: 2px 8px;
  border-radius: 10px; flex-shrink: 0;
}
.fb-o { background: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; }
.fb-y { background: #fefce8; color: #92400e; border: 1px solid #fef08a; }

.cp-body { flex: 1; overflow-y: auto; padding: 14px 16px; font-size: 12px; line-height: 1.8; }

/* 右侧内容组件 */
.rule-badge {
  display: inline-block; font-size: 10px; font-weight: 700;
  padding: 2px 9px; border-radius: 10px; margin-bottom: 8px;
}
.rb-o { background: #fff7ed; color: #c2410c; border: 1px solid #fdba74; }
.rb-y { background: #fefce8; color: #92400e; border: 1px solid #fde047; }

.prob-desc { color: #475569; margin-bottom: 12px; }

.compare { display: flex; gap: 10px; margin-top: 4px; }
.compare-box { flex: 1; border-radius: 7px; padding: 10px 12px; }
.cb-before { background: #fff5f5; border: 1.5px solid #fca5a5; }
.cb-after  { background: #f0fdf4; border: 1.5px solid #86efac; }
.cb-label  { font-size: 9px; font-weight: 700; letter-spacing: .8px; text-transform: uppercase; margin-bottom: 5px; }
.cbl-red   { color: #dc2626; }
.cbl-grn   { color: #16a34a; }
.cb-content { font-size: 11.5px; color: #1e293b; line-height: 1.6; }
.cb-content code { background: rgba(0,0,0,.06); padding: 1px 4px; border-radius: 3px; font-size: 10.5px; }

.op-chip {
  display: inline-flex; align-items: center; gap: 5px;
  background: #fff7ed; border: 1.5px solid #fdba74;
  border-radius: 6px; padding: 5px 10px; margin-top: 8px;
  font-size: 11px; font-weight: 600; color: #c2410c;
}

/* 默认空状态 */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; height: 100%; color: #94a3b8; gap: 10px;
  padding: 20px;
}
.empty-state .icon { font-size: 30px; }
.empty-state p { font-size: 12px; text-align: center; line-height: 1.7; max-width: 280px; }
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>knowledge-flow · 知识库结构治理</h1>
    <p>点击树中的问题标签，查看对应的问题定义与修复操作</p>
  </div>

  <div class="legend-bar">
    <div class="leg"><span class="leg-dot leg-o"></span>结构性问题 → 目录结构优化处理</div>
    <div class="leg"><span class="leg-dot leg-y"></span>描述质量问题 → 容器节点优化处理</div>
    <div class="leg"><span class="leg-dot leg-g"></span>正常节点</div>
    <span class="hint">← 点击橙/黄标签查看详情</span>
  </div>

  <div class="explorer">
    <div class="tree-panel">
      <div class="tree-title">知识库目录树（示例）</div>
      <div class="tree-scroll" id="tree"></div>
    </div>
    <div class="content-panel" id="cp">
      <div class="cp-header" id="cp-header" style="display:none">
        <div class="cp-title" id="cp-title"></div>
        <span class="feat-badge" id="cp-badge"></span>
      </div>
      <div class="cp-body" id="cp-body">
        <div class="empty-state">
          <span class="icon">🔍</span>
          <p>这棵树上有 <strong>3 个结构性问题</strong>（橙色）和 <strong>4 个描述质量问题</strong>（黄色）。<br>点击任意标签，查看问题定义和修复方式。</p>
        </div>
      </div>
    </div>
  </div>

</div>

<script>
// ── 树形数据 ──
// prob: {id, type:'struct'|'node'}
const TREE = [
  { id:'root', name:'knowledge/', dir:true, open:true, depth:0, children:[
    { id:'sys',  name:'系统设计/', dir:true, open:true, depth:1,
      probs:[{id:'p-rename',type:'struct',label:'命名偏差'},{id:'p-sys-desc',type:'node',label:'描述缺失'}],
      children:[
        { id:'svc', name:'服务架构/', dir:true, open:false, depth:2, children:[
          { id:'svc-1', name:'data_structure.md', depth:3 },
        ]},
        { id:'dep', name:'部署文档/', dir:true, open:false, depth:2, children:[
          { id:'dep-1', name:'data_structure.md', depth:3 },
        ]},
      ]
    },
    { id:'exp',  name:'实验记录/', dir:true, open:true, depth:1,
      probs:[{id:'p-exp-desc',type:'node',label:'描述过短'}],
      children:[
        { id:'online', name:'在线实验/', dir:true, open:false, depth:2,
          probs:[{id:'p-split',type:'struct',label:'文档过密'}],
          children:[
            { id:'online-1', name:'data_structure.md', depth:3 },
          ]
        },
        { id:'offline', name:'离线实验/', dir:true, open:false, depth:2, children:[
          { id:'offline-1', name:'data_structure.md', depth:3 },
        ]},
      ]
    },
    { id:'policy', name:'策略文档/', dir:true, open:true, depth:1,
      probs:[{id:'p-policy-desc',type:'node',label:'模板文字'}],
      children:[
        { id:'price1', name:'价格策略/', dir:true, open:false, depth:2,
          probs:[{id:'p-merge',type:'struct',label:'目录重叠'}],
          children:[
            { id:'price1-1', name:'data_structure.md', depth:3 },
          ]
        },
        { id:'price2', name:'定价逻辑/', dir:true, open:false, depth:2,
          probs:[{id:'p-merge2',type:'struct',label:'目录重叠',ref:'p-merge'}],
          children:[
            { id:'price2-1', name:'data_structure.md', depth:3 },
          ]
        },
      ]
    },
    { id:'trouble', name:'排查手册/', dir:true, open:false, depth:1,
      probs:[{id:'p-mismatch',type:'node',label:'子目录不符'}],
      children:[
        { id:'faq', name:'常见问题/', dir:true, open:false, depth:2, children:[
          { id:'faq-1', name:'data_structure.md', depth:3 },
        ]},
        { id:'flow', name:'处理流程/', dir:true, open:false, depth:2, children:[
          { id:'flow-1', name:'data_structure.md', depth:3 },
        ]},
      ]
    },
  ]}
];

// ── 右侧内容数据 ──
const DETAILS = {
  'p-rename': {
    type: 'struct',
    title: '目录命名与实际内容偏差',
    badge: '目录结构优化', badgeClass: 'fb-o',
    ruleLabel: '操作：rename_category', ruleClass: 'rb-o',
    desc: '"系统设计"这个名称暗示里面可能有需求分析、架构方案、详细设计等多种类型的文档。但实际上这个目录下只收录了服务架构相关内容，导致 Agent 导航时可能误判此处有更广泛的内容，浪费导航步骤。',
    beforeLabel: '问题现状', afterLabel: '优化结果',
    before: '系统设计/\n├── 服务架构/\n└── 部署文档/',
    after: '服务架构/         ← 重命名\n├── 服务架构/\n└── 部署文档/',
  },
  'p-split': {
    type: 'struct',
    title: '单个目录文档过于密集',
    badge: '目录结构优化', badgeClass: 'fb-o',
    ruleLabel: '操作：split_category', ruleClass: 'rb-o',
    desc: '"在线实验"目录下积累了 12 篇文档，混杂了 A/B 实验、灰度发布、流量分配三个不同主题。Agent 检索时需要逐一翻阅大量文档才能定位目标，命中精度下降。',
    beforeLabel: '问题现状', afterLabel: '优化结果',
    before: '在线实验/  （12 篇文档）\n├── AB实验方案-v1.md\n├── AB实验方案-v2.md\n├── 灰度发布规范.md\n├── 灰度发布复盘.md\n├── 流量分配策略.md\n└── ... (7 篇)',
    after: 'AB实验/    （4 篇）\n灰度发布/  （4 篇）\n流量分配/  （4 篇）',
  },
  'p-merge': {
    type: 'struct',
    title: '两个目录在内容上高度重叠',
    badge: '目录结构优化', badgeClass: 'fb-o',
    ruleLabel: '操作：merge_categories', ruleClass: 'rb-o',
    desc: '"价格策略"和"定价逻辑"在实际内容上高度重叠，都是价格相关的设计文档。Agent 检索价格问题时需要分别进两个目录查找，检索效率低，也容易遗漏。',
    beforeLabel: '问题现状', afterLabel: '优化结果',
    before: '策略文档/\n├── 价格策略/  （5 篇）\n└── 定价逻辑/  （3 篇）',
    after: '策略文档/\n└── 价格与定价/  （8 篇）  ← 合并',
  },
  'p-merge2': null,  // 指向 p-merge，在 JS 里处理
  'p-sys-desc': {
    type: 'node',
    title: '容器节点描述完全缺失',
    badge: '容器节点优化', badgeClass: 'fb-y',
    ruleLabel: '规则一：描述缺失', ruleClass: 'rb-y',
    desc: '"服务架构"容器节点的 data_structure.md 中没有任何描述文字。Agent 导航到这里时无法判断子目录各自的内容边界，只能逐一进入每个子目录探索，大幅增加导航步骤。',
    beforeLabel: '优化前（无描述）', afterLabel: '优化后（100+ 字）',
    before: '### 服务架构/\n（无内容）\n\n### 部署文档/\n（无内容）',
    after: '### 服务架构/\n收录服务拓扑设计和模块间调用关系文档，\n适合排查服务依赖或了解整体架构时检索。\n\n### 部署文档/\n收录各环境的部署规范和上线流程，\n适合需要了解发布步骤或排查环境配置时检索。',
  },
  'p-exp-desc': {
    type: 'node',
    title: '容器节点描述过短，信息不足',
    badge: '容器节点优化', badgeClass: 'fb-y',
    ruleLabel: '规则二：描述不足 100 字', ruleClass: 'rb-y',
    desc: '"实验记录"节点的描述只有 8 个字——"存放实验相关内容"，无法区分"在线实验"和"离线实验"各自的范围和差异。Agent 无法仅凭此描述判断问题该往哪个子目录走。',
    beforeLabel: '优化前（8 字）', afterLabel: '优化后（100+ 字）',
    before: '### 在线实验/\n存放实验相关内容。\n\n### 离线实验/\n存放实验相关内容。',
    after: '### 在线实验/\n记录线上 A/B 实验方案、灰度发布规范和流量\n分配策略，适合规划新实验或回溯历史实验配置。\n\n### 离线实验/\n记录离线评测集构建方案和指标对比报告，\n适合验证模型或策略效果时检索。',
  },
  'p-policy-desc': {
    type: 'node',
    title: '描述使用了模板占位文字',
    badge: '容器节点优化', badgeClass: 'fb-y',
    ruleLabel: '规则三：模板占位文字', ruleClass: 'rb-y',
    desc: '"策略文档"节点的描述是"（待补充）"，这是入库时的默认占位文字，从未被替换为真实内容。Agent 读到这里得不到任何有效信息，等同于描述缺失。',
    beforeLabel: '优化前（占位文字）', afterLabel: '优化后（真实描述）',
    before: '### 价格与定价/\n（待补充）',
    after: '### 价格与定价/\n收录价格策略设计和定价逻辑相关文档，包含\n不同场景下的定价方案、价格计算规则和历史\n策略调整记录。适合定价方案设计或价格问题\n排查时检索。',
  },
  'p-mismatch': {
    type: 'node',
    title: '描述与实际子目录列表不一致',
    badge: '容器节点优化', badgeClass: 'fb-y',
    ruleLabel: '规则四：子目录列表不一致', ruleClass: 'rb-y',
    desc: '"排查手册"节点的描述中提到了"FAQ"，但实际子目录是"常见问题"和"处理流程"，两者命名不一致。Agent 在语义上可能将"FAQ"与这两个目录产生偏差，导航偏离。',
    beforeLabel: '优化前（子目录不符）', afterLabel: '优化后（精确描述）',
    before: '### 排查手册/\n本节点包含 FAQ 快速查找和问题处理流程\n两个部分，适合遇到问题时参考。\n\n↑ 但实际子目录是：\n  常见问题/\n  处理流程/',
    after: '### 常见问题/\n整理高频问题的定位方法和根因分析，\n适合遇到已知问题时快速参考。\n\n### 处理流程/\n提供标准化的逐步处理 SOP，\n适合需要规范操作步骤时检索。',
  },
};

let selectedProb = null;

// ── 渲染树 ──
function renderTree(nodes, container) {
  nodes.forEach(node => {
    const row = document.createElement('div');
    row.className = 'ti' + (node.dir ? '' : '');
    row.style.paddingLeft = (10 + node.depth * 14) + 'px';

    // toggle
    const tog = document.createElement('span');
    tog.className = 'toggle' + (node.dir && node.children?.length ? (node.open ? ' open' : '') : ' empty');
    tog.textContent = '▶';
    row.appendChild(tog);

    // icon
    const ico = document.createElement('span');
    ico.className = 'iicon';
    ico.textContent = node.dir ? (node.open ? '📂' : '📁') : '📄';
    row.appendChild(ico);

    // name
    const nm = document.createElement('span');
    nm.className = 'iname' + (node.dir ? ' dir' : '');
    nm.textContent = node.name;
    row.appendChild(nm);

    // problem tags
    if (node.probs) {
      node.probs.forEach(prob => {
        const tag = document.createElement('span');
        tag.className = 'prob-tag ' + (prob.type === 'struct' ? 'pt-o' : 'pt-y');
        tag.textContent = prob.label;
        tag.dataset.probId = prob.ref || prob.id;
        tag.addEventListener('click', e => {
          e.stopPropagation();
          showDetail(prob.ref || prob.id, tag);
        });
        row.appendChild(tag);
      });
    }

    // dir click: toggle
    if (node.dir && node.children?.length) {
      row.classList.add('clickable');
      row.addEventListener('click', () => {
        node.open = !node.open;
        tog.className = 'toggle' + (node.children.length ? (node.open ? ' open' : '') : ' empty');
        ico.textContent = node.open ? '📂' : '📁';
        const cw = document.getElementById('cw-' + node.id);
        if (cw) cw.style.display = node.open ? 'block' : 'none';
      });
    }

    container.appendChild(row);

    if (node.dir && node.children) {
      const cw = document.createElement('div');
      cw.className = 'tree-children';
      cw.id = 'cw-' + node.id;
      cw.style.display = node.open ? 'block' : 'none';
      container.appendChild(cw);
      renderTree(node.children, cw);
    }
  });
}

function showDetail(probId, tagEl) {
  const d = DETAILS[probId];
  if (!d) return;

  // selected state on tag
  document.querySelectorAll('.prob-tag').forEach(t => {
    t.style.outline = '';
    t.style.boxShadow = '';
  });
  if (tagEl) {
    tagEl.style.outline = '2px solid ' + (d.type === 'struct' ? '#f97316' : '#ca8a04');
    tagEl.style.boxShadow = '0 0 0 3px ' + (d.type === 'struct' ? '#fff7ed' : '#fefce8');
  }

  document.getElementById('cp-header').style.display = 'flex';
  document.getElementById('cp-title').textContent = d.title;
  const badge = document.getElementById('cp-badge');
  badge.textContent = d.badge;
  badge.className = 'feat-badge ' + d.badgeClass;

  document.getElementById('cp-body').innerHTML = `
    <span class="rule-badge ${d.ruleClass}">${d.ruleLabel}</span>
    <div class="prob-desc">${d.desc}</div>
    <div class="compare">
      <div class="compare-box cb-before">
        <div class="cb-label cbl-red">${d.beforeLabel}</div>
        <pre class="cb-content" style="font-family:'SF Mono','Fira Code',monospace;font-size:10.5px;white-space:pre;line-height:1.6">${d.before}</pre>
      </div>
      <div class="compare-box cb-after">
        <div class="cb-label cbl-grn">${d.afterLabel}</div>
        <pre class="cb-content" style="font-family:'SF Mono','Fira Code',monospace;font-size:10.5px;white-space:pre;line-height:1.6">${d.after}</pre>
      </div>
    </div>
  `;
}

// ── 初始化 ──
renderTree(TREE, document.getElementById('tree'));
</script>
</body>
</html>


#### 7.2 知识质量

- **知识更新：**知识库中存储的是学城文档的摘要和关键词，而非原文。当学城上的原始文档被修改后，知识库里对应的摘要不会自动跟进——两者之间会逐渐产生偏差。知识更新负责弥合这个差距。
扫描逻辑以 `baseline = max(updated_at, ingest_date)` 作为每条文档条目的时效基准，将 baseline 距今超过阈值（默认 30 天）的条目列为候选，逐条读取原始文档最新内容，判断是否有实质变更：有变更则重新生成摘要、纲要和关键词并写回；文档已被删除或无法访问则标记为失效，提示人工确认是否从知识库移除。

- **矛盾检测：**随着知识持续入库，同一个概念可能在不同目录下被描述了两次，且两处的说法存在出入。矛盾检测通过批量生成候选对，再由 Agent 逐对做语义审查，识别出“同一件事有两个不一致答案”的情况。
候选对的生成来自两个维度：**同目录配对 **—— 同一叶子目录下的所有文档条目两两组合，覆盖同一业务领域内的潜在重叠；**跨目录关键词交集 **—— 来自不同目录但关键词交集 ≥ 2 的条目对，覆盖跨领域的潜在重叠。两个维度取并集后去重，交由 Agent 进行语义判断，输出疑似矛盾的条目对及置信度，由人工决定保留哪个版本或合并为一条更完整的描述。该功能适合在知识库规模较大、或经历了多人协同入库后，作为一次性的质量审查使用。

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>knowledge-flow · 知识质量</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 24px; }

.page-header { text-align: center; margin-bottom: 12px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }

/* ── 双栏 ── */
.cols { display: flex; gap: 10px; align-items: stretch; }
.col  { flex: 1; display: flex; flex-direction: column; gap: 8px; min-width: 0; }

/* ── 功能面板 ── */
.panel {
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  overflow: hidden; flex: 1; display: flex; flex-direction: column;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.panel-header {
  padding: 10px 14px; border-bottom: 1.5px solid #e2e8f0;
  display: flex; align-items: center; gap: 8px;
}
.ph-icon  { font-size: 16px; flex-shrink: 0; }
.ph-title { font-size: 13px; font-weight: 700; color: #0f172a; flex: 1; }
.ph-badge {
  font-size: 9.5px; font-weight: 700; padding: 2px 8px;
  border-radius: 10px; flex-shrink: 0;
}
.pb-green { background: #d1fae5; color: #065f46; }
.pb-purple{ background: #ede9fe; color: #6d28d9; }

.panel-body { padding: 12px 14px; display: flex; flex-direction: column; gap: 10px; flex: 1; }

/* ── 小节标题 ── */
.sec-lbl {
  font-size: 9.5px; font-weight: 700; letter-spacing: .8px;
  text-transform: uppercase; color: #94a3b8; margin-bottom: 5px;
}

/* ── 知识更新：叶子节点扫描展示 ── */
.leaf-box {
  background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 8px;
  overflow: hidden;
}
.leaf-dir-header {
  padding: 5px 10px; background: #f1f5f9;
  border-bottom: 1px solid #e2e8f0;
  font-size: 10px; font-weight: 700; color: #475569;
  display: flex; align-items: center; gap: 5px;
}

.entry-row {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 10px; border-bottom: 1px solid #f1f5f9;
  transition: background .12s;
}
.entry-row:last-child { border-bottom: none; }
.entry-row.stale { background: #fff5f5; }
.entry-row.warn  { background: #fffbeb; }

.er-icon { font-size: 12px; flex-shrink: 0; }
.er-title { font-size: 11px; color: #334155; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.er-baseline { font-size: 10px; color: #94a3b8; flex-shrink: 0; white-space: nowrap; }

/* 天数条 */
.days-bar { width: 64px; flex-shrink: 0; }
.db-track { height: 5px; background: #e2e8f0; border-radius: 3px; overflow: hidden; position: relative; }
.db-fill  { height: 100%; border-radius: 3px; }
.db-label { font-size: 9.5px; font-weight: 700; text-align: right; margin-top: 2px; }

/* 阈值标注线 */
.threshold-note {
  display: flex; align-items: center; gap: 6px;
  padding: 4px 10px; background: #fef9c3;
  border-top: 1px dashed #fcd34d;
  font-size: 10px; color: #92400e; font-weight: 600;
}

/* 更新动作示意 */
.update-flow {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 10px; background: #f0fdf4;
  border: 1.5px solid #bbf7d0; border-radius: 8px;
  font-size: 11px;
}
.uf-step {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  flex: 1; text-align: center;
}
.uf-icon { font-size: 15px; }
.uf-text { font-size: 10px; color: #475569; line-height: 1.3; }
.uf-arrow { color: #86efac; font-size: 13px; flex-shrink: 0; }

/* ── 矛盾检测：候选对生成展示 ── */
.cand-path {
  background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 8px;
  padding: 9px 11px; display: flex; gap: 10px; align-items: center;
}
.cp-left { flex: 1; min-width: 0; }
.cp-tag {
  font-size: 9px; font-weight: 700; padding: 1px 7px;
  border-radius: 8px; display: inline-block; margin-bottom: 5px;
}
.ct-dim1 { background: #ede9fe; color: #6d28d9; }
.ct-dim2 { background: #dbeafe; color: #1e40af; }

.mini-dir {
  display: flex; flex-direction: column; gap: 3px;
}
.mini-entry {
  display: flex; align-items: center; gap: 5px;
  font-size: 10.5px; color: #334155;
  padding: 3px 7px; background: #fff;
  border: 1px solid #e2e8f0; border-radius: 5px;
}
.me-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }

.kw-tags { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 4px; }
.kw-tag  { font-size: 9.5px; padding: 1px 6px; border-radius: 4px; }
.kw-shared { background: #dbeafe; color: #1e40af; font-weight: 700; }
.kw-own    { background: #f1f5f9; color: #64748b; }

.cp-arrow { color: #cbd5e1; font-size: 18px; flex-shrink: 0; }
.cp-result {
  flex-shrink: 0; display: flex; flex-direction: column;
  align-items: center; gap: 3px;
}
.pair-badge {
  font-size: 9px; font-weight: 700; padding: 2px 7px;
  border-radius: 8px; background: #fef3c7; color: #92400e;
  white-space: nowrap;
}

/* 疑似矛盾卡 */
.contradiction-card {
  border: 1.5px solid #ddd6fe; border-radius: 8px; overflow: hidden;
}
.cc-header {
  background: #faf5ff; padding: 5px 11px; border-bottom: 1px solid #ddd6fe;
  font-size: 10px; font-weight: 700; color: #7c3aed;
  display: flex; align-items: center; gap: 5px;
}
.cc-body { display: flex; }
.cc-side {
  flex: 1; padding: 9px 11px; font-size: 11px;
  display: flex; flex-direction: column; gap: 4px;
}
.cc-side + .cc-side { border-left: 1px solid #ede9fe; background: #faf5ff; }
.cs-src  { font-size: 9.5px; color: #94a3b8; }
.cs-desc { color: #334155; line-height: 1.5; }
.cs-conflict {
  font-size: 10.5px; font-weight: 700;
  padding: 2px 7px; border-radius: 5px; display: inline-block;
}
.cc-conflict-a { background: #fee2e2; color: #991b1b; }
.cc-conflict-b { background: #ede9fe; color: #6d28d9; }
.cc-divider {
  width: 28px; flex-shrink: 0; display: flex; align-items: center;
  justify-content: center; background: #faf5ff;
  font-size: 14px; color: #c4b5fd;
  border-left: 1px solid #ede9fe; border-right: 1px solid #ede9fe;
}
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>knowledge-flow · 知识质量</h1>
    <p>知识更新 &nbsp;·&nbsp; 矛盾检测</p>
  </div>

  <div class="cols">

    <!-- ══ 左列：知识更新 ══ -->
    <div class="col">
      <div class="panel">
        <div class="panel-header">
          <span class="ph-icon">🔄</span>
          <span class="ph-title">知识更新</span>
          <span class="ph-badge pb-green">定期巡检 · 学城文档</span>
        </div>
        <div class="panel-body">

          <div>
            <div class="sec-lbl">扫描：叶子节点 baseline 距今天数</div>
            <div class="leaf-box">
              <div class="leaf-dir-header">📁 某领域/子分类/data_structure.md</div>

              <!-- 新鲜 -->
              <div class="entry-row">
                <span class="er-icon">📄</span>
                <span class="er-title">架构设计方案 v2</span>
                <span class="er-baseline">baseline 2026-05-10</span>
                <div class="days-bar">
                  <div class="db-track"><div class="db-fill" style="width:18%;background:#22c55e"></div></div>
                  <div class="db-label" style="color:#16a34a">12 天</div>
                </div>
              </div>

              <!-- 临近阈值 -->
              <div class="entry-row warn">
                <span class="er-icon">📄</span>
                <span class="er-title">接口参数说明</span>
                <span class="er-baseline">baseline 2026-04-20</span>
                <div class="days-bar">
                  <div class="db-track"><div class="db-fill" style="width:60%;background:#f59e0b"></div></div>
                  <div class="db-label" style="color:#d97706">25 天</div>
                </div>
              </div>

              <!-- 过期 -->
              <div class="entry-row stale">
                <span class="er-icon">📄</span>
                <span class="er-title">部署流程规范</span>
                <span class="er-baseline">baseline 2026-03-01</span>
                <div class="days-bar">
                  <div class="db-track"><div class="db-fill" style="width:100%;background:#ef4444"></div></div>
                  <div class="db-label" style="color:#dc2626">92 天 ↑</div>
                </div>
              </div>

              <!-- 过期 -->
              <div class="entry-row stale">
                <span class="er-icon">📄</span>
                <span class="er-title">核心配置项说明</span>
                <span class="er-baseline">baseline 2026-02-15</span>
                <div class="days-bar">
                  <div class="db-track"><div class="db-fill" style="width:100%;background:#ef4444"></div></div>
                  <div class="db-label" style="color:#dc2626">113 天 ↑</div>
                </div>
              </div>

              <div class="threshold-note">⚡ 阈值 30 天 · 超出的 2 条进入候选列表</div>
            </div>
          </div>

          <div>
            <div class="sec-lbl">验证 & 更新动作</div>
            <div class="update-flow">
              <div class="uf-step">
                <span class="uf-icon">🌐</span>
                <span class="uf-text">citadel<br>读取原文</span>
              </div>
              <span class="uf-arrow">›</span>
              <div class="uf-step">
                <span class="uf-icon">🔍</span>
                <span class="uf-text">对比现有<br>摘要</span>
              </div>
              <span class="uf-arrow">›</span>
              <div class="uf-step">
                <span class="uf-icon">✏️</span>
                <span class="uf-text">有变更<br>重写摘要</span>
              </div>
              <span class="uf-arrow">›</span>
              <div class="uf-step">
                <span class="uf-icon">🗂️</span>
                <span class="uf-text">文档不存在<br>标记失效</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- ══ 右列：矛盾检测 ══ -->
    <div class="col">
      <div class="panel">
        <div class="panel-header">
          <span class="ph-icon">🔍</span>
          <span class="ph-title">矛盾检测</span>
          <span class="ph-badge pb-purple">定期扫描 · 本地文件</span>
        </div>
        <div class="panel-body">

          <div>
            <div class="sec-lbl">候选对生成：两个维度</div>

            <!-- 维度一：同目录 -->
            <div class="cand-path" style="margin-bottom:7px">
              <div class="cp-left">
                <span class="cp-tag ct-dim1">维度一：同目录配对</span>
                <div class="mini-dir">
                  <div class="mini-entry"><span class="me-dot" style="background:#7c3aed"></span>某配置项的作用说明</div>
                  <div class="mini-entry"><span class="me-dot" style="background:#7c3aed"></span>某配置项的默认值</div>
                  <div class="mini-entry"><span class="me-dot" style="background:#7c3aed"></span>某配置项的历史变更</div>
                </div>
              </div>
              <span class="cp-arrow">→</span>
              <div class="cp-result">
                <span class="pair-badge">C(3,2) = 3 对</span>
                <span style="font-size:9.5px;color:#94a3b8;margin-top:2px">全部配对</span>
              </div>
            </div>

            <!-- 维度二：跨目录关键词 -->
            <div class="cand-path">
              <div class="cp-left">
                <span class="cp-tag ct-dim2">维度二：跨目录关键词交集 ≥ 2</span>
                <div style="display:flex;gap:6px;align-items:flex-start">
                  <div style="flex:1">
                    <div class="mini-entry" style="margin-bottom:4px"><span class="me-dot" style="background:#3b82f6"></span>领域A / 子分类1</div>
                    <div class="kw-tags">
                      <span class="kw-tag kw-shared">超时配置</span>
                      <span class="kw-tag kw-shared">重试策略</span>
                      <span class="kw-tag kw-own">服务治理</span>
                    </div>
                  </div>
                  <div style="flex:1">
                    <div class="mini-entry" style="margin-bottom:4px"><span class="me-dot" style="background:#06b6d4"></span>领域B / 子分类3</div>
                    <div class="kw-tags">
                      <span class="kw-tag kw-shared">超时配置</span>
                      <span class="kw-tag kw-shared">重试策略</span>
                      <span class="kw-tag kw-own">链路追踪</span>
                    </div>
                  </div>
                </div>
              </div>
              <span class="cp-arrow">→</span>
              <div class="cp-result">
                <span class="pair-badge">交集 = 2</span>
                <span style="font-size:9.5px;color:#94a3b8;margin-top:2px">进入候选</span>
              </div>
            </div>
          </div>

          <div>
            <div class="sec-lbl">Agent 语义审查：疑似矛盾示例</div>
            <div class="contradiction-card">
              <div class="cc-header">⚠️ 疑似矛盾 · 同目录配对触发</div>
              <div class="cc-body">
                <div class="cc-side">
                  <span class="cs-src">领域A / 子分类1 / 文档甲</span>
                  <span class="cs-desc">描述了某组件的默认行为</span>
                  <span class="cs-conflict cc-conflict-a">默认超时时间：30s</span>
                </div>
                <div class="cc-divider">≠</div>
                <div class="cc-side">
                  <span class="cs-src">领域A / 子分类1 / 文档乙</span>
                  <span class="cs-desc">同样描述了该组件的配置</span>
                  <span class="cs-conflict cc-conflict-b">默认超时时间：60s</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

  </div>
</div>
</body>
</html>


- **评测集构建 & 评测：**评测集构建和知识库评测目标是构成一条知识质量度量的流水线，解决“知识库检索效果如何、哪里还不够”这个问题。
评测集构建从知识库的叶子节点出发，选取部分收录文档（默认为50%）自动生成一道测试题：提炼一个自然语言提问（query），并标注期望命中的目录和文档作为正确答案。这份测试集可以随知识库内容的更新反复运行，充当持续检验检索质量的“标准卷”。我们也可以将真实场景下知识库接收的问题加入评测集中，并持续补充和完善。
知识库评测针对每道题计算两项独立指标：① Dir Hit 衡量关键词索引能否将 query 路由到正确目录；② Doc Hit 衡量 Agent 完成树状导航后能否最终命中目标文档。

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>knowledge-flow · 评测集构建 & 知识库评测</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 24px; }

.page-header { text-align: center; margin-bottom: 12px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }

.pipeline { display: flex; flex-direction: column; gap: 0; }

.stage {
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.stage-header {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px; border-bottom: 1.5px solid #e2e8f0;
}
.sh-num {
  width: 22px; height: 22px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 800; flex-shrink: 0;
}
.sh-title { font-size: 13px; font-weight: 700; color: #0f172a; flex: 1; }
.sh-badge {
  font-size: 9.5px; font-weight: 700; padding: 2px 8px;
  border-radius: 10px; flex-shrink: 0;
}
.stage-body { padding: 14px 16px; display: flex; gap: 14px; align-items: flex-start; }

.s1 { border-color: #bfdbfe; }
.s1 .stage-header { background: #eff6ff; }
.s1 .sh-num { background: #2563eb; color: #fff; }
.s1 .sh-badge { background: #dbeafe; color: #1e40af; }

.s2 { border-color: #c7d2fe; }
.s2 .stage-header { background: #eef2ff; }
.s2 .sh-num { background: #4f46e5; color: #fff; }
.s2 .sh-badge { background: #e0e7ff; color: #3730a3; }

.s3 { border-color: #bbf7d0; }
.s3 .stage-header { background: #ecfdf5; }
.s3 .sh-num { background: #059669; color: #fff; }
.s3 .sh-badge { background: #d1fae5; color: #065f46; }

.stage-arrow {
  display: flex; justify-content: center; align-items: center; height: 24px; position: relative;
}
.stage-arrow::before { content:''; position:absolute; left:50%; top:0; transform:translateX(-50%); width:2px; height:16px; background:#e2e8f0; }
.stage-arrow::after  { content:'▼'; position:absolute; bottom:0; left:50%; transform:translateX(-50%); font-size:10px; color:#cbd5e1; line-height:1; }

/* ── 共用 ── */
.sec-lbl { font-size:9.5px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; color:#94a3b8; margin-bottom:5px; }
.arrow-mid { flex:0 0 24px; display:flex; align-items:center; justify-content:center; color:#cbd5e1; font-size:16px; flex-shrink:0; }

/* ── Stage 1 ── */
.leaf-mini { flex:0 0 190px; background:#f8fafc; border:1.5px solid #e2e8f0; border-radius:8px; overflow:hidden; }
.lm-header { padding:5px 10px; background:#f1f5f9; border-bottom:1px solid #e2e8f0; font-size:10px; font-weight:700; color:#475569; }
.lm-entry  { padding:6px 10px; border-bottom:1px solid #f1f5f9; font-size:11px; color:#334155; }
.lm-entry:last-child { border-bottom:none; }
.lm-field  { font-size:10px; color:#94a3b8; margin-top:2px; }

.cases-jsonl { flex:1; display:flex; flex-direction:column; gap:6px; }
.jsonl-label { font-size:9px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; color:#94a3b8; margin-bottom:4px; }
.case-card { background:#f8fafc; border:1.5px solid #bfdbfe; border-radius:7px; padding:7px 10px; font-family:'SF Mono','Fira Code',monospace; font-size:10.5px; line-height:1.7; }
.cf-key { color:#6366f1; font-weight:700; }
.cf-dir { color:#2563eb; font-weight:600; }

/* ── Stage 2 ── */
.metric-cols { flex:1; display:flex; gap:10px; }
.metric-box {
  flex:1; border-radius:8px; border:1.5px solid; padding:10px 12px;
  display:flex; flex-direction:column; gap:8px;
}
.mb-blue   { border-color:#bfdbfe; background:#f8fbff; }
.mb-indigo { border-color:#c7d2fe; background:#f5f7ff; }

.mb-title { font-size:11.5px; font-weight:700; color:#0f172a; display:flex; align-items:center; gap:6px; }
.mb-threshold { font-size:10px; font-weight:700; padding:1px 7px; border-radius:8px; }
.thr-blue   { background:#dbeafe; color:#1e40af; }
.thr-indigo { background:#e0e7ff; color:#3730a3; }

.mb-desc { font-size:11px; color:#475569; line-height:1.65; }

.score-ex { display:flex; flex-direction:column; gap:5px; }
.se-row { display:flex; align-items:center; gap:6px; }
.se-query { font-size:10.5px; color:#334155; flex:1; background:#fff; border:1px solid #e2e8f0; border-radius:5px; padding:4px 7px; }
.kw-row   { display:flex; gap:3px; flex-wrap:wrap; }
.kw-hit   { font-size:9.5px; font-weight:700; padding:1px 5px; border-radius:4px; background:#dbeafe; color:#1e40af; }
.kw-miss  { font-size:9.5px; padding:1px 5px; border-radius:4px; background:#f1f5f9; color:#94a3b8; }
.result-pill { font-size:10.5px; font-weight:700; padding:2px 8px; border-radius:8px; flex-shrink:0; }
.rp-pass { background:#d1fae5; color:#065f46; }
.rp-fail { background:#fee2e2; color:#991b1b; }

.nav-mini { display:flex; flex-direction:column; gap:3px; }
.nav-row  { display:flex; align-items:center; gap:5px; font-size:10.5px; }
.nav-dir  { padding:3px 7px; border-radius:5px; border:1px solid #e2e8f0; background:#fff; color:#334155; }
.nav-arrow{ color:#cbd5e1; font-size:11px; }
.nav-hit  { padding:3px 7px; border-radius:5px; border:1.5px solid #86efac; background:#ecfdf5; color:#065f46; font-weight:600; }
.nav-miss { padding:3px 7px; border-radius:5px; border:1.5px solid #fca5a5; background:#fff5f5; color:#991b1b; font-weight:600; }

/* ── Stage 3 ── */
.report-wrap { flex:1; display:flex; flex-direction:column; gap:10px; }

/* 总体得分 */
.score-table { border:1.5px solid #e2e8f0; border-radius:8px; overflow:hidden; }
.st-row { display:flex; border-bottom:1px solid #f1f5f9; align-items:center; }
.st-row:last-child { border-bottom:none; }
.st-row.header { background:#f8fafc; font-size:10px; font-weight:700; color:#64748b; }
.stc { padding:7px 10px; font-size:11.5px; }
.stc-name { flex:0 0 90px; }
.stc-pass { flex:0 0 55px; text-align:center; }
.stc-fail { flex:0 0 55px; text-align:center; }
.stc-score{ flex:0 0 70px; text-align:center; font-weight:700; }
.stc-thr  { flex:1; display:flex; align-items:center; gap:6px; }
.thr-bar  { flex:1; height:6px; background:#e2e8f0; border-radius:3px; overflow:hidden; }
.thr-fill { height:100%; border-radius:3px; }
.thr-mark { font-size:10px; color:#94a3b8; flex-shrink:0; }

/* 诊断矩阵 */
.matrix-title { font-size:11px; font-weight:700; color:#334155; margin-bottom:6px; }
.matrix { display:grid; grid-template-columns:1fr 1fr; gap:6px; }
.mx-cell {
  border-radius:7px; padding:9px 11px; border:1.5px solid;
  display:flex; flex-direction:column; gap:3px;
}
.mx-pp { background:#ecfdf5; border-color:#86efac; }
.mx-fp { background:#fffbeb; border-color:#fde68a; }
.mx-pf { background:#eff6ff; border-color:#bfdbfe; }
.mx-ff { background:#fff5f5; border-color:#fca5a5; }

.mx-combo { font-size:10px; font-weight:700; }
.mx-pp .mx-combo { color:#065f46; }
.mx-fp .mx-combo { color:#92400e; }
.mx-pf .mx-combo { color:#1e40af; }
.mx-ff .mx-combo { color:#991b1b; }

.mx-meaning { font-size:10.5px; color:#475569; line-height:1.5; }
.mx-action  { font-size:10px; color:#64748b; font-style:italic; }

/* FAIL 样本 */
.fail-sample { background:#fff5f5; border:1.5px solid #fca5a5; border-radius:8px; padding:10px 12px; }
.fs-title { font-size:10px; font-weight:700; color:#991b1b; letter-spacing:.5px; text-transform:uppercase; margin-bottom:7px; }
.fs-row   { display:flex; gap:6px; font-size:11px; margin-bottom:4px; align-items:flex-start; }
.fs-key   { font-weight:700; color:#334155; flex-shrink:0; }
.fs-val   { color:#475569; }
.fs-kw-row{ display:flex; gap:4px; flex-wrap:wrap; }
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>knowledge-flow · 评测集构建 &amp; 知识库评测</h1>
    <p>从知识库自动生成测试用例 · 两项指标量化检索质量 · 诊断矩阵定位改进方向</p>
  </div>

  <div class="pipeline">

    <!-- ══ Stage 1 ══ -->
    <div class="stage s1">
      <div class="stage-header">
        <span class="sh-num">1</span>
        <span class="sh-title">评测集构建</span>
        <span class="sh-badge">扫描叶子节点 → cases.jsonl</span>
      </div>
      <div class="stage-body">
        <div class="leaf-mini">
          <div class="lm-header">📁 某领域/子分类/data_structure.md</div>
          <div class="lm-entry">某技术方案设计<div class="lm-field">关键词：方案设计, 架构决策, 技术选型</div></div>
          <div class="lm-entry">某接口规范说明<div class="lm-field">关键词：接口规范, 参数说明, 错误码</div></div>
          <div class="lm-entry">某异常处理指南<div class="lm-field">关键词：异常处理, 排查路径, 处理步骤</div></div>
        </div>
        <div class="arrow-mid">→</div>
        <div class="cases-jsonl">
          <div class="jsonl-label">cases.jsonl（输出格式）</div>
          <div class="case-card">
            <span class="cf-key">"id":</span> "case_001" &nbsp; <span class="cf-key">"query":</span> "某技术方案的架构决策依据是什么？"<br>
            <span class="cf-key">"must_hit_dir":</span> <span class="cf-dir">"某领域/子分类"</span> &nbsp; <span class="cf-key">"must_hit_doc":</span> "某技术方案设计"
          </div>
          <div class="case-card">
            <span class="cf-key">"id":</span> "case_002" &nbsp; <span class="cf-key">"query":</span> "接口错误码有哪些？"<br>
            <span class="cf-key">"must_hit_dir":</span> <span class="cf-dir">"某领域/子分类"</span> &nbsp; <span class="cf-key">"must_hit_doc":</span> "某接口规范说明"
          </div>
        </div>
      </div>
    </div>

    <div class="stage-arrow"></div>

    <!-- ══ Stage 2 ══ -->
    <div class="stage s2">
      <div class="stage-header">
        <span class="sh-num">2</span>
        <span class="sh-title">运行评测：两项独立指标</span>
        <span class="sh-badge">Dir Hit 85% · Doc Hit 90%</span>
      </div>
      <div class="stage-body">
        <div class="metric-cols">

          <!-- Dir Hit -->
          <div class="metric-box mb-blue">
            <div class="mb-title">Dir Hit <span class="mb-threshold thr-blue">阈值 ≥ 85%</span></div>
            <div class="mb-desc">keyword_index 能否将 query 路由到正确目录。对 query 做关键词子串匹配，命中的关键词数越多、得分越高，判断 must_hit_dir 是否出现在 top dirs 中。</div>
            <div class="sec-lbl" style="margin-top:2px">示例</div>
            <div class="score-ex">
              <div class="se-row">
                <div class="se-query">接口错误码有哪些？</div>
                <div class="kw-row"><span class="kw-hit">接口规范</span><span class="kw-hit">错误码</span><span class="kw-miss">参数说明</span></div>
                <span class="result-pill rp-pass">pass</span>
              </div>
              <div class="se-row">
                <div class="se-query">系统超时怎么处理？</div>
                <div class="kw-row"><span class="kw-miss">接口规范</span><span class="kw-miss">错误码</span><span class="kw-miss">异常处理</span></div>
                <span class="result-pill rp-fail">fail</span>
              </div>
            </div>
          </div>

          <!-- Doc Hit -->
          <div class="metric-box mb-indigo">
            <div class="mb-title">Doc Hit <span class="mb-threshold thr-indigo">阈值 ≥ 90%</span></div>
            <div class="mb-desc">Agent 做树状导航后能否命中 must_hit_doc。Dir Hit 通过 ≠ Doc Hit 通过——即使关键词索引路由到了正确目录，Agent 读取 data_structure.md 时若描述不够清晰，仍可能选错文档。</div>
            <div class="sec-lbl" style="margin-top:2px">示例</div>
            <div class="score-ex">
              <div class="se-row">
                <div class="se-query">接口错误码有哪些？</div>
                <div class="kw-row">
                  <span class="nav-dir" style="font-size:10px">子分类/</span>
                  <span class="nav-arrow" style="font-size:11px">›</span>
                  <span class="nav-hit" style="font-size:10px">✓ 某接口规范说明</span>
                </div>
                <span class="result-pill rp-pass">pass</span>
              </div>
              <div class="se-row">
                <div class="se-query">接口错误码有哪些？</div>
                <div class="kw-row">
                  <span class="nav-dir" style="font-size:10px">子分类/</span>
                  <span class="nav-arrow" style="font-size:11px">›</span>
                  <span class="nav-miss" style="font-size:10px">✗ 某技术方案设计</span>
                </div>
                <span class="result-pill rp-fail">fail</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <div class="stage-arrow"></div>

    <!-- ══ Stage 3 ══ -->
    <div class="stage s3">
      <div class="stage-header">
        <span class="sh-num">3</span>
        <span class="sh-title">评测报告</span>
        <span class="sh-badge">总体得分 · 诊断矩阵 · FAIL 明细</span>
      </div>
      <div class="stage-body">
        <div class="report-wrap">

          <!-- 总体得分 -->
          <div>
            <div class="sec-lbl">总体得分</div>
            <div class="score-table">
              <div class="st-row header">
                <div class="stc stc-name">指标</div>
                <div class="stc stc-pass">PASS</div>
                <div class="stc stc-fail">FAIL</div>
                <div class="stc stc-score">得分</div>
                <div class="stc stc-thr">vs 达标线</div>
              </div>
              <div class="st-row">
                <div class="stc stc-name" style="font-weight:700;color:#1e40af">Dir Hit</div>
                <div class="stc stc-pass" style="color:#16a34a;font-weight:700">28</div>
                <div class="stc stc-fail" style="color:#dc2626">7</div>
                <div class="stc stc-score" style="color:#2563eb">80%</div>
                <div class="stc stc-thr">
                  <div class="thr-bar"><div class="thr-fill" style="width:80%;background:#f59e0b"></div></div>
                  <span class="thr-mark">达标线 85% ⚠️</span>
                </div>
              </div>
              <div class="st-row">
                <div class="stc stc-name" style="font-weight:700;color:#3730a3">Doc Hit</div>
                <div class="stc stc-pass" style="color:#16a34a;font-weight:700">32</div>
                <div class="stc stc-fail" style="color:#dc2626">3</div>
                <div class="stc stc-score" style="color:#4f46e5">91%</div>
                <div class="stc stc-thr">
                  <div class="thr-bar"><div class="thr-fill" style="width:91%;background:#22c55e"></div></div>
                  <span class="thr-mark">达标线 90% ✓</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 诊断矩阵 -->
          <div>
            <div class="sec-lbl">诊断矩阵</div>
            <div class="matrix">
              <div class="mx-cell mx-pp">
                <div class="mx-combo">Dir PASS + Doc PASS</div>
                <div class="mx-meaning">完全健康，检索路径通畅</div>
                <div class="mx-action">→ 无需优化</div>
              </div>
              <div class="mx-cell mx-fp">
                <div class="mx-combo">Dir FAIL + Doc PASS</div>
                <div class="mx-meaning">关键词弱，但 Agent 语义导航兜住了</div>
                <div class="mx-action">→ 补充口语化关键词</div>
              </div>
              <div class="mx-cell mx-pf">
                <div class="mx-combo">Dir PASS + Doc FAIL</div>
                <div class="mx-meaning">关键词命中了正确目录，但导航走偏</div>
                <div class="mx-action">→ 检查叶子节点描述质量</div>
              </div>
              <div class="mx-cell mx-ff">
                <div class="mx-combo">Dir FAIL + Doc FAIL</div>
                <div class="mx-meaning">彻底未命中</div>
                <div class="mx-action">→ 同时检查关键词和目录描述</div>
              </div>
            </div>
          </div>


        </div>
      </div>
    </div>

  </div>
</div>
</body>
</html>


```
// FAIL 明细示例
以下是评测报告中一条 Dir FAIL + Doc FAIL 的明细输出：

### case_007   Dir FAIL + Doc FAIL

用户 Query    ：系统超时阈值怎么配置？
目标目录      ：某领域/子分类
目标文档      ：某接口配置说明
Dir Status    ：fail
Dir Routed    ：某领域/其他分类（keyword_index 无任何关键词命中目标目录）
Doc Status    ：fail
Doc Routed    ：未记录

命中关键词    ：无
未命中关键词  ：超时阈值、超时配置、timeout（建议补充到目标目录关键词）
```

#### 7.3 运营洞察

- **知识库可视化：**知识库可视化生成一张可交互的全景图，以目录树形式展示知识库的完整结构，同时标注每个分类目录的文档数量和覆盖深度，让使用者对知识库整体状况一目了然。
覆盖深度用四个级别表示：充分覆盖（≥6 篇）、一般覆盖（2-5 篇）、覆盖薄弱（1 篇）、尚无文档。“尚无文档”的目录会被显式标注，这通常是知识库下一步入库工作的优先方向。

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>knowledge-flow · 知识库可视化</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 24px; }

.page-header { text-align: center; margin-bottom: 10px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }

/* ── 统计条 ── */
.stats-bar {
  display: flex; gap: 0;
  background: #f8fafc; border-radius: 8px;
  border: 1.5px solid #e2e8f0; overflow: hidden;
  margin-bottom: 10px;
}
.stat {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 10px 8px; gap: 3px;
  border-right: 1px solid #e2e8f0;
}
.stat:last-child { border-right: none; }
.stat-num { font-size: 22px; font-weight: 800; line-height: 1; }
.stat-lbl { font-size: 11px; color: #64748b; text-align: center; }

/* ── 图例 ── */
.legend-bar {
  display: flex; gap: 14px; align-items: center;
  padding: 7px 12px; background: #f8fafc;
  border: 1.5px solid #e2e8f0; border-radius: 8px;
  margin-bottom: 10px; flex-wrap: wrap;
}
.leg { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #475569; }
.leg-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.legend-bar .hint { margin-left: auto; font-size: 11px; color: #94a3b8; }

/* ── 树容器 ── */
.tree-wrap {
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,.05);
}
.tree-header {
  background: #f8fafc; padding: 8px 14px;
  border-bottom: 1.5px solid #e2e8f0;
  font-size: 11px; font-weight: 700; letter-spacing: .8px;
  text-transform: uppercase; color: #94a3b8;
  display: flex; align-items: center; gap: 8px;
}
.tree-body { padding: 6px 0 10px; }

/* ── 树节点行 ── */
.nd {
  display: flex; align-items: center; gap: 6px;
  padding: 5px 14px; cursor: pointer; user-select: none;
  transition: background .12s; position: relative;
}
.nd:hover { background: #f1f5f9; }

.toggle { width: 14px; font-size: 9px; color: #94a3b8; transition: transform .15s; text-align: center; flex-shrink: 0; }
.toggle.open { transform: rotate(90deg); }
.toggle.leaf { visibility: hidden; }

.nd-icon { flex-shrink: 0; font-size: 13px; }

.nd-name { font-size: 12.5px; font-weight: 600; color: #1e293b; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.nd-name.domain { font-size: 13px; }

/* 文档数角标 */
.doc-count {
  flex-shrink: 0; font-size: 10px; font-weight: 700;
  padding: 1px 7px; border-radius: 10px; background: #f1f5f9;
  color: #475569; border: 1px solid #e2e8f0;
}

/* 覆盖度条 */
.cov-bar {
  flex-shrink: 0; width: 60px; height: 6px;
  background: #e2e8f0; border-radius: 3px; overflow: hidden;
}
.cov-fill { height: 100%; border-radius: 3px; transition: width .3s; }

/* 覆盖度标签 */
.cov-tag {
  flex-shrink: 0; font-size: 9.5px; font-weight: 700;
  padding: 1px 6px; border-radius: 8px;
}
.ct-full  { background: #d1fae5; color: #065f46; }
.ct-mid   { background: #fef3c7; color: #92400e; }
.ct-low   { background: #fee2e2; color: #991b1b; }
.ct-empty { background: #f1f5f9; color: #94a3b8; }

/* 域色条 */
.domain-stripe { width: 3px; height: 100%; position: absolute; left: 0; top: 0; border-radius: 0; }

/* children wrapper */
.children { overflow: hidden; }

/* 空白提示 */
.empty-badge {
  display: inline-block; font-size: 9px; font-weight: 700;
  padding: 1px 6px; border-radius: 6px;
  background: #fee2e2; color: #991b1b; margin-left: 4px;
}

/* tooltip */
.tooltip-wrap { position: relative; }
.nd:hover .tip { display: block; }
.tip {
  display: none; position: absolute;
  left: calc(100% + 8px); top: 50%; transform: translateY(-50%);
  background: #0f172a; color: #f1f5f9; font-size: 10.5px;
  padding: 5px 9px; border-radius: 6px; white-space: nowrap;
  z-index: 10; pointer-events: none; line-height: 1.5;
  box-shadow: 0 4px 12px rgba(0,0,0,.2);
}
.tip::before {
  content: ''; position: absolute; right: 100%; top: 50%;
  transform: translateY(-50%);
  border: 5px solid transparent; border-right-color: #0f172a;
}
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>knowledge-flow · 知识库可视化</h1>
    <p>全景感知知识库的覆盖范围与文档密度分布</p>
  </div>

  <!-- 统计条 -->
  <div class="stats-bar">
    <div class="stat"><span class="stat-num" style="color:#2563eb">49</span><span class="stat-lbl">文档总数</span></div>
    <div class="stat"><span class="stat-num" style="color:#7c3aed">4</span><span class="stat-lbl">一级领域</span></div>
    <div class="stat"><span class="stat-num" style="color:#0891b2">11</span><span class="stat-lbl">分类目录</span></div>
    <div class="stat"><span class="stat-num" style="color:#059669">9</span><span class="stat-lbl">已覆盖</span></div>
    <div class="stat"><span class="stat-num" style="color:#dc2626">2</span><span class="stat-lbl">待补充</span></div>
  </div>

  <!-- 图例 -->
  <div class="legend-bar">
    <div class="leg"><span class="leg-dot" style="background:#22c55e"></span>充分覆盖（≥6 篇）</div>
    <div class="leg"><span class="leg-dot" style="background:#f59e0b"></span>一般覆盖（2-5 篇）</div>
    <div class="leg"><span class="leg-dot" style="background:#ef4444"></span>覆盖薄弱（1 篇）</div>
    <div class="leg"><span class="leg-dot" style="background:#e2e8f0"></span>尚无文档</div>
    <span class="hint">← 点击展开目录</span>
  </div>

  <!-- 目录树 -->
  <div class="tree-wrap">
    <div class="tree-header">
      📚 知识库目录树
      <span style="font-weight:400;color:#cbd5e1;font-size:10px">（示例数据）</span>
    </div>
    <div class="tree-body" id="tree"></div>
  </div>

</div>
<script>
const DOMAINS = ['#2563eb','#7c3aed','#0891b2','#d97706'];
const DATA = [
  {
    name:'系统知识', icon:'🏗️', count:18, open:true, color:DOMAINS[0],
    children:[
      { name:'架构设计',   count:8,  tip:'服务拓扑、模块设计、依赖关系' },
      { name:'接口文档',   count:6,  tip:'API 规范、参数说明、错误码' },
      { name:'部署运维',   count:4,  tip:'部署流程、环境配置、发布规范' },
    ]
  },
  {
    name:'实验记录', icon:'🧪', count:14, open:true, color:DOMAINS[1],
    children:[
      { name:'在线实验',   count:9, tip:'A/B 实验方案、流量配置、结果分析' },
      { name:'离线评测',   count:5, tip:'评测集构建、指标对比、实验结论' },
    ]
  },
  {
    name:'业务知识', icon:'📋', count:11, open:true, color:DOMAINS[2],
    children:[
      { name:'核心流程',   count:7,  tip:'业务主链路、关键决策点说明' },
      { name:'异常处理',   count:4,  tip:'常见异常、排查路径、处理 SOP' },
      { name:'历史决策',   count:0,  tip:'暂无文档 — 建议补充决策背景' },
    ]
  },
  {
    name:'工程实践', icon:'⚙️', count:6, open:false, color:DOMAINS[3],
    children:[
      { name:'开发规范',   count:4,  tip:'代码规范、评审流程、分支管理' },
      { name:'故障复盘',   count:1,  tip:'已有 1 篇复盘，建议持续沉淀' },
      { name:'性能优化',   count:1,  tip:'已有 1 篇，覆盖较薄弱' },
    ]
  },
];

function covClass(n) {
  if (n === 0) return 'ct-empty';
  if (n === 1) return 'ct-low';
  if (n <= 5)  return 'ct-mid';
  return 'ct-full';
}
function covColor(n) {
  if (n === 0) return '#e2e8f0';
  if (n === 1) return '#ef4444';
  if (n <= 5)  return '#f59e0b';
  return '#22c55e';
}
function covWidth(n) { return Math.min(100, n * 12) + '%'; }
function covLabel(n) {
  if (n === 0) return '尚无文档';
  if (n === 1) return '覆盖薄弱';
  if (n <= 5)  return '一般覆盖';
  return '充分覆盖';
}

function render(container) {
  DATA.forEach((domain, di) => {
    // domain row
    const drow = document.createElement('div');
    drow.className = 'nd';
    drow.style.paddingLeft = '14px';
    drow.innerHTML = `
      <div class="domain-stripe" style="background:${domain.color}"></div>
      <span class="toggle ${domain.open ? 'open' : ''}" id="tog-d${di}">▶</span>
      <span class="nd-icon">${domain.icon}</span>
      <span class="nd-name domain">${domain.name}</span>
      <span class="doc-count">${domain.count} 篇</span>
      <div class="cov-bar"><div class="cov-fill" style="width:${covWidth(domain.count)};background:${domain.color}40"></div></div>
    `;

    const children = document.createElement('div');
    children.className = 'children';
    children.id = 'ch-d' + di;
    children.style.display = domain.open ? 'block' : 'none';

    domain.children.forEach((cat, ci) => {
      const crow = document.createElement('div');
      crow.className = 'nd';
      crow.style.paddingLeft = '34px';
      crow.innerHTML = `
        <span class="toggle leaf">▶</span>
        <span class="nd-icon">${cat.count === 0 ? '📭' : '📄'}</span>
        <span class="nd-name">${cat.name}${cat.count === 0 ? '<span class="empty-badge">待补充</span>' : ''}</span>
        <span class="doc-count">${cat.count} 篇</span>
        <div class="cov-bar"><div class="cov-fill" style="width:${covWidth(cat.count)};background:${covColor(cat.count)}"></div></div>
        <span class="cov-tag ${covClass(cat.count)}">${covLabel(cat.count)}</span>
        <div class="tip">${cat.tip}</div>
      `;
      children.appendChild(crow);
    });

    drow.addEventListener('click', () => {
      domain.open = !domain.open;
      document.getElementById('tog-d' + di).className = 'toggle ' + (domain.open ? 'open' : '');
      children.style.display = domain.open ? 'block' : 'none';
    });

    container.appendChild(drow);
    container.appendChild(children);
  });
}

render(document.getElementById('tree'));
</script>
</body>
</html>


- **版本管理 & 团队共享：**knowledge-flow 的知识库是本地文件系统目录，这意味着它天然可以被 Git 管理。版本管理功能将知识库托管到一个共享的 Git 仓库，让团队成员可以各自在本地维护、通过推拉同步变更，知识库像代码一样拥有完整的版本历史和协作能力。

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>knowledge-flow · 版本管理 & 团队共享</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 24px; }

.page-header { text-align: center; margin-bottom: 12px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }

/* ── 协作模型 ── */
.section-title {
  font-size: 12px; font-weight: 700; color: #94a3b8;
  letter-spacing: .8px; text-transform: uppercase;
  margin-bottom: 8px;
}

.collab-model {
  display: flex; align-items: center; justify-content: center;
  gap: 0; padding: 20px 10px;
  background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 10px;
  margin-bottom: 10px; position: relative;
  box-shadow: 0 2px 10px rgba(0,0,0,.04);
}

/* 成员/远端节点卡 */
.actor {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  width: 130px; flex-shrink: 0;
}
.actor-icon {
  width: 52px; height: 52px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; border: 2.5px solid;
}
.actor-icon.member { background: #eff6ff; border-color: #3b82f6; }
.actor-icon.remote { background: #f0fdf4; border-color: #22c55e; }
.actor-name { font-size: 12px; font-weight: 700; color: #1e293b; text-align: center; }
.actor-sub  { font-size: 10px; color: #94a3b8; text-align: center; line-height: 1.4; }

/* 箭头区域 */
.arrow-col {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; gap: 6px; padding: 0 4px;
}
.arrow-row {
  display: flex; align-items: center; gap: 6px; width: 100%;
}
.arrow-line {
  flex: 1; height: 2px; border-radius: 1px;
  position: relative;
}
.al-push { background: #3b82f6; }
.al-pull { background: #8b5cf6; }
.al-push::after  { content:''; position:absolute; right:-1px; top:-4px; border:5px solid transparent; border-left-color:#3b82f6; }
.al-pull::before { content:''; position:absolute; left:-1px;  top:-4px; border:5px solid transparent; border-right-color:#8b5cf6; }

.arrow-label {
  font-size: 10px; font-weight: 700; padding: 2px 8px;
  border-radius: 8px; white-space: nowrap; flex-shrink: 0;
}
.al-push-lbl { background: #dbeafe; color: #1d4ed8; }
.al-pull-lbl { background: #ede9fe; color: #6d28d9; }

/* ── 操作流程 ── */
.workflow {
  display: flex; align-items: stretch; gap: 0;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  overflow: hidden; margin-bottom: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,.04);
}

.wf-step {
  flex: 1; display: flex; flex-direction: column;
  padding: 14px 12px; position: relative; cursor: default;
  transition: background .15s;
}
.wf-step:hover { background: #f8fafc; }
.wf-step + .wf-step { border-left: 1px solid #e2e8f0; }

.wf-sep {
  display: flex; align-items: center; justify-content: center;
  width: 28px; flex-shrink: 0; background: #f8fafc;
  border-left: 1px solid #e2e8f0;
  border-right: 1px solid #e2e8f0;
}
.wf-sep-arr { font-size: 14px; color: #cbd5e1; }

.wf-head { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.wf-icon { font-size: 18px; flex-shrink: 0; }
.wf-name { font-size: 12px; font-weight: 700; color: #0f172a; }
.wf-cmd  { font-size: 10px; font-family: 'SF Mono','Fira Code',monospace;
           background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 4px;
           padding: 2px 6px; color: #334155; display: inline-block; margin-bottom: 6px; }
.wf-desc { font-size: 11px; color: #64748b; line-height: 1.6; }
.wf-badge {
  font-size: 9px; font-weight: 700; padding: 1px 6px;
  border-radius: 8px; display: inline-block; margin-bottom: 5px;
}
.wb-once { background: #fef3c7; color: #92400e; }
.wb-daily { background: #dbeafe; color: #1e40af; }

/* ── 语义合并说明 ── */
.merge-box {
  background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 10px;
  padding: 14px 16px; display: flex; gap: 14px; align-items: flex-start;
  box-shadow: 0 2px 10px rgba(0,0,0,.04);
}
.merge-icon { font-size: 24px; flex-shrink: 0; }
.merge-body { flex: 1; }
.merge-title { font-size: 12.5px; font-weight: 700; color: #1e293b; margin-bottom: 5px; }
.merge-desc  { font-size: 12px; color: #475569; line-height: 1.7; }
.merge-example {
  display: flex; gap: 8px; margin-top: 10px;
}
.me-box {
  flex: 1; border-radius: 7px; padding: 8px 10px;
  font-size: 10.5px; line-height: 1.6;
  font-family: 'SF Mono','Fira Code',monospace;
}
.me-a { background: #eff6ff; border: 1.5px solid #bfdbfe; color: #1e40af; }
.me-b { background: #f0fdf4; border: 1.5px solid #bbf7d0; color: #14532d; }
.me-merged { background: #faf5ff; border: 1.5px solid #ddd6fe; color: #4c1d95; }
.me-label { font-size: 9px; font-weight: 700; letter-spacing: .6px; text-transform: uppercase; margin-bottom: 4px; }
.me-arrow { display: flex; align-items: center; font-size: 16px; color: #cbd5e1; flex-shrink: 0; }
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>knowledge-flow · 版本管理 &amp; 团队共享</h1>
    <p>将知识库托管在 Git 仓库，让团队知识像代码一样可协同、可回溯</p>
  </div>

  <!-- 协作模型 -->
  <div class="section-title">团队协作</div>
  <div class="collab-model">

    <div class="actor">
      <div class="actor-icon member">👤</div>
      <div class="actor-name">成员 A</div>
      <div class="actor-sub">本地知识库<br>入库 · 整理</div>
    </div>

    <div class="arrow-col">
      <div class="arrow-row">
        <span class="arrow-label al-push-lbl">推送 push</span>
        <div class="arrow-line al-push"></div>
      </div>
      <div class="arrow-row">
        <div class="arrow-line al-pull"></div>
        <span class="arrow-label al-pull-lbl">拉取 pull</span>
      </div>
    </div>

    <div class="actor">
      <div class="actor-icon remote">🗄️</div>
      <div class="actor-name">Git 远端仓库</div>
      <div class="actor-sub">共享存储<br>版本历史</div>
    </div>

    <div class="arrow-col">
      <div class="arrow-row">
        <div class="arrow-line al-push" style="transform:scaleX(-1)"></div>
        <span class="arrow-label al-pull-lbl">拉取 pull</span>
      </div>
      <div class="arrow-row">
        <span class="arrow-label al-push-lbl">推送 push</span>
        <div class="arrow-line al-pull" style="background:#3b82f6;transform:scaleX(-1)"></div>
      </div>
    </div>

    <div class="actor">
      <div class="actor-icon member">👤</div>
      <div class="actor-name">成员 B</div>
      <div class="actor-sub">本地知识库<br>入库 · 整理</div>
    </div>

  </div>

  <!-- 操作流程 -->
  <div class="section-title" style="margin-top:12px">操作流程</div>
  <div class="workflow">

    <div class="wf-step">
      <div class="wf-head"><span class="wf-icon">🔗</span><div class="wf-name">初始化连接</div></div>
      <span class="wf-badge wb-once">一次性配置</span>
      <div class="wf-desc">关联远端仓库，绑定本地知识库目录。配置一次，后续无需重复设置。</div>
    </div>

    <div class="wf-sep"><span class="wf-sep-arr">›</span></div>

    <div class="wf-step">
      <div class="wf-head"><span class="wf-icon">⬆️</span><div class="wf-name">推送更新</div></div>
      <span class="wf-badge wb-daily">日常使用</span>
      <div class="wf-desc">入库或整理完成后推送变更，自动生成提交信息。</div>
    </div>

    <div class="wf-sep"><span class="wf-sep-arr">›</span></div>

    <div class="wf-step">
      <div class="wf-head"><span class="wf-icon">⬇️</span><div class="wf-name">拉取同步</div></div>
      <span class="wf-badge wb-daily">日常使用</span>
      <div class="wf-desc">开始工作前拉取最新变更，无冲突直接合并。</div>
    </div>

    <div class="wf-sep"><span class="wf-sep-arr">›</span></div>

    <div class="wf-step">
      <div class="wf-head"><span class="wf-icon">🕙</span><div class="wf-name">版本回溯</div></div>
      <span class="wf-badge wb-daily">按需使用</span>
      <div class="wf-desc">可随时查看历史版本或恢复到指定时间点。</div>
    </div>

  </div>

  <!-- 语义合并说明 -->
  <div class="section-title" style="margin-top:12px">冲突处理：语义级别合并</div>
  <div class="merge-box">
    <span class="merge-icon">🧩</span>
    <div class="merge-body">
      <div class="merge-title">以文档块为粒度合并，而非逐行对比</div>
      <div class="merge-desc">合并粒度是<strong>单个文档条目</strong>，而非逐行 diff。两人各自新增不同文档时直接自动合并；只有双方修改了同一字段时才产生真实冲突。</div>
      <div class="merge-example">
        <div class="me-box me-a">
          <div class="me-label">成员 A 的版本</div>
          ## 文档甲<br>
          **关键词**：方案A, 设计<br>
          ---
        </div>
        <div class="me-arrow">+</div>
        <div class="me-box me-b">
          <div class="me-label">成员 B 的版本</div>
          ## 文档乙<br>
          **关键词**：方案B, 实现<br>
          ---
        </div>
        <div class="me-arrow">→</div>
        <div class="me-box me-merged">
          <div class="me-label">合并结果（自动）</div>
          ## 文档甲<br>
          **关键词**：方案A, 设计<br>
          ---<br>
          ## 文档乙<br>
          **关键词**：方案B, 实现<br>
          ---
        </div>
      </div>
    </div>
  </div>

</div>
</body>
</html>


### 8. 其他

knowledge-flow **的所有功能均可通过自然语言触发，无需记住任何指令名称。**直接向 Agent 描述你想做的事，它会自动识别并执行对应的功能。

- **一键初始化配置：**首次使用时，告诉 Agent「帮我完成初始化配置」，它会自动完成三项配置：验证相关技能的安装状态（citadel等常用官方技能）、配置知识（git）仓地址、检查用户身份（MIS）配置是否正确。配置结果写入本地配置文件，后续使用无需重复设置。

- **多知识库管理 & 切换：**如果需要同时维护多个知识库（比如一个面向自己日常使用、一个供团队共享、一个用于测试），knowledge-flow 提供知识库注册表功能。注册多个知识库后，告诉 Agent「切换到某个知识库」，当前激活项会立即切换，知识库路径、Git 远端地址、关键词索引路径等所有关联配置字段自动同步更新，无需手动修改配置文件。

- **能力速查手册：**如果不确定 knowledge-flow 当前支持哪些功能，或者不知道某个操作该怎么触发，直接问 Agent「你能做什么」或「如何入库一篇文档」，它会列出当前具备的能力清单或给出具体的操作引导。

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>knowledge-flow · 易用性</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 24px; }
.page-header { text-align: center; margin-bottom: 12px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }

/* ── 三栏布局 ── */
.cols { display: flex; gap: 10px; align-items: stretch; }
.col  { flex: 1; display: flex; flex-direction: column; }

/* ── 功能卡片 ── */
.card {
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  overflow: hidden; flex: 1;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
  display: flex; flex-direction: column;
}
.card-head {
  padding: 10px 14px 9px; border-bottom: 1.5px solid #e2e8f0;
  display: flex; flex-direction: column; gap: 4px;
}
.ch-top { display: flex; align-items: center; gap: 7px; }
.ch-icon  { font-size: 15px; }
.ch-name  { font-size: 13px; font-weight: 700; color: #0f172a; }
.ch-tag   { font-size: 9.5px; font-weight: 700; padding: 1px 7px; border-radius: 8px; margin-left: auto; }
.ch-desc  { font-size: 11px; color: #64748b; line-height: 1.6; }

.card-body { padding: 14px 14px; flex: 1; display: flex; flex-direction: column; gap: 12px; }

.c-blue   { border-color: #bfdbfe; }
.c-blue   .card-head { background: #eff6ff; border-bottom-color: #bfdbfe; }
.c-blue   .ch-tag { background: #dbeafe; color: #1e40af; }
.c-green  { border-color: #bbf7d0; }
.c-green  .card-head { background: #ecfdf5; border-bottom-color: #bbf7d0; }
.c-green  .ch-tag { background: #d1fae5; color: #065f46; }
.c-amber  { border-color: #fde68a; }
.c-amber  .card-head { background: #fffbeb; border-bottom-color: #fde68a; }
.c-amber  .ch-tag { background: #fef3c7; color: #92400e; }

/* ── 多知识库：注册表演示 ── */
.kb-table {
  border: 1.5px solid #e2e8f0; border-radius: 7px; overflow: hidden;
  font-size: 10.5px;
}
.kt-head {
  display: flex; background: #f8fafc; border-bottom: 1px solid #e2e8f0;
  font-size: 9.5px; font-weight: 700; color: #94a3b8; letter-spacing: .4px;
}
.kt-row  { display: flex; border-bottom: 1px solid #f1f5f9; align-items: center; }
.kt-row:last-child { border-bottom: none; }
.kt-row.active { background: #ecfdf5; }
.kc-mark { flex: 0 0 18px; text-align: center; font-weight: 700; font-size: 12px; padding: 5px 0; }
.kc-name { flex: 0 0 90px; padding: 5px 6px; color: #334155; font-weight: 500; }
.kc-path { flex: 1; padding: 5px 6px; color: #94a3b8; font-family: 'SF Mono','Fira Code',monospace; font-size: 9.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.kt-row.active .kc-mark { color: #059669; }
.kt-row.active .kc-name { color: #065f46; font-weight: 700; }

.switch-demo {
  background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 7px;
  padding: 7px 10px; display: flex; align-items: center; gap: 8px;
  font-size: 11px;
}
.sd-cmd { font-family: 'SF Mono','Fira Code',monospace; font-size: 10px; color: #065f46; font-weight: 600; flex: 1; }
.sd-desc { font-size: 10px; color: #94a3b8; }

/* ── 初始化：配置清单 ── */
.check-list { display: flex; flex-direction: column; gap: 5px; }
.ci {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 7px 10px; background: #f8fafc;
  border: 1.5px solid #e2e8f0; border-radius: 7px;
}
.ci-check {
  flex-shrink: 0; width: 16px; height: 16px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 9px; font-weight: 700; margin-top: 1px;
}
.ci-ok  { background: #d1fae5; color: #059669; }
.ci-body { flex: 1; }
.ci-name { font-size: 11px; font-weight: 600; color: #334155; }
.ci-sub  { font-size: 10px; color: #94a3b8; margin-top: 1px; }

.init-cmd {
  background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 7px;
  padding: 8px 11px; font-family: 'SF Mono','Fira Code',monospace;
  font-size: 11px; color: #065f46; font-weight: 600; text-align: center;
}

/* ── 能力速查：对话气泡 ── */
.chat-demo { display: flex; flex-direction: column; gap: 7px; }

.bubble-user {
  align-self: flex-end; background: #eff6ff; border: 1.5px solid #bfdbfe;
  border-radius: 10px 10px 2px 10px;
  padding: 6px 10px; font-size: 11px; color: #1e40af; max-width: 80%;
}
.bubble-agent {
  align-self: flex-start; background: #f8fafc; border: 1.5px solid #e2e8f0;
  border-radius: 10px 10px 10px 2px;
  padding: 8px 10px; font-size: 10.5px; color: #334155; max-width: 95%;
  line-height: 1.6;
}
.cap-item {
  display: flex; align-items: flex-start; gap: 5px;
  font-size: 10.5px; color: #334155; margin-bottom: 3px;
}
.cap-dot  { flex-shrink: 0; width: 5px; height: 5px; border-radius: 50%; background: #93c5fd; margin-top: 5px; }
.cap-text { flex: 1; line-height: 1.5; }

/* ── 底部注释 ── */
.note { font-size: 10.5px; color: #94a3b8; line-height: 1.6; padding-top: 6px; border-top: 1px solid #f1f5f9; margin-top: auto; }
.note strong { color: #64748b; }
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>knowledge-flow · 易用性</h1>
    <p>三个功能让知识库的配置、管理和使用更顺畅</p>
  </div>

  <div style="background:#faf5ff;border:1.5px solid #ddd6fe;border-radius:9px;padding:10px 16px;margin-bottom:14px;display:flex;align-items:center;gap:10px;">
    <span style="font-size:16px;flex-shrink:0">💬</span>
    <span style="font-size:12px;color:#4c1d95;line-height:1.6"><strong>所有功能均可通过自然语言触发</strong>，无需记住任何指令名称。直接向 Agent 描述你想做的事，它会自动识别并执行对应的功能。</span>
  </div>

  <div class="cols">

    <!-- ══ 多知识库管理 & 切换 ══ -->
    <div class="col">
      <div class="card c-blue">
        <div class="card-head">
          <div class="ch-top">
            <span class="ch-icon">🗂️</span>
            <span class="ch-name">多知识库管理 & 切换</span>
            <span class="ch-tag">多库场景</span>
          </div>
          <div class="ch-desc">维护一个知识库注册表，支持注册多个知识库，一键切换当前激活项，自动同步所有相关配置。</div>
        </div>
        <div class="card-body">

          <div class="bubble-user" style="align-self:flex-end;margin-bottom:2px">帮我切换至 knowledge-main 知识库</div>

          <div class="kb-table">
            <div class="kt-head">
              <span class="kc-mark"></span>
              <span class="kc-name" style="padding:5px 6px">名称</span>
              <span class="kc-path" style="padding:5px 6px">路径</span>
            </div>
            <div class="kt-row active">
              <span class="kc-mark">★</span>
              <span class="kc-name">knowledge-main</span>
              <span class="kc-path">references/knowledge</span>
            </div>
            <div class="kt-row">
              <span class="kc-mark"></span>
              <span class="kc-name">knowledge-test</span>
              <span class="kc-path">references/knowledge_test</span>
            </div>
            <div class="kt-row">
              <span class="kc-mark"></span>
              <span class="kc-name">knowledge-team</span>
              <span class="kc-path">references/knowledge_team</span>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- ══ 一键初始化配置 ══ -->
    <div class="col">
      <div class="card c-green">
        <div class="card-head">
          <div class="ch-top">
            <span class="ch-icon">⚡</span>
            <span class="ch-name">一键初始化配置</span>
            <span class="ch-tag">首次使用</span>
          </div>
          <div class="ch-desc">新用户运行一个命令，自动完成所有必要的环境配置，几分钟内开箱即用。</div>
        </div>
        <div class="card-body">

          <div class="bubble-user" style="align-self:flex-end;margin-bottom:2px">knowledge-flow，帮我完成初始化配置</div>

          <div class="check-list">
            <div class="ci">
              <span class="ci-check ci-ok">✓</span>
              <div class="ci-body">
                <div class="ci-name">验证相关技能安装状态</div>
                <div class="ci-sub">citadel 等常用官方技能，给出修复指引</div>
              </div>
            </div>
            <div class="ci">
              <span class="ci-check ci-ok">✓</span>
              <div class="ci-body">
                <div class="ci-name">配置知识仓地址</div>
                <div class="ci-sub">关联 Git 远端仓库，写入本地配置文件</div>
              </div>
            </div>
            <div class="ci">
              <span class="ci-check ci-ok">✓</span>
              <div class="ci-body">
                <div class="ci-name">检查用户身份配置</div>
                <div class="ci-sub">验证 MIS 是否正确设置</div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- ══ 能力速查手册 ══ -->
    <div class="col">
      <div class="card c-amber">
        <div class="card-head">
          <div class="ch-top">
            <span class="ch-icon">📖</span>
            <span class="ch-name">能力速查手册</span>
            <span class="ch-tag">使用引导</span>
          </div>
          <div class="ch-desc">通过自然语言提问，随时查看 knowledge-flow 当前具备哪些能力及对应的使用方式。</div>
        </div>
        <div class="card-body">

          <div class="chat-demo">
            <div class="bubble-user">你能做什么？</div>
            <div class="bubble-agent">
              <div class="cap-item"><span class="cap-dot"></span><span class="cap-text"><strong>知识检索</strong>：回答问题时自动检索本地知识库</span></div>
              <div class="cap-item"><span class="cap-dot"></span><span class="cap-text"><strong>知识入库</strong>：学城链接入库 / 父目录批量入库 / 冷启入库</span></div>
              <div class="cap-item"><span class="cap-dot"></span><span class="cap-text"><strong>结构治理</strong>：目录结构优化 / 容器节点优化</span></div>
              <div class="cap-item"><span class="cap-dot"></span><span class="cap-text"><strong>知识质量</strong>：评测集构建 / 知识库评测 / 矛盾检测</span></div>
              <div class="cap-item"><span class="cap-dot"></span><span class="cap-text" style="color:#94a3b8">… 更多能力</span></div>
            </div>
          </div>

        </div>
      </div>
    </div>

  </div>
</div>
</body>
</html>


### 9. 场景实践

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>knowledge-flow · 应用数据</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 0; }

.stats-bar {
  display: flex; gap: 0;
  background: #f8fafc; border-radius: 10px;
  border: 1.5px solid #e2e8f0; overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,.05);
}
.stat {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 16px 10px; gap: 5px;
  border-right: 1px solid #e2e8f0;
  transition: background .15s;
}
.stat:last-child { border-right: none; }
.stat:hover { background: #fff; }

.stat-num {
  font-size: 28px; font-weight: 800; line-height: 1;
}
.stat-label {
  font-size: 11.5px; color: #64748b; text-align: center; line-height: 1.4;
}
</style>
</head>
<body>
<div class="page">
  <div class="stats-bar">
    <div class="stat">
      <span class="stat-num" style="color:#2563eb">100<span style="font-size:18px">+</span></span>
      <span class="stat-label">活跃用户</span>
    </div>
    <div class="stat">
      <span class="stat-num" style="color:#7c3aed">12</span>
      <span class="stat-label">落地场景</span>
    </div>
    <div class="stat">
      <span class="stat-num" style="color:#0891b2">10<span style="font-size:18px">+</span></span>
      <span class="stat-label">项目组</span>
    </div>
    <div class="stat">
      <span class="stat-num" style="color:#059669">30<span style="font-size:18px">+</span></span>
      <span class="stat-label">需求实现</span>
    </div>
    <div class="stat">
      <span class="stat-num" style="color:#d97706">400<span style="font-size:18px">+</span></span>
      <span class="stat-label">答疑&排查</span>
    </div>
  </div>
</div>
</body>
</html>


#### 9.1 需求托管开发

##### **9.1.1 工程 Agent 全托管需求迭代**

AI Coding 工具的 Demo 通常从零搭建新项目，但真实的业务开发是另一幅景象：系统历史悠久，逻辑主要通过代码流传；一次变更往往横跨代码、配置中心和数据库；还有大量隐式约定 —— 降级策略的写法、枚举值的含义 —— 既塞不进系统提示词，也没有文档记录。这类场景下，让 Agent 一次性理解整个系统并不现实，代码仓库动辄成千上万个类和方法，全量输入只会让 Agent 在信息中迷失方向。

**knowledge-flow 的角色 —— **解决这个问题的关键，是让 Agent 像一个有经验的工程师一样**按需查阅资料**，而不是在任务开始时把所有内容一次性加载。

具体的做法是构建一套三层知识体系：L1 通用层存放跨项目的编码规范和框架用法，由编排器在需要时注入；L2 项目层存放单个项目的架构设计、领域模型、历史需求实现模式和隐式约定，由 knowledge-flow 在每个执行阶段按需检索；L3 任务层是当前需求的 PRD 和阶段产物，随任务启动加载。

三层中，knowledge-flow 承担的 L2 是最难维护也最关键的部分。通用规范有文档，当前任务有 PRD，唯独项目级的历史积累过去只存在于老工程师的记忆里。用代码知识提取工具将代码库结构化入库、用学城入库功能收录设计文档、用会话沉淀功能持续积累每次需求交付的经验，形成一个可查询的项目知识库。

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>工程 Agent 全托管需求迭代</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 24px; }
.page-header { text-align: center; margin-bottom: 14px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }

/* ── SDLC 流水线 ── */
.pipeline-wrap {
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  padding: 16px 16px 14px; margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,.04); background: #f8fafc;
}
.section-lbl {
  font-size: 9.5px; font-weight: 700; letter-spacing: .8px;
  text-transform: uppercase; color: #94a3b8; margin-bottom: 10px;
}

/* 阶段行 */
.stages { display: flex; align-items: stretch; gap: 0; }
.stage-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 0; }

/* 阶段卡 */
.stage-box {
  width: 100%; border-radius: 8px; border: 1.5px solid #c7d2fe;
  background: #eef2ff; padding: 10px 8px; text-align: center;
}
.sb-icon { font-size: 18px; margin-bottom: 4px; }
.sb-name { font-size: 11.5px; font-weight: 700; color: #3730a3; }

/* 箭头 */
.stage-arr {
  flex: 0 0 28px; display: flex; align-items: center; justify-content: center;
  color: #a5b4fc; font-size: 16px; padding-top: 10px;
}

/* KF 知识注入 */
.kf-inject {
  margin-top: 6px; width: 100%;
  border: 1.5px dashed #a5b4fc; border-radius: 6px;
  background: #fff; padding: 6px 8px;
}
.kfi-label { font-size: 9px; font-weight: 700; color: #818cf8; margin-bottom: 3px; letter-spacing: .4px; }
.kfi-items { display: flex; flex-direction: column; gap: 2px; }
.kfi-item  { font-size: 9.5px; color: #475569; line-height: 1.4; display: flex; gap: 4px; align-items: flex-start; }
.kfi-dot   { width: 4px; height: 4px; border-radius: 50%; background: #a5b4fc; flex-shrink: 0; margin-top: 4px; }

.no-inject { opacity: 0; pointer-events: none; }

/* ── 知识层架构 ── */
.layers-wrap {
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  padding: 14px 16px; margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.layers { display: flex; gap: 8px; }
.layer {
  flex: 1; border-radius: 8px; border: 1.5px solid;
  padding: 10px 11px; display: flex; flex-direction: column; gap: 5px;
}
.l1 { border-color: #bfdbfe; background: #eff6ff; }
.l2 { border-color: #818cf8; background: #eef2ff; border-width: 2px; }
.l3 { border-color: #d1fae5; background: #ecfdf5; }

.layer-head { display: flex; align-items: center; gap: 6px; }
.layer-num {
  width: 20px; height: 20px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 800; color: #fff; flex-shrink: 0;
}
.ln-l1 { background: #3b82f6; }
.ln-l2 { background: #4f46e5; }
.ln-l3 { background: #059669; }
.layer-title { font-size: 11.5px; font-weight: 700; }
.l1 .layer-title { color: #1e40af; }
.l2 .layer-title { color: #3730a3; }
.l3 .layer-title { color: #065f46; }
.layer-scope { font-size: 9.5px; color: #64748b; }
.layer-tags { display: flex; flex-wrap: wrap; gap: 3px; }
.ltag {
  font-size: 9.5px; font-weight: 600; padding: 1px 6px;
  border-radius: 5px;
}
.l1 .ltag { background: #dbeafe; color: #1e40af; }
.l2 .ltag { background: #e0e7ff; color: #3730a3; }
.l3 .ltag { background: #d1fae5; color: #065f46; }
.layer-mode {
  font-size: 9px; font-weight: 600; padding: 2px 7px;
  border-radius: 5px; align-self: flex-start; margin-top: 2px;
}
.l1 .layer-mode { background: #eff6ff; color: #64748b; border: 1px dashed #93c5fd; }
.l2 .layer-mode { background: #eef2ff; color: #4f46e5; border: 1px solid #818cf8; }
.l3 .layer-mode { background: #ecfdf5; color: #64748b; border: 1px dashed #6ee7b7; }
.kf-badge {
  font-size: 9px; font-weight: 700; padding: 1px 7px;
  border-radius: 8px; background: #4f46e5; color: #fff;
  align-self: flex-start;
}

/* ── 沉淀反馈 ── */
.feedback-row {
  display: flex; align-items: center; gap: 10px;
  background: #faf5ff; border: 1.5px solid #ddd6fe; border-radius: 8px;
  padding: 9px 14px;
}
.fb-icon { font-size: 16px; flex-shrink: 0; }
.fb-text { font-size: 11.5px; color: #4c1d95; line-height: 1.6; flex: 1; }
.fb-text strong { color: #3730a3; }
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>工程 Agent 全托管需求迭代</h1>
    <p>让 Agent 像老员工一样，在遗留系统上完成需求交付</p>
  </div>

  <!-- ── SDLC 各阶段 + KF 注入点 ── -->
  <div class="pipeline-wrap">
    <div class="section-lbl">需求全链路 · knowledge-flow 的注入点</div>
    <div class="stages">

      <div class="stage-col">
        <div class="stage-box">
          <div class="sb-icon">📋</div>
          <div class="sb-name">需求理解</div>
        </div>
        <div class="kf-inject">
          <div class="kfi-label">KF 提供</div>
          <div class="kfi-items">
            <div class="kfi-item"><span class="kfi-dot"></span>同类需求的历史实现模式</div>
            <div class="kfi-item"><span class="kfi-dot"></span>项目核心领域模型说明</div>
          </div>
        </div>
      </div>

      <div class="stage-arr">›</div>

      <div class="stage-col">
        <div class="stage-box">
          <div class="sb-icon">🎨</div>
          <div class="sb-name">方案设计</div>
        </div>
        <div class="kf-inject">
          <div class="kfi-label">KF 提供</div>
          <div class="kfi-items">
            <div class="kfi-item"><span class="kfi-dot"></span>架构设计规范与红线</div>
            <div class="kfi-item"><span class="kfi-dot"></span>相似需求的变更点参照</div>
          </div>
        </div>
      </div>

      <div class="stage-arr">›</div>

      <div class="stage-col">
        <div class="stage-box">
          <div class="sb-icon">⌨️</div>
          <div class="sb-name">编码实现</div>
        </div>
        <div class="kf-inject">
          <div class="kfi-label">KF 提供</div>
          <div class="kfi-items">
            <div class="kfi-item"><span class="kfi-dot"></span>项目编码规范与隐式约定</div>
            <div class="kfi-item"><span class="kfi-dot"></span>配置项语义与变更规范</div>
          </div>
        </div>
      </div>

      <div class="stage-arr">›</div>

      <div class="stage-col">
        <div class="stage-box">
          <div class="sb-icon">🚀</div>
          <div class="sb-name">部署上线</div>
        </div>
        <div class="kf-inject no-inject">
          <div class="kfi-label">KF 提供</div>
          <div class="kfi-items">
            <div class="kfi-item"><span class="kfi-dot"></span>-</div>
          </div>
        </div>
      </div>

    </div>
  </div>

  <!-- ── 知识三层架构 ── -->
  <div class="layers-wrap">
    <div class="section-lbl" style="margin-bottom:10px">知识分层架构 · 三层按需加载</div>
    <div class="layers">

      <div class="layer l1">
        <div class="layer-head">
          <span class="layer-num ln-l1">L1</span>
          <div>
            <div class="layer-title">通用层</div>
            <div class="layer-scope">跨项目通用规范</div>
          </div>
        </div>
        <div class="layer-tags">
          <span class="ltag">编码规范</span>
          <span class="ltag">架构红线</span>
          <span class="ltag">中间件用法</span>
          <span class="ltag">框架规范</span>
        </div>
        <span class="layer-mode">编排器关键词匹配注入</span>
      </div>

      <div class="layer l2">
        <div class="layer-head">
          <span class="layer-num ln-l2">L2</span>
          <div>
            <div class="layer-title">项目层</div>
            <div class="layer-scope">单项目专属知识</div>
          </div>
        </div>
        <div class="layer-tags">
          <span class="ltag">架构设计</span>
          <span class="ltag">领域模型</span>
          <span class="ltag">历史需求模式</span>
          <span class="ltag">配置语义</span>
          <span class="ltag">隐式约定</span>
        </div>
        <span class="kf-badge">knowledge-flow 按需检索</span>
      </div>

      <div class="layer l3">
        <div class="layer-head">
          <span class="layer-num ln-l3">L3</span>
          <div>
            <div class="layer-title">任务层</div>
            <div class="layer-scope">当前任务上下文</div>
          </div>
        </div>
        <div class="layer-tags">
          <span class="ltag">当前 PRD</span>
          <span class="ltag">阶段产物</span>
          <span class="ltag">执行日志</span>
        </div>
        <span class="layer-mode">任务启动时加载</span>
      </div>

    </div>
  </div>

  <!-- ── 经验沉淀反馈 ── -->
  <div class="feedback-row">
    <span class="fb-icon">🔄</span>
    <div class="fb-text">
      每次需求交付完成后，本次的排查路径、关键决策、踩坑经验通过 <strong>Agent 自主知识沉淀</strong> 写回 L2 知识库。下一个类似需求进来时，这些经验会被检索到并直接复用，知识库随迭代持续积累，Agent 对项目的理解越来越深。
    </div>
  </div>

</div>
</body>
</html>


**效果**

该套方案已投入相关领域使用，持续支持需求托管开发，已完成需求开发数量3个。

##### 9.1.2 算法 Agent 需求托管开发

算法需求的开发往往不是从零开始的——团队里已经做过很多类似的预测、分析链路，积累了大量经过验证的设计模式：分层架构怎么搭、特征工程怎么拆、预测策略的优先级怎么设计、数据处理逻辑的边界规则怎么定。这些知识有的在学城文档里，有的隐藏在历史项目的代码里，有的只有做过的人才知道。每次接到新需求，工程师都要花时间去找、去问、去翻，在"弄清楚已有的是什么"上消耗大量精力，才能进入实际的设计阶段。

**knowledge-flow 的角色 —— **将历史算法链路的设计文档、方案沉淀、字段口径说明系统地入库后，Agent 在处理新需求时可以先提取该需求的关键特征（数据来源、预测目标、处理逻辑、边界场景），向知识库检索相似的历史实现。知识库能够识别出高度相似的场景，明确哪些模块可以直接复用、哪些需要适配调整，并给出每个模块的借鉴来源和调整说明。

这个过程的核心价值在于压缩了"探索期"——也就是那段靠翻代码、问同事来理解历史脉络的阶段。有了知识库的检索结果，算法设计可以直接从“已有什么、能借鉴什么”出发，而不是每次都重新梳理一遍。

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>算法 Agent 需求托管开发</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 24px; }
.page-header { text-align: center; margin-bottom: 14px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }

.sec-lbl {
  font-size: 9.5px; font-weight: 700; letter-spacing: .8px;
  text-transform: uppercase; color: #94a3b8; margin-bottom: 8px;
}

/* ── 需求特征卡片行 ── */
.req-strip {
  display: flex; gap: 8px; margin-bottom: 12px; align-items: stretch;
}
.req-label {
  flex: 0 0 72px; background: #f8fafc; border: 1.5px solid #e2e8f0;
  border-radius: 8px; display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; color: #64748b; text-align: center;
  padding: 8px 6px; line-height: 1.4;
}
.req-features { flex: 1; display: flex; gap: 6px; flex-wrap: wrap; align-content: center; }
.rf {
  display: flex; flex-direction: column; gap: 1px;
  background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 7px;
  padding: 6px 10px; flex: 1; min-width: 120px;
}
.rf-key  { font-size: 9.5px; color: #94a3b8; font-weight: 600; letter-spacing: .3px; }
.rf-val  { font-size: 11px; font-weight: 700; color: #1e293b; }

/* ── 检索箭头 ── */
.search-arrow {
  display: flex; align-items: center; justify-content: center; gap: 10px;
  padding: 4px 0; margin-bottom: 12px;
}
.sa-line { flex: 1; height: 1.5px; background: linear-gradient(90deg, #e2e8f0, #818cf8, #e2e8f0); }
.sa-badge {
  flex-shrink: 0; font-size: 11px; font-weight: 700;
  padding: 4px 14px; border-radius: 20px;
  background: #eef2ff; border: 1.5px solid #818cf8; color: #3730a3;
  display: flex; align-items: center; gap: 6px;
}
.sa-icon { font-size: 14px; }

/* ── 相似场景卡片 ── */
.scenarios { display: flex; gap: 10px; margin-bottom: 12px; }
.sc-card {
  flex: 1; border-radius: 10px; border: 1.5px solid;
  overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.04);
  display: flex; flex-direction: column;
}
.sc-card-a { border-color: #bfdbfe; }
.sc-card-b { border-color: #c7d2fe; }

.sc-head {
  padding: 10px 13px; border-bottom: 1.5px solid;
  display: flex; flex-direction: column; gap: 3px;
}
.sc-card-a .sc-head { background: #eff6ff; border-bottom-color: #bfdbfe; }
.sc-card-b .sc-head { background: #eef2ff; border-bottom-color: #c7d2fe; }

.sc-htop { display: flex; align-items: center; gap: 7px; }
.sc-icon { font-size: 15px; }
.sc-name { font-size: 12.5px; font-weight: 700; }
.sc-card-a .sc-name { color: #1e40af; }
.sc-card-b .sc-name { color: #3730a3; }
.sc-sim-badge {
  margin-left: auto; font-size: 9.5px; font-weight: 700;
  padding: 1px 8px; border-radius: 8px;
}
.sc-card-a .sc-sim-badge { background: #dbeafe; color: #1e40af; }
.sc-card-b .sc-sim-badge { background: #e0e7ff; color: #3730a3; }
.sc-sub { font-size: 10.5px; color: #64748b; }

.sc-body { padding: 10px 13px; flex: 1; display: flex; flex-direction: column; gap: 8px; }

.sc-section-lbl { font-size: 9px; font-weight: 700; letter-spacing: .5px; text-transform: uppercase; color: #94a3b8; margin-bottom: 3px; }
.sim-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.sim-tag {
  font-size: 10px; font-weight: 600; padding: 1px 7px; border-radius: 5px;
}
.sc-card-a .sim-tag { background: #dbeafe; color: #1e40af; }
.sc-card-b .sim-tag { background: #e0e7ff; color: #3730a3; }

.borrow-items { display: flex; flex-direction: column; gap: 3px; }
.borrow-item {
  display: flex; align-items: flex-start; gap: 5px;
  font-size: 10.5px; color: #334155; line-height: 1.45;
}
.bi-dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }
.sc-card-a .bi-dot { background: #3b82f6; }
.sc-card-b .bi-dot { background: #6366f1; }

/* ── 复用清单 ── */
.reuse-table {
  border: 1.5px solid #e2e8f0; border-radius: 9px; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.rt-head {
  display: flex; background: #f8fafc; border-bottom: 1.5px solid #e2e8f0;
  padding: 7px 14px;
}
.rth { font-size: 10px; font-weight: 700; color: #64748b; }
.rt-row {
  display: flex; border-bottom: 1px solid #f1f5f9; padding: 7px 14px;
  align-items: center; transition: background .12s;
}
.rt-row:last-child { border-bottom: none; }
.rt-row:hover { background: #f8fafc; }

.rc-module { flex: 0 0 130px; font-size: 11px; font-weight: 600; color: #1e293b; }
.rc-src    { flex: 0 0 120px; display: flex; align-items: center; gap: 5px; }
.rc-adj    { flex: 1; font-size: 10.5px; color: #475569; }

.src-badge {
  font-size: 9.5px; font-weight: 700; padding: 1px 8px; border-radius: 6px;
}
.src-a { background: #dbeafe; color: #1e40af; }
.src-b { background: #e0e7ff; color: #3730a3; }

.adj-badge {
  font-size: 9.5px; font-weight: 700; padding: 1px 7px; border-radius: 6px;
}
.adj-copy   { background: #d1fae5; color: #065f46; }
.adj-adapt  { background: #fef3c7; color: #92400e; }
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>算法 Agent 需求托管开发</h1>
    <p>用历史实现作为新方案的设计参照，从探索期直接进入对齐期</p>
  </div>

  <!-- ── 新需求特征 ── -->
  <div class="sec-lbl">新算法需求的关键特征 &nbsp;→&nbsp; 向知识库查询</div>
  <div class="req-strip">
    <div class="req-features">
      <div class="rf"><span class="rf-key">数据来源</span><span class="rf-val">某类平台数据</span></div>
      <div class="rf"><span class="rf-key">核心目标</span><span class="rf-val">某业务指标预测</span></div>
      <div class="rf"><span class="rf-key">处理逻辑</span><span class="rf-val">多层级数据处理逻辑</span></div>
      <div class="rf"><span class="rf-key">特殊场景</span><span class="rf-val">边界数据的特殊处理</span></div>
    </div>
  </div>

  <!-- ── 检索动作 ── -->
  <div class="search-arrow">
    <div class="sa-line"></div>
    <div class="sa-badge"><span class="sa-icon">📚</span>knowledge-flow 检索 · 命中 2 个高度相似场景</div>
    <div class="sa-line"></div>
  </div>

  <!-- ── 相似场景卡片 ── -->
  <div class="scenarios">

    <div class="sc-card sc-card-a">
      <div class="sc-head">
        <div class="sc-htop">
          <span class="sc-icon">🎯</span>
          <span class="sc-name">历史场景 A</span>
          <span class="sc-sim-badge">高度相似</span>
        </div>
        <span class="sc-sub">数据来源、预测目标、处理逻辑、预测策略四项完全吻合</span>
      </div>
      <div class="sc-body">
        <div>
          <div class="sc-section-lbl">相似维度</div>
          <div class="sim-tags">
            <span class="sim-tag">数据来源相同</span>
            <span class="sim-tag">预测目标相同</span>
            <span class="sim-tag">处理逻辑相同</span>
            <span class="sim-tag">预测策略相同</span>
          </div>
        </div>
        <div>
          <div class="sc-section-lbl">可借鉴的内容</div>
          <div class="borrow-items">
            <div class="borrow-item"><span class="bi-dot"></span>预测策略的优先级设计</div>
            <div class="borrow-item"><span class="bi-dot"></span>系数调节逻辑</div>
            <div class="borrow-item"><span class="bi-dot"></span>数据处理逻辑</div>
            <div class="borrow-item"><span class="bi-dot"></span>核心指标计算逻辑</div>
            <div class="borrow-item"><span class="bi-dot"></span>产出表结构设计</div>
          </div>
        </div>
      </div>
    </div>

    <div class="sc-card sc-card-b">
      <div class="sc-head">
        <div class="sc-htop">
          <span class="sc-icon">🏗️</span>
          <span class="sc-name">历史场景 B</span>
          <span class="sc-sim-badge">业务形态相近</span>
        </div>
        <span class="sc-sub">业务形态相近，工程分层架构与本方案高度契合</span>
      </div>
      <div class="sc-body">
        <div>
          <div class="sc-section-lbl">相似维度</div>
          <div class="sim-tags">
            <span class="sim-tag">业务形态相近</span>
            <span class="sim-tag">分层架构一致</span>
            <span class="sim-tag">特征加工思路相同</span>
          </div>
        </div>
        <div>
          <div class="sc-section-lbl">可借鉴的内容</div>
          <div class="borrow-items">
            <div class="borrow-item"><span class="bi-dot"></span>多层数据链路的分层架构设计</div>
            <div class="borrow-item"><span class="bi-dot"></span>特征加工层的表结构规范</div>
            <div class="borrow-item"><span class="bi-dot"></span>字段口径与命名规范</div>
          </div>
        </div>
      </div>
    </div>

  </div>

  <!-- ── 复用清单 ── -->
  <div class="sec-lbl">模块级复用清单</div>
  <div class="reuse-table">
    <div class="rt-head">
      <span class="rth" style="flex:0 0 130px">设计模块</span>
      <span class="rth" style="flex:0 0 120px">来源场景</span>
      <span class="rth" style="flex:1">调整说明</span>
    </div>
    <div class="rt-row">
      <span class="rc-module">分层架构</span>
      <span class="rc-src"><span class="src-badge src-b">场景 B</span></span>
      <span class="rc-adj"><span class="adj-badge adj-copy">直接复用</span></span>
    </div>
    <div class="rt-row">
      <span class="rc-module">特征加工规范</span>
      <span class="rc-src"><span class="src-badge src-b">场景 B</span></span>
      <span class="rc-adj"><span class="adj-badge adj-adapt">适配调整</span>&ensp;命名规范按本项目适配</span>
    </div>
    <div class="rt-row">
      <span class="rc-module">预测策略优先级</span>
      <span class="rc-src"><span class="src-badge src-a">场景 A</span></span>
      <span class="rc-adj"><span class="adj-badge adj-copy">直接复用</span></span>
    </div>
    <div class="rt-row">
      <span class="rc-module">系数调节逻辑</span>
      <span class="rc-src"><span class="src-badge src-a">场景 A</span></span>
      <span class="rc-adj"><span class="adj-badge adj-adapt">适配调整</span>&ensp;替换为本项目对应数据表</span>
    </div>
    <div class="rt-row">
      <span class="rc-module">数据处理逻辑</span>
      <span class="rc-src"><span class="src-badge src-a">场景 A</span></span>
      <span class="rc-adj"><span class="adj-badge adj-copy">直接复用</span></span>
    </div>
    <div class="rt-row">
      <span class="rc-module">核心指标计算逻辑</span>
      <span class="rc-src"><span class="src-badge src-a">场景 A</span></span>
      <span class="rc-adj"><span class="adj-badge adj-copy">直接复用</span>&ensp;注意字段单位换算</span>
    </div>
  </div>

</div>
</body>
</html>


**效果**

在实际运行的案例中，新算法链路的多个核心模块（分层架构、预测策略、后处理逻辑、指标计算）均来自历史实现的复用，部分模块直接采用，部分做了少量适配调整。需求全托管开发后，交付周期压缩50%+（从12-15PD降至5-6PD），快速完成从0到1的能力搭建。节省的时间，主要来自于不再需要人工 trace 历史架构和代码细节——这两件事过去完全依赖工程师的经验和记忆，现在由知识库承担。

#### 9.2 SKILL 闭环迭代

传统 AI 技能是静态的——知识停留在编写时刻，执行中遇到的卡点只能靠人工解决，经验随任务结束消失。技能自进化机制打破了这一点：执行中产生的新经验被持续沉淀回技能自身，由两层体系支撑：

- **结构化执行日志（DEV_LOG.md）**：实时记录每步的关键决策和遇到的问题。

- **步骤切换检查点**：每个 Stage/Step 完成、进入下一步前，检测触发信号——脚本失败后找到解法、用户纠正方法、步骤遗漏、5+ 工具调用完成非显而易见任务，以及每轮末强制触发一次。命中信号后，经验分类回写各归其位。
至于"归到哪、按什么标准"，正是 knowledge-flow 分层知识结构要解决的问题。

**knowledge-flow 的角色** —— 经验分层承载与检索中枢。知识按容忍度分三层：① SKILL.md（流程主控）：主干 SOP，每次激活首先读取；② references/（步骤必读）：不能容忍遗漏的步骤强制约束（如"链路开发必须先测试再提交"），保留为必读并限制篇幅；③ 外挂知识库（领域背景）：由 knowledge-flow 按需检索，承载可接受遗漏的体量较大的领域背景知识。

三层遵循一条核心判据：**能否容忍检索遗漏 **—— 不能容忍的留在 references 必读，能容忍的下沉到外挂知识库。同时有一条硬约束：任何关键步骤开始前，必须先通过 knowledge-flow 检索知识库，不可跳过。

两条通路的评估方式不同：[SKILL.md](http://SKILL.md) / references 的知识由人工确认，保证必读层准确；外挂知识库走自动化质量管线（候选池 + 多轮汇总 + 评测集评估），支持规模化持续积累。

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SKILL 闭环迭代</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 24px; }
.page-header { text-align: center; margin-bottom: 14px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }

/* ── 效果条 ── */
.metrics-bar { display: flex; gap: 8px; margin-bottom: 14px; }
.metric {
  flex: 1; border-radius: 9px; border: 1.5px solid;
  padding: 12px 16px; display: flex; align-items: center; gap: 12px;
}
.m-green { border-color: #86efac; background: #f0fdf4; }
.m-blue  { border-color: #93c5fd; background: #eff6ff; }
.metric-nums { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.mv { font-size: 22px; font-weight: 800; line-height: 1; }
.m-green .mv { color: #059669; }
.m-blue  .mv { color: #2563eb; }
.mv-label { font-size: 10px; color: #94a3b8; margin-top: 2px; }
.m-arr { font-size: 16px; color: #cbd5e1; }
.metric-sep { width: 1px; background: #e2e8f0; align-self: stretch; flex-shrink: 0; }
.metric-desc { font-size: 11px; color: #475569; line-height: 1.6; }

.sec-lbl { font-size: 9.5px; font-weight: 700; letter-spacing: .8px; text-transform: uppercase; color: #94a3b8; margin-bottom: 8px; }

/* ── 主体两栏 ── */
.main-cols { display: flex; gap: 12px; align-items: flex-start; }
.col-left  { flex: 0 0 300px; display: flex; flex-direction: column; gap: 10px; }
.col-right { flex: 1; display: flex; flex-direction: column; gap: 10px; }

/* ── 三层知识结构 ── */
.layer-stack { display: flex; flex-direction: column; gap: 4px; }
.layer {
  border-radius: 8px; border: 1.5px solid;
  padding: 10px 13px; display: flex; flex-direction: column; gap: 4px;
}
.l-blue   { border-color: #93c5fd; background: #eff6ff; }
.l-green  { border-color: #6ee7b7; background: #ecfdf5; border-width: 2px; }
.l-purple { border-color: #818cf8; background: #eef2ff; }

.layer-head { display: flex; align-items: center; gap: 6px; }
.layer-icon { font-size: 14px; flex-shrink: 0; }
.layer-name { font-size: 12px; font-weight: 700; flex: 1; }
.l-blue   .layer-name { color: #1e40af; }
.l-green  .layer-name { color: #065f46; }
.l-purple .layer-name { color: #3730a3; }
.layer-role {
  font-size: 9.5px; font-weight: 700; padding: 1px 7px;
  border-radius: 6px; flex-shrink: 0;
}
.l-blue   .layer-role { background: #dbeafe; color: #1e40af; }
.l-green  .layer-role { background: #d1fae5; color: #065f46; }
.l-purple .layer-role { background: #e0e7ff; color: #3730a3; }
.layer-desc { font-size: 10.5px; color: #64748b; line-height: 1.55; }
.kf-badge {
  font-size: 9px; font-weight: 700; padding: 1px 7px; border-radius: 8px;
  background: #4f46e5; color: #fff; align-self: flex-start;
}
.must-badge {
  font-size: 9px; font-weight: 700; padding: 1px 7px; border-radius: 8px;
  background: #059669; color: #fff; align-self: flex-start;
}
.layer-arr { text-align: center; font-size: 10px; color: #cbd5e1; line-height: 1; padding: 1px 0; }

.hard-rule {
  background: #fef9c3; border: 1.5px solid #fde047; border-radius: 8px;
  padding: 8px 12px; font-size: 10.5px; color: #78350f; line-height: 1.65;
}

/* ── 自进化步骤 (竖向) ── */
.evo-steps { display: flex; flex-direction: column; }

.evo-step {
  display: flex; gap: 12px; align-items: flex-start;
  padding: 12px 14px;
  border: 1.5px solid #e2e8f0; border-radius: 9px;
  background: #ffffff;
  transition: box-shadow .15s;
}
.evo-step:hover { box-shadow: 0 2px 10px rgba(0,0,0,.07); }

.evo-step.step-exec   { border-color: #e2e8f0; background: #f8fafc; }
.evo-step.step-check  { border-color: #fde68a; background: #fffbeb; }
.evo-step.step-write  { border-color: #c4b5fd; background: #f5f3ff; }
.evo-step.step-result { border-color: #86efac; background: #f0fdf4; }

.evo-icon { font-size: 18px; flex-shrink: 0; margin-top: 1px; }
.evo-body { flex: 1; min-width: 0; }
.evo-name { font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
.evo-desc { font-size: 11px; color: #475569; line-height: 1.6; }

.trigger-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.tt { font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 5px; background: #fef3c7; color: #92400e; }
.tt-force { background: #fee2e2; color: #991b1b; }

.write-targets { display: flex; flex-direction: column; gap: 4px; margin-top: 6px; }
.wt { font-size: 11px; color: #475569; display: flex; gap: 6px; align-items: center; }
.wt-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.wt-kb  { background: #6366f1; }
.wt-ref { background: #059669; }

/* 步骤间连接线 */
.step-connector {
  display: flex; justify-content: flex-start; align-items: center;
  padding-left: 26px; height: 16px;
}
.step-conn-line { width: 2px; height: 100%; background: #e2e8f0; }

/* ── 晋升路径 ── */
.promo-bar {
  display: flex; align-items: flex-start; gap: 10px;
  background: #f5f3ff; border: 1.5px solid #c4b5fd; border-radius: 9px;
  padding: 10px 14px;
}
.promo-icon { font-size: 16px; flex-shrink: 0; margin-top: 1px; }
.promo-text { font-size: 11px; color: #4c1d95; line-height: 1.7; }
.promo-text strong { color: #3730a3; }
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>SKILL 闭环迭代</h1>
    <p>技能在执行中消费知识、生产经验，实现越用越强的自进化闭环</p>
  </div>

  <!-- ── 效果条 ── -->
  <div class="metrics-bar">
    <div class="metric m-green">
      <div class="metric-nums">
        <div><div class="mv">30%</div><div class="mv-label">优化前成功率</div></div>
        <span class="m-arr">→</span>
        <div><div class="mv">80-90%</div><div class="mv-label">多轮迭代后</div></div>
      </div>
      <div class="metric-sep"></div>
      <div class="metric-desc">全流程托管成功率显著提升，技能对执行细节的覆盖随迭代渐进收敛</div>
    </div>
    <div class="metric m-blue">
      <div class="metric-nums">
        <div><div class="mv">60%↓</div><div class="mv-label">人工干预减少</div></div>
      </div>
      <div class="metric-sep"></div>
      <div class="metric-desc">常见的卡点通过自动经验积累逐步消除，越用越少需要人工介入</div>
    </div>
  </div>

  <div class="main-cols">

    <!-- 左：三层知识结构 -->
    <div class="col-left">
      <div class="sec-lbl">三层知识结构（消费侧）</div>

      <div class="layer-stack">
        <div class="layer l-blue">
          <div class="layer-head">
            <span class="layer-icon">📋</span>
            <span class="layer-name">SKILL.md</span>
            <span class="layer-role">流程主控</span>
          </div>
          <div class="layer-desc">流程主控，定义阶段划分与步骤编排。每次激活首先读取。</div>
        </div>
        <div class="layer-arr">↓ 进入步骤前必读</div>
        <div class="layer l-green">
          <div class="layer-head">
            <span class="layer-icon">📁</span>
            <span class="layer-name">references/</span>
            <span class="layer-role">步骤必读</span>
          </div>
          <div class="layer-desc">步骤强制约束，不能容忍检索遗漏，保留为必读并限制篇幅。</div>
          <span class="must-badge">不可跳过 · 直接加载</span>
        </div>
        <div class="layer-arr">↓ 领域背景按需检索</div>
        <div class="layer l-purple">
          <div class="layer-head">
            <span class="layer-icon">🔍</span>
            <span class="layer-name">外挂知识库 kf</span>
            <span class="layer-role">领域知识</span>
          </div>
          <div class="layer-desc">领域背景与历史经验，可容忍遗漏，体量大，按需检索。</div>
          <span class="kf-badge">knowledge-flow 驱动</span>
        </div>
      </div>

      <div class="hard-rule">
        ⚡ <strong>硬约束</strong>：关键执行阶段每个步骤开始前，<strong>必须先通过 knowledge-flow 检索知识库</strong>，确认有无相关规范或踩坑记录，不可跳过。
      </div>
    </div>

    <!-- 右：自进化竖向流 -->
    <div class="col-right">
      <div class="sec-lbl">自进化机制（生产侧）</div>

      <div class="evo-steps">

        <div class="evo-step step-exec">
          <span class="evo-icon">⚙️</span>
          <div class="evo-body">
            <div class="evo-name">执行步骤</div>
            <div class="evo-desc">按流程逐步推进，必读 references、按需检索知识库，实时记录 DEV_LOG.md。</div>
          </div>
        </div>
        <div class="step-connector"><div class="step-conn-line"></div></div>

        <div class="evo-step step-check">
          <span class="evo-icon">🔔</span>
          <div class="evo-body">
            <div class="evo-name">步骤切换检查点</div>
            <div class="evo-desc">每步完成、进入下一步前，检测是否触发自进化信号：</div>
            <div class="trigger-tags">
              <span class="tt">脚本失败后找到解法</span>
              <span class="tt">用户纠正了方法</span>
              <span class="tt">步骤有遗漏或错误</span>
              <span class="tt">5+ 工具调用完成非显而易见任务</span>
              <span class="tt tt-force">Step6 完成时强制触发</span>
            </div>
          </div>
        </div>
        <div class="step-connector"><div class="step-conn-line"></div></div>

        <div class="evo-step step-write">
          <span class="evo-icon">✍️</span>
          <div class="evo-body">
            <div class="evo-name">经验分类回写</div>
            <div class="evo-desc">按能否容忍遗漏确定写入位置：</div>
            <div class="write-targets">
              <div class="wt"><span class="wt-dot wt-ref"></span>不能容忍遗漏的强制约束 → <strong>references/ 必读</strong>（人工确认）</div>
              <div class="wt"><span class="wt-dot wt-kb"></span>可容忍遗漏的领域经验 → <strong>外挂知识库 kf</strong>（候选池 + 评测集）</div>
            </div>
          </div>
        </div>
        <div class="step-connector"><div class="step-conn-line"></div></div>

        <div class="evo-step step-result">
          <span class="evo-icon">📈</span>
          <div class="evo-body">
            <div class="evo-name">下轮执行更强</div>
            <div class="evo-desc">知识库与必读层积累了新经验，下次执行同类步骤时直接命中，不再重复踩坑。多轮迭代后，覆盖率渐进收敛。</div>
          </div>
        </div>

      </div>

      <div class="promo-bar">
        <span class="promo-icon">⬆️</span>
        <div class="promo-text">
          <strong>SKILL.md / references</strong> 的沉淀由<strong>人工确认</strong>，保证必读层准确；<strong>外挂知识库</strong>走自动化质量管线（候选池 + 多轮汇总 + 评测集），支持规模化积累。
        </div>
      </div>

    </div>
  </div>

</div>
</body>
</html>


**效果**

全流程托管成功率从约 30% 提升至 80-90%，人工干预减少约 60%。改善是渐进收敛的 —— 随经验库积累，常见卡点逐步被知识覆盖，技能对执行细节的掌握持续完善。这一阶段的收益主要来自流程执行层面。进入第二阶段的算法指标闭环迭代后，同样的知识沉淀机制将延续，每轮实验的分析结论和调参依据同样写回知识库，为后续迭代提供参照。

#### 9.3 群答疑助手

业务团队日常会收到业务问题 —— 某个 case 按规则该怎么判断、某条数据是否符合标准、某类情况应该走哪个处理路径。这些问题需要熟悉业务规则的人来解答，但规则文档散落在学城各处，答疑全靠人工既耗时又不稳定，不同人的解答也未必一致。

**knowledge-flow 的角色 —— **首先用知识库冷启工具对存量业务规则文档进行质量精判和分类建档，形成结构化的初始知识库，并通过 Git 仓库管理，支持多人协同维护。之后将知识库挂载到 CatClaw 群聊虾机器人，加入业务群后，成员 @ 机器人提问即可获得响应。知识库接入后，Agent 每次回答前先检索知识库，加载相关规则后再作答，回答中会明确引用规则依据，结论清晰，边界情况有规则支撑。群里出现"📚 知识库：已加载"的标识，意味着这条回答是有规则根据的。

**知识持续积累**

使用过程中，如若 Agent 给出了错误判断，团队成员可以在群中指出正确答案并解释原因，同时指示 Agent 将本次经验写入知识库。Agent 完成写入后，随后继续使用 —— 整个纠错和入库的过程在群聊对话里完成，没有额外操作成本。随着使用积累，知识库的覆盖越来越完整，曾经需要反复解释的边界情况逐步沉淀为知识条目，后续遇到同类问题时直接命中，不再需要人工解答。

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>群答疑助手</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 24px; }
.page-header { text-align: center; margin-bottom: 14px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }
.sec-lbl { font-size: 9.5px; font-weight: 700; letter-spacing: .8px; text-transform: uppercase; color: #94a3b8; margin-bottom: 8px; }

/* ── 系统架构条 ── */
.arch-bar {
  display: flex; align-items: center; gap: 0;
  background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 9px;
  padding: 12px 16px; margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.arch-node {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px;
  text-align: center;
}
.an-icon { font-size: 22px; }
.an-name { font-size: 11.5px; font-weight: 700; color: #1e293b; }
.an-sub  { font-size: 10px; color: #94a3b8; line-height: 1.4; }
.an-badge {
  font-size: 9px; font-weight: 700; padding: 1px 7px; border-radius: 8px; margin-top: 2px;
}
.ab-blue   { background: #dbeafe; color: #1e40af; }
.ab-purple { background: #e0e7ff; color: #3730a3; }
.ab-green  { background: #d1fae5; color: #065f46; }

.arch-arr {
  flex: 0 0 32px; display: flex; align-items: center; justify-content: center;
  font-size: 16px; color: #cbd5e1;
}

/* ── 主体两栏 ── */
.main-cols { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 10px; }
.col-l { flex: 1; display: flex; flex-direction: column; gap: 10px; }
.col-r { flex: 1; display: flex; flex-direction: column; gap: 10px; }

/* ── 回答对比 ── */
.answer-card {
  border-radius: 9px; border: 1.5px solid; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.ac-head {
  padding: 9px 13px; border-bottom: 1.5px solid;
  display: flex; align-items: center; gap: 7px;
}
.ac-icon { font-size: 14px; }
.ac-title { font-size: 12px; font-weight: 700; flex: 1; }
.ac-mode {
  font-size: 9.5px; font-weight: 700; padding: 1px 7px; border-radius: 8px;
}

.no-kb { border-color: #e2e8f0; }
.no-kb .ac-head { background: #f8fafc; border-bottom-color: #e2e8f0; }
.no-kb .ac-title { color: #64748b; }
.no-kb .ac-mode { background: #f1f5f9; color: #64748b; }

.with-kb { border-color: #818cf8; }
.with-kb .ac-head { background: #eef2ff; border-bottom-color: #c7d2fe; }
.with-kb .ac-title { color: #3730a3; }
.with-kb .ac-mode { background: #e0e7ff; color: #3730a3; }

.ac-body { padding: 11px 13px; display: flex; flex-direction: column; gap: 7px; }

/* 对话气泡 */
.bubble-user {
  align-self: flex-end; background: #eff6ff; border: 1.5px solid #bfdbfe;
  border-radius: 10px 10px 2px 10px;
  padding: 6px 10px; font-size: 11px; color: #1e40af; max-width: 85%;
}
.bubble-bot {
  align-self: flex-start; background: #f8fafc; border: 1.5px solid #e2e8f0;
  border-radius: 10px 10px 10px 2px;
  padding: 8px 11px; font-size: 11px; color: #334155; max-width: 95%; line-height: 1.65;
}
.bubble-bot.kb-answer { border-color: #c7d2fe; background: #f5f3ff; }

.kb-indicator {
  display: flex; align-items: center; gap: 5px;
  font-size: 9.5px; color: #6366f1; font-weight: 600; margin-top: 4px;
}
.kbi-icon { font-size: 11px; }

.answer-diff {
  display: flex; gap: 6px; flex-wrap: wrap; margin-top: 3px;
}
.diff-tag {
  font-size: 10px; font-weight: 600; padding: 1px 7px; border-radius: 5px;
}
.dt-good { background: #d1fae5; color: #065f46; }
.dt-bad  { background: #fee2e2; color: #991b1b; }

/* ── 实时纠错入库 ── */
.feedback-flow { display: flex; flex-direction: column; gap: 5px; }

.ff-step {
  display: flex; gap: 10px; align-items: flex-start;
  padding: 9px 12px; border-radius: 8px; border: 1.5px solid;
}
.ff-step.s-wrong  { border-color: #fca5a5; background: #fff5f5; }
.ff-step.s-correct{ border-color: #fde68a; background: #fffbeb; }
.ff-step.s-write  { border-color: #c4b5fd; background: #f5f3ff; }
.ff-step.s-verify { border-color: #86efac; background: #f0fdf4; }

.ffs-icon { font-size: 16px; flex-shrink: 0; margin-top: 1px; }
.ffs-body { flex: 1; }
.ffs-name { font-size: 11.5px; font-weight: 700; margin-bottom: 3px; }
.s-wrong  .ffs-name { color: #dc2626; }
.s-correct .ffs-name { color: #92400e; }
.s-write  .ffs-name { color: #6d28d9; }
.s-verify .ffs-name { color: #059669; }
.ffs-desc { font-size: 10.5px; color: #475569; line-height: 1.55; }

.ff-arr { text-align: center; font-size: 10px; color: #cbd5e1; line-height: 1; padding: 1px 0; }
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>群答疑助手</h1>
    <p>知识库冷启建档 · 挂载群聊机器人 · 答疑中实时积累经验</p>
  </div>

  <!-- ── 系统架构条 ── -->
  <div class="arch-bar">
    <div class="arch-node">
      <span class="an-icon">💬</span>
      <span class="an-name">业务群聊</span>
      <span class="an-sub">成员 @机器人<br>提出问题</span>
    </div>
    <div class="arch-arr">→</div>
    <div class="arch-node">
      <span class="an-icon">🤖</span>
      <span class="an-name">CatClaw 群聊虾</span>
      <span class="an-sub">群聊 AI 机器人<br>接收 @ 消息并响应</span>
      <span class="an-badge ab-blue">Agent 基建</span>
    </div>
    <div class="arch-arr">→</div>
    <div class="arch-node">
      <span class="an-icon">📚</span>
      <span class="an-name">knowledge-flow 知识库</span>
      <span class="an-sub">业务规则 + 历史案例<br>冷启建档 + 持续积累</span>
      <span class="an-badge ab-purple">knowledge-flow 管理</span>
    </div>
    <div class="arch-arr">→</div>
    <div class="arch-node">
      <span class="an-icon">✅</span>
      <span class="an-name">有规则依据的答案</span>
      <span class="an-sub">引用知识库条目<br>来源清晰可追溯</span>
      <span class="an-badge ab-green">精准可溯源</span>
    </div>
  </div>

  <div class="main-cols">

    <!-- 左：有无知识库对比 -->
    <div class="col-l">
      <div class="sec-lbl">有无知识库的回答差异</div>

      <div class="answer-card no-kb">
        <div class="ac-head">
          <span class="ac-icon">💭</span>
          <span class="ac-title">未检索知识库</span>
          <span class="ac-mode">纯 LLM 推理</span>
        </div>
        <div class="ac-body">
          <div class="bubble-user">这个 case 按规则应该怎么判断？</div>
          <div class="bubble-bot">
            从两方面来看，一方面…另一方面…如果实际情况 A，则结论为 X；如果是情况 B，则结论为 Y。建议结合具体数据进一步判断。
          </div>
          <div class="answer-diff">
            <span class="diff-tag dt-bad">无规则依据</span>
            <span class="diff-tag dt-bad">结论模糊</span>
            <span class="diff-tag dt-bad">边界情况未处理</span>
          </div>
        </div>
      </div>

      <div class="answer-card with-kb">
        <div class="ac-head">
          <span class="ac-icon">📚</span>
          <span class="ac-title">检索知识库后作答</span>
          <span class="ac-mode">规则驱动</span>
        </div>
        <div class="ac-body">
          <div class="bubble-user">这个 case 按规则应该怎么判断？</div>
          <div class="bubble-bot kb-answer">
            知识库已在本次会话中检索过，关键规则已加载。<br><br>
            依据《业务规则文档》第 X 条：满足条件 A 时判断为结论 Y；不满足时判断为结论 Z。本 case 符合条件 A，结论：<strong>Y</strong>。
            <div class="kb-indicator"><span class="kbi-icon">📚</span>知识库：规则文档已加载</div>
          </div>
          <div class="answer-diff">
            <span class="diff-tag dt-good">引用具体规则条款</span>
            <span class="diff-tag dt-good">结论明确</span>
            <span class="diff-tag dt-good">边界情况有依据</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右：实时纠错入库 -->
    <div class="col-r">
      <div class="sec-lbl">实时纠错 → 即时入库 → 下次更准</div>

      <div class="feedback-flow">

        <div class="ff-step s-wrong">
          <span class="ffs-icon">❌</span>
          <div class="ffs-body">
            <div class="ffs-name">Agent 给出错误结论</div>
            <div class="ffs-desc">某条 case 的判断结果有误——Agent 引用了错误的规则分支，或规则边界不清晰导致判断偏差。</div>
          </div>
        </div>
        <div class="ff-arr">↓</div>

        <div class="ff-step s-correct">
          <span class="ffs-icon">💬</span>
          <div class="ffs-body">
            <div class="ffs-name">用户在群里给出正确答案</div>
            <div class="ffs-desc">团队成员指出错误根因，解释正确的规则适用逻辑，并指示 Agent 将本次经验写入知识库。</div>
          </div>
        </div>
        <div class="ff-arr">↓</div>

        <div class="ff-step s-write">
          <span class="ffs-icon">✍️</span>
          <div class="ffs-body">
            <div class="ffs-name">Agent 即时写入知识库</div>
            <div class="ffs-desc">在指定目录下新增历史案例条目，记录原始数据、错误根因、正确规则依据和规避方法。更新 data_structure.md 和关键词索引，推送 Git。</div>
          </div>
        </div>
        <div class="ff-arr">↓</div>

        <div class="ff-step s-verify">
          <span class="ffs-icon">✅</span>
          <div class="ffs-body">
            <div class="ffs-name">知识沉淀，下次复用</div>
            <div class="ffs-desc">经验写入知识库，下次遇到同类问题时直接命中，不再依赖人工解答，也不再误判。</div>
          </div>
        </div>

      </div>
    </div>
  </div>


</div>
</body>
</html>


**效果**

已投入使用，持续解答业务相关问题，效果符合预期，产品持续推广中。

#### 9.4 CASE自主排查

传统排查型 Skill 的常见设计是“大 Skill + 硬编码 SOP”：把所有排查类型的步骤和 SQL 模板写在 Skill 文件里，靠意图路由跳转到对应分支执行。这种模式的问题随规模暴露 —— 新增排查类型必须修改 Skill 文件，维护成本线性上升；排查路径固定，无法根据实际数据动态调整，即便中途已经找到根因，也得机械地把剩余步骤走完。

**knowledge-flow 的角色 —— **新的设计把排查知识从 Skill 文件里彻底抽出来，沉淀到独立的知识库，让 Agent 通过检索知识、形成假设、收集证据来动态完成排查。Skill 本身只定义执行框架，不含任何业务知识。

知识库分四层：① **线索层**是核心，每个文件对应一个假设方向，内部包含触发信号、支持证据、否定证据和验证动作——Agent 拿到的是完整的"何时触发假设 → 如何验证 → 如何排除"推理框架，而不是执行清单；② **案例层**记录真实排查过程的完整 by-case 文档，保留无法泛化的边界细节；③ **SQL 参考库**存放带参数占位符和陷阱注释的查询模板，被线索层验证动作按需引用；④ **原子层**描述客观事实，包含表结构参考、指标计算口径和字段速查（含常见查询陷阱）。四层知识库均通过 knowledge-flow 管理和检索。

执行框架如图中所示，分为 6 个阶段。排查结束后触发知识沉淀，形成知识闭环。随着实际使用，线索层的触发条件越来越准确，案例层的覆盖越来越完整，整个排查体系在使用中持续精化。

<!-- HTML 内容 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CASE 自主排查</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #ffffff; color: #1e293b;
}
.page { width: 858px; padding: 18px 20px 24px; }
.page-header { text-align: center; margin-bottom: 12px; }
.page-header h1 { font-size: 16.5px; font-weight: 700; color: #0f172a; letter-spacing: .5px; }
.page-header p  { font-size: 12px; color: #94a3b8; margin-top: 3px; }

.sec-lbl { font-size: 9.5px; font-weight: 700; letter-spacing: .8px; text-transform: uppercase; color: #94a3b8; margin-bottom: 8px; }

/* ── 对比条 ── */
.contrast {
  display: flex; gap: 0; margin-bottom: 12px;
  border: 1.5px solid #e2e8f0; border-radius: 9px; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.contrast-col {
  flex: 1; padding: 12px 16px; display: flex; flex-direction: column; gap: 6px;
}
.contrast-col.old { background: #fafafa; border-right: 1.5px solid #e2e8f0; }
.contrast-col.new { background: #f0fdf4; }
.cc-label { font-size: 10px; font-weight: 700; letter-spacing: .5px; text-transform: uppercase; }
.old .cc-label { color: #94a3b8; }
.new .cc-label { color: #059669; }
.cc-title { font-size: 12.5px; font-weight: 700; }
.old .cc-title { color: #64748b; }
.new .cc-title { color: #065f46; }
.cc-items { display: flex; flex-direction: column; gap: 3px; }
.cc-item { font-size: 10.5px; color: #475569; display: flex; gap: 6px; align-items: flex-start; }
.cci-dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }
.old .cci-dot { background: #cbd5e1; }
.new .cci-dot { background: #22c55e; }
.contrast-arrow {
  flex: 0 0 36px; display: flex; align-items: center; justify-content: center;
  font-size: 18px; color: #cbd5e1; background: #f8fafc;
}

/* ── 主体两栏 ── */
.main-cols { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 10px; }
.col-phases { flex: 0 0 200px; display: flex; flex-direction: column; }
.col-kb     { flex: 1; display: flex; flex-direction: column; gap: 8px; }

/* ── 6阶段流程 ── */
.phase {
  border-radius: 7px; border: 1.5px solid #e2e8f0;
  background: #fff; padding: 8px 11px;
  display: flex; align-items: flex-start; gap: 8px;
}
.phase.p-key { border-color: #818cf8; background: #eef2ff; }
.phase.p-feed { border-color: #86efac; background: #f0fdf4; }

.phase-num {
  flex-shrink: 0; width: 20px; height: 20px; border-radius: 50%;
  background: #e2e8f0; display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 800; color: #64748b; margin-top: 1px;
}
.p-key  .phase-num { background: #4f46e5; color: #fff; }
.p-feed .phase-num { background: #059669; color: #fff; }

.phase-body { flex: 1; }
.phase-name { font-size: 11px; font-weight: 700; color: #0f172a; }
.phase-desc { font-size: 10px; color: #64748b; margin-top: 2px; line-height: 1.4; }
.phase-badge {
  font-size: 9px; font-weight: 700; padding: 1px 6px; border-radius: 5px;
  display: inline-block; margin-top: 3px;
}
.pb-indigo { background: #e0e7ff; color: #3730a3; }
.pb-green  { background: #d1fae5; color: #065f46; }

.phase-arr { text-align: center; font-size: 10px; color: #e2e8f0; line-height: 1; padding: 2px 0; }

/* 假设集示例 */
.hypo-sample {
  margin-top: 4px; background: #fff; border: 1px solid #c7d2fe;
  border-radius: 5px; padding: 5px 7px; overflow: hidden;
}
.hs-row { display: flex; gap: 6px; font-size: 9.5px; border-bottom: 1px solid #f1f5f9; padding: 2px 0; }
.hs-row:last-child { border-bottom: none; }
.hs-dir { flex: 1; color: #334155; }
.hs-conf { flex-shrink: 0; font-weight: 700; }
.conf-h { color: #dc2626; }
.conf-m { color: #d97706; }

/* ── 知识库4层 ── */
.kb-layers { display: flex; flex-direction: column; gap: 6px; }
.kbl {
  border-radius: 8px; border: 1.5px solid;
  padding: 10px 13px; display: flex; gap: 10px; align-items: flex-start;
}
.kbl-core   { border-color: #818cf8; background: #eef2ff; border-width: 2px; }
.kbl-case   { border-color: #6ee7b7; background: #ecfdf5; }
.kbl-sql    { border-color: #93c5fd; background: #eff6ff; }
.kbl-atom   { border-color: #e2e8f0; background: #f8fafc; }

.kbl-left { flex: 0 0 auto; display: flex; flex-direction: column; align-items: center; gap: 3px; }
.kbl-icon { font-size: 18px; }
.kbl-badge {
  font-size: 9px; font-weight: 700; padding: 1px 6px; border-radius: 5px;
  text-align: center; white-space: nowrap;
}
.kbl-core .kbl-badge   { background: #e0e7ff; color: #3730a3; }
.kbl-case .kbl-badge   { background: #d1fae5; color: #065f46; }
.kbl-sql  .kbl-badge   { background: #dbeafe; color: #1e40af; }
.kbl-atom .kbl-badge   { background: #f1f5f9; color: #64748b; }

.kbl-body { flex: 1; }
.kbl-name { font-size: 12px; font-weight: 700; }
.kbl-core .kbl-name { color: #3730a3; }
.kbl-case .kbl-name { color: #065f46; }
.kbl-sql  .kbl-name { color: #1e40af; }
.kbl-atom .kbl-name { color: #334155; }

.kbl-desc { font-size: 10.5px; color: #475569; line-height: 1.55; margin-top: 3px; }
.kbl-sub { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 5px; }
.ks { font-size: 9.5px; padding: 1px 7px; border-radius: 5px; }
.kbl-core .ks { background: #e0e7ff; color: #4338ca; }
.kbl-case .ks { background: #d1fae5; color: #065f46; }
.kbl-sql  .ks { background: #dbeafe; color: #1d4ed8; }
.kbl-atom .ks { background: #f1f5f9; color: #475569; }

/* ── Phase 5 反馈闭环 ── */
.feedback-wrap {
  border: 1.5px solid #e2e8f0; border-radius: 10px; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.fb-header {
  background: #f0fdf4; border-bottom: 1.5px solid #bbf7d0;
  padding: 9px 16px; display: flex; align-items: center; gap: 8px;
}
.fb-icon  { font-size: 15px; }
.fb-title { font-size: 12.5px; font-weight: 700; color: #065f46; flex: 1; }
.fb-q { font-size: 11px; color: #065f46; font-style: italic; }

.fb-body { display: flex; gap: 0; }
.fb-path {
  flex: 1; padding: 12px 14px; display: flex; flex-direction: column; gap: 7px;
}
.fb-path.correct { border-right: 1px solid #f1f5f9; }
.fb-path-head { display: flex; align-items: center; gap: 6px; margin-bottom: 2px; }
.fph-icon { font-size: 14px; }
.fph-label { font-size: 11.5px; font-weight: 700; }
.correct .fph-label { color: #065f46; }
.wrong   .fph-label { color: #dc2626; }

.fb-step { font-size: 10.5px; color: #475569; line-height: 1.6; display: flex; gap: 6px; align-items: flex-start; }
.fbs-dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; margin-top: 5px; }
.correct .fbs-dot { background: #22c55e; }
.wrong   .fbs-dot { background: #f87171; }

.constraint-note {
  margin-top: 6px; padding: 6px 10px; border-radius: 6px; font-size: 10px; line-height: 1.55;
}
.cn-green { background: #dcfce7; color: #065f46; border: 1px solid #86efac; }
.cn-red   { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
</style>
</head>
<body>
<div class="page">

  <div class="page-header">
    <h1>CASE 自主排查</h1>
    <p>从硬编码 SOP 到证据驱动排查 · 知识驱动假设形成 · 排查经验持续积累</p>
  </div>

  <!-- ── 新旧对比 ── -->
  <div class="contrast">
    <div class="contrast-col old">
      <span class="cc-label">旧模式</span>
      <span class="cc-title">硬编码 SOP</span>
      <div class="cc-items">
        <div class="cc-item"><span class="cci-dot"></span>排查步骤写在 skill 文件里，新类型必须改 skill</div>
        <div class="cc-item"><span class="cci-dot"></span>路径固定，机械走完步骤 1→2→3，无法提前收敛</div>
        <div class="cc-item"><span class="cci-dot"></span>每次排查从零开始，经验无处积累</div>
      </div>
    </div>
    <div class="contrast-arrow">→</div>
    <div class="contrast-col new">
      <span class="cc-label">新模式</span>
      <span class="cc-title">证据驱动排查</span>
      <div class="cc-items">
        <div class="cc-item"><span class="cci-dot"></span>skill 只定义执行框架，业务知识全部在知识库</div>
        <div class="cc-item"><span class="cci-dot"></span>假设集驱动，证据足够时提前收敛，发现新线索时动态插入</div>
        <div class="cc-item"><span class="cci-dot"></span>Phase 5 自动沉淀，线索层逐步精化</div>
      </div>
    </div>
  </div>

  <!-- ── 主体 ── -->
  <div class="main-cols">

    <!-- 左：6 阶段 -->
    <div class="col-phases">
      <div class="sec-lbl">执行框架（6 阶段）</div>

      <div class="phase">
        <span class="phase-num">0</span>
        <div class="phase-body">
          <div class="phase-name">意图识别</div>
          <div class="phase-desc">提取业务对象 ID、日期、异常描述</div>
        </div>
      </div>
      <div class="phase-arr">↓</div>

      <div class="phase p-key">
        <span class="phase-num">1</span>
        <div class="phase-body">
          <div class="phase-name">知识检索</div>
          <div class="phase-desc">检索线索层，形成初始假设集</div>
          <span class="phase-badge pb-indigo">knowledge-flow</span>
        </div>
      </div>
      <div class="phase-arr">↓</div>

      <div class="phase p-key">
        <span class="phase-num">2</span>
        <div class="phase-body">
          <div class="phase-name">规划输出</div>
          <div class="phase-desc">假设集 + 置信度，用户确认后执行</div>
          <div class="hypo-sample">
            <div class="hs-row"><span class="hs-dir">假设方向 A</span><span class="hs-conf conf-h">高</span></div>
            <div class="hs-row"><span class="hs-dir">假设方向 B</span><span class="hs-conf conf-m">中</span></div>
          </div>
        </div>
      </div>
      <div class="phase-arr">↓</div>

      <div class="phase">
        <span class="phase-num">3</span>
        <div class="phase-body">
          <div class="phase-name">逐步执行</div>
          <div class="phase-desc">每步结果动态更新假设置信度</div>
        </div>
      </div>
      <div class="phase-arr">↓</div>

      <div class="phase">
        <span class="phase-num">4</span>
        <div class="phase-body">
          <div class="phase-name">结论输出</div>
          <div class="phase-desc">根因定位 + 佐证数据 + 处理建议</div>
        </div>
      </div>
      <div class="phase-arr">↓</div>

      <div class="phase p-feed">
        <span class="phase-num">5</span>
        <div class="phase-body">
          <div class="phase-name">知识反馈</div>
          <div class="phase-desc">沉淀新知识或修正错误线索</div>
          <span class="phase-badge pb-green">闭环关键</span>
        </div>
      </div>
    </div>

    <!-- 右：知识库4层 -->
    <div class="col-kb">
      <div class="sec-lbl">知识库结构（knowledge-flow 管理）</div>

      <div class="kb-layers">
        <div class="kbl kbl-core">
          <div class="kbl-left">
            <span class="kbl-icon">🎯</span>
            <span class="kbl-badge">线索层<br>核心</span>
          </div>
          <div class="kbl-body">
            <div class="kbl-name">线索层 — 假设驱动的推理框架</div>
            <div class="kbl-desc">统一结构：触发信号 / 支持证据 / 否定证据 / 验证动作，给 Agent「触发→验证→排除」完整推理框架，而不是执行清单。</div>
          </div>
        </div>

        <div class="kbl kbl-case">
          <div class="kbl-left">
            <span class="kbl-icon">📂</span>
            <span class="kbl-badge">案例层</span>
          </div>
          <div class="kbl-body">
            <div class="kbl-name">案例层 — 真实排查过程记录</div>
            <div class="kbl-desc">真实排查记录，保留边界条件和踩坑细节。线索层是通用规则，案例层补充无法泛化的细节。</div>
          </div>
        </div>

        <div class="kbl kbl-sql">
          <div class="kbl-left">
            <span class="kbl-icon">🗄️</span>
            <span class="kbl-badge">SQL<br>参考库</span>
          </div>
          <div class="kbl-body">
            <div class="kbl-name">SQL 参考库 — 带陷阱注释的查询模板</div>
            <div class="kbl-desc">带陷阱注释的查询模板，由线索层验证动作按需引用。</div>
          </div>
        </div>

        <div class="kbl kbl-atom">
          <div class="kbl-left">
            <span class="kbl-icon">🔩</span>
            <span class="kbl-badge">原子层</span>
          </div>
          <div class="kbl-body">
            <div class="kbl-name">原子层 — 客观事实描述</div>
            <div class="kbl-desc">客观事实描述，三个子目录：</div>
            <div class="kbl-sub">
              <span class="ks">表结构参考</span>
              <span class="ks">指标计算口径</span>
              <span class="ks">字段速查（含查询陷阱）</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ── Phase 5 反馈闭环 ── -->
  <div class="sec-lbl">Phase 5 · 知识反馈闭环</div>
  <div class="feedback-wrap">
    <div class="fb-header">
      <span class="fb-icon">🔄</span>
      <span class="fb-title">知识反馈</span>
      <span class="fb-q">「这次排查结论是否正确？」</span>
    </div>
    <div class="fb-body">

      <div class="fb-path correct">
        <div class="fb-path-head"><span class="fph-icon">✅</span><span class="fph-label">正确路线</span></div>
        <div class="fb-step"><span class="fbs-dot"></span>判断是否产生新知识，输出审查报告，用户确认后写入</div>
        <div class="constraint-note cn-green">
          📌 案例层可自动写入；<strong>线索层修改必须人工确认</strong>。
        </div>
      </div>

      <div class="fb-path wrong">
        <div class="fb-path-head"><span class="fph-icon">❌</span><span class="fph-label">错误路线</span></div>
        <div class="fb-step"><span class="fbs-dot"></span>追问正确根因，对错误命中的假设逐一归因</div>
        <div class="fb-step"><span class="fbs-dot"></span>归因类型：触发信号过宽 / 执行判断失误 / 线索层缺失</div>
        <div class="fb-step"><span class="fbs-dot"></span>提议修正动作</div>
        <div class="constraint-note cn-red">
          🚫 禁止静默修改线索层，修改必须经用户确认。
        </div>
      </div>

    </div>
  </div>

</div>
</body>
</html>


**效果**

持续支持相关场景的CASE自主排查，一次排查准确率~70%，效果优于相较于使用 SOP 式的 SKILL 排查方式。

> 📌 **附录区域**

### 附录

#### knowledge-flow 和传统 RAG 的对比

> **ℹ️ 信息：**
>
> knowledge-flow 采用文件系统目录索引设计，以分级目录树对知识进行结构化组织。Agent 按需下钻、渐进式召回。相比传统 RAG，定位更精准、上下文更完整，做到知识沉得下、易更新、用得好。

| **维度** | **传统 RAG（如Friday 知识库）** | **knowledge-flow** |
| --- | --- | --- |
| 检索方式 | 单次切片召回，天花板明显 | 多轮检索 + 跨文档推理 + 上下文语义理解，避免"召回即天花板" |
| 知识组织 | 扁平向量库 | 目录树分层索引，支持分域隔离、精准定位与透明知识结构 |
| 运营机制 | 无闭环 | 入库结构化审查 → 上线矛盾检测 → 更新巡检 → 下线历史存档，保障体量、新鲜度与一致性 |
| 进化能力 | 依赖人工规则优化 | 随 Agent 理解力、上下文长度与推理能力自然提升 |

#### Agent 知识使用的痛点与 knowledge-flow 的解法

| 痛点 | 解法思路 | knowledge-flow 关键能力 |
| --- | --- | --- |
| 知识难沉淀 | 多通道沉淀，覆盖三类知识形态 | **a. 显性知识统一接入**：学城文档、TT工单知识、代码仓知识、数据任务表等多种来源统一收敛进知识库。 **b. 过程知识当场沉淀**：依托 Agent 上下文，在交互过程中即刻提炼、即刻入库，避免上下文一散就难以追溯。 **c. 隐性知识协同显性化**：专家与 Agent 协作的过程本身就是隐性知识显性化，借过程知识路径同步落库。 |
| 知识难更新 | 低成本、系统化的更新闭环 | **a. 更新动作轻量化**：发现即修复，修复即生效。 **b. 过期知识主动识别**：知识库主动追踪源头变化，发现已过期的内容并驱动更新。 **c. 知识库持续自我治理**：定期发现并修复重复、混乱、失准等内部失修，让知识库长期保持健康。 |
| 知识难用好 | 主动导航、多类型知识统一组织 & 按需取用 | **a. 从被动召回到主动导航：**Agent 像人翻目录一样，逐层判断、逐步下钻，每一步决策都基于当层的目录描述，而非黑盒打分。整个检索过程可观测、可调优——走了哪条路径、为什么选这一支、在哪一步停下，全程可追溯。 **b. 多类型知识统一组织、按需取用：**学城文档、代码语义、数据任务血缘、历史排查经验等不同类型的知识，全部纳入同一套目录体系；Agent 在执行任务时，可根据当前需要在不同分支间穿插检索，把分散在多处的知识一次性拿齐。 |