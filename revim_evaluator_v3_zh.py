import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import math
import traceback # Import traceback for detailed error logging

# --- Configuration & Constants ---
TIME_HORIZON_YEARS = 5
NA_STRING = "不适用/未考虑" # Consistent N/A string

# --- FULL QUESTIONNAIRE STRUCTURE (REVIEW AND COMPLETE THIS THOROUGHLY) ---
# Ensure all questions from your Task 3 design are here.
# Ensure 'type' is correct: 'scale', 'text', 'text_int', 'combo', 'radio_na'.
# Ensure 'range' is correct for 'scale'.
# Ensure 'options' are correct for 'combo' and 'radio_na'.
# Ensure flags are correct: 'is_cost': True, 'is_cost_direct': True, 'is_i0_component': True, 'amplify_extremes': True.
QUESTIONNAIRE_STRUCTURE_FULL = {
    "A": {
        "title": "基本信息与整体感受",
        "questions": {
            "A1": {"text": "当前关系持续时间(例如: 2年3个月):", "type": "text"},
            "A2": {"text": "与伴侣的居住情况:", "type": "combo", "options": ["同居", "分居（同城）", "异地"]},
            "A3": {"text": "总体而言，您对当前关系的快乐程度 (1=非常不快乐, 10=非常快乐):", "type": "scale", "range": (1, 10)},
            "A4_1": {"text": "您认为这段关系在接下来一年继续的可能性 (1=完全不可能, 10=极可能):", "type": "scale", "range": (1, 10)},
            "A4_5": {"text": "您认为这段关系在接下来五年继续的可能性 (1=完全不可能, 10=极可能):", "type": "scale", "range": (1, 10)},
            "A5": {"text": "若此关系今天结束, 您如何评价您的最佳替代选择? (1=比现关系差很多, 5=差不多, 10=比现关系好很多):", "type": "scale", "range": (1, 10)},
            "A6_BATNA_Confidence": {"text": "您有多大信心在短期内找到一个至少和当前伴侣一样好，甚至更好的替代关系？ (1=毫无信心, 10=极有信心):", "type": "scale", "range": (1, 10)},
            "A7_Self_Age": {"text": "您的年龄:", "type": "text_int"},
            "A8_Partner_Age": {"text": "您伴侣的年龄:", "type": "text_int"},
        }
    },
    "B": { # 心理学
        "title": "心理学因素",
        "questions": {
            "B1.1": {"text": "这段关系通常让我感到快乐和满足。", "type": "scale", "range": (1, 7)},
            "B1.2": {"text": "我常因这段关系直接感到压力、焦虑或悲伤。", "type": "scale", "range": (1, 7), "is_cost": True},
            "B1.3": {"text": "这段关系满足了我的核心情感需求（如爱、归属感、情感支持）。", "type": "scale", "range": (1, 7)},
            "B1.4": {"text": "我感到伴侣真诚地关心我的情绪健康。", "type": "scale", "range": (1, 7)},
            "B1.5": {"text": "这段关系对我的整体心理健康有积极贡献。", "type": "scale", "range": (1, 7)},
            "B2.1": {"text": "我和伴侣的个性大体上是兼容的。", "type": "scale", "range": (1, 7)},
            "B2.2": {"text": "我们有相似的幽默感。", "type": "scale", "range": (1, 7)},
            "B2.3": {"text": "我们根本性的个性差异造成了显著的摩擦。", "type": "scale", "range": (1, 7), "is_cost": True},
            "B3.1": {"text": "我对伴侣的爱和承诺感到安全和自信。", "type": "scale", "range": (1, 7)},
            "B3.2": {"text": "我担心伴侣会离开我或对我失去兴趣。", "type": "scale", "range": (1, 7), "is_cost": True},
            "B3.3": {"text": "我感到伴侣总能在我需要时出现并回应我的需求。", "type": "scale", "range": (1, 7)},
            "B4.1": {"text": "这段关系支持我的个人成长和发展。", "type": "scale", "range": (1, 7)},
            "B4.2": {"text": "因为这段关系，我感觉自己成为了一个更好的人。", "type": "scale", "range": (1, 7)},
            "B4.3": {"text": "我有时觉得必须压抑部分自我来维持这段关系。", "type": "scale", "range": (1, 7), "is_cost": True},
            "B5.1_Pity_Cost": {"text": "我维持这段关系，在多大程度上是因为同情、内疚或不忍心伤害对方？ (1=完全不是, 7=很大程度上是):", "type": "scale", "range": (1, 7), "is_cost_direct": True},
        }
    },
    "C": { # 经济学
        "title": "经济学因素",
        "questions": {
            "C1.1": {"text": "我和伴侣在金钱管理（消费、储蓄、投资）上有相似的看法。", "type": "scale", "range": (1, 7)},
            "C1.2": {"text": "我们能够公开有效地讨论财务问题。", "type": "scale", "range": (1, 7)},
            "C1.3": {"text": "财务分歧是我们关系中一个主要的冲突来源。", "type": "scale", "range": (1, 7), "is_cost": True},
            "C1.4": {"text": "我对我们共同的财务未来感到安心。", "type": "scale", "range": (1, 7)},
            "C2.1": {"text": "我觉得我们关系中财务责任的划分是公平的。", "type": "scale", "range": (1, 7)},
            "C2.2": {"text": "我觉得我们关系中家务劳动和其他非财务贡献的划分是公平的。", "type": "scale", "range": (1, 7)},
            "C2.3": {"text": "我感觉伴侣为关系付出了他/她公平的一份（财务、情感、实际行动）。", "type": "scale", "range": (1, 7)},
            "C3.1_Invest_TimeEmotion": {"text": "我已为这段关系投入了大量难以割舍的时间和情感。", "type": "scale", "range": (1, 7), "is_i0_component": True},
            "C3.2_Invest_Intertwined": {"text": "我们的生活已深度交织（如共同财产、子女、共同事业），使得分离成本高昂。", "type": "scale", "range": (1, 7), "is_i0_component": True},
            "C3.3": {"text": "我相信这段关系能提升我整体的经济前景或稳定性。", "type": "scale", "range": (1, 7)},
            "C3.4": {"text": "我有时觉得这段关系阻碍了我追求个人或职业机会。", "type": "scale", "range": (1, 7), "is_cost": True},
        }
    },
    "D": { # 社会学
        "title": "社会学因素",
        "questions": {
            "D1.1": {"text": "我的朋友和家人大体上认可并与我的伴侣相处融洽。", "type": "scale", "range": (1, 7)},
            "D1.2": {"text": "在伴侣的社交圈（朋友和家人）中，我感到舒适和被接纳。", "type": "scale", "range": (1, 7)},
            "D1.3": {"text": "我们共同的社交网络为我们的关系提供了有力的支持。", "type": "scale", "range": (1, 7)},
            "D1.4": {"text": "我的社交圈与伴侣社交圈之间的互动常常是压力或冲突的来源。", "type": "scale", "range": (1, 7), "is_cost": True},
            "D2.1": {"text": "我们的关系与我们所在社群/家庭的社会文化期望相符。", "type": "scale", "range": (1, 7)},
            "D2.2": {"text": "我感受到来自社会或家庭关于我们关系进展或状态（如婚姻、子女）的压力。", "type": "scale", "range": (1, 7), "is_cost": True},
            "D3.1": {"text": "这段关系以积极的方式扩展了我的社交联系。", "type": "scale", "range": (1, 7)},
            "D3.2": {"text": "伴侣的社交关系曾对我有益（如职业、机会方面）。", "type": "scale", "range": (1, 7)},
        }
    },
    "E": { # 人类学
        "title": "人类学因素",
        "questions": {
            "E1.1": {"text": "我和伴侣拥有相似的核心文化价值观和信仰。", "type": "scale", "range": (1, 7)},
            "E1.2": {"text": "我们文化背景（如民族、宗教、成长环境）的差异是丰富的源泉而非冲突。", "type": "scale", "range": (1, 7)},
            "E1.3": {"text": "我们能有效地处理任何出现的文化差异。", "type": "scale", "range": (1, 7)},
            "E2.1": {"text": "我们拥有有意义的共同仪式或传统（如庆祝节日、纪念日的方式，日常习惯）。", "type": "scale", "range": (1, 7)},
            "E2.2": {"text": "这些共同的仪式对我来说很重要。", "type": "scale", "range": (1, 7)},
            "E3.1": {"text": "我们各自家庭的结构和互动模式大体上是兼容的。", "type": "scale", "range": (1, 7)},
            "E3.2": {"text": "我对与伴侣的大家庭进一步融合的前景感到乐观（如果适用）。", "type": "scale", "range": (1, 7)},
        }
    },
    "F": { # 生物学/医学
        "title": "生物学/医学因素",
        "questions": {
            "F1.1": {"text": "我和伴侣在健康生活方式（如饮食、锻炼、物质使用）上是兼容的。", "type": "scale", "range": (1, 7)},
            "F1.2": {"text": "伴侣支持我保持健康的生活方式，我也支持他/她。", "type": "scale", "range": (1, 7)},
            "F1.3": {"text": "我担心伴侣的健康习惯或选择。", "type": "scale", "range": (1, 7), "is_cost": True},
            "F1.4": {"text": "如果我们中有一人面临严重的健康问题，我相信我们会有效地互相支持。", "type": "scale", "range": (1, 7)},
            "F2.1_Partner_Attraction": {"text": "我对伴侣当前的生理吸引力有多满意？ (1=非常不满意, 7=非常满意):", "type": "scale", "range": (1, 7), "amplify_extremes": True},
            "F2.2_Self_Attraction_Perception": {"text": "我如何评价自己当前的生理吸引力？ (1=很不吸引, 7=非常有吸引力):", "type": "scale", "range": (1, 7)},
            "F2.3_Attraction_Gap_Perception": {"text": "我感觉我和伴侣在生理吸引力上是否存在较大差距？ (1=我觉得我远不如伴侣吸引, 4=差不多, 7=我觉得我远比伴侣吸引):", "type": "scale", "range": (1, 7)},
            "F2.4_Intimacy_Satisfaction": {"text": "我对我们关系中身体亲密的程度和质量感到满意。", "type": "scale", "range": (1, 7), "amplify_extremes": True},
            "F2.5": {"text": "我们能就性需求和愿望进行开放有效的沟通。", "type": "scale", "range": (1, 7)},
            "F3.1_Child_Alignment": {"text": "我和伴侣在生育问题上（时机、数量、育儿理念）是否一致？", "type": "radio_na", "options": ["非常一致", "比较一致", "中立/不确定", "有些分歧", "严重分歧", NA_STRING]},
            "F3.2_Coparent_Confidence": {"text": "作为潜在的共同抚养人，您对伴侣的信心如何？", "type": "radio_na", "options": ["非常有信心", "比较有信心", "中立/不确定", "信心不足", "非常没信心", NA_STRING]},
        }
    },
    "G": { # 政治学
        "title": "政治学因素",
        "questions": {
            "G1.1": {"text": "我觉得关系中的权力和决策是公平共享的。", "type": "scale", "range": (1, 7)},
            "G1.2": {"text": "在重要的关系决策中，我的意见和偏好得到同等重视。", "type": "scale", "range": (1, 7)},
            "G1.3": {"text": "我有时感到被伴侣控制或支配。", "type": "scale", "range": (1, 7), "is_cost": True},
            "G2.1": {"text": "我们能有效地以建设性的方式解决冲突。", "type": "scale", "range": (1, 7)},
            "G2.2": {"text": "当我们意见不合时，通常能达成双方都满意的妥协。", "type": "scale", "range": (1, 7)},
            "G2.3": {"text": "冲突经常升级或悬而未决。", "type": "scale", "range": (1, 7), "is_cost": True},
            "G3.1": {"text": "我们对关系的未来有共同的愿景。", "type": "scale", "range": (1, 7)},
            "G3.2": {"text": "我的个人自主性（个人空间、独处时间、独立追求）在这段关系中得到尊重。", "type": "scale", "range": (1, 7)},
        }
    },
    "H": { # 哲学
        "title": "哲学因素",
        "questions": {
            "H1.1": {"text": "我和伴侣拥有相似的核心伦理和道德价值观。", "type": "scale", "range": (1, 7)},
            "H1.2": {"text": "在多数重要的人生情境中，我们对是非的判断是一致的。", "type": "scale", "range": (1, 7)},
            "H1.3": {"text": "我对伴侣的伦理行为或道德标准有严重关切。", "type": "scale", "range": (1, 7), "is_cost": True},
            "H2.1": {"text": "这段关系有助于我的人生意义感和目标感。", "type": "scale", "range": (1, 7)},
            "H2.2": {"text": "伴侣支持我追求个人的人生目标和抱负。", "type": "scale", "range": (1, 7)},
            "H2.3": {"text": "我们有一些共同的长远人生目标或抱负。", "type": "scale", "range": (1, 7)},
            "H3.1": {"text": "在这段关系中，我能做真实的自我。", "type": "scale", "range": (1, 7)},
        }
    },
    "I": { # 法学/准法学
        "title": "法学/准法学因素",
        "questions": {
            "I1.1": {"text": "我完全致力于这段关系。", "type": "scale", "range": (1, 7)},
            "I1.2": {"text": "我相信我的伴侣完全致力于这段关系。", "type": "scale", "range": (1, 7)},
            "I1.3": {"text": "我完全信任我的伴侣。", "type": "scale", "range": (1, 7)},
            "I2.1": {"text": "我们关系中不成文的规则和期望感觉是公平和平衡的。", "type": "scale", "range": (1, 7)},
            "I2.2": {"text": "伴侣一贯能满足我对他们在这段关系中的期望（反之亦然）。", "type": "scale", "range": (1, 7)},
            "I3.1": {"text": "我对这段关系的长远未来感到安心。", "type": "scale", "range": (1, 7)},
            "I3.2_Discuss_Future": {"text": "我们是否已公开讨论过对这段关系的长期打算（如婚姻、同居）？", "type": "radio_na", "options": ["清晰讨论过且方向一致", "讨论过但尚无明确结论", "几乎未讨论过", NA_STRING]},
        }
    },
    "J": { # 传播学
        "title": "传播学因素",
        "questions": {
            "J1.1": {"text": "我们能就重要事务进行开放和诚实的沟通。", "type": "scale", "range": (1, 7)},
            "J1.2": {"text": "当我表达自己时，我感到被伴侣倾听和理解。", "type": "scale", "range": (1, 7)},
            "J1.3": {"text": "我的伴侣是一个好的倾听者。", "type": "scale", "range": (1, 7)},
            "J1.4": {"text": "我们擅长向对方表达爱意和感激。", "type": "scale", "range": (1, 7)},
            "J2.1": {"text": "我们的沟通经常包含批评、辩护或指责。", "type": "scale", "range": (1, 7), "is_cost": True},
            "J2.2": {"text": "我们能够给予和接受建设性的反馈而不会引发大问题。", "type": "scale", "range": (1, 7)},
            "J2.3": {"text": "我们很能理解对方的非语言暗示（如肢体语言、语气）。", "type": "scale", "range": (1, 7)},
        }
    },
    "K": { # 历史学
        "title": "历史学因素",
        "questions": {
            "K1.1": {"text": "我们拥有丰富的积极共同经历。", "type": "scale", "range": (1, 7)},
            "K1.2": {"text": "回顾我们的关系，美好的回忆远超不好的回忆。", "type": "scale", "range": (1, 7)},
            "K1.3": {"text": "过去我们曾一起成功应对过困难的挑战。", "type": "scale", "range": (1, 7)},
            "K2.1": {"text": "我们从过去关系中的冲突或错误中学习并成长了。", "type": "scale", "range": (1, 7)},
            "K2.2": {"text": "我看到我们一遍又一遍地重复着同样的负面互动模式。", "type": "scale", "range": (1, 7), "is_cost": True},
            "K3.1_Initial_Motivation_Attraction": {"text": "关系开始时，相互的强烈生理和情感吸引是主要的驱动力吗？ (1=完全不是, 7=绝对是):", "type": "scale", "range": (1, 7)},
            "K3.2_Initial_Motivation_No_Alternative": {"text": "关系开始时，缺乏其他更好的选择在多大程度上是您接受关系的原因之一？ (1=完全不是, 7=很大程度上是):", "type": "scale", "range": (1, 7)},
        }
    },
    "L": { # 地理学
        "title": "地理学因素",
        "questions": {
            "L1.1_Shared_Space": {"text": "（如果同居）我对我们共享的居住空间及其管理方式的感受如何？", "type": "radio_na", "options": ["非常满意", "比较满意", "一般", "不太满意", "非常不满意", NA_STRING]},
            "L1.2": {"text": "我们目前的地理位置是否能很好地满足双方的需求（职业、家庭、生活方式）？", "type": "scale", "range": (1, 7)},
            "L2.1_Distance_Strain": {"text": "（如果异地或频繁出差）我们之间的物理距离对关系的压力程度如何？", "type": "radio_na", "options": ["几乎无压力", "有些压力但可控", "影响较大构成压力", "严重影响关系质量", NA_STRING]},
            "L2.2_Manage_Separation": {"text": "我们如何有效地管理分离期？", "type": "radio_na", "options": ["管理得非常好", "管理得比较好", "一般", "管理得不太好", "管理得很差", NA_STRING]},
        }
    },
    "M": { # 生态学
        "title": "生态学因素",
        "questions": {
            "M1.1": {"text": "我们的关系感觉很有韧性；我们能从挫折中恢复过来。", "type": "scale", "range": (1, 7)},
            "M1.2": {"text": "我们的关系能很好地适应我们生活或外部环境的变化。", "type": "scale", "range": (1, 7)},
            "M2.1": {"text": "这段关系总体上给我的能量多于消耗我的能量。", "type": "scale", "range": (1, 7)},
            "M2.2": {"text": "我觉得我们关系中给予和接受支持是健康平衡的。", "type": "scale", "range": (1, 7)},
            "M3.1": {"text": "我们的相互依赖感觉是健康的、互利的，而非共生依赖或单方面的。", "type": "scale", "range": (1, 7)},
        }
    },
    "N": { # 信息论/系统论
        "title": "信息论/系统论因素",
        "questions": {
            "N1.1": {"text": "我们的关系中有舒适的可预测性和常规。", "type": "scale", "range": (1, 7)},
            "N1.2": {"text": "我们的关系常常感觉混乱或不稳定。", "type": "scale", "range": (1, 7), "is_cost": True},
            "N2.1": {"text": "我们的关系系统对新信息持开放态度，并能够调整（例如，如果旧方法无效则尝试新方法）。", "type": "scale", "range": (1, 7)},
            "N2.2": {"text": "我们通常擅长识别何时事情不顺利并做出改变。", "type": "scale", "range": (1, 7)},
            "N3.1": {"text": "我们的关系通常能很好地抵御负面的外部影响。", "type": "scale", "range": (1, 7)},
            "N3.2": {"text": "我们擅长在有益时采纳积极的外部意见（如信任的朋友的建议，必要时的专业帮助）。", "type": "scale", "range": (1, 7)},
        }
    },
    "O": {
        "title": "未来预期与贴现率代理",
        "questions": {
            "O1": {"text": "展望未来，我对这段关系持乐观态度。", "type": "scale", "range": (1, 7)},
            "O2": {"text": "我预期这段关系带来的益处会随时间增加或保持较高水平。", "type": "scale", "range": (1, 7)},
            "O3": {"text": "我预期这段关系的成本或困难会随时间减少或保持可控。", "type": "scale", "range": (1, 7)},
            "O4": {"text": "做重要人生决策时，我倾向于优先考虑长期利益而非即时满足。", "type": "scale", "range": (1, 7)},
        }
    },
    "WEIGHTS": {
        "title": "各因素重要性权重分配",
        "questions": {
            "W_B_Psych": {"text": "心理学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_C_Econ": {"text": "经济学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_D_Soc": {"text": "社会学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_E_Anth": {"text": "人类学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_F_BioMed": {"text": "生物/医学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_G_PolSci": {"text": "政治学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_H_Phil": {"text": "哲学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_I_Law": {"text": "法学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_J_Comm": {"text": "传播学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_K_Hist": {"text": "历史学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_L_Geo": {"text": "地理学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_M_Eco": {"text": "生态学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_N_InfoSys": {"text": "信息/系统论因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_I0_Importance": {"text": "已投入的转换成本(I_0)对您决策的重要性:", "type": "scale", "range": (1, 5)},
        }
    }
}


# --- RVCUM Calculator Class ---
class RVCUMCalculator:
    def __init__(self, responses, questionnaire_structure):
        self.responses = responses
        self.q_struct = questionnaire_structure
        self.detailed_log = []
        self.discipline_summary = {}

    def _log(self, message):
        self.detailed_log.append(message)
        # print(message) # Optional: for console debugging

    def _get_raw_score(self, section_id, q_key):
        """Safely gets raw score string, returns None if not found."""
        try:
            return self.responses[section_id][q_key]
        except KeyError:
            self._log(f"警告: 无法在响应中找到 {section_id} - {q_key}")
            return None

    def _transform_score(self, score_str, q_def):
        """Transforms raw score to a normalized [-1, 1] or specific mapping. Returns (value, is_na)"""
        if score_str is None or score_str == "":
            if q_def["type"] == "scale": score_str = str((q_def["range"][0] + q_def["range"][1]) / 2.0) # Default scale to neutral
            elif q_def["type"] == "text_int": return 0, True # Cannot default int easily
            elif q_def["type"] in ["combo", "radio_na"] and q_def["options"]: score_str = q_def["options"][0] # Default combo/radio to first option
            else: return 0, True # Treat other empty as N/A

        if q_def["type"] == "radio_na":
            if score_str == NA_STRING: return 0, True
            try:
                idx = q_def["options"].index(score_str)
                num_options_no_na = len(q_def["options"]) - (1 if NA_STRING in q_def["options"] else 0)
                if num_options_no_na <= 1: return 0, False
                raw_val = float(num_options_no_na - 1 - idx)
                neutral = (num_options_no_na - 1) / 2.0
                max_dev = neutral
                if max_dev == 0: return 0, False
                return (raw_val - neutral) / max_dev, False
            except ValueError:
                self._log(f"警告: 无法解析 radio_na 选项 '{score_str}' for {q_def['text']}")
                return 0, True

        try:
            score = float(score_str)
        except ValueError:
            self._log(f"警告: 无法将分数 '{score_str}' 解析为浮点数 for {q_def['text']}")
            return 0, True

        if q_def["type"] == "scale":
            low, high = q_def["range"]
            neutral = (low + high) / 2.0
            max_deviation = high - neutral
            if max_deviation == 0: return 0, False
            transformed = (score - neutral) / max_deviation

            if q_def.get("amplify_extremes", False):
                power = 1.2
                if transformed > 0: transformed = math.pow(transformed, power)
                elif transformed < 0: transformed = -math.pow(abs(transformed), power)
            return max(-1.0,min(1.0,transformed)), False # Clamp to [-1,1]
        
        if q_def["type"] == "text_int":
             # For text_int, the value is the score itself, no normalization needed here
             # It will be used directly (e.g., age difference) or as a raw value.
             return score, False

        return 0, False

    def _calculate_i0_value(self):
        """Refined I_0 calculation."""
        i0_value_raw_sum = 0
        max_possible_raw_sum = 0
        self._log("\n--- 计算初始投资/转换成本 (I_0) ---")

        i0_component_keys = []
        for section_id, section_data in self.q_struct.items():
             for q_key, q_def in section_data["questions"].items():
                 if q_def.get("is_i0_component", False):
                     i0_component_keys.append((section_id, q_key))

        if not i0_component_keys:
             self._log("  没有定义I_0组件问题。I_0 = 0")
             return 0

        for section_id, q_key in i0_component_keys:
            q_def = self.q_struct[section_id]["questions"][q_key]
            raw_score_str = self._get_raw_score(section_id, q_key)
            if raw_score_str is None: continue

            try:
                raw_score = float(raw_score_str)
                low, high = q_def["range"]
                # Costliness points: 0 for min score, (high-low) for max score
                costliness_points = (raw_score - low)
                i0_value_raw_sum += costliness_points
                max_possible_raw_sum += (high - low)
                self._log(f"  I_0 组件 {q_key}: \"{q_def['text'][:30]}...\" 原始分={raw_score_str}, 贡献点数={costliness_points:.2f}")
            except ValueError:
                self._log(f"  警告: I_0 组件 {q_key} 的原始分无效: {raw_score_str}")

        if max_possible_raw_sum == 0:
             self._log("  I_0组件的最大可能原始分总和为0。I_0 = 0")
             return 0

        # Normalize raw I0 value (0 to 1 based on sum of max possible points)
        normalized_i0 = i0_value_raw_sum / max_possible_raw_sum

        # User's perceived importance of I0 (1-5 scale)
        i0_importance_raw = self._get_raw_score("WEIGHTS", "W_I0_Importance")
        i0_importance_qdef = self.q_struct["WEIGHTS"]["questions"]["W_I0_Importance"]
        i0_importance_transformed = self._transform_score(i0_importance_raw, i0_importance_qdef)[0] # -1 to 1
        # Map importance (-1 to 1) to a multiplier (e.g., 0.5 to 1.5 for the max_i0_value)
        i0_importance_multiplier = 1.0 + (i0_importance_transformed * 0.5) # Range 0.5 to 1.5
        self._log(f"  I_0 重要性评分: 原始={i0_importance_raw}, 转换后={i0_importance_transformed:.2f}, 乘数={i0_importance_multiplier:.2f}")

        # Max possible I0 value (e.g., 15 points of NPV). This is a tuning parameter.
        max_i0_npv_contribution_base = 15.0
        scaled_i0_value = normalized_i0 * max_i0_npv_contribution_base * i0_importance_multiplier

        self._log(f"  归一化I_0={normalized_i0:.2f}, 计算的I_0价值 (加到关系NPV上): {scaled_i0_value:.2f}")
        return scaled_i0_value


    def calculate_rvcum(self):
        self.detailed_log = []
        self.discipline_summary = {}
        self._log("--- 开始RVCUM计算 (v3.1 - 完整版) ---")

        # --- 1. Extract Key Parameters & New Factors ---
        try:
            batna_score_raw = self._get_raw_score("A", "A5")
            batna_q_def = self.q_struct["A"]["questions"]["A5"]
            batna_transformed_score = self._transform_score(batna_score_raw, batna_q_def)[0]

            batna_confidence_raw = self._get_raw_score("A", "A6_BATNA_Confidence")
            batna_conf_q_def = self.q_struct["A"]["questions"]["A6_BATNA_Confidence"]
            batna_confidence_transformed = self._transform_score(batna_confidence_raw, batna_conf_q_def)[0]
            self._log(f"原始BATNA评分 (A5): {batna_score_raw}, 转换后: {batna_transformed_score:.2f}")
            self._log(f"BATNA信心 (A6): {batna_confidence_raw}, 转换后: {batna_confidence_transformed:.2f}")

            self_age_str = self._get_raw_score("A", "A7_Self_Age")
            partner_age_str = self._get_raw_score("A", "A8_Partner_Age")
            self_age = int(self_age_str) if self_age_str and self_age_str.isdigit() else 0
            partner_age = int(partner_age_str) if partner_age_str and partner_age_str.isdigit() else 0
            age_difference = abs(self_age - partner_age) if self_age > 0 and partner_age > 0 else 0
            self._log(f"年龄: 自己={self_age}, 伴侣={partner_age}, 差异={age_difference}岁")
            age_diff_cost_factor = min(age_difference * 0.005, 0.1)

            o4_raw = self._get_raw_score("O", "O4")
            o4_q_def = self.q_struct["O"]["questions"]["O4"]
            o4_val = self._transform_score(o4_raw, o4_q_def)[0]
            r_min, r_max = 0.03, 0.15
            discount_rate = r_max - ((o4_val + 1) / 2) * (r_max - r_min)
            discount_rate = max(0.01, min(discount_rate, 0.20))
            self._log(f"贴现率代理 (O4): 原始={o4_raw}, 转换后={o4_val:.2f}, 计算贴现率 r: {discount_rate:.4f}")

            o1_raw = self._get_raw_score("O", "O1"); o1_qdef = self.q_struct["O"]["questions"]["O1"]
            o2_raw = self._get_raw_score("O", "O2"); o2_qdef = self.q_struct["O"]["questions"]["O2"]
            o3_raw = self._get_raw_score("O", "O3"); o3_qdef = self.q_struct["O"]["questions"]["O3"]
            o1_optimism = self._transform_score(o1_raw, o1_qdef)[0]
            o2_benefits_growth = self._transform_score(o2_raw, o2_qdef)[0]
            o3_costs_reduction = self._transform_score(o3_raw, o3_qdef)[0]

            avg_outlook_transformed = (o1_optimism + o2_benefits_growth + o3_costs_reduction) / 3.0
            current_period_outlook_penalty_factor = 0
            if avg_outlook_transformed < -0.1:
                current_period_outlook_penalty_factor = abs(avg_outlook_transformed) * 0.1
                self._log(f"未来预期偏负面，对当前周期施加惩罚因子: {current_period_outlook_penalty_factor:.3f}")

            utility_annual_growth_factor = 1.0 + (o1_optimism * 0.02) + (o2_benefits_growth * 0.02)
            cost_annual_reduction_factor = 1.0 - (o1_optimism * 0.01) - (o3_costs_reduction * 0.02)
            utility_annual_growth_factor = max(0.95, min(utility_annual_growth_factor, 1.05))
            cost_annual_reduction_factor = max(0.95, min(cost_annual_reduction_factor, 1.05))
            self._log(f"未来预期: 乐观度={o1_optimism:.2f}, 益处增长={o2_benefits_growth:.2f}, 成本降低={o3_costs_reduction:.2f}")
            self._log(f"效用年增长因子: {utility_annual_growth_factor:.3f}, 成本年变化因子: {cost_annual_reduction_factor:.3f}")

        except Exception as e:
            self._log(f"错误：提取关键参数失败 - {e}")
            self._log(traceback.format_exc())
            return {"error": f"提取关键参数失败: {e}", "detailed_log": self.detailed_log}

        # --- Get Weights ---
        weights = self._get_normalized_weights()

        # --- 2. Calculate Initial Investment / Switching Costs (I_0) ---
        scaled_i0_value = self._calculate_i0_value()

        # --- 3. Calculate Weighted Current Net Utility from Disciplines ---
        current_period_total_utility = 0
        current_period_total_cost = 0
        discipline_scores = {}

        # --- 3a. Special "Direct Add" Costs ---
        if "B5.1_Pity_Cost" in self.q_struct.get("B", {}).get("questions", {}):
            pity_q_def = self.q_struct["B"]["questions"]["B5.1_Pity_Cost"]
            pity_raw = self._get_raw_score("B", "B5.1_Pity_Cost")
            if pity_raw is not None:
                try:
                    pity_raw_float = float(pity_raw)
                    pity_cost_factor = (pity_raw_float - pity_q_def["range"][0]) / (pity_q_def["range"][1] - pity_q_def["range"][0])
                    pity_cost_value = pity_cost_factor * 0.5 # Max 0.5 points of cost
                    current_period_total_cost += pity_cost_value
                    self._log(f"直接成本项 (B5.1 同情成本): 原始={pity_raw}, 成本贡献={pity_cost_value:.2f}")
                except ValueError:
                     self._log(f"警告: B5.1 原始分无效: {pity_raw}")


        # --- 3b. Attraction Asymmetry Cost ---
        attraction_asymmetry_cost = 0
        try:
            partner_attr_raw = self._get_raw_score("F", "F2.1_Partner_Attraction")
            partner_attr_qdef = self.q_struct["F"]["questions"]["F2.1_Partner_Attraction"]
            partner_attr_transformed = self._transform_score(partner_attr_raw, partner_attr_qdef)[0]

            self_attr_raw = self._get_raw_score("F", "F2.2_Self_Attraction_Perception")
            self_attr_qdef = self.q_struct["F"]["questions"]["F2.2_Self_Attraction_Perception"]
            self_attr_transformed = self._transform_score(self_attr_raw, self_attr_qdef)[0]

            gap_attr_raw = self._get_raw_score("F", "F2.3_Attraction_Gap_Perception")
            gap_attr_qdef = self.q_struct["F"]["questions"]["F2.3_Attraction_Gap_Perception"]
            gap_attr_transformed = self._transform_score(gap_attr_raw, gap_attr_qdef)[0]
            self._log(f"吸引力评分: 伴侣={partner_attr_transformed:.2f}, 自己={self_attr_transformed:.2f}, 感知差距={gap_attr_transformed:.2f}")

            if gap_attr_transformed > 0.5 and partner_attr_transformed < -0.2 and self_attr_transformed > 0.5:
                asymmetry_magnitude = (gap_attr_transformed) + abs(partner_attr_transformed) + (self_attr_transformed)
                attraction_asymmetry_cost = (asymmetry_magnitude / 3.0) * 0.6
                current_period_total_cost += attraction_asymmetry_cost
                self._log(f"显著吸引力不对称，产生额外成本: {attraction_asymmetry_cost:.2f}")
        except Exception as e: self._log(f"计算吸引力不对称成本时出错: {e}")

        # --- 3c. Initial Motivation Modifier ---
        try:
            k31_raw = self._get_raw_score("K", "K3.1_Initial_Motivation_Attraction")
            k31_qdef = self.q_struct["K"]["questions"]["K3.1_Initial_Motivation_Attraction"]
            k31_transformed = self._transform_score(k31_raw, k31_qdef)[0]

            k32_raw = self._get_raw_score("K", "K3.2_Initial_Motivation_No_Alternative")
            k32_qdef = self.q_struct["K"]["questions"]["K3.2_Initial_Motivation_No_Alternative"]
            k32_transformed = self._transform_score(k32_raw, k32_qdef)[0]
            self._log(f"初始动机: 吸引力驱动={k31_transformed:.2f}, 缺乏替代方案驱动={k32_transformed:.2f}")

            if k31_transformed < -0.2 and k32_transformed > 0.2:
                initial_motivation_penalty = (abs(k31_transformed) + k32_transformed) * 0.15
                current_period_total_cost += initial_motivation_penalty
                self._log(f"初始动机不佳，对当前周期成本产生调整: +{initial_motivation_penalty:.2f}")
        except Exception as e: self._log(f"计算初始动机调整子时出错: {e}")

        # --- 3d. Iterate through main questionnaire sections (B to N) ---
        weight_key_map = {
                'B': 'W_B_Psych', 'C': 'W_C_Econ', 'D': 'W_D_Soc', 'E': 'W_E_Anth',
                'F': 'W_F_BioMed', 'G': 'W_G_PolSci', 'H': 'W_H_Phil', 'I': 'W_I_Law',
                'J': 'W_J_Comm', 'K': 'W_K_Hist', 'L': 'W_L_Geo', 'M': 'W_M_Eco', 'N': 'W_N_InfoSys'
        }
        for section_id in "BCDEFGHIJKLMN":
            if section_id not in self.q_struct: continue
            section_data = self.q_struct[section_id]
            self._log(f"\n处理学科: {section_data['title']} ({section_id})")

            section_utility_sum = 0; section_cost_sum = 0
            num_valid_utility_q_weighted = 0; num_valid_cost_q_weighted = 0

            internal_weights_config = {}
            if section_id == 'F':
                internal_weights_config = { "F2.1_Partner_Attraction": 2.0, "F2.4_Intimacy_Satisfaction": 1.5 }

            current_section_q_details = []

            for q_key, q_def in section_data["questions"].items():
                if q_def.get("is_i0_component", False) or q_def.get("is_cost_direct", False): continue

                raw_response = self._get_raw_score(section_id, q_key)
                if raw_response is None: continue
                transformed_score, is_na = self._transform_score(raw_response, q_def)
                if is_na: continue

                q_internal_weight = internal_weights_config.get(q_key, 1.0)
                current_section_q_details.append({
                    "text": q_def['text'][:40] + "...",
                    "raw": raw_response,
                    "transformed": transformed_score,
                    "is_cost_q": q_def.get("is_cost", False)
                })

                if q_def.get("is_cost", False):
                    section_cost_sum += transformed_score * q_internal_weight
                    num_valid_cost_q_weighted += q_internal_weight
                else:
                    section_utility_sum += transformed_score * q_internal_weight
                    num_valid_utility_q_weighted += q_internal_weight

            avg_section_utility = section_utility_sum / num_valid_utility_q_weighted if num_valid_utility_q_weighted > 0 else 0
            avg_section_cost = section_cost_sum / num_valid_cost_q_weighted if num_valid_cost_q_weighted > 0 else 0
            net_section_score = avg_section_utility - avg_section_cost

            discipline_scores[section_id] = net_section_score

            actual_weight_key = weight_key_map.get(section_id)
            section_weight = weights.get(actual_weight_key, 0) if actual_weight_key else 0

            weighted_net_score = net_section_score * section_weight
            if weighted_net_score > 0: current_period_total_utility += weighted_net_score
            else: current_period_total_cost += abs(weighted_net_score)

            self.discipline_summary[section_id] = {
                "title": section_data['title'],
                "avg_utility": avg_section_utility, "avg_cost": avg_section_cost,
                "net_score": net_section_score, "weight": section_weight,
                "weighted_net_score": weighted_net_score,
                "questions": current_section_q_details
            }
            self._log(f"  学科 {section_id} ({section_data['title']}): AvgU={avg_section_utility:.2f}, AvgC={avg_section_cost:.2f}, Net={net_section_score:.2f}, WeightedNet={weighted_net_score:.2f} (W={section_weight:.3f})")

        # --- 3e. Apply Age Difference Cost Factor ---
        if age_diff_cost_factor > 0 and age_difference > 5:
            base_for_age_cost = max(0.5, abs(current_period_total_utility - current_period_total_cost))
            age_related_cost = base_for_age_cost * age_diff_cost_factor
            current_period_total_cost += age_related_cost
            self._log(f"年龄差异 ({age_difference}岁) 导致额外成本调整: +{age_related_cost:.2f}")

        # --- 3f. Apply Pessimism Penalty ---
        if current_period_outlook_penalty_factor > 0:
            net_utility_val = current_period_total_utility - current_period_total_cost
            penalty_amount = abs(net_utility_val) * current_period_outlook_penalty_factor
            if net_utility_val > 0 : current_period_total_utility -= penalty_amount
            else: current_period_total_cost += penalty_amount
            self._log(f"未来预期悲观，调整当前净效用，惩罚量 (影响值): {penalty_amount:.2f}")

        # --- 3g. Enhanced Interaction Terms ---
        if batna_confidence_transformed > 0.5 and discipline_scores.get('F',0) < -0.3 :
            gap_attr_raw = self._get_raw_score("F", "F2.3_Attraction_Gap_Perception")
            gap_attr_qdef = self.q_struct["F"]["questions"]["F2.3_Attraction_Gap_Perception"]
            gap_attr_transformed = self._transform_score(gap_attr_raw, gap_attr_qdef)[0]
            if gap_attr_transformed > 0.5:
                opportunity_cost_interaction = batna_confidence_transformed * gap_attr_transformed * 0.3
                current_period_total_cost += opportunity_cost_interaction
                self._log(f"互动项 (高BATNA信心 + 自感吸引力差距大): 增加机会成本感知 +{opportunity_cost_interaction:.2f}")

        self._log(f"\n当前周期总计 (所有调整后): 效用流={current_period_total_utility:.2f}, 成本流={current_period_total_cost:.2f}")

        # --- 4. Calculate NPV of the Relationship ---
        npv_relationship_before_i0 = 0
        projected_utility = current_period_total_utility
        projected_cost = current_period_total_cost
        self._log("\n--- NPV 计算 (逐年) ---")
        self._log("年 | 预期效用 | 预期成本 | 净效用 | 折现因子 | 折现净效用")
        for t_year in range(TIME_HORIZON_YEARS):
            if t_year > 0:
                projected_utility *= utility_annual_growth_factor
                projected_cost *= cost_annual_reduction_factor
            net_period_utility = projected_utility - projected_cost
            discount_factor = 1 / ((1 + discount_rate) ** t_year)
            discounted_net_period_utility = net_period_utility * discount_factor
            npv_relationship_before_i0 += discounted_net_period_utility
            self._log(f"{t_year+1:2d} | {projected_utility:9.2f} | {projected_cost:9.2f} | {net_period_utility:8.2f} | {discount_factor:9.4f} | {discounted_net_period_utility:11.2f}")
        self._log(f"--- NPV (关系本身，未加I_0): {npv_relationship_before_i0:.2f} ---")

        # Cap I0 contribution
        # Max I0 contribution is the calculated scaled_i0_value, but capped.
        # Cap 1: Absolute cap (e.g., 15 points)
        # Cap 2: Relative cap (e.g., 75% of the absolute value of NPV before I0)
        max_i0_from_npv_base = abs(npv_relationship_before_i0) * 0.75 if npv_relationship_before_i0 != 0 else 5.0 # Use a smaller base if NPV is 0
        capped_i0_value = min(scaled_i0_value, max_i0_from_npv_base, 15.0) # Apply both caps

        if scaled_i0_value > capped_i0_value:
            self._log(f"I_0贡献被调整/封顶: 从{scaled_i0_value:.2f} 到 {capped_i0_value:.2f}")
        else:
            self._log(f"I_0贡献未经调整/封顶: {capped_i0_value:.2f}")

        npv_relationship_final = npv_relationship_before_i0 + capped_i0_value
        self._log(f"NPV (关系本身，已加调整后I_0={capped_i0_value:.2f}): {npv_relationship_final:.2f}")

        # --- 5. Estimate NPV_BATNA-R ---
        effective_batna_quality_score = batna_transformed_score * ((batna_confidence_transformed + 1) / 1.5)
        effective_batna_quality_score = max(-1.0, min(1.0, effective_batna_quality_score))
        self._log(f"BATNA调整: 原始质量分={batna_transformed_score:.2f}, 信心调整后有效质量分={effective_batna_quality_score:.2f}")

        significant_diff_factor = 0.4
        # Min diff relative to final relationship NPV if positive, or a fixed base if negative/zero
        min_abs_diff_for_batna = abs(npv_relationship_final) * 0.15 if npv_relationship_final != 0 else 5.0

        if abs(effective_batna_quality_score) < 0.1: npv_batna_r = npv_relationship_before_i0
        elif effective_batna_quality_score > 0:
            diff = max(abs(npv_relationship_before_i0) * significant_diff_factor * effective_batna_quality_score, min_abs_diff_for_batna * effective_batna_quality_score)
            npv_batna_r = npv_relationship_before_i0 + diff
        else:
            diff = max(abs(npv_relationship_before_i0) * significant_diff_factor * abs(effective_batna_quality_score), min_abs_diff_for_batna * abs(effective_batna_quality_score))
            npv_batna_r = npv_relationship_before_i0 - diff
        self._log(f"NPV (最佳替代方案 BATNA-R): {npv_batna_r:.2f} (基于当前关系NPV(无I_0)={npv_relationship_before_i0:.2f} 和调整后BATNA评分)")

        # --- 6. Decision Logic & Output ---
        decision_code = 0 # 0: continue, 1: consider, 2: strongly consider leaving
        if npv_relationship_final > npv_batna_r:
            decision = "值得继续"
            decision_code = 0
            if npv_relationship_before_i0 < npv_batna_r :
                decision += " (但主要由于转换成本较高)"
        else:
            decision = "可能不值得继续，请仔细考虑"
            decision_code = 1
            if npv_batna_r > npv_relationship_final + abs(npv_relationship_final) * 0.5 + 5: # If BATNA is significantly better (e.g., > 50% better + 5 points)
                 decision = "强烈建议考虑其他选择"
                 decision_code = 2

        self._log(f"\n最终决策建议: {decision}")
        return {
            "npv_relationship_final": npv_relationship_final,
            "npv_relationship_before_i0": npv_relationship_before_i0,
            "npv_batna_r": npv_batna_r,
            "decision_text": decision,
            "decision_code": decision_code,
            "discount_rate": discount_rate,
            "i0_value_final": capped_i0_value,
            "current_period_utility_final": current_period_total_utility,
            "current_period_cost_final": current_period_total_cost,
            "detailed_log": self.detailed_log,
            "discipline_summary": self.discipline_summary,
            "future_outlook": {"optimism": o1_optimism, "benefit_growth": o2_benefits_growth, "cost_reduction": o3_costs_reduction, "avg_transformed": avg_outlook_transformed},
            "batna_details": {"score": batna_transformed_score, "confidence": batna_confidence_transformed, "effective_quality": effective_batna_quality_score},
            "age_details": {"self_age": self_age, "partner_age": partner_age, "difference": age_difference}
        }

    def _get_normalized_weights(self):
        weights = {}
        total_weight_sum = 0
        weight_key_map = { # Map section IDs to weight keys
                'B': 'W_B_Psych', 'C': 'W_C_Econ', 'D': 'W_D_Soc', 'E': 'W_E_Anth',
                'F': 'W_F_BioMed', 'G': 'W_G_PolSci', 'H': 'W_H_Phil', 'I': 'W_I_Law',
                'J': 'W_J_Comm', 'K': 'W_K_Hist', 'L': 'W_L_Geo', 'M': 'W_M_Eco', 'N': 'W_N_InfoSys'
        }
        
        for section_id, weight_key in weight_key_map.items():
            if weight_key not in self.q_struct.get("WEIGHTS", {}).get("questions", {}):
                 self._log(f"警告: 权重 {weight_key} 未在 WEIGHTS 部分定义。")
                 weights[weight_key] = 0
                 continue

            w_data = self.q_struct["WEIGHTS"]["questions"][weight_key]
            raw_val = self._get_raw_score("WEIGHTS", weight_key)
            if raw_val is None: raw_val = str((w_data["range"][0] + w_data["range"][1]) / 2.0) # Default to neutral
            try:
                weight_val = float(raw_val)
                weights[weight_key] = weight_val
                total_weight_sum += weight_val
            except ValueError:
                self._log(f"警告: 权重 {weight_key} 无效 ({raw_val})，设为0。")
                weights[weight_key] = 0

        if total_weight_sum > 0:
            for w_key in weights: weights[w_key] /= total_weight_sum
        else:
            num_main_weights = len(weights)
            for w_key in weights: weights[w_key] = 1.0 / num_main_weights if num_main_weights > 0 else 0
        self._log(f"归一化后的学科权重: { {k: f'{v:.3f}' for k, v in weights.items()} }")
        return weights


    def generate_natural_language_interpretation(self, results):
        lang_log = []
        lang_log.append("--- 恋爱关系价值评估解读 ---")

        npv_rel_final = results['npv_relationship_final']
        npv_rel_no_i0 = results['npv_relationship_before_i0']
        npv_batna = results['npv_batna_r']
        i0_val = results['i0_value_final']
        decision_text = results['decision_text']
        decision_code = results['decision_code']

        lang_log.append(f"\n【核心结论】")
        lang_log.append(f"模型计算得出，您当前关系的总体价值潜力 (NPV) 估算为 {npv_rel_final:.2f} 点。")
        lang_log.append(f"相较之下，您的最佳替代选择 (BATNA-R) 的价值潜力估算为 {npv_batna:.2f} 点。")
        lang_log.append(f"基于此对比，模型的初步建议是：【{decision_text}】")

        lang_log.append(f"\n【深入分析】")
        # Current state
        current_u = results['current_period_utility_final']
        current_c = results['current_period_cost_final']
        current_net = current_u - current_c
        lang_log.append(f"当前感受：您目前从关系中获得的即时满足感（效用流 {current_u:.2f}）与不适感（成本流 {current_c:.2f}）相抵后，净体验值为 {current_net:.2f}。")
        if current_net > 0.8: lang_log.append("  这表明当前关系整体上能给您带来较为强烈的积极即时感受。")
        elif current_net > 0.2: lang_log.append("  这表明当前关系整体上能给您带来一些积极的即时感受。")
        elif current_net > -0.2 : lang_log.append("  这表明当前关系带来的积极与消极感受可能较为平衡。")
        else: lang_log.append("  这表明当前关系可能给您带来了较多的即时不适感。")

        # I_0 (转换成本) 的影响
        lang_log.append(f"\n转换成本的角色：模型估算了您离开这段关系可能面临的“转换成本”（如情感投入、生活交织等），其“避免价值”为 {i0_val:.2f} 点，并已计入当前关系的总NPV中。")
        lang_log.append(f"  若不考虑这部分转换成本，关系本身的未来净效用流NPV为 {npv_rel_no_i0:.2f} 点。")
        if i0_val > abs(npv_rel_no_i0) * 0.6 and i0_val > 4.0 : # If I0 is significant
            lang_log.append(f"  请注意，转换成本在您的总评估中占有较大比重。这意味着“难以离开”的因素对最终“值得继续”的结论有显著影响。")
            if npv_rel_no_i0 < npv_batna and decision_code == 0:
                 lang_log.append("    事实上，若不考虑转换成本，您的最佳替代方案看起来比关系本身更有吸引力。这可能提示您思考，是真心满意还是“习惯了”或“怕麻烦”？")
        elif i0_val > 1.0:
             lang_log.append(f"  转换成本对您的决策有一定影响，但可能不是决定性因素。")
        else:
             lang_log.append(f"  转换成本在您的评估中占比较小。")


        # 未来预期
        outlook = results['future_outlook']
        avg_outlook = outlook['avg_transformed']
        lang_log.append(f"\n未来展望：您对关系的未来预期 ({avg_outlook:.2f}，范围-1到1，正数表示乐观) 会影响模型对未来价值的预测。")
        if avg_outlook < -0.4: lang_log.append("  您对未来的看法似乎偏向悲观，这会显著拉低关系长期的价值预期，并可能已对您当下的感受产生负面影响。")
        elif avg_outlook < -0.1: lang_log.append("  您对未来的看法似乎偏向谨慎或略有悲观。")
        elif avg_outlook > 0.4: lang_log.append("  您对未来抱有积极甚至乐观的期望，这为关系的长期价值增添了潜力。")
        elif avg_outlook > 0.1: lang_log.append("  您对未来抱有积极的期望。")
        else: lang_log.append("  您对未来的看法较为中性。")

        # BATNA
        batna_details = results['batna_details']
        lang_log.append(f"\n关于您的“后路”(BATNA)：您对最佳替代方案的评价 ({batna_details['score']:.2f}) 和找到它的信心 ({batna_details['confidence']:.2f}) 对决策至关重要。")
        if batna_details['effective_quality'] > 0.5:
             lang_log.append("  模型认为您有非常不错的替代选择，且您对此有信心。这使得当前关系的“性价比”面临较大考验。")
        elif batna_details['effective_quality'] > 0.1:
             lang_log.append("  您似乎认为有不错的替代选择，且您对此有一定信心。")
        elif batna_details['effective_quality'] < -0.5:
             lang_log.append("  您可能认为替代选择不太理想，且对此信心不足。这会增加您对当前关系的依赖性。")
        elif batna_details['effective_quality'] < -0.1:
             lang_log.append("  您可能认为替代选择不太理想或对此信心不足。")
        else:
             lang_log.append("  您对替代选择的看法较为中性。")


        # 学科亮点与痛点
        lang_log.append("\n【各方面表现概览】（基于您的评分和权重，加权净得分越高越好）:")
        sorted_disciplines = sorted(results['discipline_summary'].items(), key=lambda item: item[1]['weighted_net_score'], reverse=True)

        strong_points = []
        weak_points = []
        for sec_id, summary in sorted_disciplines:
            log_entry = f"  - {summary['title']} ({sec_id}): 加权净得分 {summary['weighted_net_score']:.2f} (原始净分 {summary['net_score']:.2f}, 权重 {summary['weight']:.3f})"
            lang_log.append(log_entry)
            if summary['weighted_net_score'] > 0.05 : strong_points.append(summary['title'])
            elif summary['weighted_net_score'] < -0.05 : weak_points.append(summary['title'])

        if strong_points: lang_log.append(f"\n  主要优势领域可能包括：{', '.join(strong_points[:3])}{'等' if len(strong_points)>3 else ''}。")
        if weak_points: lang_log.append(f"  需要关注和改善的领域可能包括：{', '.join(weak_points[:3])}{'等' if len(weak_points)>3 else ''}。")

        # Specific advice based on your situation (attraction gap, age)
        f_summary = results['discipline_summary'].get('F')
        if f_summary and f_summary['net_score'] < -0.2:
            partner_attr_score = None
            gap_score = None
            for q_detail in f_summary['questions']:
                if "F2.1_Partner_Attraction" in q_detail['text']: partner_attr_score = q_detail['transformed']
                if "F2.3_Attraction_Gap_Perception" in q_detail['text']: gap_score = q_detail['transformed']

            if partner_attr_score is not None and partner_attr_score < -0.3 and gap_score is not None and gap_score > 0.3:
                lang_log.append("\n  特别提示：您在“生物/医学因素”（尤其是伴侣生理吸引力和双方吸引力差距感知）方面评分较低。")
                lang_log.append("    这种吸引力的显著落差，结合您较高的“约会市场价值”感知，可能是关系中一个持续的挑战和不满来源。模型已将此计为一项成本。")

        age_diff = results['age_details']['difference']
        if age_diff > 8: # Arbitrary threshold for significant age difference
             lang_log.append(f"\n  年龄差异 ({age_diff}岁) 可能在生活阶段、未来规划等方面带来潜在挑战，模型已对此有所考量。")


        lang_log.append("\n【行动建议】")
        if decision_code == 0:
            if npv_rel_no_i0 < npv_batna :
                 lang_log.append("1. 深入思考转换成本：明确是哪些“沉没成本”或“转换壁垒”让您倾向于留下。这些因素的真实分量是否足以弥补关系其他方面的不足？")
                 lang_log.append("2. 关注核心问题：特别关注那些得分较低且您认为重要的领域（如生物/医学、地理等）。评估这些问题是否可以沟通、改善，或它们是否是您无法妥协的核心需求。")
            else:
                 lang_log.append("1. 巩固优势：识别关系中的优势领域（如沟通、共同经历等），并努力维持和增强它们。")
                 lang_log.append("2. 积极应对挑战：对于得分较低的领域，尝试与伴侣沟通并共同寻找改善的方法。")

        elif decision_code == 1:
            lang_log.append("1. 认真评估BATNA：您的最佳替代方案看起来有一定吸引力。花时间更具体地构想和探索这些替代方案的可能性。")
            lang_log.append("2. 坦诚沟通：如果决定尝试改善当前关系，请就核心不满（特别是得分低的领域）与伴侣进行坦诚沟通，看看是否有共同解决的意愿和能力。")
            lang_log.append("3. 设定观察期：可以给自己和关系设定一个观察期，看问题是否能得到改善，再做最终决定。")

        elif decision_code == 2:
            lang_log.append("1. 优先考虑替代方案：模型强烈暗示您的最佳替代方案可能远优于当前关系。建议您积极探索这些可能性。")
            lang_log.append("2. 制定退出计划：如果决定离开，提前规划可以减少过程中的不确定性和困难。寻求信任的朋友、家人或专业人士的支持。")

        if avg_outlook < -0.1:
            lang_log.append(f"{len(lang_log)-2}. 扭转悲观预期：思考是什么导致您对未来预期不佳，这些因素是否有可能改变？积极的改变或接受现实，都可能比持续的悲观更有益。")

        lang_log.append(f"\n--- 免责声明 ---")
        lang_log.append("本解读基于您输入的数据和模型的算法。它提供了一个结构化的视角，但不能替代您的个人判断和感受。请将此作为一种辅助思考工具，结合现实情况做出最适合您的决定。")
        return "\n".join(lang_log)


# --- GUI Application Class ---
class RVCUMAppGUI:
    def __init__(self, master):
        self.master = master
        master.title("恋爱关系价值评估模型 (RVCUM) - v3.1 完整版")
        master.geometry("950x780")

        self.q_struct = QUESTIONNAIRE_STRUCTURE_FULL
        self.user_responses_vars = {}

        # --- CORRECTED: Initialize Tkinter variables AFTER root is created ---
        for section_key, section_data in self.q_struct.items():
            self.user_responses_vars[section_key] = {}
            for q_key, q_data in section_data["questions"].items():
                if q_data["type"] == "scale":
                    q_data["var"] = tk.DoubleVar(master) # Pass master
                elif q_data["type"] == "text_int":
                    q_data["var"] = tk.StringVar(master) # Pass master
                else: # text, combo, radio_na
                    q_data["var"] = tk.StringVar(master) # Pass master
                self.user_responses_vars[section_key][q_key] = q_data["var"]
        # --- END CORRECTION ---


        self.main_frame = ttk.Frame(master, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        menubar = tk.Menu(master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="保存答案", command=self.save_answers)
        filemenu.add_command(label="加载答案", command=self.load_answers)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=master.quit)
        menubar.add_cascade(label="文件", menu=filemenu)
        master.config(menu=menubar)

        self.notebook = ttk.Notebook(self.main_frame)
        self.frames = {}
        self.section_keys_ordered = list(self.q_struct.keys())

        for section_key in self.section_keys_ordered:
            frame = ttk.Frame(self.notebook, padding="10")
            self.notebook.add(frame, text=self.q_struct[section_key]["title"])
            self.frames[section_key] = frame
            self._create_section_widgets(frame, section_key)

        self.notebook.pack(expand=True, fill='both')
        self.notebook.bind("<<NotebookTabChanged>>", self._update_nav_buttons)

        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.pack(fill=tk.X, pady=10, side=tk.BOTTOM)

        self.prev_button = ttk.Button(self.nav_frame, text="上一步", command=self._prev_section)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.next_button = ttk.Button(self.nav_frame, text="下一步", command=self._next_section)
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.calculate_button = ttk.Button(self.nav_frame, text="完成并评估", command=self._collect_and_calculate)
        self.calculate_button.pack(side=tk.RIGHT, padx=5)

        self._update_nav_buttons()

    def _validate_int_input(self, P):
        if P == "" or P.isdigit() or (P.startswith('-') and P[1:].isdigit()): return True # Allow negative for age? Probably not needed.
        self.master.bell()
        return False

    def _create_section_widgets(self, parent_frame, section_key):
        section_data = self.q_struct[section_key]

        canvas = tk.Canvas(parent_frame)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=(0,0,15,0))

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        # Bind mouse wheel to the canvas itself, not all
        canvas.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Shift-MouseWheel>", lambda e: canvas.xview_scroll(int(-1*(e.delta/120)), "units")) # Optional horizontal scroll

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        row_num = 0
        for q_key, q_data in section_data["questions"].items():
            q_label = ttk.Label(scrollable_frame, text=q_data["text"], wraplength=700, justify=tk.LEFT)
            q_label.grid(row=row_num, column=0, sticky="w", pady=(10,2), padx=5)

            var = q_data["var"]

            if q_data["type"] == "scale":
                low, high = q_data["range"]
                scale_frame = ttk.Frame(scrollable_frame)
                scale_frame.grid(row=row_num, column=1, columnspan=2, sticky="ew", padx=5, pady=(10,2))

                current_val_label = ttk.Label(scale_frame, text=f"{var.get():.0f}", width=3)
                current_val_label.pack(side=tk.RIGHT, padx=(5,0))

                def on_scale_change_factory(v, lbl, r):
                    def on_scale_change(event_val_str):
                        try:
                            val = float(event_val_str) # Get value from event string
                            val = round(max(r[0], min(r[1], val)))
                            v.set(val)
                            lbl.config(text=f"{val:.0f}")
                        except ValueError:
                            pass # Ignore invalid event values
                    return on_scale_change

                scale = ttk.Scale(scale_frame, from_=low, to=high, orient=tk.HORIZONTAL, variable=var, length=300,
                                  command=on_scale_change_factory(var, current_val_label, q_data["range"]))
                scale.pack(side=tk.LEFT, expand=True, fill=tk.X)

                # Initialize label text based on initial var value
                current_val_label.config(text=f"{round(var.get()):.0f}")


            elif q_data["type"] == "text":
                entry = ttk.Entry(scrollable_frame, textvariable=var, width=45)
                entry.grid(row=row_num, column=1, columnspan=2, sticky="w", padx=5, pady=(10,2))
            elif q_data["type"] == "text_int":
                vcmd = (self.master.register(self._validate_int_input), '%P')
                entry = ttk.Entry(scrollable_frame, textvariable=var, width=10, validate='key', validatecommand=vcmd)
                entry.grid(row=row_num, column=1, columnspan=2, sticky="w", padx=5, pady=(10,2))
            elif q_data["type"] == "combo":
                combo = ttk.Combobox(scrollable_frame, textvariable=var, values=q_data["options"], state="readonly", width=42)
                combo.grid(row=row_num, column=1, columnspan=2, sticky="w", padx=5, pady=(10,2))
                if q_data["options"] and not var.get(): var.set(q_data["options"][0])
            elif q_data["type"] == "radio_na":
                radio_frame = ttk.Frame(scrollable_frame)
                radio_frame.grid(row=row_num, column=1, columnspan=2, sticky="w", padx=5, pady=(10,2))
                default_set = False
                for i, option_text in enumerate(q_data["options"]):
                    rb = ttk.Radiobutton(radio_frame, text=option_text, variable=var, value=option_text)
                    rb.pack(side=tk.LEFT, padx=(0,10), anchor="w", pady=2)
                    if not var.get() and i == 0:
                        var.set(option_text)
                        default_set = True
                if q_data["options"] and not var.get() and not default_set: var.set(q_data["options"][0])
            row_num += 1

    def _update_nav_buttons(self, event=None):
        current_tab_index = self.notebook.index(self.notebook.select())
        self.prev_button.state(['!disabled'] if current_tab_index > 0 else ['disabled'])
        self.next_button.state(['!disabled'] if current_tab_index < len(self.section_keys_ordered) - 1 else ['disabled'])
        self.calculate_button.state(['!disabled'] if current_tab_index == len(self.section_keys_ordered) -1 else ['disabled'])

    def _prev_section(self):
        current_tab_index = self.notebook.index(self.notebook.select())
        if current_tab_index > 0: self.notebook.select(current_tab_index - 1)

    def _next_section(self):
        current_tab_index = self.notebook.index(self.notebook.select())
        if current_tab_index < len(self.section_keys_ordered) - 1: self.notebook.select(current_tab_index + 1)

    def _get_all_responses(self):
        responses_dict = {}
        for section_key, questions_vars in self.user_responses_vars.items():
            responses_dict[section_key] = {}
            for q_key, var in questions_vars.items():
                try:
                    val = var.get()
                    q_def = self.q_struct[section_key]["questions"][q_key]
                    if q_def["type"] == "text_int":
                        if val == "":
                             # messagebox.showerror("输入错误", f"问题 '{q_def['text']}' 需要一个整数，但为空。")
                             # self.notebook.select(self.frames[section_key])
                             # return None # Indicate error
                             responses_dict[section_key][q_key] = "0" # Default to 0 if empty for calculation
                        elif val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
                            responses_dict[section_key][q_key] = val
                        else:
                            messagebox.showerror("输入错误", f"问题 '{q_def['text']}' 需要一个整数。当前值: '{val}'")
                            self.notebook.select(self.frames[section_key])
                            return None
                    else:
                        responses_dict[section_key][q_key] = val
                except tk.TclError:
                    # Fallback for uninitialized or problematic vars - should be less likely now
                    q_def = self.q_struct[section_key]["questions"][q_key]
                    if q_def["type"] == "scale": responses_dict[section_key][q_key] = str((q_def["range"][0] + q_def["range"][1]) / 2.0)
                    elif q_def["type"] in ["combo", "radio_na"] and q_def["options"]: responses_dict[section_key][q_key] = q_def["options"][0]
                    else: responses_dict[section_key][q_key] = ""
        return responses_dict

    def _collect_and_calculate(self):
        all_responses = self._get_all_responses()
        if all_responses is None: return

        # Basic validation for weights (ensure they are numbers)
        for q_key, var in self.user_responses_vars["WEIGHTS"].items():
            try: float(var.get())
            except ValueError:
                messagebox.showerror("输入错误", f"权重 '{self.q_struct['WEIGHTS']['questions'][q_key]['text']}' 不是有效数字。")
                self.notebook.select(self.frames["WEIGHTS"])
                return

        calculator = RVCUMCalculator(all_responses, self.q_struct)
        results = calculator.calculate_rvcum()

        if "error" in results:
            messagebox.showerror("计算错误", results["error"])
            if results.get("detailed_log"):
                self._display_results_text("计算部分日志 (发生错误):\n\n" + "\n".join(results["detailed_log"]))
            return

        interpretation_text = calculator.generate_natural_language_interpretation(results)
        full_results_text = interpretation_text + "\n\n--- 详细计算过程 ---\n" + "\n".join(results.get("detailed_log", []))
        self._display_results_text(full_results_text)

    def _display_results_text(self, text_content):
        result_window = tk.Toplevel(self.master)
        result_window.title("RVCUM 评估结果与解读")
        result_window.geometry("850x650")

        text_frame = ttk.Frame(result_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        text_area = tk.Text(text_frame, wrap=tk.WORD, padx=10, pady=10, font=("Arial", 10), relief=tk.SOLID, borderwidth=1)

        v_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_area.yview)
        text_area.configure(yscrollcommand=v_scroll.set)

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        text_area.insert(tk.END, text_content)
        text_area.config(state=tk.DISABLED)

    def save_answers(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".rvcum_json", filetypes=[("RVCUM JSON data", "*.rvcum_json"), ("All files", "*.*")], title="保存答案")
        if not filepath: return
        responses_to_save = self._get_all_responses()
        if responses_to_save is None: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(responses_to_save, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("成功", "答案已成功保存！")
        except Exception as e: messagebox.showerror("错误", f"保存失败: {e}")

    def load_answers(self):
        filepath = filedialog.askopenfilename(filetypes=[("RVCUM JSON data", "*.rvcum_json"), ("All files", "*.*")], title="加载答案")
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: loaded_responses = json.load(f)
            for section_key, questions in loaded_responses.items():
                if section_key in self.user_responses_vars:
                    for q_key, value in questions.items():
                        if q_key in self.user_responses_vars[section_key]:
                            # Need to handle potential type mismatches if loading old data or bad data
                            try:
                                target_var = self.user_responses_vars[section_key][q_key]
                                if isinstance(target_var, tk.DoubleVar):
                                     target_var.set(float(value))
                                elif isinstance(target_var, tk.StringVar):
                                     target_var.set(str(value))
                                # Add other types if necessary
                            except (ValueError, tk.TclError) as e:
                                self._log(f"警告: 加载数据时设置变量失败 {section_key}-{q_key} with value '{value}': {e}")
                                # Optionally set to default or leave as is

            # Refresh current tab's scale labels by simulating tab change
            current_tab_index = self.notebook.index(self.notebook.select())
            self.notebook.select((current_tab_index + 1) % len(self.section_keys_ordered)) # Move away
            self.notebook.select(current_tab_index) # Move back

            messagebox.showinfo("成功", "答案已成功加载！")
        except Exception as e: messagebox.showerror("错误", f"加载失败: {e}")


# --- Main Application Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    available_themes = style.theme_names()
    preferred_themes = ['clam', 'alt', 'vista', 'xpnative']
    for theme in preferred_themes:
        if theme in available_themes:
            try:
                style.theme_use(theme)
                break
            except tk.TclError:
                continue
    else:
        if 'default' not in available_themes and available_themes:
             try: style.theme_use(available_themes[0])
             except: pass

    app = RVCUMAppGUI(root)
    root.mainloop()