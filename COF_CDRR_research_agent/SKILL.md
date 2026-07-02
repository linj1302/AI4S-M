# CDRR Literature Review Agent

智能体名称：文献检索智能体（步骤一：文献回顾与知识提取）

## 🎯 核心目标
从海量文献中提取COF基光催化CO2还原反应的关键信息，为材料设计提供知识基础。

## 📋 四大关键科学问题 (KSQ)

### KSQ1: "设计高效 COFs 活性位点的原则是什么？"
- 提取COF的连接子类型（共价键、配位键）
- 提取光催化剂节点（金属位点、非金属位点）
- 提取活性位点的电子结构特征
- 提取光催化条件（光源、溶剂、pH等）

## 🔧 核心功能

### 1. 智能文献检索
- 搜索策略：COF + 光催化 + CO2还原 + 金属/非金属位点
- 关键词组合：COF photocatalyst CO2 reduction, covalent organic framework photocatalysis, MOF-like COFs, etc.
- 搜索范围：高影响因子期刊（IF ≥ 15）近5年文献

### 2. 结构信息提取
- COF拓扑结构（六边形、网格、层状等）
- 连接子类型（刚性、柔性、共轭）
- 光催化剂类型（单一金属、双金属、非金属）
- 表面修饰策略（配体修饰、缺陷工程）

### 3. 性能数据提取
- 光催化活性指标（CO产率、法拉第效率、选择性）
- 光电化学参数（带隙、导带位置、价带位置）
- 稳定性数据（循环次数、操作时间）

### 4. 反应条件提取
- 光源类型（LED、激光、太阳光）
- 反应体系（水溶液、有机溶剂、离子液体）
- 催化剂浓度、负载量
- 温度、压力等参数

## 📊 输出格式

### 结构化Markdown报告
```markdown
# CDRR文献综述报告

## 1. COF结构特征
### 1.1 拓扑结构
- 典型结构类型：[六边形网格/层状/三维]
- 空隙率：[X%]
- 比表面积：[X m²/g]

### 1.2 连接子类型
- 刚性连接子：[列表]
- 柔性连接子：[列表]
- 共轭连接子：[列表]

### 1.3 光催化剂节点
- 金属位点：[列表，含金属类型]
- 非金属位点：[列表]
- 双金属协同：[列表]

## 2. 光催化性能
### 2.1 活性指标
- CO产率：[X μmol/(g·h)]
- 法拉第效率：[X%]
- 选择性：[CO: X%, CH4: X%, 其他: X%]

### 2.2 光电化学参数
- 带隙：[X eV]
- 导带位置：[X eV vs NHE]
- 价带位置：[X eV vs NHE]
- 载流子寿命：[X ns]

## 3. 反应条件
### 3.1 光源
- 类型：[LED/激光/太阳光]
- 波长：[X nm]
- 光强：[X mW/cm²]

### 3.2 反应体系
- 溶剂：[列表]
- pH：[X]
- 温度：[X °C]
- 压力：[X bar]

## 4. 研究趋势
### 4.1 结构设计策略
- [策略1]
- [策略2]
- [策略3]

### 4.2 性能优化方向
- [方向1]
- [方向2]
- [方向3]

### 4.3 待解决问题
- [问题1]
- [问题2]
```

### Excel数据库
- 文献ID、标题、作者、期刊、年份、DOI
- COF结构特征（拓扑、连接子、节点）
- 光催化性能指标
- 反应条件参数
- 性能-结构关联分析

## 🚀 使用方式

### 命令行调用
```bash
python CDRR_research_skill.py --mode literature_review
python CDRR_research_skill.py --mode structure_extraction
python CDRR_research_skill.py --mode performance_analysis
python CDRR_research_skill.py --mode trend_analysis
```

### Python API调用
```python
from CDRR_research_skill import CDRRLiteratureAgent

# 初始化智能体
agent = CDRRLiteratureAgent()

# 执行文献回顾
results = agent.literature_review(
    query="COF photocatalyst CO2 reduction",
    min_impact_factor=15,
    years_back=5
)

# 提取结构信息
structure_info = agent.extract_structure_info(results)

# 分析性能数据
performance_data = agent.analyze_performance(results)

# 生成报告
agent.generate_report(
    structure_info=structure_info,
    performance_data=performance_data,
    output_dir="literature/review"
)
```

## 📈 支持的文献数据库

- Web of Science
- Scopus
- Google Scholar
- arXiv预印本

## 🔍 搜索策略优化

### 多维度关键词组合
1. **结构维度**：
   - "covalent organic framework"
   - "porous organic polymer"
   - "COF photocatalyst"

2. **活性维度**：
   - "CO2 reduction"
   - "carbon monoxide evolution"
   - "photoelectrochemical"

3. **性能维度**：
   - "high activity"
   - "selective CO production"
   - "efficient photocatalysis"

### 过滤条件
- 期刊影响因子 ≥ 15
- 发表年份 ≥ 2019
- 研究类型：实验 + 理论计算
- 语言：英语

## 🔄 工作流程

```
1. 文献检索
   ↓
2. 初步筛选（IF、年份、相关性）
   ↓
3. 深度阅读与信息提取
   ↓
4. 结构化数据存储
   ↓
5. 数据分析与可视化
   ↓
6. 知识图谱构建
   ↓
7. 研究趋势识别
   ↓
8. 关键科学问题总结
```

## 📚 知识库整合

- 提取的文献数据存储到本地知识库
- 与材料数据库（Material Project、COF-DB）对接
- 构建COF结构-性能关联图谱
- 生成设计指南和优化建议

## 🎓 输出交付物

1. **文献综述报告**（Markdown格式）
2. **结构特征数据库**（Excel格式）
3. **性能数据表**（Excel格式）
4. **研究趋势分析**（图表+文字）
5. **关键科学问题清单**（KSQ汇总）

## 🔄 持续学习

- 定期更新文献库（每周/每月）
- 自动跟踪最新研究进展
- 识别新兴设计策略
- 评估技术成熟度

---

**版本**: v2.0
**最后更新**: 2026-06-30
**作者**: CDRR Research Team