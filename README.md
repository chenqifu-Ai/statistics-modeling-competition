# 📊 全国大学生统计建模大赛项目

## 🎯 项目信息

### 基本信息
- **大赛名称**: 2026年第十二届全国大学生统计建模大赛
- **组别**: 本科生组
- **赛区**: 辽宁赛区
- **参赛单位**: 辽宁中医药大学

### 团队成员
| 姓名 | 院系 | 年级 | 手机号 |
|------|------|------|--------|
| 李柳萱 | 基础医学院 | 大一 | 18540086892 |
| 夏玉臻 | 基础医学院 | 大一 | 16641492021 |
| 陈昱仪 | 基础医学院 | 大一 | 18540081202 |

### 重要时间
- **报名表提交**: 2026年4月8日16:00前
- **材料提交**: 2026年5月6日10:00前（电子版）
- **材料提交**: 2026年5月6日16:00前（纸质版）
- **提交邮箱**: lnutcmxxgcxytjjmjs@163.com

## 📁 项目结构

```
statistics-modeling-competition/
├── README.md              # 项目说明
├── docs/                  # 文档资料
│   ├── competition_requirements.md  # 大赛要求
│   ├── submission_guide.md          # 提交指南
│   └── format_template.md           # 格式模板
├── submission/            # 提交材料
│   ├── application_form/            # 报名表
│   ├── commitment_letter/           # 承诺书
│   ├── ai_usage_form/              # AI使用情况表
│   ├── paper/                      # 论文
│   └── plagiarism_report/          # 查重报告
├── data/                  # 数据文件
│   ├── raw/                       # 原始数据
│   ├── processed/                  # 处理后的数据
│   └── analysis/                   # 分析结果
├── scripts/               # 分析脚本
│   ├── data_cleaning/             # 数据清洗
│   ├── analysis/                  # 统计分析
│   ├── visualization/             # 数据可视化
│   └── modeling/                  # 建模代码
├── references/            # 参考文献
│   ├── papers/                    # 相关论文
│   ├── books/                     # 参考书籍
│   └── online_resources/          # 网络资源
└── .gitignore            # Git忽略文件
```

## 🚀 快速开始

### 1. 环境设置
```bash
# 克隆项目
git clone <repository-url>

# 安装必要的Python包
pip install pandas numpy matplotlib seaborn scikit-learn statsmodels

# 或者使用R语言
# install.packages(c("tidyverse", "ggplot2", "caret"))
```

### 2. 项目工作流程
1. **数据收集** → `data/raw/`
2. **数据清洗** → `scripts/data_cleaning/`
3. **统计分析** → `scripts/analysis/`
4. **建模验证** → `scripts/modeling/`
5. **论文撰写** → `submission/paper/`
6. **材料准备** → `submission/` 各文件夹

### 3. 提交准备
```bash
# 生成最终提交文件
python scripts/prepare_submission.py

# 检查格式是否符合要求
python scripts/check_format.py
```

## 📋 提交要求

### 电子版材料（5月6日10:00前）
- ✅ 论文Word完整版: `作品全文—本科生组—报名序号.docx`
- ✅ 论文PDF匿名版: `匿名作品—本科生组—报名序号.pdf`
- ✅ 知网查重报告: `查重报告—报名序号.pdf`

### 纸质版材料（5月6日16:00前）
- ✅ 承诺书（手写签字+公章）
- ✅ AI工具使用情况表（手写签字+公章）
- ✅ 匿名版论文
- ✅ 知网查重报告

## 🛠️ 技术栈建议

### 统计分析
- **Python**: pandas, numpy, scipy, statsmodels, scikit-learn
- **R**: tidyverse, ggplot2, caret, lme4
- **统计软件**: SPSS, SAS（可选）

### 数据可视化
- **Python**: matplotlib, seaborn, plotly
- **R**: ggplot2, plotly
- **工具**: Tableau（可选）

### 文档撰写
- **论文写作**: LaTeX / Word
- **文献管理**: Zotero / EndNote
- **协作工具**: Overleaf / Git

## 📞 联系方式

- **院校负责人**: 董丹 (13889145027)
- **提交邮箱**: lnutcmxxgcxytjjmjs@163.com
- **项目仓库**: [Git Repository URL]

## 📝 更新日志

- **2026-04-12**: 项目初始化，创建基础结构
- **2026-04-12**: 添加大赛要求和提交指南
- **2026-04-12**: 配置Git版本控制

---
**祝您比赛顺利！加油！** 🎉