# 农业银行股价 × 天干地支五行关系检验

## 目录结构

```
研究结果/
├── README.md                          # 本说明文件
├── 结论报告.md                        # 一页终结结论报告
├── 研究进度.md                        # 进度追踪
├── 学术论文_农行天干地支五行检验.docx  # 完整论文（Word，含嵌入图表）
│
├── 参考文献/                          # 参考文献资料
│   ├── references.md                  # 参考文献详细清单（含metaso搜索结果）
│   └── 学术论文_农行天干地支五行检验.md # 论文Markdown版
│
├── 图表/                              # 可视化图表
│   ├── fig1_daily_boxplot.png         # 日频箱线图（天干×地支）
│   ├── fig2_weekly_rolling.png        # 周频滚动窗口差异时序
│   ├── fig3_monthly_train_test.png    # 月频训练/测试对比
│   └── fig4_summary_all.png           # 汇总四格图+p值条形图
│
├── 数据/                              # 中间数据
│   ├── data_daily_with_ganzhi.csv     # 日频完整数据（3,833条）
│   ├── data_weekly.csv                # 周频聚合（811周）
│   └── data_monthly.csv               # 月频聚合（191个月）
│
├── 统计表/                            # 统计分析结果
│   ├── table_all_tests.csv            # 全部9个检验结果
│   ├── table_daily_tg_wuxing.csv      # 日天干五行描述统计
│   ├── table_daily_dz_wuxing.csv      # 日地支五行描述统计
│   └── table_weekly_rolling.csv       # 周滚动窗口差异
│
└── 脚本/                              # 分析脚本
    ├── analysis_main.py               # 核心分析（数据提取→三层分析→回归）
    ├── visualizations_v3.py           # 可视化 v3（当前使用，Noto Sans CJK JP）
    ├── visualizations.py              # 可视化 v1（DroidSansFallback，字符不全）
    ├── visualizations_v2.py           # 可视化 v2（FontProperties方式）
    └── generate_paper_docx.py         # Word论文生成脚本
```

## 使用说明

### 重现分析

```bash
cd /home/cpy/文档/金融数据库建立/研究结果
python3 脚本/analysis_main.py          # 重新运行全部分析
python3 脚本/visualizations_v3.py      # 重新生成图表
python3 脚本/generate_paper_docx.py    # 重新生成论文.docx
```

### 模型说明

- 统计分析脚本：使用本地 Python + MySQL 数据库跑算
- 论文撰写：当前由 deepseek-v4-flash 完成

研究结果/结论报告.md
