import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import math

# --- 全局 N/A 字符串 ---
NA_STRING = "不适用/未考虑"

# --- 全问卷结构 ---
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
            "C2.3": {"text": "我感觉伴侣为关系付出了他/她公平的一份（财务、情感、实际行动上）。", "type": "scale", "range": (1, 7)},
            "C3.1": {"text": "我已为这段关系投入了大量难以割舍的时间和情感。", "type": "scale", "range": (1, 7)}, # I_0 component
            "C3.2": {"text": "我们的生活已深度交织（如共同财产、子女、共同事业），使得分离的代价高昂且复杂。", "type": "scale", "range": (1, 7)}, # I_0 component
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
            "E1.2": {"text": "我们文化背景（如民族、宗教、成长环境）的差异是丰富的源泉而非冲突的起因。", "type": "scale", "range": (1, 7)},
            "E1.3": {"text": "我们能有效地处理任何出现的文化差异。", "type": "scale", "range": (1, 7)},
            "E2.1": {"text": "我们拥有有意义的共同仪式或传统（如庆祝节日、纪念日的方式，日常习惯），这加强了我们的联系。", "type": "scale", "range": (1, 7)},
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
            "F2.1": {"text": "我仍然对我的伴侣有身体上的吸引力。", "type": "scale", "range": (1, 7)},
            "F2.2": {"text": "我对我们关系中身体亲密的程度和质量感到满意。", "type": "scale", "range": (1, 7)},
            "F2.3": {"text": "我们能就性需求和愿望进行开放有效的沟通。", "type": "scale", "range": (1, 7)},
            "F3.1": {"text": "我和伴侣在生育问题上（时机、数量、育儿理念）是否一致？", "type": "radio_na", "options": ["非常一致", "比较一致", "中立/不确定", "有些分歧", "严重分歧", NA_STRING]},
            "F3.2": {"text": "作为潜在的共同抚养人，您对伴侣的信心如何？", "type": "radio_na", "options": ["非常有信心", "比较有信心", "中立/不确定", "有些担忧", "非常担忧", NA_STRING]},
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
            "I3.2": {"text": "我们是否已公开讨论过对这段关系的长期打算（如婚姻、同居）？", "type": "radio_na", "options": ["已充分讨论且意向一致", "已讨论但存在分歧", "讨论过但尚无明确结论", "未曾认真讨论", NA_STRING]},
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
        }
    },
    "L": { # 地理学
        "title": "地理学因素",
        "questions": {
            "L1.1": {"text": "（如果同居）我对我们共享的居住空间及其管理方式的感受如何？", "type": "radio_na", "options": ["非常舒适满意", "比较舒适满意", "中立", "有些不适/不满", "非常不适/不满", NA_STRING]},
            "L1.2": {"text": "我们目前的地理位置是否能很好地满足双方的需求（职业、家庭、生活方式）？", "type": "scale", "range": (1, 7)}, # High score is good
            "L2.1": {"text": "（如果异地或频繁出差）我们之间的物理距离对关系的压力程度如何？", "type": "radio_na", "options": ["完全没有影响", "影响较小可控", "有一定影响", "影响较大构成压力", "影响非常大难以维系", NA_STRING]}, # "完全没有影响" is best (less cost)
            "L2.2": {"text": "我们如何有效地管理分离期？", "type": "radio_na", "options": ["管理得非常好", "管理得比较好", "一般", "管理得不太好", "管理得很差", NA_STRING]}, # "非常好" is best
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
            "N2.1": {"text": "我们的关系系统对新信息持开放态度，并能够调整（例如，如果旧方法行不通，尝试新方法）。", "type": "scale", "range": (1, 7)},
            "N2.2": {"text": "我们通常擅长识别何时事情不顺利并做出改变。", "type": "scale", "range": (1, 7)},
            "N3.1": {"text": "我们的关系通常能很好地抵御负面的外部影响。", "type": "scale", "range": (1, 7)},
            "N3.2": {"text": "我们擅长在有益时采纳积极的外部意见（如信任的朋友的建议，必要时的咨询）。", "type": "scale", "range": (1, 7)},
        }
    },
    "O": {
        "title": "未来预期与贴现率代理",
        "questions": {
            "O1": {"text": "展望未来，我对这段关系持乐观态度。", "type": "scale", "range": (1, 7)},
            "O2": {"text": "我预期这段关系带来的益处会随时间增加或保持较高水平。", "type": "scale", "range": (1, 7)},
            "O3": {"text": "我预期这段关系的成本或困难会随时间减少或保持可控。", "type": "scale", "range": (1, 7)},
            "O4": {"text": "做重要人生决策时，我倾向于优先考虑长期利益而非即时满足。", "type": "scale", "range": (1, 7)},
            "O5": {"text": "想到要为目前这样的关系再投入数年时间，我感觉：(1=令人望而却步, 7=令人兴奋)", "type": "scale", "range": (1, 7)},
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
            "W_I_Law": {"text": "法学/准法学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_J_Comm": {"text": "传播学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_K_Hist": {"text": "历史学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_L_Geo": {"text": "地理学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_M_Eco": {"text": "生态学因素的重要性:", "type": "scale", "range": (1, 5)},
            "W_N_InfoSys": {"text": "信息/系统论因素的重要性:", "type": "scale", "range": (1, 5)},
        }
    }
}

# --- Configuration & Constants ---
TIME_HORIZON_YEARS = 5

# --- RVCUM Calculator Class ---
class RVCUMCalculator:
    def __init__(self, responses, questionnaire_structure):
        self.responses = responses
        self.q_struct = questionnaire_structure
        self.detailed_log = []

    def _log(self, message):
        self.detailed_log.append(message)

    def _transform_score(self, score_str, q_def):
        q_text_short = q_def['text'][:30] + "..."
        if score_str is None or score_str == "":
            if q_def["type"] == "scale":
                score_str = str((q_def["range"][0] + q_def["range"][1]) / 2) # Convert to string for consistency
                self._log(f"  处理 '{q_text_short}': 空值，默认为中性值 {float(score_str):.1f}")
            else:
                self._log(f"  处理 '{q_text_short}': 空值，视为N/A。")
                return 0, True
        
        # Ensure score_str is a string before further processing, especially for scale values from .get()
        score_str = str(score_str)

        if q_def["type"] == "radio_na":
            if score_str == NA_STRING:
                self._log(f"  处理 '{q_text_short}': 选择 {NA_STRING}，视为N/A。")
                return 0, True
            try:
                options_no_na = [opt for opt in q_def["options"] if opt != NA_STRING]
                num_options = len(options_no_na)
                if num_options == 0: return 0, True 
                idx = options_no_na.index(score_str) 
                if num_options == 1: transformed = 0 
                else: transformed = 1 - (2 * idx / (num_options - 1))
                self._log(f"  处理 '{q_text_short}': 选项 '{score_str}' (idx {idx}/{num_options-1}), 转换后: {transformed:.2f}")
                return transformed, False
            except ValueError:
                self._log(f"  警告: '{q_text_short}': 无法解析 radio_na 选项 '{score_str}'，视为N/A。")
                return 0, True
        if q_def["type"] == "scale":
            try:
                score = float(score_str)
                low, high = q_def["range"]
                neutral = (low + high) / 2.0
                max_deviation = high - neutral
                if max_deviation == 0: return 0, False
                transformed = (score - neutral) / max_deviation
                self._log(f"  处理 '{q_text_short}': 原始值 {score:.1f}, 转换后: {transformed:.2f}")
                return transformed, False
            except ValueError:
                self._log(f"  警告: '{q_text_short}': 无法解析 scale 值 '{score_str}'，视为N/A。")
                return 0, True
        self._log(f"  处理 '{q_text_short}': 类型 {q_def['type']}，值 '{score_str}'，视为N/A。")
        return 0, True

    def calculate_rvcum(self):
        self.detailed_log = [] 
        self._log("--- 开始RVCUM计算 ---")
        try:
            batna_q_def = self.q_struct["A"]["questions"]["A5"]
            batna_score_raw = float(self.responses["A"]["A5"])
            batna_transformed_score = self._transform_score(str(batna_score_raw), batna_q_def)[0]
            self._log(f"原始BATNA评分 (A5): {batna_score_raw}, 转换后 (归一化-1到1): {batna_transformed_score:.2f}")

            o4_q_def = self.q_struct["O"]["questions"]["O4"]
            o4_val_raw = float(self.responses["O"]["O4"])
            r_min, r_max = 0.03, 0.15
            discount_rate = r_max - (((o4_val_raw - o4_q_def["range"][0]) / (o4_q_def["range"][1] - o4_q_def["range"][0])) * (r_max - r_min))
            discount_rate = max(0.01, min(discount_rate, 0.20))
            self._log(f"贴现率代理 (O4): {o4_val_raw}, 计算贴现率 r: {discount_rate:.4f}")

            o1_optimism = self._transform_score(str(self.responses["O"]["O1"]), self.q_struct["O"]["questions"]["O1"])[0]
            o2_benefits_growth = self._transform_score(str(self.responses["O"]["O2"]), self.q_struct["O"]["questions"]["O2"])[0]
            o3_costs_reduction = self._transform_score(str(self.responses["O"]["O3"]), self.q_struct["O"]["questions"]["O3"])[0]
            self._log(f"未来预期: 乐观度={o1_optimism:.2f}, 益处增长={o2_benefits_growth:.2f}, 成本降低={o3_costs_reduction:.2f} (均为-1到1范围)")

            utility_annual_growth_factor = 1.0 + (o1_optimism * 0.025) + (o2_benefits_growth * 0.025)
            cost_annual_change_factor = 1.0 - (o1_optimism * 0.015) - (o3_costs_reduction * 0.025) 
            utility_annual_growth_factor = max(0.90, min(utility_annual_growth_factor, 1.10))
            cost_annual_change_factor = max(0.90, min(cost_annual_change_factor, 1.10))
            self._log(f"效用年增长因子: {utility_annual_growth_factor:.3f}, 成本年变化因子: {cost_annual_change_factor:.3f}")
        except Exception as e:
            self._log(f"错误：提取关键参数失败 - {e}")
            import traceback; self._log(traceback.format_exc())
            return {"error": f"提取关键参数失败: {e}"}

        i0_value_normalized_sum = 0 
        num_i0_components = 0
        i0_question_specs = [{"q_id": "C3.1", "section_id": "C"}, {"q_id": "C3.2", "section_id": "C"}]
        self._log("\n--- 计算初始投资/转换成本 (I_0) ---")
        for spec in i0_question_specs:
            q_key, section_id = spec["q_id"], spec["section_id"]
            if section_id not in self.responses or q_key not in self.responses[section_id]:
                self._log(f"  警告: I_0 计算中，问题 {section_id}.{q_key} 在回应中未找到，跳过。")
                continue
            q_def = self.q_struct[section_id]["questions"][q_key]
            raw_score_str = str(self.responses[section_id][q_key])
            transformed_score, is_na = self._transform_score(raw_score_str, q_def)
            if not is_na:
                i0_value_normalized_sum += (transformed_score + 1) / 2 
                num_i0_components +=1
        avg_i0_normalized = i0_value_normalized_sum / num_i0_components if num_i0_components > 0 else 0
        scaled_i0_value = avg_i0_normalized * 15 
        self._log(f"  计算的初始投资/转换成本 (I_0) 价值 (加到关系NPV上): {scaled_i0_value:.2f} (基于{num_i0_components}个问题)")

        current_period_total_utility_weighted = 0
        current_period_total_cost_weighted = 0
        weights = {}
        total_weight_sum = 0
        self._log("\n--- 计算学科权重 ---")
        for w_key, w_data_def in self.q_struct["WEIGHTS"]["questions"].items():
            try:
                weight_val_raw = float(self.responses["WEIGHTS"][w_key])
                weights[w_key] = weight_val_raw
                total_weight_sum += weight_val_raw
                self._log(f"  权重 {w_key} ({w_data_def['text']}): {weight_val_raw:.1f}")
            except ValueError: self._log(f"  警告: 权重 {w_key} 无效，设为0。"); weights[w_key] = 0
        if total_weight_sum > 0:
            for w_key in weights: weights[w_key] /= total_weight_sum
        else: 
             num_disciplines = len(weights)
             default_weight = 1.0 / num_disciplines if num_disciplines > 0 else 0
             for w_key in weights: weights[w_key] = default_weight
             self._log(f"  所有权重为0，使用平均权重: {default_weight:.3f}")
        self._log(f"  归一化后的学科权重: { {k: f'{v:.3f}' for k,v in weights.items()} }")

        discipline_scores = {}
        self._log("\n--- 计算各学科当前周期贡献 ---")
        for section_id in "BCDEFGHIJKLMN": 
            if section_id not in self.q_struct: continue
            section_data_def = self.q_struct[section_id]
            self._log(f"\n  处理学科: {section_data_def['title']} ({section_id})")
            section_utility_sum_transformed, section_cost_sum_transformed = 0, 0
            num_valid_utility_q, num_valid_cost_q = 0, 0
            for q_key, q_def in section_data_def["questions"].items():
                raw_response_str = str(self.responses[section_id].get(q_key, ""))
                transformed_score, is_na = self._transform_score(raw_response_str, q_def)
                if is_na: continue
                if q_def.get("is_cost", False):
                    section_cost_sum_transformed += transformed_score 
                    num_valid_cost_q += 1
                else:
                    section_utility_sum_transformed += transformed_score
                    num_valid_utility_q += 1
            avg_section_utility_transformed = section_utility_sum_transformed / num_valid_utility_q if num_valid_utility_q > 0 else 0
            avg_section_cost_transformed = section_cost_sum_transformed / num_valid_cost_q if num_valid_cost_q > 0 else 0
            net_section_score_transformed = avg_section_utility_transformed - avg_section_cost_transformed
            discipline_scores[section_id] = net_section_score_transformed
            self._log(f"    学科 {section_id} 总结: 平均效用分={avg_section_utility_transformed:.2f} (来自{num_valid_utility_q}题), 平均成本分={avg_section_cost_transformed:.2f} (来自{num_valid_cost_q}题)")
            self._log(f"    学科 {section_id} 净得分 (效用-成本, 范围约-2到+2): {net_section_score_transformed:.2f}")
            weight_key_map = {'B': 'W_B_Psych', 'C': 'W_C_Econ', 'D': 'W_D_Soc', 'E': 'W_E_Anth', 'F': 'W_F_BioMed', 'G': 'W_G_PolSci', 'H': 'W_H_Phil', 'I': 'W_I_Law', 'J': 'W_J_Comm', 'K': 'W_K_Hist', 'L': 'W_L_Geo', 'M': 'W_M_Eco', 'N': 'W_N_InfoSys'}
            actual_weight_key = weight_key_map.get(section_id)
            section_weight = weights.get(actual_weight_key, 0) if actual_weight_key else 0
            SCALING_FACTOR_FOR_UTILITY_UNITS = 5 
            scaled_net_contribution = net_section_score_transformed * SCALING_FACTOR_FOR_UTILITY_UNITS
            if scaled_net_contribution > 0: current_period_total_utility_weighted += scaled_net_contribution * section_weight
            else: current_period_total_cost_weighted += (-scaled_net_contribution) * section_weight
            self._log(f"    学科 {section_id} 加权贡献 (scaled): 效用 += {(scaled_net_contribution * section_weight) if scaled_net_contribution > 0 else 0:.2f}, 成本 += {(-scaled_net_contribution * section_weight) if scaled_net_contribution < 0 else 0:.2f} (权重 {section_weight:.3f})")

        self._log("\n--- 计算互动项 ---")
        interaction_utility_bonus, interaction_cost_reduction = 0, 0
        comm_score, conflict_res_score = discipline_scores.get('J', 0), discipline_scores.get('G', 0)
        if comm_score > 0.2 and conflict_res_score > 0.2:
            j_weight, g_weight = weights.get(weight_key_map['J'],0), weights.get(weight_key_map['G'],0)
            avg_interaction_weight = (j_weight + g_weight) / 2
            bonus = comm_score * conflict_res_score * SCALING_FACTOR_FOR_UTILITY_UNITS * 0.25 * avg_interaction_weight
            interaction_utility_bonus += bonus
            self._log(f"  互动项 (J & G): 沟通({comm_score:.2f}) * 冲突解决({conflict_res_score:.2f}) -> 额外效用: +{bonus:.2f}")
        cultural_score = discipline_scores.get('E', 0)
        if comm_score > 0.2 and cultural_score < -0.2:
            e_weight = weights.get(weight_key_map['E'],0)
            original_cost_from_E = (-cultural_score) * e_weight * SCALING_FACTOR_FOR_UTILITY_UNITS
            mitigation_factor = comm_score * 0.3 
            reduction = original_cost_from_E * mitigation_factor
            interaction_cost_reduction += reduction
            self._log(f"  互动项 (J & E): 沟通({comm_score:.2f}) 缓解 文化冲突({cultural_score:.2f}) -> 成本降低: -{reduction:.2f}")
        current_period_total_utility_weighted += interaction_utility_bonus
        current_period_total_cost_weighted -= interaction_cost_reduction
        current_period_total_cost_weighted = max(0, current_period_total_cost_weighted)
        self._log(f"\n当前周期总计 (已加权和互动调整): 原始效用流={current_period_total_utility_weighted:.2f}, 原始成本流={current_period_total_cost_weighted:.2f}")

        npv_relationship = 0
        projected_period_utility, projected_period_cost = current_period_total_utility_weighted, current_period_total_cost_weighted
        self._log("\n--- NPV 计算 (逐年) ---")
        self._log("年 | 预期效用 | 预期成本 | 净效用 | 折现因子 | 折现净效用")
        for t_year in range(TIME_HORIZON_YEARS):
            current_year_utility, current_year_cost = projected_period_utility, projected_period_cost
            if t_year > 0:
                projected_period_utility *= utility_annual_growth_factor
                projected_period_cost *= cost_annual_change_factor
                projected_period_cost = max(0, projected_period_cost)
            net_period_utility = current_year_utility - current_year_cost
            discount_factor = 1 / ((1 + discount_rate) ** t_year)
            discounted_net_period_utility = net_period_utility * discount_factor
            npv_relationship += discounted_net_period_utility
            self._log(f"{t_year+1:2d} | {current_year_utility:9.2f} | {current_year_cost:9.2f} | {net_period_utility:8.2f} | {discount_factor:9.4f} | {discounted_net_period_utility:11.2f}")
        self._log(f"--- NPV (关系本身，未加I_0): {npv_relationship:.2f} ---")
        npv_relationship_final = npv_relationship + scaled_i0_value
        self._log(f"NPV (关系本身，已加I_0={scaled_i0_value:.2f}): {npv_relationship_final:.2f}")

        base_for_batna_npv = npv_relationship 
        batna_difference_percentage = 0.25 
        min_abs_batna_difference_value = (SCALING_FACTOR_FOR_UTILITY_UNITS * TIME_HORIZON_YEARS * 0.1)
        adjustment_value = 0
        if abs(base_for_batna_npv) > 1e-6 : adjustment_value = abs(base_for_batna_npv) * batna_difference_percentage * batna_transformed_score
        else: adjustment_value = min_abs_batna_difference_value * batna_transformed_score
        if batna_transformed_score > 0 and adjustment_value < min_abs_batna_difference_value * batna_transformed_score : adjustment_value = min_abs_batna_difference_value * batna_transformed_score
        elif batna_transformed_score < 0 and adjustment_value > min_abs_batna_difference_value * batna_transformed_score : adjustment_value = min_abs_batna_difference_value * batna_transformed_score
        npv_batna_r = base_for_batna_npv + adjustment_value
        self._log(f"NPV (最佳替代方案 BATNA-R): {npv_batna_r:.2f} (基于当前关系NPV(无I_0)={base_for_batna_npv:.2f} 和 BATNA评分调整)")

        decision = "值得继续" if npv_relationship_final > npv_batna_r else "可能不值得继续，请仔细考虑"
        self._log(f"\n最终决策建议: {decision}")
        return {"npv_relationship": npv_relationship_final, "npv_batna_r": npv_batna_r, "decision": decision, "discount_rate": discount_rate, "i0_value": scaled_i0_value, "current_period_utility_calc": current_period_total_utility_weighted, "current_period_cost_calc": current_period_total_cost_weighted, "detailed_log": self.detailed_log}

# --- GUI Application Class ---
class RVCUMAppGUI:
    def __init__(self, master, q_struct_with_vars): # Pass structure with initialized vars
        self.master = master
        master.title("恋爱关系价值评估模型 (RVCUM) - 进阶版 v3")
        master.geometry("900x750")

        self.q_struct = q_struct_with_vars # Use the passed structure
        self.user_responses_vars = {} 
        for section_key, section_data in self.q_struct.items():
            self.user_responses_vars[section_key] = {}
            for q_key, q_data in section_data["questions"].items():
                self.user_responses_vars[section_key][q_key] = q_data["var"]

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

    def _create_section_widgets(self, parent_frame, section_key):
        section_data = self.q_struct[section_key]
        canvas = tk.Canvas(parent_frame)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=(0,0,10,0)) 
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        row_num = 0
        for q_key, q_data in section_data["questions"].items():
            q_label = ttk.Label(scrollable_frame, text=q_data["text"], wraplength=650, justify=tk.LEFT)
            q_label.grid(row=row_num, column=0, sticky="w", pady=(8,2), padx=5)
            var = q_data["var"] 
            if q_data["type"] == "scale":
                low, high = q_data["range"]
                value_label_for_scale = ttk.Label(scrollable_frame, text=f"{var.get():.0f}")
                def make_scale_callback(v, lbl, r):
                    def callback(event_or_value):
                        val_from_var = v.get() 
                        val = round(max(r[0], min(r[1], float(val_from_var))))
                        v.set(val) 
                        lbl.config(text=f"{val:.0f}")
                    return callback
                scale_callback = make_scale_callback(var, value_label_for_scale, q_data["range"])
                scale = ttk.Scale(scrollable_frame, from_=low, to=high, orient=tk.HORIZONTAL, variable=var, length=250, command=scale_callback)
                scale.grid(row=row_num, column=1, sticky="ew", padx=5, pady=(8,2))
                default_val = (low + high) // 2
                # Check if var is at its default Tkinter DoubleVar value (0.0) and q_data has no prior .get() value
                # This logic might need refinement if 0.0 is a valid initial value from loaded data.
                # A simple check: if the string representation of var.get() is "0.0" and it's a scale
                if isinstance(var, tk.DoubleVar) and var.get() == 0.0 and not str(default_val) == "0.0":
                     var.set(default_val)

                value_label_for_scale.config(text=f"{var.get():.0f}")
                value_label_for_scale.grid(row=row_num, column=2, padx=5, pady=(8,2))
            elif q_data["type"] == "text":
                entry = ttk.Entry(scrollable_frame, textvariable=var, width=40)
                entry.grid(row=row_num, column=1, columnspan=2, sticky="w", padx=5, pady=(8,2))
            elif q_data["type"] == "combo":
                combo = ttk.Combobox(scrollable_frame, textvariable=var, values=q_data["options"], state="readonly", width=37)
                combo.grid(row=row_num, column=1, columnspan=2, sticky="w", padx=5, pady=(8,2))
                if q_data["options"] and not var.get(): var.set(q_data["options"][0])
            elif q_data["type"] == "radio_na":
                radio_frame = ttk.Frame(scrollable_frame)
                radio_frame.grid(row=row_num, column=1, columnspan=2, sticky="w", padx=5, pady=(8,2))
                for i, option_text in enumerate(q_data["options"]):
                    rb = ttk.Radiobutton(radio_frame, text=option_text, variable=var, value=option_text)
                    rb.pack(side=tk.LEFT, padx=3, anchor="w")
                if q_data["options"] and not var.get(): var.set(q_data["options"][0])
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
        for section_key, questions_vars_dict in self.user_responses_vars.items():
            responses_dict[section_key] = {}
            for q_key, var in questions_vars_dict.items():
                try:
                    val = var.get()
                    q_def = self.q_struct[section_key]["questions"][q_key]
                    if q_def["type"] == "scale": val = float(val) 
                    responses_dict[section_key][q_key] = val
                except tk.TclError:
                    q_def = self.q_struct[section_key]["questions"][q_key]
                    if q_def["type"] == "scale": responses_dict[section_key][q_key] = float((q_def["range"][0] + q_def["range"][1]) / 2)
                    elif q_def["type"] in ["combo", "radio_na"] and q_def.get("options"): responses_dict[section_key][q_key] = q_def["options"][0]
                    else: responses_dict[section_key][q_key] = ""
        return responses_dict

    def _collect_and_calculate(self):
        all_responses = self._get_all_responses()
        for q_key, var in self.user_responses_vars["WEIGHTS"].items():
            try: float(var.get())
            except ValueError:
                messagebox.showerror("输入错误", f"权重 '{self.q_struct['WEIGHTS']['questions'][q_key]['text']}' 不是有效数字。请返回修改。")
                for i, key in enumerate(self.section_keys_ordered):
                    if key == "WEIGHTS": self.notebook.select(i); break
                return
        calculator = RVCUMCalculator(all_responses, self.q_struct)
        results = calculator.calculate_rvcum()
        if "error" in results: messagebox.showerror("计算错误", results["error"]); return
        result_window = tk.Toplevel(self.master)
        result_window.title("RVCUM 评估结果")
        result_window.geometry("750x600")
        text_area_frame = ttk.Frame(result_window)
        text_area_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_area = tk.Text(text_area_frame, wrap=tk.WORD, padx=10, pady=10, font=("Arial", 10))
        v_scroll = ttk.Scrollbar(text_area_frame, orient=tk.VERTICAL, command=text_area.yview)
        text_area.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        summary = f"--- 关系评估概要 ---\n\n"
        summary += f"当前关系估算NPV: {results['npv_relationship']:.2f}\n"
        summary += f"  (其中转换成本效益 I_0: {results['i0_value']:.2f})\n"
        summary += f"最佳替代方案(BATNA-R)估算NPV: {results['npv_batna_r']:.2f}\n"
        summary += f"使用的年贴现率: {results['discount_rate']*100:.1f}%\n"
        summary += f"当前周期估算总效用流 (加权和互动后): {results['current_period_utility_calc']:.2f}\n"
        summary += f"当前周期估算总成本流 (加权和互动后): {results['current_period_cost_calc']:.2f}\n\n"
        summary += f"结论: {results['decision']}\n\n"
        summary += "重要提示：本模型基于您的主观评估和一系列经济学假设，结果仅供参考，请结合您的实际感受和更多现实因素做出最终决定。\n\n"
        summary += "--- 详细计算日志 ---\n"
        text_area.insert(tk.END, summary)
        for log_entry in results.get("detailed_log", []): text_area.insert(tk.END, log_entry + "\n")
        text_area.config(state=tk.DISABLED)

    def save_answers(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")], title="保存答案")
        if not filepath: return
        responses_to_save = self._get_all_responses()
        try:
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(responses_to_save, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("成功", "答案已成功保存！")
        except Exception as e: messagebox.showerror("错误", f"保存失败: {e}")

    def load_answers(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")], title="加载答案")
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: loaded_responses = json.load(f)
            for section_key, questions in loaded_responses.items():
                if section_key in self.user_responses_vars:
                    for q_key, value in questions.items():
                        if q_key in self.user_responses_vars[section_key]:
                            q_def = self.q_struct[section_key]["questions"][q_key]
                            if q_def["type"] == "scale": self.user_responses_vars[section_key][q_key].set(float(value))
                            else: self.user_responses_vars[section_key][q_key].set(str(value))
            current_tab_idx = self.notebook.index(self.notebook.select())
            for i, key in enumerate(self.section_keys_ordered):
                for widget in self.frames[key].winfo_children(): widget.destroy()
                self._create_section_widgets(self.frames[key], key)
            self.notebook.select(current_tab_idx) 
            messagebox.showinfo("成功", "答案已成功加载！")
        except Exception as e:
            messagebox.showerror("错误", f"加载失败: {e}")
            import traceback; print(traceback.format_exc())

# --- Main Application Execution ---
if __name__ == "__main__":
    root = tk.Tk() # Create the root window FIRST

    # Initialize Tkinter variables for the full structure AFTER root is created
    for section_key_init, section_data_init in QUESTIONNAIRE_STRUCTURE_FULL.items():
        for q_key_init, q_data_init in section_data_init["questions"].items():
            if "var" not in q_data_init: # If 'var' was not pre-defined (it should be now)
                if q_data_init["type"] == "scale":
                    q_data_init["var"] = tk.DoubleVar(master=root) # Associate with root
                elif q_data_init["type"] == "radio_na":
                    q_data_init["var"] = tk.StringVar(master=root)
                else: # text, combo
                    q_data_init["var"] = tk.StringVar(master=root)
            # If 'var' was defined but not as a Tk variable (e.g. if you had None placeholders)
            elif not isinstance(q_data_init["var"], (tk.StringVar, tk.DoubleVar, tk.IntVar, tk.BooleanVar)):
                if q_data_init["type"] == "scale":
                    q_data_init["var"] = tk.DoubleVar(master=root)
                else:
                    q_data_init["var"] = tk.StringVar(master=root)
            # If 'var' was already a Tk variable, it's fine, but ensure it's associated with this root if it matters
            # For this structure, it's safer to re-create them here or ensure they are created with master=root.
            # The simplest is to always create them here.
            
            # Re-creating them here to be certain they are tied to the root window.
            if q_data_init["type"] == "scale":
                q_data_init["var"] = tk.DoubleVar(master=root)
            else: # Covers text, combo, radio_na
                q_data_init["var"] = tk.StringVar(master=root)


    style = ttk.Style(root)
    available_themes = style.theme_names() 
    try:
        if 'clam' in available_themes: style.theme_use('clam')
        elif 'vista' in available_themes: style.theme_use('vista') 
        elif 'aqua' in available_themes: style.theme_use('aqua') 
    except tk.TclError:
        print("TTK theme not available or applicable, using default.")

    app = RVCUMAppGUI(root, QUESTIONNAIRE_STRUCTURE_FULL) # Pass the modified structure
    root.mainloop()