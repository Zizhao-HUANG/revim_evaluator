import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import math

# --- Global N/A String ---
NA_STRING = "Not Applicable / Not Considered"

# --- Full Questionnaire Structure ---
QUESTIONNAIRE_STRUCTURE_FULL = {
    "A": {
        "title": "Basic Information and Overall Feelings",
        "questions": {
            "A1": {"text": "Current relationship duration (e.g., 2 years 3 months):", "type": "text"},
            "A2": {"text": "Living situation with partner:", "type": "combo", "options": ["Cohabiting", "Living Separately (Same City)", "Long Distance"]},
            "A3": {"text": "Overall, how happy are you with your current relationship (1=Very Unhappy, 10=Very Happy):", "type": "scale", "range": (1, 10)},
            "A4_1": {"text": "How likely do you think this relationship is to continue in the next year (1=Completely Unlikely, 10=Extremely Likely):", "type": "scale", "range": (1, 10)},
            "A4_5": {"text": "How likely do you think this relationship is to continue in the next five years (1=Completely Unlikely, 10=Extremely Likely):", "type": "scale", "range": (1, 10)},
            "A5": {"text": "If this relationship were to end today, how would you rate your best alternative? (1=Much Worse than current, 5=About the Same, 10=Much Better than current):", "type": "scale", "range": (1, 10)},
        }
    },
    "B": { # Psychology
        "title": "Psychological Factors",
        "questions": {
            "B1.1": {"text": "This relationship generally makes me feel happy and satisfied.", "type": "scale", "range": (1, 7)},
            "B1.2": {"text": "I often feel stressed, anxious, or sad directly because of this relationship.", "type": "scale", "range": (1, 7), "is_cost": True},
            "B1.3": {"text": "This relationship meets my core emotional needs (e.g., love, belonging, emotional support).", "type": "scale", "range": (1, 7)},
            "B1.4": {"text": "I feel that my partner genuinely cares about my emotional well-being.", "type": "scale", "range": (1, 7)},
            "B1.5": {"text": "This relationship contributes positively to my overall mental health.", "type": "scale", "range": (1, 7)},
            "B2.1": {"text": "My partner's and my personalities are generally compatible.", "type": "scale", "range": (1, 7)},
            "B2.2": {"text": "We have a similar sense of humor.", "type": "scale", "range": (1, 7)},
            "B2.3": {"text": "Fundamental personality differences between us cause significant friction.", "type": "scale", "range": (1, 7), "is_cost": True},
            "B3.1": {"text": "I feel secure and confident in my partner's love and commitment.", "type": "scale", "range": (1, 7)},
            "B3.2": {"text": "I worry that my partner might leave me or lose interest.", "type": "scale", "range": (1, 7), "is_cost": True},
            "B3.3": {"text": "I feel that my partner is consistently there for me and responsive to my needs.", "type": "scale", "range": (1, 7)},
            "B4.1": {"text": "This relationship supports my personal growth and development.", "type": "scale", "range": (1, 7)},
            "B4.2": {"text": "I feel like I have become a better person because of this relationship.", "type": "scale", "range": (1, 7)},
            "B4.3": {"text": "I sometimes feel I have to suppress parts of myself to maintain this relationship.", "type": "scale", "range": (1, 7), "is_cost": True},
        }
    },
    "C": { # Economics
        "title": "Economic Factors",
        "questions": {
            "C1.1": {"text": "My partner and I have similar views on money management (spending, saving, investing).", "type": "scale", "range": (1, 7)},
            "C1.2": {"text": "We are able to discuss financial matters openly and effectively.", "type": "scale", "range": (1, 7)},
            "C1.3": {"text": "Financial disagreements are a major source of conflict in our relationship.", "type": "scale", "range": (1, 7), "is_cost": True},
            "C1.4": {"text": "I feel secure about our shared financial future.", "type": "scale", "range": (1, 7)},
            "C2.1": {"text": "I feel the division of financial responsibilities in our relationship is fair.", "type": "scale", "range": (1, 7)},
            "C2.2": {"text": "I feel the division of household labor and other non-financial contributions in our relationship is fair.", "type": "scale", "range": (1, 7)},
            "C2.3": {"text": "I feel my partner contributes his/her fair share to the relationship (financially, emotionally, practically).", "type": "scale", "range": (1, 7)},
            "C3.1": {"text": "I have invested significant time and emotional energy into this relationship that would be difficult to abandon.", "type": "scale", "range": (1, 7)}, # I_0 component
            "C3.2": {"text": "Our lives are deeply intertwined (e.g., shared property, children, joint ventures), making separation costly and complex.", "type": "scale", "range": (1, 7)}, # I_0 component
            "C3.3": {"text": "I believe this relationship enhances my overall economic prospects or stability.", "type": "scale", "range": (1, 7)},
            "C3.4": {"text": "I sometimes feel this relationship hinders me from pursuing personal or professional opportunities.", "type": "scale", "range": (1, 7), "is_cost": True},
        }
    },
    "D": { # Sociology
        "title": "Sociological Factors",
        "questions": {
            "D1.1": {"text": "My friends and family generally approve of and get along well with my partner.", "type": "scale", "range": (1, 7)},
            "D1.2": {"text": "I feel comfortable and accepted within my partner's social circle (friends and family).", "type": "scale", "range": (1, 7)},
            "D1.3": {"text": "Our shared social network provides strong support for our relationship.", "type": "scale", "range": (1, 7)},
            "D1.4": {"text": "Interactions between my social circle and my partner's social circle are often a source of stress or conflict.", "type": "scale", "range": (1, 7), "is_cost": True},
            "D2.1": {"text": "Our relationship aligns with the socio-cultural expectations of our community/families.", "type": "scale", "range": (1, 7)},
            "D2.2": {"text": "I feel pressure from society or family regarding the progression or status of our relationship (e.g., marriage, children).", "type": "scale", "range": (1, 7), "is_cost": True},
            "D3.1": {"text": "This relationship has expanded my social connections in a positive way.", "type": "scale", "range": (1, 7)},
            "D3.2": {"text": "My partner's social connections have been beneficial to me (e.g., professionally, opportunities).", "type": "scale", "range": (1, 7)},
        }
    },
    "E": { # Anthropology
        "title": "Anthropological Factors",
        "questions": {
            "E1.1": {"text": "My partner and I share similar core cultural values and beliefs.", "type": "scale", "range": (1, 7)},
            "E1.2": {"text": "Differences in our cultural backgrounds (e.g., ethnicity, religion, upbringing) are a source of richness rather than conflict.", "type": "scale", "range": (1, 7)},
            "E1.3": {"text": "We are able to effectively navigate any cultural differences that arise.", "type": "scale", "range": (1, 7)},
            "E2.1": {"text": "We have meaningful shared rituals or traditions (e.g., ways of celebrating holidays, anniversaries, daily habits) that strengthen our bond.", "type": "scale", "range": (1, 7)},
            "E2.2": {"text": "These shared rituals are important to me.", "type": "scale", "range": (1, 7)},
            "E3.1": {"text": "The structures and interaction patterns of our respective families are generally compatible.", "type": "scale", "range": (1, 7)},
            "E3.2": {"text": "I feel optimistic about the prospect of further integration with my partner's extended family (if applicable).", "type": "scale", "range": (1, 7)},
        }
    },
    "F": { # Biology/Medicine
        "title": "Biological/Medical Factors",
        "questions": {
            "F1.1": {"text": "My partner and I are compatible in our health habits (e.g., diet, exercise, substance use).", "type": "scale", "range": (1, 7)},
            "F1.2": {"text": "My partner supports me in maintaining a healthy lifestyle, and I support him/her.", "type": "scale", "range": (1, 7)},
            "F1.3": {"text": "I am concerned about my partner's health habits or choices.", "type": "scale", "range": (1, 7), "is_cost": True},
            "F1.4": {"text": "If one of us faced a serious health issue, I am confident we would effectively support each other.", "type": "scale", "range": (1, 7)},
            "F2.1": {"text": "I am still physically attracted to my partner.", "type": "scale", "range": (1, 7)},
            "F2.2": {"text": "I am satisfied with the level and quality of physical intimacy in our relationship.", "type": "scale", "range": (1, 7)},
            "F2.3": {"text": "We are able to communicate openly and effectively about sexual needs and desires.", "type": "scale", "range": (1, 7)},
            "F3.1": {"text": "Are my partner and I aligned on matters of procreation (timing, number of children, parenting philosophy)?", "type": "radio_na", "options": ["Very Consistent", "Fairly Consistent", "Neutral/Uncertain", "Some Disagreement", "Serious Disagreement", NA_STRING]},
            "F3.2": {"text": "How confident are you in your partner as a potential co-parent?", "type": "radio_na", "options": ["Very Confident", "Fairly Confident", "Neutral/Uncertain", "Some Concern", "Very Concerned", NA_STRING]},
        }
    },
    "G": { # Political Science
        "title": "Political Science Factors",
        "questions": {
            "G1.1": {"text": "I feel that power and decision-making in the relationship are shared fairly.", "type": "scale", "range": (1, 7)},
            "G1.2": {"text": "My opinions and preferences are given equal weight in important relationship decisions.", "type": "scale", "range": (1, 7)},
            "G1.3": {"text": "I sometimes feel controlled or dominated by my partner.", "type": "scale", "range": (1, 7), "is_cost": True},
            "G2.1": {"text": "We are able to resolve conflicts effectively and constructively.", "type": "scale", "range": (1, 7)},
            "G2.2": {"text": "When we disagree, we can usually reach a compromise that satisfies both of us.", "type": "scale", "range": (1, 7)},
            "G2.3": {"text": "Conflicts often escalate or remain unresolved.", "type": "scale", "range": (1, 7), "is_cost": True},
            "G3.1": {"text": "We have a shared vision for the future of our relationship.", "type": "scale", "range": (1, 7)},
            "G3.2": {"text": "My personal autonomy (personal space, alone time, independent pursuits) is respected in this relationship.", "type": "scale", "range": (1, 7)},
        }
    },
    "H": { # Philosophy
        "title": "Philosophical Factors",
        "questions": {
            "H1.1": {"text": "My partner and I share similar core ethical and moral values.", "type": "scale", "range": (1, 7)},
            "H1.2": {"text": "In most important life situations, we agree on what is right and wrong.", "type": "scale", "range": (1, 7)},
            "H1.3": {"text": "I have serious concerns about my partner's ethical behavior or moral standards.", "type": "scale", "range": (1, 7), "is_cost": True},
            "H2.1": {"text": "This relationship contributes to my sense of meaning and purpose in life.", "type": "scale", "range": (1, 7)},
            "H2.2": {"text": "My partner supports me in pursuing my personal life goals and ambitions.", "type": "scale", "range": (1, 7)},
            "H2.3": {"text": "We have some shared long-term life goals or ambitions.", "type": "scale", "range": (1, 7)},
            "H3.1": {"text": "I am able to be my authentic self in this relationship.", "type": "scale", "range": (1, 7)},
        }
    },
    "I": { # Legal/Quasi-Legal
        "title": "Legal/Quasi-Legal Factors",
        "questions": {
            "I1.1": {"text": "I am fully committed to this relationship.", "type": "scale", "range": (1, 7)},
            "I1.2": {"text": "I believe my partner is fully committed to this relationship.", "type": "scale", "range": (1, 7)},
            "I1.3": {"text": "I fully trust my partner.", "type": "scale", "range": (1, 7)},
            "I2.1": {"text": "The unwritten rules and expectations in our relationship feel fair and balanced.", "type": "scale", "range": (1, 7)},
            "I2.2": {"text": "My partner consistently meets my expectations of them in this relationship (and vice versa).", "type": "scale", "range": (1, 7)},
            "I3.1": {"text": "I feel secure about the long-term future of this relationship.", "type": "scale", "range": (1, 7)},
            "I3.2": {"text": "Have we openly discussed our long-term intentions for this relationship (e.g., marriage, cohabitation)?", "type": "radio_na", "options": ["Fully Discussed and Aligned", "Discussed but Disagreements Exist", "Discussed but No Clear Conclusion Yet", "Never Seriously Discussed", NA_STRING]},
        }
    },
    "J": { # Communication
        "title": "Communication Factors",
        "questions": {
            "J1.1": {"text": "We are able to communicate openly and honestly about important matters.", "type": "scale", "range": (1, 7)},
            "J1.2": {"text": "When I express myself, I feel heard and understood by my partner.", "type": "scale", "range": (1, 7)},
            "J1.3": {"text": "My partner is a good listener.", "type": "scale", "range": (1, 7)},
            "J1.4": {"text": "We are good at expressing affection and appreciation for each other.", "type": "scale", "range": (1, 7)},
            "J2.1": {"text": "Our communication often involves criticism, defensiveness, or blaming.", "type": "scale", "range": (1, 7), "is_cost": True},
            "J2.2": {"text": "We are able to give and receive constructive feedback without major issues.", "type": "scale", "range": (1, 7)},
            "J2.3": {"text": "We are good at understanding each other's non-verbal cues (e.g., body language, tone).", "type": "scale", "range": (1, 7)},
        }
    },
    "K": { # History
        "title": "Historical Factors",
        "questions": {
            "K1.1": {"text": "We have a rich history of positive shared experiences.", "type": "scale", "range": (1, 7)},
            "K1.2": {"text": "Looking back on our relationship, good memories far outweigh the bad ones.", "type": "scale", "range": (1, 7)},
            "K1.3": {"text": "We have successfully navigated difficult challenges together in the past.", "type": "scale", "range": (1, 7)},
            "K2.1": {"text": "We have learned and grown from past conflicts or mistakes in the relationship.", "type": "scale", "range": (1, 7)},
            "K2.2": {"text": "I see us repeating the same negative patterns of interaction over and over.", "type": "scale", "range": (1, 7), "is_cost": True},
        }
    },
    "L": { # Geography
        "title": "Geographical Factors",
        "questions": {
            "L1.1": {"text": "(If cohabiting) How do I feel about our shared living space and how it is managed?", "type": "radio_na", "options": ["Very Comfortable/Satisfied", "Fairly Comfortable/Satisfied", "Neutral", "Somewhat Uncomfortable/Dissatisfied", "Very Uncomfortable/Dissatisfied", NA_STRING]},
            "L1.2": {"text": "Does our current geographical location serve both of our needs well (career, family, lifestyle)?", "type": "scale", "range": (1, 7)}, # High score is good
            "L2.1": {"text": "(If long distance or frequent travel) How stressful is the physical distance between us on the relationship?", "type": "radio_na", "options": ["No Impact At All", "Minor, Manageable Impact", "Some Impact", "Significant Impact, Causes Stress", "Very Significant Impact, Difficult to Maintain", NA_STRING]}, # "No Impact At All" is best (less cost)
            "L2.2": {"text": "How effectively do we manage periods of separation?", "type": "radio_na", "options": ["Managed Very Well", "Managed Fairly Well", "Average", "Managed Not So Well", "Managed Very Poorly", NA_STRING]}, # "Managed Very Well" is best
        }
    },
    "M": { # Ecology
        "title": "Ecological Factors",
        "questions": {
            "M1.1": {"text": "Our relationship feels resilient; we can bounce back from setbacks.", "type": "scale", "range": (1, 7)},
            "M1.2": {"text": "Our relationship adapts well to changes in our lives or external circumstances.", "type": "scale", "range": (1, 7)},
            "M2.1": {"text": "This relationship generally gives me more energy than it drains.", "type": "scale", "range": (1, 7)},
            "M2.2": {"text": "I feel the giving and receiving of support in our relationship is healthy and balanced.", "type": "scale", "range": (1, 7)},
            "M3.1": {"text": "Our interdependence feels healthy and mutually beneficial, not co-dependent or one-sided.", "type": "scale", "range": (1, 7)},
        }
    },
    "N": { # Information Theory/Systems Theory
        "title": "Information Theory/Systems Theory Factors",
        "questions": {
            "N1.1": {"text": "There is a comfortable level of predictability and routine in our relationship.", "type": "scale", "range": (1, 7)},
            "N1.2": {"text": "Our relationship often feels chaotic or unstable.", "type": "scale", "range": (1, 7), "is_cost": True},
            "N2.1": {"text": "Our relationship system is open to new information and able to adapt (e.g., trying new approaches if old ones don't work).", "type": "scale", "range": (1, 7)},
            "N2.2": {"text": "We are generally good at recognizing when things aren't working and making changes.", "type": "scale", "range": (1, 7)},
            "N3.1": {"text": "Our relationship is generally resilient to negative external influences.", "type": "scale", "range": (1, 7)},
            "N3.2": {"text": "We are good at incorporating positive external input when beneficial (e.g., advice from trusted friends, therapy if needed).", "type": "scale", "range": (1, 7)},
        }
    },
    "O": {
        "title": "Future Expectations and Discount Rate Proxy",
        "questions": {
            "O1": {"text": "Looking ahead, I am optimistic about this relationship.", "type": "scale", "range": (1, 7)},
            "O2": {"text": "I expect the benefits from this relationship to increase or remain high over time.", "type": "scale", "range": (1, 7)},
            "O3": {"text": "I expect the costs or difficulties of this relationship to decrease or remain manageable over time.", "type": "scale", "range": (1, 7)},
            "O4": {"text": "When making important life decisions, I tend to prioritize long-term benefits over immediate gratification.", "type": "scale", "range": (1, 7)},
            "O5": {"text": "Thinking about committing several more years to a relationship like this makes me feel: (1=Daunted, 7=Excited)", "type": "scale", "range": (1, 7)},
        }
    },
    "WEIGHTS": {
        "title": "Importance Weight Allocation for Factors",
        "questions": {
            "W_B_Psych": {"text": "Importance of Psychological Factors:", "type": "scale", "range": (1, 5)},
            "W_C_Econ": {"text": "Importance of Economic Factors:", "type": "scale", "range": (1, 5)},
            "W_D_Soc": {"text": "Importance of Sociological Factors:", "type": "scale", "range": (1, 5)},
            "W_E_Anth": {"text": "Importance of Anthropological Factors:", "type": "scale", "range": (1, 5)},
            "W_F_BioMed": {"text": "Importance of Biological/Medical Factors:", "type": "scale", "range": (1, 5)},
            "W_G_PolSci": {"text": "Importance of Political Science Factors:", "type": "scale", "range": (1, 5)},
            "W_H_Phil": {"text": "Importance of Philosophical Factors:", "type": "scale", "range": (1, 5)},
            "W_I_Law": {"text": "Importance of Legal/Quasi-Legal Factors:", "type": "scale", "range": (1, 5)},
            "W_J_Comm": {"text": "Importance of Communication Factors:", "type": "scale", "range": (1, 5)},
            "W_K_Hist": {"text": "Importance of Historical Factors:", "type": "scale", "range": (1, 5)},
            "W_L_Geo": {"text": "Importance of Geographical Factors:", "type": "scale", "range": (1, 5)},
            "W_M_Eco": {"text": "Importance of Ecological Factors:", "type": "scale", "range": (1, 5)},
            "W_N_InfoSys": {"text": "Importance of Information Theory/Systems Theory Factors:", "type": "scale", "range": (1, 5)},
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
                self._log(f"  Processing '{q_text_short}': Empty value, defaulting to neutral value {float(score_str):.1f}")
            else:
                self._log(f"  Processing '{q_text_short}': Empty value, treated as N/A.")
                return 0, True
        
        # Ensure score_str is a string before further processing, especially for scale values from .get()
        score_str = str(score_str)

        if q_def["type"] == "radio_na":
            if score_str == NA_STRING:
                self._log(f"  Processing '{q_text_short}': Selected {NA_STRING}, treated as N/A.")
                return 0, True
            try:
                options_no_na = [opt for opt in q_def["options"] if opt != NA_STRING]
                num_options = len(options_no_na)
                if num_options == 0: return 0, True 
                idx = options_no_na.index(score_str) 
                if num_options == 1: transformed = 0 
                else: transformed = 1 - (2 * idx / (num_options - 1))
                self._log(f"  Processing '{q_text_short}': Option '{score_str}' (idx {idx}/{num_options-1}), Transformed: {transformed:.2f}")
                return transformed, False
            except ValueError:
                self._log(f"  Warning: '{q_text_short}': Could not parse radio_na option '{score_str}', treated as N/A.")
                return 0, True
        if q_def["type"] == "scale":
            try:
                score = float(score_str)
                low, high = q_def["range"]
                neutral = (low + high) / 2.0
                max_deviation = high - neutral
                if max_deviation == 0: return 0, False
                transformed = (score - neutral) / max_deviation
                self._log(f"  Processing '{q_text_short}': Raw value {score:.1f}, Transformed: {transformed:.2f}")
                return transformed, False
            except ValueError:
                self._log(f"  Warning: '{q_text_short}': Could not parse scale value '{score_str}', treated as N/A.")
                return 0, True
        self._log(f"  Processing '{q_text_short}': Type {q_def['type']}, value '{score_str}', treated as N/A.")
        return 0, True

    def calculate_rvcum(self):
        self.detailed_log = [] 
        self._log("--- Starting RVCUM Calculation ---")
        try:
            batna_q_def = self.q_struct["A"]["questions"]["A5"]
            batna_score_raw = float(self.responses["A"]["A5"])
            batna_transformed_score = self._transform_score(str(batna_score_raw), batna_q_def)[0]
            self._log(f"Raw BATNA score (A5): {batna_score_raw}, Transformed (normalized -1 to 1): {batna_transformed_score:.2f}")

            o4_q_def = self.q_struct["O"]["questions"]["O4"]
            o4_val_raw = float(self.responses["O"]["O4"])
            r_min, r_max = 0.03, 0.15
            discount_rate = r_max - (((o4_val_raw - o4_q_def["range"][0]) / (o4_q_def["range"][1] - o4_q_def["range"][0])) * (r_max - r_min))
            discount_rate = max(0.01, min(discount_rate, 0.20))
            self._log(f"Discount Rate Proxy (O4): {o4_val_raw}, Calculated Discount Rate r: {discount_rate:.4f}")

            o1_optimism = self._transform_score(str(self.responses["O"]["O1"]), self.q_struct["O"]["questions"]["O1"])[0]
            o2_benefits_growth = self._transform_score(str(self.responses["O"]["O2"]), self.q_struct["O"]["questions"]["O2"])[0]
            o3_costs_reduction = self._transform_score(str(self.responses["O"]["O3"]), self.q_struct["O"]["questions"]["O3"])[0]
            self._log(f"Future Expectations: Optimism={o1_optimism:.2f}, Benefit Growth={o2_benefits_growth:.2f}, Cost Reduction={o3_costs_reduction:.2f} (all in -1 to 1 range)")

            utility_annual_growth_factor = 1.0 + (o1_optimism * 0.025) + (o2_benefits_growth * 0.025)
            cost_annual_change_factor = 1.0 - (o1_optimism * 0.015) - (o3_costs_reduction * 0.025) 
            utility_annual_growth_factor = max(0.90, min(utility_annual_growth_factor, 1.10))
            cost_annual_change_factor = max(0.90, min(cost_annual_change_factor, 1.10))
            self._log(f"Annual Utility Growth Factor: {utility_annual_growth_factor:.3f}, Annual Cost Change Factor: {cost_annual_change_factor:.3f}")
        except Exception as e:
            self._log(f"Error: Failed to extract key parameters - {e}")
            import traceback; self._log(traceback.format_exc())
            return {"error": f"Failed to extract key parameters: {e}"}

        i0_value_normalized_sum = 0 
        num_i0_components = 0
        i0_question_specs = [{"q_id": "C3.1", "section_id": "C"}, {"q_id": "C3.2", "section_id": "C"}]
        self._log("\n--- Calculating Initial Investment / Switching Costs (I_0) ---")
        for spec in i0_question_specs:
            q_key, section_id = spec["q_id"], spec["section_id"]
            if section_id not in self.responses or q_key not in self.responses[section_id]:
                self._log(f"  Warning: In I_0 calculation, question {section_id}.{q_key} not found in responses, skipping.")
                continue
            q_def = self.q_struct[section_id]["questions"][q_key]
            raw_score_str = str(self.responses[section_id].get(q_key, ""))
            transformed_score, is_na = self._transform_score(raw_score_str, q_def)
            if not is_na:
                i0_value_normalized_sum += (transformed_score + 1) / 2 
                num_i0_components +=1
        avg_i0_normalized = i0_value_normalized_sum / num_i0_components if num_i0_components > 0 else 0
        scaled_i0_value = avg_i0_normalized * 15 
        self._log(f"  Calculated Initial Investment / Switching Costs (I_0) Value (added to relationship NPV): {scaled_i0_value:.2f} (based on {num_i0_components} questions)")

        current_period_total_utility_weighted = 0
        current_period_total_cost_weighted = 0
        weights = {}
        total_weight_sum = 0
        self._log("\n--- Calculating Discipline Weights ---")
        for w_key, w_data_def in self.q_struct["WEIGHTS"]["questions"].items():
            try:
                weight_val_raw = float(self.responses["WEIGHTS"].get(w_key, 0)) # Use .get with default 0
                weights[w_key] = weight_val_raw
                total_weight_sum += weight_val_raw
                self._log(f"  Weight {w_key} ({w_data_def['text']}): {weight_val_raw:.1f}")
            except ValueError: self._log(f"  Warning: Weight {w_key} is invalid, setting to 0."); weights[w_key] = 0
        if total_weight_sum > 0:
            for w_key in weights: weights[w_key] /= total_weight_sum
        else: 
             num_disciplines = len(weights)
             default_weight = 1.0 / num_disciplines if num_disciplines > 0 else 0
             for w_key in weights: weights[w_key] = default_weight
             self._log(f"  All weights are 0, using average weight: {default_weight:.3f}")
        self._log(f"  Normalized Discipline Weights: { {k: f'{v:.3f}' for k,v in weights.items()} }")

        discipline_scores = {}
        self._log("\n--- Calculating Current Period Contribution per Discipline ---")
        for section_id in "BCDEFGHIJKLMN": 
            if section_id not in self.q_struct: continue
            section_data_def = self.q_struct[section_id]
            self._log(f"\n  Processing Discipline: {section_data_def['title']} ({section_id})")
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
            self._log(f"    Discipline {section_id} Summary: Avg Utility Score={avg_section_utility_transformed:.2f} (from {num_valid_utility_q} questions), Avg Cost Score={avg_section_cost_transformed:.2f} (from {num_valid_cost_q} questions)")
            self._log(f"    Discipline {section_id} Net Score (Utility-Cost, range approx -2 to +2): {net_section_score_transformed:.2f}")
            weight_key_map = {'B': 'W_B_Psych', 'C': 'W_C_Econ', 'D': 'W_D_Soc', 'E': 'W_E_Anth', 'F': 'W_F_BioMed', 'G': 'W_G_PolSci', 'H': 'W_H_Phil', 'I': 'W_I_Law', 'J': 'W_J_Comm', 'K': 'W_K_Hist', 'L': 'W_L_Geo', 'M': 'W_M_Eco', 'N': 'W_N_InfoSys'}
            actual_weight_key = weight_key_map.get(section_id)
            section_weight = weights.get(actual_weight_key, 0) if actual_weight_key else 0
            SCALING_FACTOR_FOR_UTILITY_UNITS = 5 
            scaled_net_contribution = net_section_score_transformed * SCALING_FACTOR_FOR_UTILITY_UNITS
            if scaled_net_contribution > 0: current_period_total_utility_weighted += scaled_net_contribution * section_weight
            else: current_period_total_cost_weighted += (-scaled_net_contribution) * section_weight
            self._log(f"    Discipline {section_id} Weighted Contribution (scaled): Utility += {(scaled_net_contribution * section_weight) if scaled_net_contribution > 0 else 0:.2f}, Cost += {(-scaled_net_contribution * section_weight) if scaled_net_contribution < 0 else 0:.2f} (Weight {section_weight:.3f})")

        self._log("\n--- Calculating Interaction Terms ---")
        interaction_utility_bonus, interaction_cost_reduction = 0, 0
        comm_score, conflict_res_score = discipline_scores.get('J', 0), discipline_scores.get('G', 0)
        if comm_score > 0.2 and conflict_res_score > 0.2:
            j_weight, g_weight = weights.get(weight_key_map['J'],0), weights.get(weight_key_map['G'],0)
            avg_interaction_weight = (j_weight + g_weight) / 2
            bonus = comm_score * conflict_res_score * SCALING_FACTOR_FOR_UTILITY_UNITS * 0.25 * avg_interaction_weight
            interaction_utility_bonus += bonus
            self._log(f"  Interaction Term (J & G): Communication({comm_score:.2f}) * Conflict Resolution({conflict_res_score:.2f}) -> Additional Utility: +{bonus:.2f}")
        cultural_score = discipline_scores.get('E', 0)
        if comm_score > 0.2 and cultural_score < -0.2:
            e_weight = weights.get(weight_key_map['E'],0)
            original_cost_from_E = (-cultural_score) * e_weight * SCALING_FACTOR_FOR_UTILITY_UNITS
            mitigation_factor = comm_score * 0.3 
            reduction = original_cost_from_E * mitigation_factor
            interaction_cost_reduction += reduction
            self._log(f"  Interaction Term (J & E): Communication({comm_score:.2f}) mitigates Cultural Conflict({cultural_score:.2f}) -> Cost Reduction: -{reduction:.2f}")
        current_period_total_utility_weighted += interaction_utility_bonus
        current_period_total_cost_weighted -= interaction_cost_reduction
        current_period_total_cost_weighted = max(0, current_period_total_cost_weighted)
        self._log(f"\nCurrent Period Total (Weighted and Interaction Adjusted): Raw Utility Flow={current_period_total_utility_weighted:.2f}, Raw Cost Flow={current_period_total_cost_weighted:.2f}")

        npv_relationship = 0
        projected_period_utility, projected_period_cost = current_period_total_utility_weighted, current_period_total_cost_weighted
        self._log("\n--- NPV Calculation (Year by Year) ---")
        self._log("Year | Expected Utility | Expected Cost | Net Utility | Discount Factor | Discounted Net Utility")
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
            self._log(f"{t_year+1:2d} | {current_year_utility:16.2f} | {current_year_cost:13.2f} | {net_period_utility:11.2f} | {discount_factor:15.4f} | {discounted_net_period_utility:20.2f}")
        self._log(f"--- NPV (Relationship itself, without I_0): {npv_relationship:.2f} ---")
        npv_relationship_final = npv_relationship + scaled_i0_value
        self._log(f"NPV (Relationship itself, with I_0={scaled_i0_value:.2f}): {npv_relationship_final:.2f}")

        base_for_batna_npv = npv_relationship 
        batna_difference_percentage = 0.25 
        min_abs_batna_difference_value = (SCALING_FACTOR_FOR_UTILITY_UNITS * TIME_HORIZON_YEARS * 0.1)
        adjustment_value = 0
        if abs(base_for_batna_npv) > 1e-6 : adjustment_value = abs(base_for_batna_npv) * batna_difference_percentage * batna_transformed_score
        else: adjustment_value = min_abs_batna_difference_value * batna_transformed_score
        if batna_transformed_score > 0 and adjustment_value < min_abs_batna_difference_value * batna_transformed_score : adjustment_value = min_abs_batna_difference_value * batna_transformed_score
        elif batna_transformed_score < 0 and adjustment_value > min_abs_batna_difference_value * batna_transformed_score : adjustment_value = min_abs_batna_difference_value * batna_transformed_score
        npv_batna_r = base_for_batna_npv + adjustment_value
        self._log(f"NPV (Best Alternative BATNA-R): {npv_batna_r:.2f} (based on current relationship NPV(without I_0)={base_for_batna_npv:.2f} and BATNA score adjustment)")

        decision = "Worth Continuing" if npv_relationship_final > npv_batna_r else "May Not Be Worth Continuing, Please Consider Carefully"
        self._log(f"\nFinal Decision Recommendation: {decision}")
        return {"npv_relationship": npv_relationship_final, "npv_batna_r": npv_batna_r, "decision": decision, "discount_rate": discount_rate, "i0_value": scaled_i0_value, "current_period_utility_calc": current_period_total_utility_weighted, "current_period_cost_calc": current_period_total_cost_weighted, "detailed_log": self.detailed_log}

# --- GUI Application Class ---
class RVCUMAppGUI:
    def __init__(self, master, q_struct_with_vars): # Pass structure with initialized vars
        self.master = master
        master.title("Relationship Value Assessment Model (RVCUM) - Advanced v3")
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
        filemenu.add_command(label="Save Answers", command=self.save_answers)
        filemenu.add_command(label="Load Answers", command=self.load_answers)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=master.quit)
        menubar.add_cascade(label="File", menu=filemenu)
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
        self.prev_button = ttk.Button(self.nav_frame, text="Previous", command=self._prev_section)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.next_button = ttk.Button(self.nav_frame, text="Next", command=self._next_section)
        self.next_button.pack(side=tk.LEFT, padx=5)
        self.calculate_button = ttk.Button(self.nav_frame, text="Finish and Evaluate", command=self._collect_and_calculate)
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
                messagebox.showerror("Input Error", f"Weight '{self.q_struct['WEIGHTS']['questions'][q_key]['text']}' is not a valid number. Please go back and correct it.")
                for i, key in enumerate(self.section_keys_ordered):
                    if key == "WEIGHTS": self.notebook.select(i); break
                return
        calculator = RVCUMCalculator(all_responses, self.q_struct)
        results = calculator.calculate_rvcum()
        if "error" in results: messagebox.showerror("Calculation Error", results["error"]); return
        result_window = tk.Toplevel(self.master)
        result_window.title("RVCUM Assessment Results")
        result_window.geometry("750x600")
        text_area_frame = ttk.Frame(result_window)
        text_area_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_area = tk.Text(text_area_frame, wrap=tk.WORD, padx=10, pady=10, font=("Arial", 10))
        v_scroll = ttk.Scrollbar(text_area_frame, orient=tk.VERTICAL, command=text_area.yview)
        text_area.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        summary = f"--- Relationship Assessment Summary ---\n\n"
        summary += f"Estimated NPV of Current Relationship: {results['npv_relationship']:.2f}\n"
        summary += f"  (Including Switching Cost Benefit I_0: {results['i0_value']:.2f})\n"
        summary += f"Estimated NPV of Best Alternative (BATNA-R): {results['npv_batna_r']:.2f}\n"
        summary += f"Annual Discount Rate Used: {results['discount_rate']*100:.1f}%\n"
        summary += f"Estimated Total Utility Flow (Weighted and Interaction Adjusted) for Current Period: {results['current_period_utility_calc']:.2f}\n"
        summary += f"Estimated Total Cost Flow (Weighted and Interaction Adjusted) for Current Period: {results['current_period_cost_calc']:.2f}\n\n"
        summary += f"Conclusion: {results['decision']}\n\n"
        summary += "Important Note: This model is based on your subjective assessment and a series of economic assumptions. The results are for reference only. Please combine them with your actual feelings and other real-world factors to make your final decision.\n\n"
        summary += "--- Detailed Calculation Log ---\n"
        text_area.insert(tk.END, summary)
        for log_entry in results.get("detailed_log", []): text_area.insert(tk.END, log_entry + "\n")
        text_area.config(state=tk.DISABLED)

    def save_answers(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")], title="Save Answers")
        if not filepath: return
        responses_to_save = self._get_all_responses()
        try:
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(responses_to_save, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Success", "Answers saved successfully!")
        except Exception as e: messagebox.showerror("Error", f"Save failed: {e}")

    def load_answers(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")], title="Load Answers")
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
                # Re-create widgets to ensure they reflect loaded values
                for widget in self.frames[key].winfo_children(): widget.destroy()
                self._create_section_widgets(self.frames[key], key)
            self.notebook.select(current_tab_idx) 
            messagebox.showinfo("Success", "Answers loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Load failed: {e}")
            import traceback; print(traceback.format_exc())

# --- Main Application Execution ---
if __name__ == "__main__":
    root = tk.Tk() # Create the root window FIRST

    # Initialize Tkinter variables for the full structure AFTER root is created
    # This loop ensures every question definition has a 'var' attribute holding a Tkinter variable
    for section_key_init, section_data_init in QUESTIONNAIRE_STRUCTURE_FULL.items():
        for q_key_init, q_data_init in section_data_init["questions"].items():
            # Always create a new Tkinter variable here, associated with the root window
            if q_data_init["type"] == "scale":
                q_data_init["var"] = tk.DoubleVar(master=root)
            else: # Covers text, combo, radio_na, and weights (which are scales but treated slightly differently in GUI)
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