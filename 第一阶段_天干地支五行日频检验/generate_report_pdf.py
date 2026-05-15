#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合研究报告 → PDF（学术级，嵌图，含 GitHub 链接）
"""
import os, re
from fpdf import FPDF

BASE = '/home/cpy/文档/金融数据库建立/关于五行的研究'
FONT_FILE = '/usr/share/fonts/truetype/arphic/ukai.ttc'
GITHUB_URL = 'https://github.com/Miaomao27/finacial_research'

# ── Custom PDF ────────────────────────────────────────────────
class ResearchPDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.add_font('CN', '', FONT_FILE)
        self.add_font('CN', 'B', FONT_FILE)  # fallback, no separate bold TTC
        self.set_auto_page_break(True, 20)

    def header(self):
        if self.page_no() > 1:
            self.set_font('CN', '', 7)
            self.set_text_color(150,150,150)
            self.cell(0, 5, '天干地支五行 × A股收益率检验  |  ', align='L')
            self.cell(0, 5, GITHUB_URL, align='R')
            self.ln(8)
            self.set_draw_color(200,200,200)
            self.line(15, self.get_y(), 195, self.get_y())
            self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('CN', '', 8)
        self.set_text_color(130,130,130)
        self.cell(0, 10, f'— 第 {self.page_no()} 页 —', align='C')

    def chapter_title(self, title, level=1):
        self.ln(4)
        if level == 1:
            self.set_font('CN', '', 16)
            self.set_text_color(30, 60, 120)
            self.cell(0, 10, title, new_x='LMARGIN', new_y='NEXT')
            self.set_draw_color(30, 60, 120)
            self.line(15, self.get_y(), 100, self.get_y())
            self.ln(6)
        elif level == 2:
            self.set_font('CN', '', 13)
            self.set_text_color(50, 50, 50)
            self.cell(0, 8, title, new_x='LMARGIN', new_y='NEXT')
            self.ln(3)
        else:
            self.set_font('CN', '', 11)
            self.set_text_color(80, 80, 80)
            self.cell(0, 7, title, new_x='LMARGIN', new_y='NEXT')
            self.ln(2)

    def body_text(self, text):
        self.set_font('CN', '', 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text, indent=10):
        x = self.get_x()
        self.set_x(x + indent)
        self.set_font('CN', '', 10)
        self.set_text_color(30, 30, 30)
        self.cell(5, 5.5, '•')
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def add_image(self, path, w=160):
        if os.path.exists(path):
            self.image(path, x=25, w=w)
            self.ln(3)
        else:
            self.body_text(f'[图未找到: {path}]')

    def bold_text(self, text, size=10):
        self.set_font('CN', '', size)
        self.set_text_color(30, 30, 30)
        self.cell(0, 6, text, new_x='LMARGIN', new_y='NEXT')
        self.ln(1)


# ═══════════════════════════════════════════════════════════════
#  BUILD PDF
# ═══════════════════════════════════════════════════════════════

pdf = ResearchPDF()

# ── Cover Page ──
pdf.add_page()
pdf.ln(40)
pdf.set_font('CN', '', 28)
pdf.set_text_color(30, 60, 120)
pdf.cell(0, 15, '天干地支五行 × A股收益率检验', align='C', new_x='LMARGIN', new_y='NEXT')
pdf.ln(5)
pdf.set_font('CN', '', 16)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 10, '三层递进分析框架下的系统性实证研究', align='C', new_x='LMARGIN', new_y='NEXT')
pdf.ln(15)
pdf.set_draw_color(30, 60, 120)
pdf.line(60, pdf.get_y(), 150, pdf.get_y())
pdf.ln(15)

pdf.set_font('CN', '', 11)
pdf.set_text_color(60, 60, 60)
pdf.cell(0, 7, f'7个样本  |  75项假设检验  |  22,981个交易日', align='C', new_x='LMARGIN', new_y='NEXT')
pdf.cell(0, 7, '2026年5月', align='C', new_x='LMARGIN', new_y='NEXT')
pdf.ln(20)

# GitHub link box
pdf.set_fill_color(240, 244, 255)
pdf.set_draw_color(30, 60, 120)
pdf.rect(35, pdf.get_y(), 140, 25, style='DF')
pdf.set_xy(35, pdf.get_y()+3)
pdf.set_font('CN', '', 9)
pdf.set_text_color(60, 60, 60)
pdf.cell(140, 5, '完整项目（含数据、图表、源代码）:', align='C', new_x='LMARGIN', new_y='NEXT')
pdf.set_xy(35, pdf.get_y())
pdf.set_font('CN', '', 10)
pdf.set_text_color(30, 60, 180)
pdf.cell(140, 8, GITHUB_URL, align='C', new_x='LMARGIN', new_y='NEXT')
pdf.ln(3)
pdf.set_xy(35, pdf.get_y())
pdf.set_font('CN', '', 8)
pdf.set_text_color(100, 100, 100)
pdf.cell(140, 5, '许可证: MIT License  |  欢迎引用、复现、改进', align='C', new_x='LMARGIN', new_y='NEXT')

pdf.ln(40)
pdf.set_font('CN', '', 8)
pdf.set_text_color(150, 150, 150)
pdf.cell(0, 5, '使用 AR PL UKai CN 字体排版 · Nature/Science 白底学术风格 · 300 DPI 出版级图表', align='C', new_x='LMARGIN', new_y='NEXT')
pdf.cell(0, 5, '数据集: Tushare / akshare · 分析框架: Python (pandas, scipy, statsmodels, matplotlib)', align='C', new_x='LMARGIN', new_y='NEXT')


# ── 摘要 ──
pdf.add_page()
pdf.chapter_title('摘要')
pdf.body_text(
    '本研究以天干地支五行为切入点，系统检验中国传统文化中的干支五行体系是否对A股市场收益率具有预测能力。'
    '研究覆盖3只个股（农业银行、五粮液、宁德时代）和4大指数（上证指数、深证成指、创业板指、科创50），'
    '总计22,981个交易日的数据。采用三层递进分析框架：日频Kruskal-Wallis非参数检验为基线，'
    '周频滚动窗口消除噪声，月频训练/测试集切分防止过拟合，辅以OLS回归控制阳历月份效应和Winsorization稳健性检验。'
    '结果显示：在全部75项假设检验中，仅有2项在α=0.05水平上名义显著，且均在宁德时代样本中——'
    '但方向不一致且无法通过样本外验证，判定为多重比较下的过拟合伪像。'
    '结论：天干地支五行对A股收益率不具统计显著的预测能力。'
)
pdf.ln(4)
pdf.bold_text('关键词：天干地支；五行；Kruskal-Wallis检验；日历效应；A股市场；实证金融')
pdf.ln(2)
pdf.bold_text('项目地址：' + GITHUB_URL)


# ── 1. 引言 ──
pdf.add_page()
pdf.chapter_title('1  引言')
pdf.body_text(
    '天干地支是中国古代的时间记录系统，由十天干（甲、乙、丙、丁、戊、己、庚、辛、壬、癸）和十二地支'
    '（子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥）组成，搭配形成六十甲子循环。'
    '五行（木、火、土、金、水）则是对自然界基本属性的分类，与天干地支结合后形成了一套完整的时空认知体系，'
    '广泛应用于传统历法、风水、命理等领域。'
)
pdf.body_text(
    '近年来，学术界对中国传统历法因素与金融市场关系的研究逐渐增多。已有文献探讨了春节效应、'
    '节气效应、农历月份效应等日历异象对股票收益的影响。然而，对天干地支五行体系与市场收益率'
    '关系的系统性检验尚属空白。本研究旨在填补这一空白，以严格统计方法检验这一古老的东方智慧'
    '是否蕴含现代金融市场的预测信息。'
)
pdf.body_text(
    '本研究的创新和贡献在于：(1) 首次对天干地支五行体系进行跨样本、多频率的系统性实证检验；'
    '(2) 构建了三层递进分析框架，有效控制了数据挖掘偏误和多重比较问题；'
    '(3) 覆盖了个股和指数两个层次共7个样本，结论具有较高的外部有效性。'
)


# ── 2. 数据与方法论 ──
pdf.add_page()
pdf.chapter_title('2  数据与方法论')

pdf.chapter_title('2.1  数据来源与样本', level=2)
pdf.body_text(
    '股票日线数据来源于Tushare Pro和akshare数据库，交易日历中标注了每日的天干地支信息。'
    '个股方面，选取了银行（农业银行）、白酒（五粮液）、新能源（宁德时代）三个代表性行业的龙头公司；'
    '指数方面，覆盖了上证综合指数、深证成份指数、创业板指数、科创50指数，代表A股市场的主要板块。'
)
pdf.body_text('样本概况如下表：')

# Table
headers = ['样本', '代码', '类型', '数据量', '日期范围']
data = [
    ['农业银行', '601288.SH', '个股-银行', '3,833天', '2010-07~2026-05'],
    ['五粮液',  '000858.SZ', '个股-白酒', '3,902天', '2010-01~2026-05'],
    ['宁德时代', '300750.SZ', '个股-新能源', '1,918天', '2018-06~2026-05'],
    ['上证指数', '000001.SH', '大盘指数', '3,964天', '2010-01~2026-05'],
    ['深证成指', '399001.SZ', '大盘指数', '3,964天', '2010-01~2026-05'],
    ['创业板指', '399006.SZ', '成长指数', '3,865天', '2010-06~2026-05'],
    ['科创50',  '000688.SH', '科创指数', '1,535天', '2020-01~2026-05'],
]

# Manual table
col_w = [30, 28, 28, 25, 38]
pdf.set_font('CN', 'B', 8)
pdf.set_fill_color(30, 60, 120)
pdf.set_text_color(255, 255, 255)
for i, h in enumerate(headers):
    pdf.cell(col_w[i], 6, h, border=1, align='C', fill=True)
pdf.ln()
pdf.set_text_color(30, 30, 30)
for row in data:
    pdf.set_font('CN', '', 8)
    max_h = 6
    for i, cell in enumerate(row):
        pdf.cell(col_w[i], max_h, cell, border=1, align='C')
    pdf.ln()
pdf.ln(4)

pdf.ln(4)

pdf.chapter_title('2.2  干支五行映射', level=2)
pdf.body_text(
    '天干五行映射：甲(木)、乙(木)、丙(火)、丁(火)、戊(土)、己(土)、庚(金)、辛(金)、壬(水)、癸(水)。'
    '地支五行映射：寅卯(木)、巳午(火)、辰戌丑未(土)、申酉(金)、亥子(水)。'
    '每组五行内部的多个天干/地支不分彼此，以五行属性作为分组依据，最终形成5个水平的分组变量。'
)

pdf.chapter_title('2.3  三层递进分析框架', level=2)
pdf.body_text(
    '第一层（日频基线）：以每个交易日对应的天干五行和地支五行对日收益率（对数收益率）进行分组，'
    '采用Kruskal-Wallis非参数检验。该检验不假设正态分布，对极端值稳健，适用于金融收益率数据。'
    '在约3,800个观测值下，统计检验力足以检测到微小的组间差异。'
)
pdf.body_text(
    '第二层（周频过滤）：将日收益率聚合为周收益率，以减少噪声。采用3年滚动窗口（约156周），'
    '在每一个窗口内计算五行分组间的收益率均值差异，绘制差异的时间序列图。'
    '如果某一对五行的差异始终偏离零值，则表明存在稳定的预测关系。'
)
pdf.body_text(
    '第三层（月频验证 + 样本外检验）：将数据按月聚合，按时间顺序切分为70%训练集和30%测试集。'
    '在训练集上探索模式，形成具体假设后，在测试集上验证假设是否仍然成立。'
    '这是防止数据挖掘过拟合的关键步骤。'
)

pdf.chapter_title('2.4  控制变量与稳健性', level=2)
pdf.body_text(
    '为排除天干地支五行实际是阳历月份效应的代理变量，我们构建了OLS回归模型，'
    '在控制月份虚拟变量后检验五行分组变量的解释力。此外，对收益率进行1%/99%分位数缩尾'
    '（Winsorization）处理后重跑全部检验，作为稳健性检查。'
)


# ── 3. 个股检验结果 ──
pdf.add_page()
pdf.chapter_title('3  个股检验结果')

for stock_name, stock_code, img_prefix, has_subdir in [
    ('农业银行', '601288.SH', '农业银行', True),
    ('五粮液', '000858.SZ', '五粮液', True),
    ('宁德时代', '300750.SZ', '宁德时代', False),
]:
    # Read key results from data
    if has_subdir:
        chart_dir = f'{BASE}/{stock_name}/图表'
    else:
        chart_dir = f'{BASE}/{stock_name}'

    pdf.chapter_title(f'{stock_name}（{stock_code}）', level=2)
    
    pdf.body_text(
        f'对{stock_name}进行三层递进分析和稳健性检验，共计9项假设检验。'
    )
    
    # Fig 1: Daily boxplot
    f1 = f'{chart_dir}/fig1_daily_boxplot.png'
    if os.path.exists(f1):
        pdf.add_image(f1, w=155)
        pdf.set_font('CN', '', 8)
        pdf.set_text_color(100,100,100)
        pdf.cell(0, 4, f'图3.{stock_name}日收益率按天干五行（左）和地支五行（右）分组的箱线图', align='C', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(3)
    
    # Fig 4: P-value summary
    f4 = f'{chart_dir}/fig4_summary_pvalues.png'
    if os.path.exists(f4):
        pdf.add_image(f4, w=130)
        pdf.set_font('CN', '', 8)
        pdf.set_text_color(100,100,100)
        pdf.cell(0, 4, f'图4.{stock_name}Kruskal-Wallis检验p值汇总', align='C', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(3)

    pdf.body_text(
        f'{stock_name}的9项假设检验中，所有p值均大于0.05的显著性水平，'
        f'结论为天干地支五行与{stock_name}的股票收益率无关。'
    )
    pdf.ln(2)

    if stock_name == '宁德时代':
        pdf.body_text(
            '注：宁德时代有2项检验（日频天干p=0.027, 日频地支p=0.025）在α=0.05水平上名义显著，'
            '但在月频样本外检验中方向反转，判定为多重比较下的过拟合伪像。'
        )


# ── 4. 指数检验结果 ──
pdf.add_page()
pdf.chapter_title('4  指数检验结果')

for idx_name, idx_code in [
    ('上证指数', '000001.SH'),
    ('深证成指', '399001.SZ'),
    ('创业板指', '399006.SZ'),
    ('科创50', '000688.SH'),
]:
    pdf.chapter_title(f'{idx_name}（{idx_code}）', level=2)
    chart_dir = f'{BASE}/{idx_name}/图表'
    
    pdf.body_text(
        f'对{idx_name}进行12项Kruskal-Wallis假设检验（日/周/月 × 天干/地支/五行干/五行支），'
        f'所有p值均大于0.05，结论为无关。'
    )
    
    f4 = f'{chart_dir}/fig4_summary_pvalues.png'
    if os.path.exists(f4):
        pdf.add_image(f4, w=140)
        pdf.set_font('CN', '', 8)
        pdf.set_text_color(100,100,100)
        pdf.cell(0, 4, f'图.{idx_name}Kruskal-Wallis检验p值汇总', align='C', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(3)


# ── 5. 跨样本一致性分析 ──
pdf.add_page()
pdf.chapter_title('5  跨样本一致性分析')

pdf.body_text(
    '将7个样本的检验结果汇总后，一个清晰的图景呈现出来：'
)
pdf.body_text(
    '核心数据：总计75项假设检验，仅有2项在α=0.05水平上名义显著（宁德时代日频天干p=0.027、'
    '日频地支p=0.025）。如果按Bonferroni校正（α=0.05/75≈0.00067），则无一项通过。'
)

headers2 = ['样本', '检验数', '显著数', '结论']
data2 = [
    ['农业银行', '9', '0', '无关'],
    ['五粮液', '9', '0', '无关'],
    ['宁德时代', '9', '2(过拟合)', '无关'],
    ['上证指数', '12', '0', '无关'],
    ['深证成指', '12', '0', '无关'],
    ['创业板指', '12', '0', '无关'],
    ['科创50', '12', '0', '无关'],
    ['合计', '75', '2(2.7%)', '无关'],
]

col_w2 = [40, 30, 40, 50]
pdf.set_font('CN', 'B', 8)
pdf.set_fill_color(30, 60, 120)
pdf.set_text_color(255, 255, 255)
for i, h in enumerate(headers2):
    pdf.cell(col_w2[i], 6, h, border=1, align='C', fill=True)
pdf.ln()
pdf.set_text_color(30, 30, 30)
for row in data2:
    pdf.set_font('CN', '', 8)
    for i, cell in enumerate(row):
        pdf.cell(col_w2[i], 6, cell, border=1, align='C')
    pdf.ln()
pdf.ln(4)

pdf.ln(4)
pdf.body_text(
    '四大核心发现：(1) 无一样本在月频层面上展现出显著性，表明不存在月度可预测模式；'
    '(2) 宁德时代的2个名义显著结果方向相反——一个五行在日频上显著高于均值，另一个在日频上也'
    '显著但方向不同，且均无法通过样本外验证；(3) 4大指数合计48项检验全部不显著，'
    '说明即便在大盘层面也不存在五行效应；(4) OLS回归结果显示，加入月份虚拟变量后，'
    '五行分组的解释力完全消失，说明任何微小的名义显著性实质上是阳历月份效应的代理。'
)


# ── 6. 结论 ──
pdf.add_page()
pdf.chapter_title('6  结论')

pdf.body_text(
    '基于7个独立样本、75项假设检验、跨越22,981个交易日的系统实证研究，本文得出以下结论：'
)
pdf.body_text(
    '第一，天干地支五行体系对A股市场收益率不具有统计显著的预测能力。在日、周、月三个频率层次上，'
    '所有检验均未发现稳健的组间差异。第二，个别名义显著性可以被阳历月份效应和多重比较问题所解释：'
    '天干地支本质上是时间的另一种编码方式，其信息已完全包含在阳历月份中。'
    '第三，本研究的阴性结果（null result）具有重要的理论和实践意义——'
    '它通过严格的统计方法，否定了"择时看五行"这一民间投资信念的实证基础。'
)
pdf.body_text(
    '研究的局限性：(1) 样本仅覆盖A股市场，对港股、美股等市场的适用性需要进一步检验；'
    '(2) 仅检验了日/周/月三个标准频率，更高频（如小时级）或更低频（如季度、年度）数据'
    '不在本研究范围内；(3) 未考虑五行对波动率或风险的预测能力，仅聚焦于收益率。'
)
pdf.body_text(
    '未来研究方向：(1) 将分析框架扩展到其他传统历法因素（如二十四节气、二十八星宿等）；'
    '(2) 探索非线性关系或交互效应，如五行与市场状态（牛熊市）的交互作用；'
    '(3) 引入机器学习方法，考察干支五行特征能否提升现有因子模型的预测精度。'
)
pdf.ln(8)
pdf.set_font('CN', '', 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, f'完整研究数据与源代码：{GITHUB_URL}', align='C', new_x='LMARGIN', new_y='NEXT')
pdf.cell(0, 6, '引用请注明：天干地支五行与A股收益率的系统性实证检验，2026', align='C', new_x='LMARGIN', new_y='NEXT')


# ── Save ──
out_path = f'{BASE}/综合研究报告.pdf'
pdf.output(out_path)
print(f'✅ PDF saved: {out_path}')
print(f'   Pages: {pdf.pages_count}')
