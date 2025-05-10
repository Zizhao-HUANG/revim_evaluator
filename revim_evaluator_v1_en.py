import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- ReVIM Model Calculation Logic ---
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
                    if val_str == "不适用": return "N/A" # Translate "Not Applicable"
                    if val_str == "": return default_val

                    if is_future_expect:
                        mapping = {"显著改善": 0.03, "略有改善": 0.015, "保持不变": 0, "略有恶化": -0.015, "显著恶化": -0.03, "不确定": -0.005}
                        # Translate future expectation options
                        mapping_en = {"Significantly improved": 0.03, "Slightly improved": 0.015, "Remained unchanged": 0, "Slightly worsened": -0.015, "Significantly worsened": -0.03, "Uncertain": -0.005}
                        return mapping_en.get(val_str, 0)
                    if is_duration:
                        mapping = {"几个月": 0.5, "1-2年": 1.5, "3-5年": 4, "5-10年": 7.5, "10年以上": 15, "终身": 25, "非常不确定": 3}
                        # Translate duration options
                        mapping_en = {"Several months": 0.5, "1-2 years": 1.5, "3-5 years": 4, "5-10 years": 7.5, "More than 10 years": 15, "Lifelong": 25, "Very uncertain": 3}
                        return mapping_en.get(val_str, 3)
                    if is_single_satisfaction:
                        mapping = {"显著更高": 3, "略高": 1.5, "差不多": 0, "略低": -1.5, "显著更低": -3}
                        # Translate single satisfaction options
                        mapping_en = {"Significantly higher": 3, "Slightly higher": 1.5, "About the same": 0, "Slightly lower": -1.5, "Significantly lower": -3}
                        return mapping_en.get(val_str, 0)
                    if is_recovery_time:
                        mapping = {"很快（1-3个月内）": 0.25, "一般（3-6个月）": 0.5, "较长（6个月-1年）": 1, "很长（1年以上）": 1.5, "不确定": 0.75}
                        # Translate recovery time options
                        mapping_en = {"Very soon (within 1-3 months)": 0.25, "Average (3-6 months)": 0.5, "Longer (6 months-1 year)": 1, "Very long (more than 1 year)": 1.5, "Uncertain": 0.75}
                        return mapping_en.get(val_str, 0.75)
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
        # Translate utility category labels
        utility_labels_en = {
            "心理": "Psychological", "经济": "Economic", "社交": "Sociological",
            "文化人类": "Anthropological", "生理医学": "Biological/Medical", "权力治理": "Political",
            "哲学精神": "Philosophical/Spiritual", "法律承诺": "Legal Commitment", "沟通传播": "Communication",
            "地理空间": "Geospatial", "生态系统": "Ecological/Systems Theory"
        }

        cost_details = [
            ("C_psych", "心理", 5), ("C_econ", "经济", 3), ("C_socio", "社交", 3),
            ("C_anthro", "文化人类", 2), ("C_bio", "生理医学", 3), ("C_poli", "权力治理", 3),
            ("C_philo", "哲学精神", 2), ("C_law", "法律承诺", 2), ("C_comm", "沟通传播", 2),
            ("C_eco_sys", "生态系统", 3)
            # C_geo handled separately
        ]
         # Translate cost category labels
        cost_labels_en = {
            "心理": "Psychological", "经济": "Economic", "社交": "Sociological",
            "文化人类": "Anthropological", "生理医学": "Biological/Medical", "权力治理": "Political",
            "哲学精神": "Philosophical/Spiritual", "法律承诺": "Legal Commitment", "沟通传播": "Communication",
            "生态系统": "Ecological/Systems Theory"
        }


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
                                      # It's better to calculate U_law separately for clarity.
                    if num_q_actual == 1 and num_q_default == 2: # Only U_law_LAW.2 is scored
                        # This requires calculate_category_value_at_t to handle a start_index or specific question list
                        # For now, let's assume if num_q_actual is 1, it scores the first question of that category.
                        # This is problematic for U_law if U_law_LAW.1 is NA.
                        # Let's calculate U_law separately for clarity.
                        if cat_key == "U_law": continue # Skip in loop, handle below

                val_t = self.calculate_category_value_at_t(cat_key, num_q_actual, f"{cat_key}_future", f"W_{cat_key}", t)
                current_total_utility += val_t
                if t == 0: self.initial_utility_breakdown[utility_labels_en.get(label, label)] = val_t # Use English label
            
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
            if t == 0: self.initial_utility_breakdown[utility_labels_en.get("法律承诺", "法律承诺")] = u_law_t # Use English label


            current_total_cost = 0
            for cat_key, label, num_q in cost_details:
                val_t = self.calculate_category_value_at_t(cat_key, num_q, f"{cat_key}_future", f"W_{cat_key}", t)
                current_total_cost += val_t
                if t == 0: self.initial_cost_breakdown[cost_labels_en.get(label, label)] = val_t # Use English label

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
            if t == 0: self.initial_cost_breakdown[utility_labels_en.get("地理空间", "地理空间")] = c_geo_t # Use English label
            
            # Synergy/Conflict Factors
            u_psych_val_t0 = self.initial_utility_breakdown.get("Psychological", 0) # Use t=0 value for simplicity of synergy factor, use English key
            u_comm_val_t0 = self.initial_utility_breakdown.get("Communication", 0) # Use English key
            
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

            c_philo_val_t0 = self.initial_cost_breakdown.get("Philosophical/Spiritual", 0) # Use English key
            c_psych_val_t0 = self.initial_cost_breakdown.get("Psychological", 0) # Use English key
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
        
        feedback = f"**ReVIM Model Analysis Results**\n" # Translate
        feedback += f"--------------------------------------------------\n"
        feedback += f"Calculated Net Relationship Utility Present Value (NRUPV): {self.nrupv:.2f}\n" # Translate
        feedback += f"  (Calculated based on discounting expected utility and costs over the next {self.T_realistic:.1f} years)\n" # Translate
        initial_total_U = sum(self.initial_utility_breakdown.values()) if hasattr(self, 'initial_utility_breakdown') else 0
        initial_total_C = sum(self.initial_cost_breakdown.values()) if hasattr(self, 'initial_cost_breakdown') else 0
        feedback += f"  (Initial Total Utility (Weighted): {initial_total_U:.2f}, Initial Total Cost (Weighted): {initial_total_C:.2f})\n" # Translate
        feedback += f"--------------------------------------------------\n"
        feedback += f"Calculated Opportunity Cost / Alternative Utility (OCAU): {self.ocau:.2f}\n" # Translate
        feedback += f"  (Estimated Utility in Single State: {self.u_single:.2f}, Estimated Utility with Other Potential Partners: {self.e_u_alt:.2f})\n" # Translate
        feedback += f"--------------------------------------------------\n"
        feedback += f"Sunk Cost Fallacy Adjustment: {self.sunk_cost_adj:.2f}\n" # Translate
        feedback += f"  (A higher value indicates you may be more influenced by sunk costs, raising the decision 'threshold' in the model)\n" # Translate
        feedback += f"--------------------------------------------------\n"
        feedback += f"**Decision Threshold Comparison:**\n" # Translate
        decision_threshold = self.ocau + self.sunk_cost_adj
        feedback += f"  NRUPV ({self.nrupv:.2f})  vs  (OCAU ({self.ocau:.2f}) + Sunk Cost Adjustment ({self.sunk_cost_adj:.2f}))\n" # Translate
        feedback += f"  NRUPV ({self.nrupv:.2f})  vs  Decision Threshold ({decision_threshold:.2f})\n" # Translate
        feedback += f"--------------------------------------------------\n"

        if is_worth_continuing:
            feedback += "**Conclusion: Based on the ReVIM model and your input, this relationship currently appears to be [WORTH CONTINUING].**" # Translate
            margin = self.nrupv - decision_threshold
            if abs(decision_threshold) > 1e-6 and margin < abs(decision_threshold) * 0.15 :
                 feedback += "\n  Note: Although worth continuing, the advantage is small. It is recommended to focus on weak areas in the relationship and actively improve them." # Translate
        else:
            feedback += "**Conclusion: Based on the ReVIM model and your input, this relationship currently appears to be [POSSIBLY NOT WORTH CONTINUING, or requires significant improvement].**" # Translate
            margin = decision_threshold - self.nrupv
            if abs(decision_threshold) > 1e-6 and margin < abs(decision_threshold) * 0.15:
                feedback += "\n  Note: Although not recommended to continue at present, the difference is small. If both parties have a strong desire, re-evaluation is possible after targeted improvement of key issues." # Translate
        
        feedback += "\n\n*Disclaimer: This result is based purely on theoretical model calculation and should not replace your personal judgment or professional advice.*" # Translate
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
        master.title("ReVIM - Relationship Viability Integrated Model") # Translate title
        master.geometry("950x800") # Increased size slightly more

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(family="Microsoft YaHei", size=9) # Font name remains as is
        master.option_add("*Font", default_font)
        
        self.data_vars = {}
        self.sensitivity_vars = {}

        self.notebook = ttk.Notebook(master)
        
        tab_titles = [
            "Part 1: Basic Information", "Part 2: Relationship Utility", "Part 3: Relationship Costs", # Translate tab titles
            "Part 4: Dynamics and Future", "Part 5: Opportunity Costs", "Part 6: Sunk Costs",
            "Part 7: Weight Allocation", "Sensitivity Analysis", "Results and Visualization" # Combined results and viz
        ]
        self.tabs = {}
        for title in tab_titles:
            self.tabs[title] = self.create_scrollable_tab(title)

        self.populate_basic_info_tab(self.tabs["Part 1: Basic Information"].scrollable_frame) # Use translated title
        self.populate_utility_tab(self.tabs["Part 2: Relationship Utility"].scrollable_frame) # Use translated title
        self.populate_cost_tab(self.tabs["Part 3: Relationship Costs"].scrollable_frame) # Use translated title
        self.populate_dynamics_tab(self.tabs["Part 4: Dynamics and Future"].scrollable_frame) # Use translated title
        self.populate_ocau_tab(self.tabs["Part 5: Opportunity Costs"].scrollable_frame) # Use translated title
        self.populate_sunk_cost_tab(self.tabs["Part 6: Sunk Costs"].scrollable_frame) # Use translated title
        self.populate_weights_tab(self.tabs["Part 7: Weight Allocation"].scrollable_frame) # Use translated title
        self.populate_sensitivity_tab(self.tabs["Sensitivity Analysis"].scrollable_frame) # Use translated title
        self.populate_results_and_visualization_tab(self.tabs["Results and Visualization"].scrollable_frame) # Use translated title

        self.notebook.pack(expand=1, fill="both")

        self.calculate_button = ttk.Button(master, text="Calculate Relationship Viability", command=self.run_calculation_and_show_results) # Translate button text
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
            na_cb = ttk.Checkbutton(frame, text="N/A", variable=na_var) # Translate "Not Applicable"
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
        
        # Translate radio button labels
        options_map_en = {}
        for label_cn, val_str in options_map.items():
            if label_cn == "是": options_map_en["Yes"] = val_str
            elif label_cn == "否": options_map_en["No"] = val_str
            else: options_map_en[label_cn] = val_str # Keep if not Yes/No

        for label_en, val_str in options_map_en.items():
            rb = ttk.Radiobutton(frame, text=label_en, variable=var, value=val_str)
            rb.pack(side=tk.LEFT, padx=3, anchor='w')
        return var

    def add_section_header(self, parent, text):
        ttk.Label(parent, text=text, font=("Microsoft YaHei", 10, "bold")).pack(anchor="w", padx=5, pady=(8,2)) # Font name remains as is

    def populate_basic_info_tab(self, parent_frame):
        self.add_section_header(parent_frame, "Part 1: Basic Information and Relationship Overview") # Translate
        self.add_entry(parent_frame, "Your age:", "P1_Q1_user_age", "1", "30") # Translate
        self.add_dropdown(parent_frame, "Your gender:", "P1_Q2_user_gender", ["Male", "Female", "Other"], 0, "2") # Translate
        self.add_entry(parent_frame, "Your partner's age:", "P1_Q3_partner_age", "3", "30") # Translate
        self.add_dropdown(parent_frame, "Your partner's gender:", "P1_Q4_partner_gender", ["Male", "Female", "Other"], 1, "4") # Translate
        
        dur_frame = ttk.LabelFrame(parent_frame, text="5. Duration of your current relationship:", padding=(5,2)) # Translate
        dur_frame.pack(fill="x", padx=5, pady=1)
        self.data_vars["P1_Q5_duration_years"] = tk.StringVar(value="1") # Used by get_val if needed, though T comes from Q_exp_duration_realistic
        ttk.Entry(dur_frame, textvariable=self.data_vars["P1_Q5_duration_years"], width=5).pack(side=tk.LEFT)
        ttk.Label(dur_frame, text="Years").pack(side=tk.LEFT) # Translate
        self.data_vars["P1_Q5_duration_months"] = tk.StringVar(value="0")
        ttk.Entry(dur_frame, textvariable=self.data_vars["P1_Q5_duration_months"], width=5).pack(side=tk.LEFT)
        ttk.Label(dur_frame, text="Months").pack(side=tk.LEFT) # Translate

        self.add_dropdown(parent_frame, "Your current cohabitation status:", "P1_Q6_cohabitation", # Translate
                          ["Not cohabiting", "Part-time cohabiting", "Fully cohabiting"], 0, "6") # Translate options
        self.add_likert_scale(parent_frame, "Overall satisfaction with the current relationship?", "P1", "Q7_satisfaction") # Translate
        
        trend_options = ["Significantly improved", "Slightly improved", "Remained unchanged", "Slightly worsened", "Significantly worsened", "Uncertain"] # Translate options
        self.add_dropdown(parent_frame, "How has the relationship changed in the past year?", "P1_Q8_past_trend", trend_options, 2, "8") # Translate
        self.add_dropdown(parent_frame, "What is your expectation for the relationship's development in the next year?", "P1_Q9_future_trend", trend_options, 2, "9") # Translate

    def populate_utility_tab(self, parent_frame):
        self.add_section_header(parent_frame, "Part 2: Relationship Utility (Benefits you gain from the relationship)") # Translate
        future_options = ["Significantly improved", "Slightly improved", "Remained unchanged", "Slightly worsened", "Significantly worsened", "Uncertain"] # Translate options
        utility_categories = {
            "U_psych": ("A. Psychological Utility", 10, ["Feeling loved and cherished", "Deep intimacy", "Companionship reducing loneliness", "Sense of security and stability", "Intellectual stimulation and inspiration", "Enjoyment of shared interests", "Facilitating personal growth", "Support for personal goals", "Satisfaction of basic psychological needs", "Increased happiness"]), # Translate
            "U_econ": ("B. Economic Utility", 5, ["Reduced cost of living", "Financial security", "Potential for joint wealth accumulation", "Career support and resources", "Sharing financial risks"]), # Translate
            "U_socio": ("C. Sociological Utility", 5, ["Expansion of social network", "Integration of social circles", "Receiving social support", "Acceptance by family and friends", "Enhanced sense of social belonging"]), # Translate
            "U_anthro": ("D. Anthropological Utility", 5, ["Respect and adaptation to cultural backgrounds", "Compatibility of values and customs", "Shared rituals and habits", "Integration into kinship systems", "Perception of partner's long-term value"]), # Translate
            "U_bio": ("E. Biological/Medical Utility", 5, ["Continued physical attraction", "Harmonious and satisfying sex life", "Open communication about sex and health", "Promoting healthy lifestyle habits", "(If considering children) Alignment/negotiability of views/plans on childbearing"]), # Translate
            "U_poli": ("F. Political Utility", 4, ["Relative balance of power", "Equal negotiation on important decisions", "Respect for personal will and needs", "Similar vision for life together"]), # Translate
            "U_philo": ("G. Philosophical Utility", 3, ["Alignment of core values and ethics", "Understanding and support for life pursuits", "Feeling closer to one's true self"]), # Translate
            "U_law": ("H. Legal Utility", 2, ["(If applicable) Legal commitment providing security and stability", "Perception of clear and fair rights and obligations"]), # Translate
            "U_comm": ("I. Communication Utility", 4, ["Smooth and effective communication", "Accurate understanding of each other", "Effectively building shared meaning", "Constructive communication for handling disagreements"]), # Translate
            "U_geo": ("J. Geographical Utility", 3, ["Comfort and satisfaction with shared space", "Alignment/negotiability of residential choices/plans", "Building a sense of belonging to a 'place'"]), # Translate
            "U_eco_sys": ("K. Ecological/Systems Theory Utility", 3, ["Relationship as a healthy system that self-repairs and grows", "Significantly more positive than negative interactions", "Relationship stability, predictability, and peace of mind"]) # Translate
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
            self.add_dropdown(parent_frame, f"Expected change in {cat_label.split(' ')[1]} over the next 5 years:", f"{cat_key_prefix}_future", future_options, 2) # Translate

    def populate_cost_tab(self, parent_frame):
        self.add_section_header(parent_frame, "Part 3: Relationship Costs (Costs you incur for the relationship)") # Translate
        future_options = ["Significantly improved", "Slightly improved", "Remained unchanged", "Slightly worsened", "Significantly worsened", "Uncertain"] # Translate options
        cost_categories = {
            "C_psych": ("A. Psychological Costs", 5, ["Emotional depletion", "Conflict of values and expectations", "Hindered or suppressed personal growth", "Negative impact on mental health", "Frustration from unmet important needs"]), # Translate
            "C_econ": ("B. Economic Costs", 3, ["Significant financial pressure", "Giving up career/investment opportunities", "Worry about partner's financial risks"]), # Translate
            "C_socio": ("C. Sociological Costs", 3, ["Estrangement or tension with friends/family", "Negative external pressure", "Discomfort integrating into partner's circle"]), # Translate
            "C_anthro": ("D. Anthropological Costs", 2, ["Discomfort from cultural differences/conflicts", "Sense of loss from giving up cultural identity"]), # Translate
            "C_bio": ("E. Biological/Medical Costs", 3, ["Sexual disharmony/dissatisfaction/pressure", "Unhealthy lifestyle habits impacting health", "Energy spent caring for partner's health"]), # Translate
            "C_poli": ("F. Political Costs", 3, ["Power imbalance and feeling suppressed", "Conflict over 'who is in charge'", "Limited autonomy and personal space"]), # Translate
            "C_philo": ("G. Philosophical Costs", 2, ["Fundamental differences in values and ethics", "Ambiguity/forced change in life meaning/goals"]), # Translate
            "C_law": ("H. Legal Costs", 2, ["Worry about legal/property disputes upon breakup", "Trouble from unclear or unfair rights/obligations"]), # Translate
            "C_comm": ("I. Communication Costs", 2, ["Communication barriers, misunderstandings, ineffectiveness", "Harmful communication patterns"]), # Translate
            "C_geo": ("J. Geographical Costs", 2, ["(If long-distance) Significant long-distance relationship costs", "Dissatisfaction/pressure with living environment/shared space"]), # Translate
            "C_eco_sys": ("K. Ecological/Systems Theory Costs", 3, ["Relationship stuck in negative cycles", "Uncertainty, chaos, fatigue, and unease", "Relationship rigidity and lack of flexibility"]) # Translate
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
            self.add_dropdown(parent_frame, f"Expected change in {cat_label.split(' ')[1]} over the next 5 years:", f"{cat_key_prefix}_future", future_options, 2) # Translate

    def populate_dynamics_tab(self, parent_frame):
        self.add_section_header(parent_frame, "Part 4: Relationship Dynamics and Future Expectations") # Translate
        self.add_section_header(parent_frame, "A. Relationship Risk and Uncertainty") # Translate
        self.add_likert_scale(parent_frame, "How likely is this relationship to face unexpected breakup within the next 5 years?", "Q_risk_breakup", "A.1") # Translate
        self.add_radiobuttons(parent_frame, "Are there recurring and difficult-to-resolve fundamental conflict patterns in the relationship?", "Q_conflict_patterns_exist_A_2", {"Yes":"1", "No":"0"}, "A.2") # Translate
        self.add_likert_scale(parent_frame, "How certain are you about the future direction of this relationship?", "Q_certainty_future", "A.3") # Translate
        self.add_likert_scale(parent_frame, "How confident are you in your partner's long-term loyalty and commitment?", "Q_loyalty_confidence", "A.4") # Translate

        self.add_section_header(parent_frame, "B. Relationship Capital and Learning Adaptation") # Translate
        self.add_likert_scale(parent_frame, "How much 'relationship capital' do you and your partner believe you have jointly accumulated?", "Q_rel_capital", "B.1") # Translate
        self.add_likert_scale(parent_frame, "Do you and your partner regularly invest time and effort to actively maintain and enhance the relationship?", "Q_rel_investment", "B.2") # Translate
        self.add_likert_scale(parent_frame, "When relationship problems or conflicts arise, how is the ability to jointly solve problems and learn/improve?", "Q_adapt_solve", "B.3") # Translate
        self.add_likert_scale(parent_frame, "How is the ability to jointly adapt and cope with significant life changes or external pressures?", "Q_adapt_stress", "B.4") # Translate
        self.add_likert_scale(parent_frame, "Looking back at the relationship history, to what extent have both parties learned from past experiences and improved the relationship?", "Q_adapt_learn_hist", "B.5") # Translate

        self.add_section_header(parent_frame, "C. Expected Relationship Duration") # Translate
        duration_options = ["Several months", "1-2 years", "3-5 years", "5-10 years", "More than 10 years", "Lifelong", "Very uncertain"] # Translate options
        self.add_dropdown(parent_frame, "Ideally, how long do you hope this relationship will last?", "Q_exp_duration_ideal_C_1", duration_options, 5, "C.1") # Translate
        self.add_dropdown(parent_frame, "Realistically, how long is this relationship most likely to last?", "Q_exp_duration_realistic", duration_options, 5, "C.2") # Translate

        self.add_section_header(parent_frame, "D. Perception of External Shocks") # Translate
        self.add_radiobuttons(parent_frame, "Do you foresee any external events likely to significantly impact the relationship within the next 1-3 years?", "Q_external_shock_exist_D_1", {"Yes":"1", "No":"0"}, "D.1") # Translate

    def populate_ocau_tab(self, parent_frame):
        self.add_section_header(parent_frame, "Part 5: Opportunity Costs and Alternatives (OCAU)") # Translate
        single_options = ["Significantly higher", "Slightly higher", "About the same", "Slightly lower", "Significantly lower"] # Translate options
        self.add_dropdown(parent_frame, "If you were single now, would your expected personal life satisfaction be higher or lower than currently?", "Q_single_satisfaction_1", single_options, 2, "1") # Translate
        
        ttk.Label(parent_frame, text="2. Potential benefits of being single (Select multiple, not directly included in the model for now):").pack(anchor='w', padx=5, pady=(5,0)) # Translate
        # ... (checkboxes as before, not stored in self.data_vars for calculation)
        single_benefits = ["More personal freedom and time", "More focus on personal career/academic development", "Avoiding relationship conflicts and emotional depletion", "Opportunity to meet new potential partners", "Greater financial independence"] # Translate
        for benefit in single_benefits:
             cb_var = tk.IntVar()
             cb = ttk.Checkbutton(parent_frame, text=benefit, variable=cb_var)
             cb.pack(anchor='w', padx=15)
        
        ttk.Label(parent_frame, text="3. Potential drawbacks of being single (Select multiple, not directly included in the model for now):").pack(anchor='w', padx=5, pady=(5,0)) # Translate
        single_drawbacks = ["Loneliness", "Lack of emotional support and intimacy", "Potentially higher cost of living", "Lack of help in certain aspects of life", "Social pressure"] # Translate
        for drawback in single_drawbacks:
             cb_var = tk.IntVar()
             cb = ttk.Checkbutton(parent_frame, text=drawback, variable=cb_var)
             cb.pack(anchor='w', padx=15)

        self.add_likert_scale(parent_frame, "Within your current reach, how likely is it to find someone more suitable than your current partner with whom you could build a satisfying relationship?", "Q_alt_partner_likelihood", "4") # Translate
        recovery_options = ["Very soon (within 1-3 months)", "Average (3-6 months)", "Longer (6 months-1 year)", "Very long (more than 1 year)", "Uncertain"] # Translate options
        self.add_dropdown(parent_frame, "If you were to break up with your current partner, how long do you estimate it would take to recover emotionally?", "Q_recovery_time_5", recovery_options, 1, "5") # Translate

    def populate_sunk_cost_tab(self, parent_frame):
        self.add_section_header(parent_frame, "Part 6: Sunk Costs and Decision Tendency") # Translate
        self.add_likert_scale(parent_frame, "How deep is the emotional investment you have made in this relationship?", "Q_sunk_emotion_depth", "2") # Translate
        self.add_likert_scale(parent_frame, "How important are the material/financial resources you have invested in this relationship to you?", "Q_sunk_material_importance", "3") # Translate
        self.add_likert_scale(parent_frame, "To what extent does the thought 'I've invested too much, I shouldn't give up easily' influence your judgment?", "Q_sunk_cost_influence", "4") # Translate
        self.add_likert_scale(parent_frame, "Are you worried that if you break up now, all past investments will be 'wasted'?", "Q_sunk_cost_worry", "5") # Translate

    def populate_weights_tab(self, parent_frame):
        self.add_section_header(parent_frame, "Part 7: Weight Allocation (Personalized Factor Importance)") # Translate
        self.add_section_header(parent_frame, "A. Importance of Relationship Utility Aspects (1=Not important at all, 7=Extremely important)") # Translate
        utility_weight_map = {
            "W_U_psych": "Psychological and emotional satisfaction", "W_U_econ": "Economic and financial stability", "W_U_socio": "Social network and support", # Translate
            "W_U_anthro": "Cultural and value compatibility", "W_U_bio": "Physical attraction and sexual health", "W_U_poli": "Power balance and fair decision-making", # Translate
            "W_U_philo": "Shared meaning and goals in life", "W_U_law": "Security from legal commitment", "W_U_comm": "High-quality communication and understanding", # Translate
            "W_U_geo": "Comfortable shared space and sense of belonging", "W_U_eco_sys": "Relationship system health and stability" # Translate
        }
        for i, (key, text) in enumerate(utility_weight_map.items()): # key is direct key for data_vars
            self.add_likert_scale(parent_frame, text, key.split('_')[0], f"{key.split('_')[-1].upper()}.{i+1}") # Use key directly

        self.add_section_header(parent_frame, "B. Sensitivity to Relationship Cost Aspects (1=High tolerance/Insensitive, 7=Extremely low tolerance/Highly sensitive)") # Translate
        cost_weight_map = {
            "W_C_psych": "Psychological and emotional depletion", "W_C_econ": "Economic and financial burden", "W_C_socio": "Social isolation and external pressure", # Translate
            "W_C_anthro": "Cultural conflict and loss of identity", "W_C_bio": "Impaired physical health and sexual dissatisfaction", "W_C_poli": "Power imbalance and limited autonomy", # Translate
            "W_C_philo": "Value conflict and loss of meaning", "W_C_law": "Potential legal risks and disputes", "W_C_comm": "Communication barriers and negative interactions", # Translate
            "W_C_geo": "Geospatial discomfort and long-distance costs", "W_C_eco_sys": "Relationship system rigidity and chaos" # Translate
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
        self.add_section_header(parent_frame, "Sensitivity Analysis Adjustments") # Translate
        ttk.Label(parent_frame, text="Adjust the parameters below to observe their impact on the final result (Default value is 1.0, indicating no adjustment to the original calculation):").pack(padx=5, pady=5, anchor='w') # Translate
        self.add_sensitivity_slider(parent_frame, "Base Discount Rate Adjustment Factor (r_base Adj.):", "base_discount_rate_adj") # Translate
        self.add_sensitivity_slider(parent_frame, "Future Expectation Optimism Adjustment (Future Optimism Adj.):", "future_projection_optimism_adj") # Translate
        self.add_sensitivity_slider(parent_frame, "Overall Risk Perception Adjustment (Risk Perception Adj.):", "overall_risk_perception_adj") # Translate
        self.add_sensitivity_slider(parent_frame, "Utility/Cost Realization Probability Adjustment (Realization Prob Adj.):", "realization_prob_adj") # Translate

    def populate_results_and_visualization_tab(self, parent_frame):
        # This tab will be split into two main areas: Text results and Visualizations
        # Top part for text results
        self.results_text_widget = tk.Text(parent_frame, wrap=tk.WORD, padx=10, pady=10, height=15, font=("Microsoft YaHei", 10)) # Font name remains as is
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
            ax1.set_title("Initial Utility Composition (Weighted)", fontsize=8) # Translate
        else:
            ax1.text(0.5, 0.5, "No significant utility data", ha='center', va='center', fontsize=8) # Translate
            ax1.set_title("Initial Utility Composition", fontsize=8) # Translate

        ax2 = fig.add_subplot(2, 2, 2)
        cost_data = {k: v for k, v in calculator.initial_cost_breakdown.items() if abs(v) > 1e-3}
        cost_labels = [f"{k} ({v:.1f})" for k,v in cost_data.items()]
        cost_sizes = [abs(v) for v in cost_data.values()]
        if cost_sizes:
            ax2.pie(cost_sizes, labels=cost_labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 6})
            ax2.set_title("Initial Cost Composition (Weighted)", fontsize=8) # Translate
        else:
            ax2.text(0.5, 0.5, "No significant cost data", ha='center', va='center', fontsize=8) # Translate
            ax2.set_title("Initial Cost Composition", fontsize=8) # Translate

        ax3 = fig.add_subplot(2, 2, 3)
        if hasattr(calculator, 'time_periods') and calculator.time_periods:
            ax3.plot(calculator.time_periods, calculator.Net_U_t_series, marker='o', markersize=3, label="Net Utility per Period") # Translate
            ax3.plot(calculator.time_periods, calculator.discounted_Net_U_t_series, marker='x', markersize=3, linestyle='--', label="Discounted Net Utility per Period") # Translate
            ax3.axhline(0, color='grey', lw=0.8, linestyle=':')
            ax3.set_xlabel("Time Period (Years)", fontsize=7) # Translate
            ax3.set_ylabel("Net Utility Value", fontsize=7) # Translate
            ax3.set_title("Expected Net Utility Over Time", fontsize=8) # Translate
            ax3.legend(fontsize=6)
            ax3.tick_params(axis='both', which='major', labelsize=6)
        else:
            ax3.text(0.5, 0.5, "No time series data", ha='center', va='center', fontsize=8) # Translate
            ax3.set_title("Expected Net Utility Over Time", fontsize=8) # Translate

        ax4 = fig.add_subplot(2, 2, 4)
        if hasattr(calculator, 'time_periods') and calculator.time_periods:
            ax4.plot(calculator.time_periods, calculator.cumulative_nrupv_series, marker='o', markersize=3, label="Cumulative NRUPV") # Translate
            ax4.axhline(0, color='grey', lw=0.8, linestyle=':')
            ax4.set_xlabel("Time Period (Years)", fontsize=7) # Translate
            ax4.set_ylabel("Cumulative NRUPV", fontsize=7) # Translate
            ax4.set_title("Cumulative Net Relationship Utility Present Value", fontsize=8) # Translate
            ax4.legend(fontsize=6)
            ax4.tick_params(axis='both', which='major', labelsize=6)
        else:
            ax4.text(0.5, 0.5, "No cumulative data", ha='center', va='center', fontsize=8) # Translate
            ax4.set_title("Cumulative Net Relationship Utility Present Value", fontsize=8) # Translate

        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS'] # Font names remain as is
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
            self.notebook.select(self.tabs["Results and Visualization"]) # Use translated title

        except Exception as e:
            error_message = f"An error occurred during calculation:\n{e}\n\nPlease ensure all relevant fields are filled correctly." # Translate
            if self.results_text_widget:
                self.results_text_widget.insert(tk.END, error_message)
                self.results_text_widget.config(state=tk.DISABLED)
            else: # Fallback if text widget is not yet created or accessible
                messagebox.showerror("Calculation Error", error_message) # Translate
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