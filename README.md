# ReVIM: 恋爱关系持续性综合评估模型 (Python GUI 程序)

用多学科视角，理性分析你的亲密关系是否值得持续。

## 项目简介

你是否曾在一段感情中感到迷茫，不确定是该坚持还是放手？感性上难以抉择，渴望一个更全面、更理性的视角？

**ReVIM (Relational Viability Integrated Model)** 是一个旨在帮助你系统性评估恋爱关系“持续价值”的理论模型。它跳脱出单一的情感或经济视角，融合了来自多学科的理论框架。

本项目是 ReVIM 理论模型的一个 **Python 图形用户界面 (GUI) 实现**。通过一个详细的交互式问卷，程序收集用户对关系各个维度的感知数据，然后运用 ReVIM 模型进行复杂计算，最终提供一个基于多学科分析的“关系持续价值”评估结果和可视化图表，辅助用户进行更明智的决策。

**请注意：** 本程序提供的结果是基于理论模型和您的主观输入的计算，仅作为辅助思考工具，不能替代您个人的情感体验、判断或专业的心理/情感咨询。

## 主要特性

*   **详细交互式问卷：** 通过结构化问题全面收集关系数据。
*   **复杂模型计算：** 实现 ReVIM 模型的核心逻辑，包括：
    *   计算关系的预期总效用 (E(U_t)) 和预期总成本 (E(C_t))。
    *   考虑效用/成本随时间（基于未来预期）的动态变化。
    *   应用时变贴现率 (r_t)，反映关系风险和不确定性的变化。
    *   评估机会成本/替代选项效用 (OCAU)。
    *   纳入沉没成本谬误调整项，辅助去偏。
*   **可视化结果：** 提供饼图展示效用/成本构成，折线图展示净效用和累计价值随时间的变化趋势。
*   **敏感性分析：** 允许用户调整关键参数（如贴现率、乐观度），观察结果如何变化。
*   **中文界面与解读：** 所有用户界面和计算结果均使用中文呈现，并包含对经济学概念的通俗注释。
*   **本地运行：** Python GUI 程序，可在本地计算机上运行，保护用户数据隐私。

## ReVIM 模型核心概念 (简述)

ReVIM 模型将一段恋爱关系视为一项具有长期回报和成本的“投资项目”。其核心是计算关系在预期持续时间内的“净关系效用现值 (NRUPV)”，并与“机会成本/替代选项效用 (OCAU)”进行比较。

*   **净关系效用现值 (NRUPV):** 关系未来所有预期收益（效用）减去所有预期成本，并考虑时间价值（折现）后，在当下的总价值。
*   **预期总效用 (E(U_t)):** 关系在某个时间点带来的所有积极方面，如情感满足、经济支持、社会资本、个人成长等。
*   **预期总成本 (E(C_t)):** 关系在某个时间点带来的所有消极方面，如情感消耗、财务负担、机会损失、心理压力等。
*   **动态贴现率 (r_t):** 用于衡量未来效用/成本相对于当前价值的折扣率。它会随时间、关系风险、不确定性、学习适应能力等因素动态调整。
*   **机会成本/替代选项效用 (OCAU):** 如果不选择当前这段关系，你可能获得的最佳替代选项（如单身状态或与其他潜在伴侣建立关系）的预期效用。
*   **沉没成本谬误调整项:** 一个用于量化并抵消“已经投入太多，不愿放弃”这种非理性心理倾向对决策影响的修正因子。

**决策规则：** 如果 **NRUPV > OCAU + 沉没成本谬误调整项**，则模型倾向于认为这段关系从多学科理性分析的角度看是值得持续的。

*(请注意：本程序是对上述理论框架的一种具体实现，模型内部的参数量化、动态函数、协同效应等均是基于对理论的理解和一定程度的简化假设。)*

## 安装

1.  **确保安装 Python 3.x：**
    访问 [Python 官网](https://www.python.org/downloads/) 下载并安装最新版本。

2.  **安装所需库：**
    打开终端或命令提示符，运行以下命令安装 `matplotlib` 库：
    ```bash
    pip install matplotlib
    ```

## 使用方法

1.  **运行主程序：**
    在项目目录下，运行以下命令启动程序：
    ```bash
    python revim_evaluator.py
    ```

2.  **填写问卷：**
    程序将打开一个图形界面窗口，包含多个标签页。请按顺序仔细阅读并根据您的真实感受填写每个标签页中的问题。使用滑动条、下拉菜单、单选按钮和输入框进行选择和输入。

3.  **进行计算：**
    填写完所有问题后（开放性问题除外，它们不直接参与计算），点击窗口底部的 **“开始计算关系持续价值”** 按钮。

4.  **查看结果：**
    计算完成后，将弹出一个新的窗口显示详细的计算结果和解读。同时，主窗口将自动切换到 **“结果可视化”** 标签页，展示效用/成本构成、净效用趋势和累计价值图表。

5.  **敏感性分析 (可选)：**
    在 **“敏感性分析”** 标签页，您可以调整一些关键的全局参数（如基础贴现率、未来预期乐观度等），然后重新点击计算按钮，观察这些参数变化如何影响最终结果。

## 局限性与免责声明

*   **非专业建议：** 本程序仅提供一个基于模型的分析视角，其结果不能替代专业的心理咨询、情感辅导或您个人的深思熟虑。
*   **主观性：** 模型计算高度依赖于您对问卷问题的主观评分和预期。请尽量诚实和客观地回答。
*   **模型假设：** 复杂的现实关系被抽象为模型，其中包含简化的假设（例如，协同效应的量化方式、未来变化的线性或指数模式等）。这些假设可能与您的具体情况存在差异。
*   **数据隐私：** 本程序在本地运行，不会将您的数据上传到任何服务器。您的数据仅保存在您自己的计算机上（除非您自行导出或保存）。

**使用本程序即表示您理解并接受上述局限性与免责声明。最终的恋爱关系决策权完全在于您自己。**

## 贡献

欢迎对本项目做出贡献！如果您有任何改进建议、发现 Bug 或想提交新的功能，请随时：

1.  提交一个 Issue。
2.  Fork 本仓库并提交 Pull Request。

## 联系方式

如果您对本项目有任何疑问或想与作者交流，可以通过以下方式：

*   GitHub Issues
*   Lyahn.here@gamil.com
