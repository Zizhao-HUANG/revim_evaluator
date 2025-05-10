import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- ReVIM 模型计算逻辑 ---
class ReVIMCalculator:
    def __init__(self, data_vars, sensitivity_vars):
        self.data = data_vars
        self.sens = sensitivity_vars

    def get_val(self, key, default_val=0, is_future_expect=False, is_duration=False, is_single_satisfaction=False, is_recovery_time=False):
        try:
            var = self.data.get(key)
            if var:
                val_str = var.get()
                if isinstance(val_str, (int, float)): # If already numeric (e.g. from IntVar for NA)
                    return val_str
                if isinstance(val_str, str):
                    if val_str.isdigit(): return int(val_str)
                    if val_str == "不适用": return "N/A"
                    if val_str == "": return default_val

                    if is_future_expect:
                        mapping = {"显著改善": 0.03, "略有改善": 0.015, "保持不变": 0, "略有恶化": -0.015, "显著恶化": -0.03, "不确定": -0.005}
                        return mapping.get(val_str, 0)
                    if is_duration:
                        mapping = {"几个月": 0.5, "1-2年": 1.5, "3-5年": 4, "5-10年": 7.5, "10年以上": 15, "终身": 25, "非常不确定": 3}
                        return mapping.get(val_str, 3)
                    if is_single_satisfaction:
                        mapping = {"显著更高": 3, "略高": 1.5, "差不多": 0, "略低": -1.5, "显著更低": -3}
                        return mapping.get(val_str, 0)
                    if is_recovery_time:
                        mapping = {"很快（1-3个月内）": 0.25, "一般（3-6个月）": 0.5, "较长（6个月-1年）": 1, "很长（1年以上）": 1.5, "不确定": 0.75}
                        return mapping.get(val_str, 0.75)
                    return val_str 
                return val_str 
            return default_val
        except Exception:
            return default_val

    def get_sens_val(self, key, default_val=1.0):
        try:
            var = self.sens.get(key)
            return var.get() if var else default_val
        except:
            return default_val

    def calculate_category_value_at_t(self, base_score_key_prefix, num_q, future_expect_key, weight_key, t, is_cost=False):
        base_category_score = 0
        actual_q_count = 0
        
        category_code_from_prefix = base_score_key_prefix.split('_')[-1].upper()

        for i in range(1, num_q + 1):
            q_num_for_key = f"{category_code_from_prefix}.{i}"
            # Corrected key formation to match add_likert_scale
            q_key = f"{base_score_key_prefix}_{q_num_for_key.replace('.', '_')}"
            
            # NA handling is done by adjusting num_q before calling this function for U_bio.
            # C_geo is handled separately.
            # For other categories, assume no NA options within the loop here.

            score = self.get_val(q_key, default_val=4)
            if score == "N/A": # Should ideally not happen if num_q is adjusted for NA
                continue
            base_category_score += score
            actual_q_count += 1

        if actual_q_count == 0: return 0
        
        avg_base_score = base_category_score / actual_q_count
        normalized_base_score = avg_base_score - 4

        growth_rate = self.get_val(future_expect_key, is_future_expect=True, default_val=0)
        optimism_adj = self.get_sens_val("future_projection_optimism_adj", 1.0)
        effective_growth_rate = growth_rate * optimism_adj
        current_period_score = normalized_base_score * ((1 + effective_growth_rate) ** t)

        weight_val = self.get_val(weight_key, default_val=4)
        weight = weight_val / 7.0 if isinstance(weight_val, (int, float)) else 4.0/7.0


        realization_prob_adj = self.get_sens_val("realization_prob_adj", 1.0)
        final_value = current_period_score * weight * realization_prob_adj
        return final_value

    def calculate_nrupv_components_over_time(self):
        T_realistic = self.get_val("Q_exp_duration_realistic", is_duration=True, default_val=5)
        T = int(math.ceil(T_realistic)) 

        self.time_periods = list(range(T))
        self.U_t_series = []
        self.C_t_series = []
        self.Net_U_t_series = []
        self.r_t_series = []
        self.discounted_Net_U_t_series = []
        
        r_base_adj = self.get_sens_val("base_discount_rate_adj", 1.0)
        r_base = 0.03 * r_base_adj 
        risk_perception_adj = self.get_sens_val("overall_risk_perception_adj", 1.0)
        r_risk_initial_val = self.get_val("Q_risk_breakup_A_1", 4) # Ensure key matches add_likert_scale
        r_risk_initial = (r_risk_initial_val - 1) * 0.005 * risk_perception_adj
        
        r_certainty_future_val = self.get_val("Q_certainty_future_A_3", 4)
        r_uncertainty_initial = (7 - r_certainty_future_val) * 0.005 * risk_perception_adj

        learning_adapt_solve_val = self.get_val("Q_adapt_solve_B_3", 4)
        learning_adapt_stress_val = self.get_val("Q_adapt_stress_B_4", 4)
        learning_adapt_learn_hist_val = self.get_val("Q_adapt_learn_hist_B_5", 4)
        learning_adapt_avg = (learning_adapt_solve_val + learning_adapt_stress_val + learning_adapt_learn_hist_val) / 3.0
        r_learning_initial_effect = (learning_adapt_avg - 4) * 0.005 

        nrupv = 0
        cumulative_nrupv = 0
        self.cumulative_nrupv_series = []

        self.initial_utility_breakdown = {}
        self.initial_cost_breakdown = {}

        utility_details = [
            ("U_psych", "心理", 10), ("U_econ", "经济", 5), ("U_socio", "社交", 5),
            ("U_anthro", "文化人类", 5), ("U_bio", "生理医学", 5), ("U_poli", "权力治理", 4),
            ("U_philo", "哲学精神", 3), ("U_law", "法律承诺", 2), ("U_comm", "沟通传播", 4),
            ("U_geo", "地理空间", 3), ("U_eco_sys", "生态系统", 3)
        ]
        cost_details = [
            ("C_psych", "心理", 5), ("C_econ", "经济", 3), ("C_socio", "社交", 3),
            ("C_anthro", "文化人类", 2), ("C_bio", "生理医学", 3), ("C_poli", "权力治理", 3),
            ("C_philo", "哲学精神", 2), ("C_law", "法律承诺", 2), ("C_comm", "沟通传播", 2),
            ("C_eco_sys", "生态系统", 3)
            # C_geo handled separately
        ]

        for t in range(T):
            current_total_utility = 0
            for cat_key, label, num_q_default in utility_details:
                num_q_actual = num_q_default
                if cat_key == "U_bio" and self.get_val("U_bio_5_na") == 1: # Specific NA key for U_bio_5
                    num_q_actual = 4
                elif cat_key == "U_law" and self.get_val("U_law_1_na") == 1: # Specific NA key for U_law_1
                    num_q_actual = 1 # Only U_law_LAW.2 remains if U_law_LAW.1 is NA
                                      # This means the loop for U_law should go from i=2 to 2 if U_law_1 is NA
                                      # Or, more simply, if U_law_1 is NA, num_q_actual becomes 1,
                                      # and the loop in calculate_category_value_at_t will try to get U_law_LAW.1.
                                      # This needs careful handling.
                                      # For U_law, if U_law_1_na is true, we only score U_law_LAW.2
                                      # It's better to calculate U_law separately if it has complex NA.
                    if num_q_actual == 1 and num_q_default == 2: # Only U_law_LAW.2 is scored
                        # This requires calculate_category_value_at_t to handle a start_index or specific question list
                        # For now, let's assume if num_q_actual is 1, it scores the first question of that category.
                        # This is problematic for U_law if U_law_LAW.1 is NA.
                        # Let's calculate U_law separately for clarity.
                        if cat_key == "U_law": continue # Skip in loop, handle below

                val_t = self.calculate_category_value_at_t(cat_key, num_q_actual, f"{cat_key}_future", f"W_{cat_key}", t)
                current_total_utility += val_t
                if t == 0: self.initial_utility_breakdown[label] = val_t
            
            # Special handling for U_law due to NA on its first question
            u_law_t = 0
            if self.get_val("U_law_1_na") == 1: # U_law_LAW.1 is NA, only score U_law_LAW.2
                # Calculate score for U_law_LAW.2 directly
                score_law2 = self.get_val("U_law_LAW.2", default_val=4)
                if score_law2 != "N/A":
                    norm_score = score_law2 - 4
                    growth = self.get_val("U_law_future", is_future_expect=True, default_val=0)
                    opt_adj = self.get_sens_val("future_projection_optimism_adj", 1.0)
                    eff_growth = growth * opt_adj
                    curr_score = norm_score * ((1 + eff_growth) ** t)
                    weight_val = self.get_val("W_U_law", default_val=4)
                    weight = weight_val / 7.0 if isinstance(weight_val, (int,float)) else 4.0/7.0
                    prob_adj = self.get_sens_val("realization_prob_adj", 1.0)
                    u_law_t = curr_score * weight * prob_adj
            else: # Both U_law_LAW.1 and U_law_LAW.2 are scored
                u_law_t = self.calculate_category_value_at_t("U_law", 2, "U_law_future", "W_U_law", t)
            current_total_utility += u_law_t
            if t == 0: self.initial_utility_breakdown["法律承诺"] = u_law_t


            current_total_cost = 0
            for cat_key, label, num_q in cost_details:
                val_t = self.calculate_category_value_at_t(cat_key, num_q, f"{cat_key}_future", f"W_{cat_key}", t)
                current_total_cost += val_t
                if t == 0: self.initial_cost_breakdown[label] = val_t

            # Corrected c_geo_t calculation (direct)
            c_geo_t = 0
            geo_scores = []
            if self.get_val("C_geo_1_na") != 1:
                score1 = self.get_val("C_geo_GEO.1", default_val=4)
                if score1 != "N/A": geo_scores.append(score1)
            score2 = self.get_val("C_geo_GEO.2", default_val=4)
            if score2 != "N/A": geo_scores.append(score2)

            if geo_scores:
                avg_base_score = sum(geo_scores) / len(geo_scores)
                normalized_base_score = avg_base_score - 4
                growth_rate = self.get_val("C_geo_future", is_future_expect=True, default_val=0)
                optimism_adj = self.get_sens_val("future_projection_optimism_adj", 1.0)
                effective_growth_rate = growth_rate * optimism_adj
                current_period_score = normalized_base_score * ((1 + effective_growth_rate) ** t)
                weight_val = self.get_val("W_C_geo", default_val=4)
                weight = weight_val / 7.0 if isinstance(weight_val, (int,float)) else 4.0/7.0
                realization_prob_adj = self.get_sens_val("realization_prob_adj", 1.0)
                c_geo_t = current_period_score * weight * realization_prob_adj
            
            current_total_cost += c_geo_t
            if t == 0: self.initial_cost_breakdown["地理空间"] = c_geo_t
            
            # Synergy/Conflict Factors
            u_psych_val_t0 = self.initial_utility_breakdown.get("心理", 0) # Use t=0 value for simplicity of synergy factor
            u_comm_val_t0 = self.initial_utility_breakdown.get("沟通传播", 0)
            
            # Normalize initial scores for synergy factor (0-1 range approx)
            # This is a rough proxy. A better way would be to use the non-weighted, non-projected base scores.
            synergy_comm_psych_factor = 1.0
            if u_comm_val_t0 > 0 : # Assuming positive communication is synergistic
                 synergy_comm_psych_factor = 1 + 0.1 * (u_comm_val_t0 / ( (self.get_val("W_U_comm",4)/7.0) * 3) ) # Max 10% boost if comm is at max (3)
            
            # Find u_psych_t from the series if needed, or re-calculate its component for modification
            # For simplicity, apply synergy to the already calculated total utility's psychological component proxy
            # This is an approximation. A more precise way would be to modify u_psych_t before summing.
            # Let's assume u_psych_val_t0 is a proxy for the psychological component's magnitude.
            current_total_utility += u_psych_val_t0 * (synergy_comm_psych_factor - 1.0) # Add the synergistic part

            c_philo_val_t0 = self.initial_cost_breakdown.get("哲学精神", 0)
            c_psych_val_t0 = self.initial_cost_breakdown.get("心理", 0)
            conflict_philo_psych_factor = 1.0
            if c_philo_val_t0 > 0: # Assuming philosophical cost amplifies psychological cost
                conflict_philo_psych_factor = 1 + 0.1 * (c_philo_val_t0 / ( (self.get_val("W_C_philo",4)/7.0) * 3) )
            current_total_cost += c_psych_val_t0 * (conflict_philo_psych_factor - 1.0)


            self.U_t_series.append(current_total_utility)
            self.C_t_series.append(current_total_cost)
            net_utility_this_period = current_total_utility - current_total_cost
            self.Net_U_t_series.append(net_utility_this_period)

            conflict_pattern_exists_val = self.get_val("Q_conflict_patterns_exist_A_2", "0")
            stability_factor = (1 - 0.05 * t) if conflict_pattern_exists_val == "0" else (1 + 0.02 * t)
            r_risk_t = r_risk_initial * max(0.5, stability_factor) 
            r_uncertainty_t = r_uncertainty_initial * max(0.5, (1 - 0.03 * t)) 
            r_learning_t_effect = r_learning_initial_effect * max(0.7, (1 - 0.02 * t)) 
            r_t_period = r_base + r_risk_t + r_uncertainty_t - r_learning_t_effect
            r_t_period = max(0.001, r_t_period) 
            self.r_t_series.append(r_t_period)

            discounted_net_utility = net_utility_this_period / ((1 + r_t_period) ** (t + 1)) 
            self.discounted_Net_U_t_series.append(discounted_net_utility)
            nrupv += discounted_net_utility
            cumulative_nrupv += discounted_net_utility
            self.cumulative_nrupv_series.append(cumulative_nrupv)
            
        return nrupv, T_realistic

    def calculate_ocau(self):
        u_single_satisfaction = self.get_val("Q_single_satisfaction_1", is_single_satisfaction=True, default_val=0)
        u_single = u_single_satisfaction 

        alt_partner_likelihood_val = self.get_val("Q_alt_partner_likelihood_4", 1)
        alt_partner_likelihood = alt_partner_likelihood_val / 7.0
        
        initial_gross_U = sum(self.initial_utility_breakdown.values()) if hasattr(self, 'initial_utility_breakdown') and self.initial_utility_breakdown else 5 
        e_u_alternative = alt_partner_likelihood * (initial_gross_U * 0.7) 
        
        ocau = max(u_single, e_u_alternative)
        return ocau, u_single, e_u_alternative

    def calculate_sunk_cost_adjustment(self):
        sunk_influence_val = self.get_val("Q_sunk_cost_influence_4", 1)
        sunk_worry_val = self.get_val("Q_sunk_cost_worry_5", 1)
        
        adjustment_factor = ((sunk_influence_val - 1) + (sunk_worry_val - 1)) / 12.0 
        max_possible_adjustment = 3.0 
        sunk_cost_adj = adjustment_factor * max_possible_adjustment
        return sunk_cost_adj

    def evaluate(self):
        # Ensure all data_vars keys used in calculation match those created in GUI population
        # Example: Q_risk_breakup_A_1, Q_certainty_future_A_3 etc.
        # These were formed by f"{key_prefix}_{q_num_str.replace('.', '_')}"
        
        self.nrupv, self.T_realistic = self.calculate_nrupv_components_over_time()
        self.ocau, self.u_single, self.e_u_alt = self.calculate_ocau()
        self.sunk_cost_adj = self.calculate_sunk_cost_adjustment()

        is_worth_continuing = self.nrupv > (self.ocau + self.sunk_cost_adj)
        
        feedback = f"**ReVIM 模型分析结果**\n"
        feedback += f"--------------------------------------------------\n"
        feedback += f"计算的净关系效用现值 (NRUPV): {self.nrupv:.2f}\n"
        feedback += f"  (基于对未来 {self.T_realistic:.1f} 年的预期效用与成本进行折现计算)\n"
        initial_total_U = sum(self.initial_utility_breakdown.values()) if hasattr(self, 'initial_utility_breakdown') else 0
        initial_total_C = sum(self.initial_cost_breakdown.values()) if hasattr(self, 'initial_cost_breakdown') else 0
        feedback += f"  (首期总效用(加权): {initial_total_U:.2f}, 首期总成本(加权): {initial_total_C:.2f})\n"
        feedback += f"--------------------------------------------------\n"
        feedback += f"计算的机会成本/替代选项效用 (OCAU): {self.ocau:.2f}\n"
        feedback += f"  (单身状态预估效用: {self.u_single:.2f}, 其他潜在伴侣预估效用: {self.e_u_alt:.2f})\n"
        feedback += f"--------------------------------------------------\n"
        feedback += f"沉没成本谬误调整项: {self.sunk_cost_adj:.2f}\n"
        feedback += f"  (此数值越高，表明您可能受沉没成本影响越大，模型会提高决策的“门槛”)\n"
        feedback += f"--------------------------------------------------\n"
        feedback += f"**决策阈值比较:**\n"
        decision_threshold = self.ocau + self.sunk_cost_adj
        feedback += f"  NRUPV ({self.nrupv:.2f})  vs  (OCAU ({self.ocau:.2f}) + 沉没成本调整 ({self.sunk_cost_adj:.2f}))\n"
        feedback += f"  NRUPV ({self.nrupv:.2f})  vs  决策阈值 ({decision_threshold:.2f})\n"
        feedback += f"--------------------------------------------------\n"

        if is_worth_continuing:
            feedback += "**结论：根据ReVIM模型及您的输入，此段恋爱关系目前看来【值得继续】。**"
            margin = self.nrupv - decision_threshold
            if abs(decision_threshold) > 1e-6 and margin < abs(decision_threshold) * 0.15 : 
                 feedback += "\n  注意：尽管值得继续，但优势较小。建议关注关系中的薄弱环节并积极改善。"
        else:
            feedback += "**结论：根据ReVIM模型及您的输入，此段恋爱关系目前看来【可能不值得继续，或需重大改善】。**"
            margin = decision_threshold - self.nrupv
            if abs(decision_threshold) > 1e-6 and margin < abs(decision_threshold) * 0.15:
                feedback += "\n  注意：尽管目前不建议继续，但差距较小。若双方有强烈意愿，针对性改善关键问题后可重新评估。"
        
        feedback += "\n\n*免责声明：本结果仅为理论模型计算，不能替代您的个人判断和专业咨询。*"
        return feedback, is_worth_continuing

# --- GUI Application (ReVIMApp class and its methods) ---
# ... (The entire ReVIMApp class from the previous response, no changes needed there based on this error) ...
# Make sure the keys used in get_val in ReVIMCalculator match exactly how they are created in ReVIMApp.
# For example, in populate_dynamics_tab:
# self.add_likert_scale(parent_frame, "...", "Q_risk_breakup", "A.1")
# This creates key "Q_risk_breakup_A_1". This is what ReVIMCalculator.get_val("Q_risk_breakup_A_1",...) should use.
# This was corrected in the ReVIMCalculator part above.

class ReVIMApp:
    def __init__(self, master):
        self.master = master
        master.title("ReVIM - 恋爱关系持续性综合评估模型")
        master.geometry("950x800") # Increased size slightly more

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(family="Microsoft YaHei", size=9) 
        master.option_add("*Font", default_font)
        
        self.data_vars = {} 
        self.sensitivity_vars = {} 

        self.notebook = ttk.Notebook(master)
        
        tab_titles = [
            "第1部分: 基本信息", "第2部分: 关系效用", "第3部分: 关系成本",
            "第4部分: 动态与未来", "第5部分: 机会成本", "第6部分: 沉没成本",
            "第7部分: 权重分配", "敏感性分析", "结果与可视化" # Combined results and viz
        ]
        self.tabs = {}
        for title in tab_titles:
            self.tabs[title] = self.create_scrollable_tab(title)

        self.populate_basic_info_tab(self.tabs["第1部分: 基本信息"].scrollable_frame)
        self.populate_utility_tab(self.tabs["第2部分: 关系效用"].scrollable_frame)
        self.populate_cost_tab(self.tabs["第3部分: 关系成本"].scrollable_frame)
        self.populate_dynamics_tab(self.tabs["第4部分: 动态与未来"].scrollable_frame)
        self.populate_ocau_tab(self.tabs["第5部分: 机会成本"].scrollable_frame)
        self.populate_sunk_cost_tab(self.tabs["第6部分: 沉没成本"].scrollable_frame)
        self.populate_weights_tab(self.tabs["第7部分: 权重分配"].scrollable_frame)
        self.populate_sensitivity_tab(self.tabs["敏感性分析"].scrollable_frame)
        self.populate_results_and_visualization_tab(self.tabs["结果与可视化"].scrollable_frame)

        self.notebook.pack(expand=1, fill="both")

        self.calculate_button = ttk.Button(master, text="开始计算关系持续价值", command=self.run_calculation_and_show_results)
        self.calculate_button.pack(pady=10)
        
    def create_scrollable_tab(self, tab_title):
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=tab_title)

        canvas = tk.Canvas(tab_frame)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tab_frame.scrollable_frame = scrollable_frame 
        return tab_frame

    def add_likert_scale(self, parent, text, key_prefix, q_num_str, not_applicable_key=None, default_val=4):
        frame = ttk.LabelFrame(parent, text=f"{q_num_str}. {text}", padding=(5,2))
        frame.pack(fill="x", padx=5, pady=1)
        
        var = tk.IntVar(value=default_val)
        # Ensure q_num_str part of key is consistent (e.g. A_1, B_2)
        processed_q_num_str = str(q_num_str).replace('.', '_')
        full_key = f"{key_prefix}_{processed_q_num_str}"
        self.data_vars[full_key] = var
        
        scale = tk.Scale(frame, from_=1, to=7, orient=tk.HORIZONTAL, variable=var, length=250, resolution=1)
        scale.pack(side=tk.LEFT, padx=5)

        if not_applicable_key: # This key should be the exact key for the NA IntVar
            na_var = tk.IntVar(value=0)
            self.data_vars[not_applicable_key] = na_var # e.g. "U_bio_5_na"
            na_cb = ttk.Checkbutton(frame, text="不适用", variable=na_var)
            na_cb.pack(side=tk.LEFT, padx=5)
        return var

    def add_dropdown(self, parent, text, key, options, default_option_idx=0, q_num_str=""):
        # Key here is the direct key for data_vars
        frame = ttk.LabelFrame(parent, text=f"{q_num_str}. {text}" if q_num_str else text, padding=(5,2))
        frame.pack(fill="x", padx=5, pady=1)
        var = tk.StringVar(value=options[default_option_idx])
        self.data_vars[key] = var
        dropdown = ttk.Combobox(frame, textvariable=var, values=options, state="readonly", width=20)
        dropdown.pack(side=tk.LEFT, padx=5)
        return var

    def add_entry(self, parent, text, key, q_num_str="", default_value="30", width=8):
        frame = ttk.LabelFrame(parent, text=f"{q_num_str}. {text}", padding=(5,2))
        frame.pack(fill="x", padx=5, pady=1)
        var = tk.StringVar(value=default_value)
        self.data_vars[key] = var # Direct key
        entry = ttk.Entry(frame, textvariable=var, width=width)
        entry.pack(side=tk.LEFT, padx=5)
        return var
        
    def add_radiobuttons(self, parent, text, key, options_map, q_num_str="", default_key_idx=0):
        frame = ttk.LabelFrame(parent, text=f"{q_num_str}. {text}", padding=(5,2))
        frame.pack(fill="x", padx=5, pady=1)
        
        default_val_str = list(options_map.values())[default_key_idx]
        var = tk.StringVar(value=default_val_str)
        self.data_vars[key] = var # Direct key
        for label, val_str in options_map.items():
            rb = ttk.Radiobutton(frame, text=label, variable=var, value=val_str)
            rb.pack(side=tk.LEFT, padx=3, anchor='w')
        return var

    def add_section_header(self, parent, text):
        ttk.Label(parent, text=text, font=("Microsoft YaHei", 10, "bold")).pack(anchor="w", padx=5, pady=(8,2))

    def populate_basic_info_tab(self, parent_frame):
        self.add_section_header(parent_frame, "第1部分: 基本信息与关系概况")
        self.add_entry(parent_frame, "您的年龄：", "P1_Q1_user_age", "1", "30")
        self.add_dropdown(parent_frame, "您的性别：", "P1_Q2_user_gender", ["男", "女", "其他"], 0, "2")
        self.add_entry(parent_frame, "您伴侣的年龄：", "P1_Q3_partner_age", "3", "30")
        self.add_dropdown(parent_frame, "您伴侣的性别：", "P1_Q4_partner_gender", ["男", "女", "其他"], 1, "4")
        
        dur_frame = ttk.LabelFrame(parent_frame, text="5. 您目前这段恋爱关系已持续时间：", padding=(5,2))
        dur_frame.pack(fill="x", padx=5, pady=1)
        self.data_vars["P1_Q5_duration_years"] = tk.StringVar(value="1") # Used by get_val if needed, though T comes from Q_exp_duration_realistic
        ttk.Entry(dur_frame, textvariable=self.data_vars["P1_Q5_duration_years"], width=5).pack(side=tk.LEFT)
        ttk.Label(dur_frame, text="年").pack(side=tk.LEFT)
        self.data_vars["P1_Q5_duration_months"] = tk.StringVar(value="0")
        ttk.Entry(dur_frame, textvariable=self.data_vars["P1_Q5_duration_months"], width=5).pack(side=tk.LEFT)
        ttk.Label(dur_frame, text="月").pack(side=tk.LEFT)

        self.add_dropdown(parent_frame, "您与伴侣目前的同居状态：", "P1_Q6_cohabitation", 
                          ["未同居", "部分时间同居", "完全同居"], 0, "6")
        self.add_likert_scale(parent_frame, "您对目前这段关系的总体满意度如何？", "P1", "Q7_satisfaction") # Key: P1_Q7_satisfaction
        
        trend_options = ["显著改善", "略有改善", "基本不变", "略有恶化", "显著恶化", "不确定"]
        self.add_dropdown(parent_frame, "您认为这段关系在过去一年中是：", "P1_Q8_past_trend", trend_options, 2, "8")
        self.add_dropdown(parent_frame, "您对这段关系未来一年的发展预期是：", "P1_Q9_future_trend", trend_options, 2, "9")

    def populate_utility_tab(self, parent_frame):
        self.add_section_header(parent_frame, "第2部分: 关系效用 (您从关系中获得的益处)")
        future_options = ["显著改善", "略有改善", "保持不变", "略有恶化", "显著恶化", "不确定"]
        utility_categories = {
            "U_psych": ("A. 心理学效用", 10, ["被爱和被珍视", "深厚亲密感", "陪伴感减少孤独", "安全稳定感", "智力启发激励", "共同兴趣享受", "促进个人成长", "支持个人目标", "基本心理需求满足", "提升幸福感"]),
            "U_econ": ("B. 经济学效用", 5, ["降低生活成本", "财务安全感", "共同财富积累潜力", "事业支持资源", "共同分担财务风险"]),
            "U_socio": ("C. 社会学效用", 5, ["社交网络扩展", "社交圈融合", "获得社会支持", "家庭朋友接纳", "增强社会归属感"]),
            "U_anthro": ("D. 人类学效用", 5, ["文化背景尊重适应", "价值观习俗兼容", "共同仪式习惯", "融入亲属体系", "感知伴侣长期价值"]),
            "U_bio": ("E. 生物学/医学效用", 5, ["持续生理吸引力", "性生活和谐满意", "坦诚沟通性与健康", "促进健康生活习惯", "（若考虑生育）生育看法计划一致/可协商"]),
            "U_poli": ("F. 政治学效用", 4, ["权力相对平衡", "重要决策平等协商", "个人意愿需求尊重", "共同生活愿景相似"]),
            "U_philo": ("G. 哲学效用", 3, ["核心价值观道德观契合", "理解支持人生追求", "感觉更接近真实自我"]),
            "U_law": ("H. 法学效用", 2, ["（若有）法律承诺带来安全稳定", "权利义务清晰公平感知"]),
            "U_comm": ("I. 传播学效用", 4, ["沟通顺畅高效", "准确理解对方", "有效构建共享意义", "建设性沟通处理分歧"]),
            "U_geo": ("J. 地理学效用", 3, ["共享空间舒适满意", "居住选择规划一致/可协调", "对“地方”建归属感"]),
            "U_eco_sys": ("K. 生态学/系统论效用", 3, ["关系如健康系统自我修复成长", "积极互动远多于消极", "关系稳定可预测安心"])
        }
        for cat_key_prefix, (cat_label, num_q, q_texts) in utility_categories.items():
            self.add_section_header(parent_frame, cat_label)
            cat_code = cat_key_prefix.split('_')[-1].upper() # PSYCH, ECON etc.
            for i in range(num_q):
                q_num_str_display = f"{cat_code}.{i+1}" # For display "PSYCH.1"
                na_opt_key_specific = None
                if cat_key_prefix == "U_bio" and i == 4: na_opt_key_specific = "U_bio_5_na" # Hardcoded specific NA key
                if cat_key_prefix == "U_law" and i == 0: na_opt_key_specific = "U_law_1_na" # Hardcoded specific NA key
                self.add_likert_scale(parent_frame, q_texts[i], cat_key_prefix, q_num_str_display, not_applicable_key=na_opt_key_specific)
            self.add_dropdown(parent_frame, f"预期未来5年，以上{cat_label.split(' ')[1]}会：", f"{cat_key_prefix}_future", future_options, 2)
    
    def populate_cost_tab(self, parent_frame):
        self.add_section_header(parent_frame, "第3部分: 关系成本 (您为关系付出的代价)")
        future_options = ["显著改善", "略有改善", "保持不变", "略有恶化", "显著恶化", "不确定"]
        cost_categories = {
            "C_psych": ("A. 心理学成本", 5, ["情感被消耗", "价值观期望冲突", "个人成长受阻压抑", "心理健康负面影响", "重要需求未满足挫败"]),
            "C_econ": ("B. 经济学成本", 3, ["财务压力大", "放弃职业投资机会", "担忧伴侣财务风险"]),
            "C_socio": ("C. 社会学成本", 3, ["与友亲疏远紧张", "外界负面压力", "融入对方圈子不适"]),
            "C_anthro": ("D. 人类学成本", 2, ["文化差异冲突不适", "放弃文化认同失落感"]),
            "C_bio": ("E. 生物学/医学成本", 3, ["性生活不和谐不满/压力", "不良生活习惯影响健康", "照顾伴侣健康耗费精力"]),
            "C_poli": ("F. 政治学成本", 3, ["权力不平等被压制", "为“谁说了算”冲突", "自主性私人空间受限"]),
            "C_philo": ("G. 哲学成本", 2, ["根本价值观道德观分歧", "生活意义目标模糊/被迫改变"]),
            "C_law": ("H. 法学成本", 2, ["担忧分手法律财产纠纷", "权利义务不清不公困扰"]),
            "C_comm": ("I. 传播学成本", 2, ["沟通障碍误解无效", "伤害性沟通模式"]),
            "C_geo": ("J. 地理学成本", 2, ["（若异地）异地恋成本显著", "居住环境共享空间不满/压力"]),
            "C_eco_sys": ("K. 生态学/系统论成本", 3, ["关系陷入负面循环", "不确定混乱感疲惫不安", "关系僵化缺弹性"])
        }
        for cat_key_prefix, (cat_label, num_q, q_texts) in cost_categories.items():
            self.add_section_header(parent_frame, cat_label)
            cat_code = cat_key_prefix.split('_')[-1].upper()
            for i in range(num_q):
                q_num_str_display = f"{cat_code}.{i+1}"
                na_opt_key_specific = None
                if cat_key_prefix == "C_geo" and i == 0: 
                    na_opt_key_specific = "C_geo_1_na" 
                self.add_likert_scale(parent_frame, q_texts[i], cat_key_prefix, q_num_str_display, not_applicable_key=na_opt_key_specific)
            self.add_dropdown(parent_frame, f"预期未来5年，以上{cat_label.split(' ')[1]}会：", f"{cat_key_prefix}_future", future_options, 2)

    def populate_dynamics_tab(self, parent_frame):
        self.add_section_header(parent_frame, "第4部分: 关系动态与未来预期")
        self.add_section_header(parent_frame, "A. 关系风险与不确定性")
        self.add_likert_scale(parent_frame, "您认为这段关系在未来5年内面临意外破裂的风险有多大？", "Q_risk_breakup", "A.1")
        self.add_radiobuttons(parent_frame, "关系中是否存在一些反复出现且难以解决的根本性冲突模式？", "Q_conflict_patterns_exist_A_2", {"是":"1", "否":"0"}, "A.2")
        self.add_likert_scale(parent_frame, "您对这段关系的未来走向有多大的确定性？", "Q_certainty_future", "A.3")
        self.add_likert_scale(parent_frame, "您对伴侣的长期忠诚度和承诺有多大信心？", "Q_loyalty_confidence", "A.4")

        self.add_section_header(parent_frame, "B. 关系资本与学习适应")
        self.add_likert_scale(parent_frame, "您认为您和伴侣共同积累了多少“关系资产”？", "Q_rel_capital", "B.1")
        self.add_likert_scale(parent_frame, "您和伴侣是否经常投入时间和精力来主动维护和增进感情？", "Q_rel_investment", "B.2")
        self.add_likert_scale(parent_frame, "当关系出现问题或矛盾时，共同解决问题、学习改进的能力如何？", "Q_adapt_solve", "B.3")
        self.add_likert_scale(parent_frame, "面对生活中的重大变化或外部压力，共同适应和应对的能力如何？", "Q_adapt_stress", "B.4")
        self.add_likert_scale(parent_frame, "回顾关系历史，双方从过去的经验教训中学习并使关系向好的程度如何？", "Q_adapt_learn_hist", "B.5")

        self.add_section_header(parent_frame, "C. 预期关系持续时间")
        duration_options = ["几个月", "1-2年", "3-5年", "5-10年", "10年以上", "终身", "非常不确定"]
        self.add_dropdown(parent_frame, "理想中希望这段关系能持续多久？", "Q_exp_duration_ideal_C_1", duration_options, 5, "C.1") # Key changed
        self.add_dropdown(parent_frame, "现实地预期这段关系最有可能持续多久？", "Q_exp_duration_realistic", duration_options, 5, "C.2") # Key is Q_exp_duration_realistic

        self.add_section_header(parent_frame, "D. 外部冲击感知")
        self.add_radiobuttons(parent_frame, "预见到未来1-3年内可能出现对关系产生重大影响的外部事件？", "Q_external_shock_exist_D_1", {"是":"1", "否":"0"}, "D.1") # Key changed

    def populate_ocau_tab(self, parent_frame):
        self.add_section_header(parent_frame, "第5部分: 机会成本与替代选项 (OCAU)")
        single_options = ["显著更高", "略高", "差不多", "略低", "显著更低"]
        self.add_dropdown(parent_frame, "如果您现在是单身状态，您预期的个人生活满意度会比目前高还是低？", "Q_single_satisfaction_1", single_options, 2, "1") # Key changed
        
        ttk.Label(parent_frame, text="2. 单身状态可能益处 (多选，暂不直接计入模型):").pack(anchor='w', padx=5, pady=(5,0))
        # ... (checkboxes as before, not stored in self.data_vars for calculation)
        single_benefits = ["更多个人自由和时间", "更能专注个人事业/学业发展", "避免关系中的冲突和情感消耗", "有机会结识新的潜在伴侣", "财务更独立自主"]
        for benefit in single_benefits:
             cb_var = tk.IntVar() 
             cb = ttk.Checkbutton(parent_frame, text=benefit, variable=cb_var)
             cb.pack(anchor='w', padx=15)
        
        ttk.Label(parent_frame, text="3. 单身状态可能弊端 (多选，暂不直接计入模型):").pack(anchor='w', padx=5, pady=(5,0))
        single_drawbacks = ["孤独感", "缺乏情感支持和亲密感", "生活成本可能更高", "某些生活方面缺乏帮助", "社会压力"]
        for drawback in single_drawbacks:
             cb_var = tk.IntVar() 
             cb = ttk.Checkbutton(parent_frame, text=drawback, variable=cb_var)
             cb.pack(anchor='w', padx=15)

        self.add_likert_scale(parent_frame, "您认为在您当前可接触的范围内，找到一个比现任伴侣更适合您、且能建立满意关系的人的可能性有多大？", "Q_alt_partner_likelihood", "4")
        recovery_options = ["很快（1-3个月内）", "一般（3-6个月）", "较长（6个月-1年）", "很长（1年以上）", "不确定"]
        self.add_dropdown(parent_frame, "如果与现任伴侣分手，您估计需要多长时间才能从情感上恢复？", "Q_recovery_time_5", recovery_options, 1, "5") # Key changed

    def populate_sunk_cost_tab(self, parent_frame):
        self.add_section_header(parent_frame, "第6部分: 沉没成本与决策倾向")
        self.add_likert_scale(parent_frame, "您在这段关系中投入的情感有多深？", "Q_sunk_emotion_depth", "2")
        self.add_likert_scale(parent_frame, "您在这段关系中投入的物质/财务资源对您而言有多重要？", "Q_sunk_material_importance", "3")
        self.add_likert_scale(parent_frame, "“我已经投入太多，不应轻易放弃”的想法在多大程度上影响您的判断？", "Q_sunk_cost_influence", "4")
        self.add_likert_scale(parent_frame, "您是否担心如果现在分手，过去的投入就都“白费”了？", "Q_sunk_cost_worry", "5")

    def populate_weights_tab(self, parent_frame):
        self.add_section_header(parent_frame, "第7部分: 权重分配 (个性化因子重要性)")
        self.add_section_header(parent_frame, "A. 关系效用方面的重要性 (1=完全不重要, 7=极其重要)")
        utility_weight_map = {
            "W_U_psych": "心理情感满足", "W_U_econ": "经济财务稳定", "W_U_socio": "社会网络与支持",
            "W_U_anthro": "文化与价值观兼容", "W_U_bio": "生理吸引与性健康", "W_U_poli": "权力平衡与公平决策",
            "W_U_philo": "共同生活意义与目标", "W_U_law": "法律承诺的保障", "W_U_comm": "高质量的沟通理解",
            "W_U_geo": "舒适共享空间归属感", "W_U_eco_sys": "关系系统健康稳定"
        }
        for i, (key, text) in enumerate(utility_weight_map.items()): # key is direct key for data_vars
            self.add_likert_scale(parent_frame, text, key.split('_')[0], f"{key.split('_')[-1].upper()}.{i+1}") # Use key directly

        self.add_section_header(parent_frame, "B. 关系成本方面的敏感度 (1=容忍度高/不敏感, 7=容忍度极低/极敏感)")
        cost_weight_map = {
            "W_C_psych": "心理情感消耗", "W_C_econ": "经济财务负担", "W_C_socio": "社交孤立与外部压力",
            "W_C_anthro": "文化冲突与认同丧失", "W_C_bio": "生理健康受损与性不满", "W_C_poli": "权力失衡与自主性受限",
            "W_C_philo": "价值观冲突与意义迷失", "W_C_law": "潜在法律风险与纠纷", "W_C_comm": "沟通障碍与负面互动",
            "W_C_geo": "地理空间不适异地成本", "W_C_eco_sys": "关系系统僵化与混乱"
        }
        for i, (key, text) in enumerate(cost_weight_map.items()): # key is direct key for data_vars
             self.add_likert_scale(parent_frame, text, key.split('_')[0], f"{key.split('_')[-1].upper()}.{i+1}") # Use key directly

    def add_sensitivity_slider(self, parent, text, key, from_=0.5, to=1.5, default_val=1.0, resolution=0.05):
        frame = ttk.Frame(parent, padding=(5,2))
        frame.pack(fill="x", padx=5, pady=1)
        ttk.Label(frame, text=text, width=35, anchor='w').pack(side=tk.LEFT)
        
        var = tk.DoubleVar(value=default_val)
        self.sensitivity_vars[key] = var
        
        val_label = ttk.Label(frame, text=f"{default_val:.2f}", width=5)
        val_label.pack(side=tk.RIGHT, padx=5)

        def update_label(v): 
            val_label.config(text=f"{float(v):.2f}")

        scale = tk.Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL, variable=var, length=200, resolution=resolution, showvalue=0, command=update_label)
        scale.pack(side=tk.LEFT, padx=5)
        return var

    def populate_sensitivity_tab(self, parent_frame):
        self.add_section_header(parent_frame, "敏感性分析调整项")
        ttk.Label(parent_frame, text="调整以下参数，观察其对最终结果的影响（默认值为1.0，表示不调整原始计算）：").pack(padx=5, pady=5, anchor='w')
        self.add_sensitivity_slider(parent_frame, "基础贴现率调整因子 (r_base Adj.):", "base_discount_rate_adj")
        self.add_sensitivity_slider(parent_frame, "未来预期乐观度调整 (Future Optimism Adj.):", "future_projection_optimism_adj")
        self.add_sensitivity_slider(parent_frame, "总体风险感知调整 (Risk Perception Adj.):", "overall_risk_perception_adj")
        self.add_sensitivity_slider(parent_frame, "效用/成本实现概率调整 (Realization Prob Adj.):", "realization_prob_adj")

    def populate_results_and_visualization_tab(self, parent_frame):
        # This tab will be split into two main areas: Text results and Visualizations
        # Top part for text results
        self.results_text_widget = tk.Text(parent_frame, wrap=tk.WORD, padx=10, pady=10, height=15, font=("Microsoft YaHei", 10))
        results_scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=self.results_text_widget.yview)
        self.results_text_widget.config(yscrollcommand=results_scrollbar.set)
        
        self.results_text_widget.grid(row=0, column=0, sticky="nsew")
        results_scrollbar.grid(row=0, column=1, sticky="ns")

        # Bottom part for visualizations
        self.vis_frame = ttk.Frame(parent_frame) 
        self.vis_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10,0))

        parent_frame.grid_rowconfigure(0, weight=1) # Text area takes some space
        parent_frame.grid_rowconfigure(1, weight=2) # Visualization takes more space
        parent_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas_agg = None

    def display_visualizations(self, calculator):
        if self.canvas_agg: 
            self.canvas_agg.get_tk_widget().destroy()

        fig = plt.Figure(figsize=(8, 7), dpi=100) # Adjusted figsize
        fig.subplots_adjust(hspace=0.5, wspace=0.35) 

        ax1 = fig.add_subplot(2, 2, 1)
        utility_data = {k: v for k, v in calculator.initial_utility_breakdown.items() if abs(v) > 1e-3} # Filter small/zero values
        utility_labels = [f"{k} ({v:.1f})" for k,v in utility_data.items()]
        utility_sizes = [abs(v) for v in utility_data.values()] # Pie needs positive values
        if utility_sizes:
            ax1.pie(utility_sizes, labels=utility_labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 6})
            ax1.set_title("首期效用构成 (加权后)", fontsize=8)
        else:
            ax1.text(0.5, 0.5, "无显著效用数据", ha='center', va='center', fontsize=8)
            ax1.set_title("首期效用构成", fontsize=8)

        ax2 = fig.add_subplot(2, 2, 2)
        cost_data = {k: v for k, v in calculator.initial_cost_breakdown.items() if abs(v) > 1e-3}
        cost_labels = [f"{k} ({v:.1f})" for k,v in cost_data.items()]
        cost_sizes = [abs(v) for v in cost_data.values()]
        if cost_sizes:
            ax2.pie(cost_sizes, labels=cost_labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 6})
            ax2.set_title("首期成本构成 (加权后)", fontsize=8)
        else:
            ax2.text(0.5, 0.5, "无显著成本数据", ha='center', va='center', fontsize=8)
            ax2.set_title("首期成本构成", fontsize=8)

        ax3 = fig.add_subplot(2, 2, 3)
        if hasattr(calculator, 'time_periods') and calculator.time_periods:
            ax3.plot(calculator.time_periods, calculator.Net_U_t_series, marker='o', markersize=3, label="每期净效用")
            ax3.plot(calculator.time_periods, calculator.discounted_Net_U_t_series, marker='x', markersize=3, linestyle='--', label="每期折现后净效用")
            ax3.axhline(0, color='grey', lw=0.8, linestyle=':')
            ax3.set_xlabel("时间周期 (年)", fontsize=7)
            ax3.set_ylabel("净效用值", fontsize=7)
            ax3.set_title("预期净效用随时间变化", fontsize=8)
            ax3.legend(fontsize=6)
            ax3.tick_params(axis='both', which='major', labelsize=6)
        else:
            ax3.text(0.5, 0.5, "无时间序列数据", ha='center', va='center', fontsize=8)
            ax3.set_title("预期净效用随时间变化", fontsize=8)

        ax4 = fig.add_subplot(2, 2, 4)
        if hasattr(calculator, 'time_periods') and calculator.time_periods:
            ax4.plot(calculator.time_periods, calculator.cumulative_nrupv_series, marker='o', markersize=3, label="累计NRUPV")
            ax4.axhline(0, color='grey', lw=0.8, linestyle=':')
            ax4.set_xlabel("时间周期 (年)", fontsize=7)
            ax4.set_ylabel("累计NRUPV", fontsize=7)
            ax4.set_title("累计净关系效用现值", fontsize=8)
            ax4.legend(fontsize=6)
            ax4.tick_params(axis='both', which='major', labelsize=6)
        else:
            ax4.text(0.5, 0.5, "无累计数据", ha='center', va='center', fontsize=8)
            ax4.set_title("累计净关系效用现值", fontsize=8)

        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS'] 
        plt.rcParams['axes.unicode_minus'] = False 

        self.canvas_agg = FigureCanvasTkAgg(fig, master=self.vis_frame)
        self.canvas_agg.draw()
        self.canvas_agg.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def run_calculation_and_show_results(self):
        # Clear previous results from text widget
        if self.results_text_widget:
            self.results_text_widget.config(state=tk.NORMAL)
            self.results_text_widget.delete('1.0', tk.END)
        
        try:
            calculator = ReVIMCalculator(self.data_vars, self.sensitivity_vars)
            feedback, _ = calculator.evaluate() 
            
            if self.results_text_widget:
                self.results_text_widget.insert(tk.END, feedback)
                self.results_text_widget.config(state=tk.DISABLED) 

            self.display_visualizations(calculator)
            self.notebook.select(self.tabs["结果与可视化"]) 

        except Exception as e:
            error_message = f"计算过程中发生错误：\n{e}\n\n请确保所有相关字段已正确填写。"
            if self.results_text_widget:
                self.results_text_widget.insert(tk.END, error_message)
                self.results_text_widget.config(state=tk.DISABLED)
            else: # Fallback if text widget is not yet created or accessible
                messagebox.showerror("计算错误", error_message)
            import traceback
            traceback.print_exc() 


if __name__ == '__main__':
    root = tk.Tk()
    style = ttk.Style(root)
    available_themes = style.theme_names()
    if "clam" in available_themes: 
        style.theme_use("clam")
    elif "vista" in available_themes: 
        style.theme_use("vista")
    app = ReVIMApp(root)
    root.mainloop()