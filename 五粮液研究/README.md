# 五粮液(000858.SZ)股价 × 天干地支五行关系检验

## 目录结构

```
五粮液研究/
├── 结论报告.md                        # 一页终结结论报告
├── README.md                          # 本说明文件
│
├── 数据/                              # 中间数据
│   ├── data_daily_with_ganzhi.csv     # 日频完整数据（3,902条）
│   ├── data_weekly.csv                # 周频聚合（824周）
│   └── data_monthly.csv               # 月频聚合（194个月）
│
├── 统计表/                            # 统计分析结果
│   ├── table_all_tests.csv            # 全部9个检验结果
│   ├── table_daily_tg_wuxing.csv      # 日天干五行描述统计
│   ├── table_daily_dz_wuxing.csv      # 日地支五行描述统计
│   └── table_weekly_rolling.csv       # 周滚动窗口差异
│
├── 图表/                              # 可视化图表（待生成）
│
├── 脚本/                              # 分析脚本
│   └── analysis_main.py               # 核心分析（数据提取→三层分析→回归）
│
└── 参考文献/                          # 参考文献（待整理）
```

## 使用说明

### 重现分析

```bash
cd /home/cpy/文档/金融数据库建立/五粮液研究
python3 脚本/analysis_main.py          # 重新运行全部分析
```

### 模型说明

- 统计分析脚本：使用本地 Python + MySQL 数据库跑算
- 分析方法：日/周/月三层频率 × Kruskal-Wallis + 样本外验证 + 回归混杂剥离
- 结论撰写由 Hermes AI Agent 完成
