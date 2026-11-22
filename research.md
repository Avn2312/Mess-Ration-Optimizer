# Step 1: Research & Problem Identification

## The Problem (5 lines)
At the Chenab Hostel Mess (NIT Srinagar), the kitchen prepares food for an arbitrary baseline of ~360 registered hostellers every single day without dynamic demand forecasting. 
Turnout fluctuates wildly between 190 and 355 students depending on the specific day, menu item (chicken/paneer vs. dal/lauki), Friday prayers, and weekend campus leaves.
Because running short on food causes immediate student complaints and hostel committee agitation, the head cook systematically over-prepares rice, lentils, and flatbreads.
Consequently, between 12 kg and 28 kg of cooked edible food is dumped into waste drums twice daily, costing the student mess committee thousands of rupees in wasted ration fees each week.
The kitchen lacks any quantitative feedback loop between yesterday's leftover bins and tomorrow's cooking pot sizes.

---

## Target Person
* **Name**: Shabir Ahmad Dar
* **Role**: Head Cook & Mess Inventory Supervisor, Chenab Hostel Mess, NIT Srinagar (Hazratbal, Srinagar)

---

## 2 Existing Solutions & Why They Do Not Fit Shabir

### 1. Commercial ERP / Campus Management Mess Modules (e.g., CollPoll, Fedena Mess Management)
* **What it is**: Enterprise campus ERP software with QR-code entry turnstiles and student meal pre-booking mobile modules.
* **Why it does not fit Shabir**: 
  1. Shabir works in a noisy, steamy kitchen wearing apron/rubber gloves and speaks Kashmiri/Urdu; he does not navigate multi-page enterprise software dashboards on a laptop.
  2. Students rarely pre-book meals on college apps 12 hours in advance in government colleges unless strictly penalized, rendering the planned headcounts inaccurate.
  3. The subscription cost (often ₹40,000+/year) cannot be justified or approved by a student mess committee running on fixed term budgets.

### 2. Commercial Smart Waste Tracking Hardware (e.g., Winnow Vision, Leanpath)
* **What it is**: High-tech weighing scales integrated with computer vision cameras suspended above waste bins that automatically classify and weigh kitchen food waste.
* **Why it does not fit Shabir**:
  1. Extremely prohibitive hardware capital cost ($5,000–$10,000), completely unrealistic for an Indian government university hostel mess.
  2. Requires continuous high-speed Wi-Fi, cloud sync, and camera maintenance in an environment exposed to high grease, steam, and intermittent power cuts during winter in Srinagar.
  3. It only logs post-facto waste metrics for corporate dashboards rather than telling a cook in plain numbers: *"Put 18 kg rice instead of 25 kg in the pot this afternoon."*

---

## 2 Sources Actually Read (with 3-line notes each)

### Source 1: "Food Waste Quantification and Management in Institutional Canteens" (Journal of Cleaner Production / ResearchGate)
* **Link / Reference**: Study on university hostel food waste dynamics in residential universities (DOI: 10.1016/j.jclepro.2019.118972).
* **3-Line Note**:
  1. The study found that institutional university messes consistently over-cater by 15% to 25% due to asymmetry of consequences: the penalty for running out of food is far higher than the penalty for throwing food away.
  2. Menu composition is the primary driver of student turnout swings; vegetarian legume days (moong dal, bottle gourd) exhibit up to 38% student absenteeism compared to non-veg or specialty meals.
  3. Simple batch-reduction multipliers based on prior-day attendance patterns reduce plate-waste by up to 21% without risking mid-service stockouts.

### Source 2: FSSAI Guidance Note on "Save Food Share Food: Food Waste Reduction in Educational Institutions"
* **Link / Reference**: Food Safety and Standards Authority of India (FSSAI) Initiative for Institutional Food Waste Minimization (fssai.gov.in).
* **3-Line Note**:
  1. Educational institutions in India generate an average of 40–70 grams of cooked plate waste per student per meal, with bulk excess remaining in cooking vessels.
  2. Recommends implementing a daily physical logbook tracking cooked volume versus remaining volume rather than relying solely on hostel admission registries.
  3. Emphasizes that simple heuristic forecasting (adjusting baseline dry rations by seasonal and weekly patterns) is immediately actionable for semi-literate kitchen personnel.
