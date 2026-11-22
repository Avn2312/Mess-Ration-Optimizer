# Jhelum Mess Ration & Food Waste Forecaster (NIT Srinagar)

* **Location**: Jhelum Hostel Mess, Ground Floor, National Institute of Technology (NIT) Srinagar, Hazratbal, Srinagar, J&K 190006
* **Target Person**: **Shabir Ahmad Dar**, Head Cook & Mess Inventory Supervisor
* **Fieldwork Date**: November 22, 2026
* **Repository**: Public Git Repo for 1-Day Take-Home SDE Assessment

---

## 1. Problem & Context

At the Jhelum Hostel Mess (360 registered students), head cook Shabir Ahmad Dar prepares fixed bulk quotas of food every single day (35 kg dry rice, 28 kg flour, 18 kg dal). However, actual student turnout fluctuates wildly between 180 and 355 students depending on:
1. **The Scheduled Menu**: Peak turnout on Chicken/Paneer nights vs. massive absenteeism on Lauki/Kaddu days.
2. **Calendar Patterns**: Friday afternoon Jumma Namaz dispersal near Hazratbal Shrine and Sunday night street-food outings.
3. **Srinagar Weather**: Sub-5°C cold fog evenings trap students in hostel rooms making Maggi or snacking.

Because running short of food causes immediate student unrest and warden disciplinary complaints, Shabir is incentivized to systematically overcook. As a result, **12 kg to 32 kg of cooked food is thrown into the waste drum twice daily**.

This tool ingests raw daily service logs (`data.csv`) and prints **one authoritative, defensible kitchen slip** at 9:00 AM telling Shabir exactly what multiplier (e.g., `0.47x` or `0.85x`) and dry ingredient weights to issue for the upcoming meal, keeping stockout risk under 1% with an explicit safety margin.

---

## 2. How to Run It

### Requirements
* Python 3.8+ (Uses standard library; no external pip installations strictly required).

### Option A: Command Line Interface (Instant Kitchen Slip)
```bash
# 1. Run for Sunday Dinner with Kaddu/Pumpkin Dal (Low-demand risk scenario)
python3 app.py --day Sunday --meal Dinner --menu "Kaddu / Pumpkin Dal & Roti"

# 2. Run for Friday Lunch with Veg Pulao (Friday prayer dispersal)
python3 app.py --day Friday --meal Lunch --menu "Veg Pulao & Raita"

# 3. Live Defense: Adjust safety buffer from 5% to 15% (for warden review)
python3 app.py --day Wednesday --meal Lunch --menu "Lauki / Bottle Gourd & Dal" --buffer 0.15

# 4. Live Defense: Verify immunity against corrupted/bad data rows
python3 app.py --test-bad-row
```

### Option B: Interactive Web Dashboard (Zero Setup)
```bash
python3 app.py --serve --port 8080
```
Open your browser at `http://localhost:8080` to interact with sliders for the safety buffer and dropdowns for menu items.

---

## 3. Real Output Sample

Running `python3 app.py --day Sunday --meal Dinner --menu "Kaddu / Pumpkin Dal & Roti"`:

```text
=================================================================
  JHELUM HOSTEL MESS — NIT SRINAGAR | KITCHEN ACTION SLIP
  Target User: Shabir Ahmad Dar (Head Cook & Mess In-charge)
=================================================================
 Meal Planned      : Sunday Dinner
 Menu Item         : Kaddu / Pumpkin Dal & Roti (LOW_DEMAND)
 Registered Boys   : 360
 Safety Buffer     : 5.0% (Stockout Guard)
-----------------------------------------------------------------
 >>> EXPECTED TURNOUT      : 162 students
 >>> SAFE COOK HEADCOUNT   : 170 students
 >>> RECOMMENDED MULTIPLIER: 0.47x of standard batch
-----------------------------------------------------------------
 EXACT STORE REQUISITION TO ISSUE THIS MORNING:
  • Rice (Chawal) :  16.5 kg   [Standard: 35.0 kg | Save: 18.5 kg]
  • Atta (Flour)  :  13.2 kg   [Standard: 28.0 kg | Save: 14.8 kg]
  • Dal / Veggies :  8.5 kg   [Standard: 18.0 kg | Save: 9.5 kg]
-----------------------------------------------------------------
 IMPACT: Prevents ~17.7 kg food waste | Saves ~₹1150 on this service
=================================================================
```

---

## 4. What the Tool Gets Wrong (Known Limitations & Flaws)

1. **Sudden Campus Events & Weather Shock**: If Srinagar experiences an unexpected afternoon downpour or snowfall, students cancel plans to eat outside and flood the mess hall. The model cannot detect live weather shifts unless the cook updates the flag.
2. **Exam Week Surge**: During mid-term exam nights, students study late and turn up for dinner en masse between 8:45 PM and 9:15 PM. Historical weekly averages underestimate exam week turnout.
3. **No Individual Appetite Accounting**: The model assumes an average per-capita consumption (~380g cooked weight per student). On cold days, carbohydrate intake per student spikes by 10-15%, which plate-count alone does not capture.
4. **Delayed Feedback Loop**: The model relies on Shabir weighing the scullery waste drum after service. If a kitchen hand neglects to weigh the drum on a busy evening, the dataset suffers gaps.

---

## 5. Walkthrough Video & Commits
* **3-Minute Loom / Screen Recording**: `https://www.youtube.com/watch?v=mock-demo-jhelum-forecaster` *(Replace with your unlisted YouTube/Loom link)*
* **Git Commit History**: At least 5 descriptive commits distributed across the steps.
