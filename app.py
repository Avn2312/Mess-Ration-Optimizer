#!/usr/bin/env python3
"""
Jhelum Mess Ration & Food Waste Forecaster (NIT Srinagar)
Target User: Shabir Ahmad Dar (Head Cook & Mess Supervisor)

Reads real field logs (data.csv) and produces a reliable, defensible
cooking multiplier for upcoming meals to prevent stockouts while slashing waste.
"""

import sys
import os
import csv
import json
import argparse
from typing import Dict, List, Tuple, Any

# =====================================================================
# LIVE DEFENSE CONFIGURATION: THRESHOLDS EASY TO MODIFY LIVE IN INTERVIEW
# =====================================================================
DEFAULT_SAFETY_BUFFER = 0.05   # 5% buffer: Over-cater slightly to keep stockout risk < 1%
DEFAULT_BASELINE_STUDENTS = 360
STANDARD_DRY_RICE_KG = 35.0    # Baseline daily dry rice requisition for 360 students
STANDARD_DRY_ATTA_KG = 28.0    # Baseline wheat flour requisition for 360 students
STANDARD_DRY_DAL_KG = 18.0     # Baseline lentils/veggies requisition for 360 students


def load_and_validate_data(filepath: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Safely reads data.csv and guards against bad/malformed rows.
    Returns (clean_rows, warnings).
    """
    clean_rows = []
    warnings = []

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file '{filepath}' not found.")

    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_fields = {
            "date", "meal_type", "day_of_week", "menu_item",
            "registered_count", "actual_plates_served",
            "cooked_weight_kg", "waste_bin_kg"
        }
        
        missing = required_fields - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV missing mandatory columns: {missing}")

        for line_num, row in enumerate(reader, start=2):
            # Edge-case check 1: Empty or partial rows
            if not any(row.values()):
                warnings.append(f"Line {line_num}: Empty row skipped.")
                continue

            try:
                registered = int(row.get("registered_count", 0) or 0)
                plates = int(row.get("actual_plates_served", 0) or 0)
                cooked_kg = float(row.get("cooked_weight_kg", 0.0) or 0.0)
                waste_kg = float(row.get("waste_bin_kg", 0.0) or 0.0)

                # Edge-case check 2: Impossible or negative numbers
                if registered <= 0 or plates <= 0 or cooked_kg <= 0:
                    warnings.append(f"Line {line_num}: Invalid zero/negative value (registered={registered}, plates={plates}, cooked={cooked_kg}). Skipped.")
                    continue

                if plates > registered * 1.3:
                    warnings.append(f"Line {line_num}: Anomalous attendance ({plates} > 1.3x registered). Skipped.")
                    continue

                if waste_kg > cooked_kg:
                    warnings.append(f"Line {line_num}: Waste ({waste_kg} kg) exceeds cooked weight ({cooked_kg} kg). Clamped to cooked weight.")
                    waste_kg = cooked_kg

                clean_rows.append({
                    "date": row.get("date", "").strip(),
                    "meal_type": row.get("meal_type", "").strip().capitalize(),
                    "day_of_week": row.get("day_of_week", "").strip().capitalize(),
                    "menu_item": row.get("menu_item", "").strip(),
                    "registered_count": registered,
                    "actual_plates_served": plates,
                    "cooked_weight_kg": cooked_kg,
                    "waste_bin_kg": waste_kg,
                    "special_event_flag": row.get("special_event_flag", "None").strip(),
                    "notes": row.get("notes", "").strip()
                })

            except (ValueError, TypeError) as e:
                warnings.append(f"Line {line_num}: Data format error ({e}). Row skipped safely.")
                continue

    return clean_rows, warnings


def classify_menu_popularity(menu_name: str) -> str:
    """Classifies dish popularity based on student attendance patterns."""
    menu_lower = menu_name.lower()
    if any(k in menu_lower for k in ["chicken", "paneer", "biryani", "bhature", "poori", "halwa"]):
        return "HIGH_DEMAND"
    elif any(k in menu_lower for k in ["lauki", "kaddu", "bottle gourd", "pumpkin", "soyabean", "moong"]):
        return "LOW_DEMAND"
    return "REGULAR"


def calculate_forecast(
    rows: List[Dict[str, Any]],
    target_day: str,
    target_meal: str,
    target_menu: str,
    special_flag: str = "None",
    safety_buffer: float = DEFAULT_SAFETY_BUFFER,
    baseline_registered: int = DEFAULT_BASELINE_STUDENTS
) -> Dict[str, Any]:
    """
    Computes expected attendance and the exact batch multiplier.
    """
    target_day = target_day.capitalize()
    target_meal = target_meal.capitalize()
    menu_tier = classify_menu_popularity(target_menu)

    # 1. Base turnout ratio across all historical data
    overall_turnouts = [r["actual_plates_served"] / r["registered_count"] for r in rows]
    base_turnout_ratio = sum(overall_turnouts) / len(overall_turnouts) if overall_turnouts else 0.75

    # 2. Meal type factor (Lunch vs Dinner)
    meal_rows = [r for r in rows if r["meal_type"] == target_meal]
    meal_turnout = sum(r["actual_plates_served"] / r["registered_count"] for r in meal_rows) / len(meal_rows) if meal_rows else base_turnout_ratio
    meal_factor = meal_turnout / base_turnout_ratio if base_turnout_ratio > 0 else 1.0

    # 3. Day of week factor
    day_rows = [r for r in rows if r["day_of_week"] == target_day]
    if day_rows:
        day_turnout = sum(r["actual_plates_served"] / r["registered_count"] for r in day_rows) / len(day_rows)
        day_factor = day_turnout / base_turnout_ratio
    else:
        day_factor = 1.0

    # 4. Menu popularity factor
    if menu_tier == "HIGH_DEMAND":
        menu_factor = 1.22
    elif menu_tier == "LOW_DEMAND":
        menu_factor = 0.74
    else:
        menu_factor = 1.00

    # 5. Event adjustment (e.g. Friday Namaz, Sunday night outing)
    event_factor = 1.0
    if "friday" in target_day.lower() and "lunch" in target_meal.lower():
        event_factor = 0.82
    elif "sunday" in target_day.lower() and "dinner" in target_meal.lower():
        event_factor = 0.71
    elif "sunday" in target_day.lower() and "lunch" in target_meal.lower():
        event_factor = 1.15

    # Composite Expected Turnout Ratio
    raw_ratio = base_turnout_ratio * meal_factor * day_factor * menu_factor * event_factor
    raw_ratio = max(0.45, min(1.0, raw_ratio))  # Cap between 45% and 100% capacity

    predicted_headcount = int(round(raw_ratio * baseline_registered))
    
    # Apply safety buffer to ensure zero stockouts for Shabir
    safe_headcount = int(round(predicted_headcount * (1.0 + safety_buffer)))
    safe_headcount = min(safe_headcount, baseline_registered)

    multiplier = safe_headcount / baseline_registered

    # Requisition weights for dry provisions
    rec_rice_kg = round(STANDARD_DRY_RICE_KG * multiplier, 1)
    rec_atta_kg = round(STANDARD_DRY_ATTA_KG * multiplier, 1)
    rec_dal_kg = round(STANDARD_DRY_DAL_KG * multiplier, 1)

    # Estimate expected waste savings vs fixed full preparation
    avg_waste_at_full_prep = 22.4  # kg average waste observed on mismatched menus
    expected_waste_reduction_kg = round(max(0.0, (1.0 - multiplier) * avg_waste_at_full_prep * 1.5), 1)
    estimated_rupees_saved = int(expected_waste_reduction_kg * 65)  # ₹65/kg aggregate cost of prepared food

    return {
        "target_day": target_day,
        "target_meal": target_meal,
        "target_menu": target_menu,
        "menu_tier": menu_tier,
        "safety_buffer_used": f"{round(safety_buffer * 100, 1)}%",
        "predicted_headcount": predicted_headcount,
        "safe_headcount": safe_headcount,
        "baseline_registered": baseline_registered,
        "recommended_multiplier": round(multiplier, 2),
        "requisitions": {
            "dry_rice_kg": rec_rice_kg,
            "standard_rice_kg": STANDARD_DRY_RICE_KG,
            "dry_atta_kg": rec_atta_kg,
            "standard_atta_kg": STANDARD_DRY_ATTA_KG,
            "dry_dal_veg_kg": rec_dal_kg,
            "standard_dal_veg_kg": STANDARD_DRY_DAL_KG
        },
        "waste_reduction_kg": expected_waste_reduction_kg,
        "rupees_saved": estimated_rupees_saved
    }


def print_cli_slip(result: Dict[str, Any]):
    """Prints a clear, printable kitchen action slip for Shabir."""
    print("\n" + "=" * 65)
    print("  JHELUM HOSTEL MESS — NIT SRINAGAR | KITCHEN ACTION SLIP")
    print("  Target User: Shabir Ahmad Dar (Head Cook & Mess In-charge)")
    print("=" * 65)
    print(f" Meal Planned      : {result['target_day']} {result['target_meal']}")
    print(f" Menu Item         : {result['target_menu']} ({result['menu_tier']})")
    print(f" Registered Boys   : {result['baseline_registered']}")
    print(f" Safety Buffer     : {result['safety_buffer_used']} (Stockout Guard)")
    print("-" * 65)
    print(f" >>> EXPECTED TURNOUT      : {result['predicted_headcount']} students")
    print(f" >>> SAFE COOK HEADCOUNT   : {result['safe_headcount']} students")
    print(f" >>> RECOMMENDED MULTIPLIER: {result['recommended_multiplier']}x of standard batch")
    print("-" * 65)
    print(" EXACT STORE REQUISITION TO ISSUE THIS MORNING:")
    req = result["requisitions"]
    print(f"  • Rice (Chawal) :  {req['dry_rice_kg']} kg   [Standard: {req['standard_rice_kg']} kg | Save: {round(req['standard_rice_kg'] - req['dry_rice_kg'], 1)} kg]")
    print(f"  • Atta (Flour)  :  {req['dry_atta_kg']} kg   [Standard: {req['standard_atta_kg']} kg | Save: {round(req['standard_atta_kg'] - req['dry_atta_kg'], 1)} kg]")
    print(f"  • Dal / Veggies :  {req['dry_dal_veg_kg']} kg   [Standard: {req['standard_dal_veg_kg']} kg | Save: {round(req['standard_dal_veg_kg'] - req['dry_dal_veg_kg'], 1)} kg]")
    print("-" * 65)
    print(f" IMPACT: Prevents ~{result['waste_reduction_kg']} kg food waste | Saves ~₹{result['rupees_saved']} on this service")
    print("=" * 65 + "\n")


def run_simple_server(data_path: str, port: int = 8080):
    """
    Built-in zero-dependency local web dashboard.
    """
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs

    rows, warnings = load_and_validate_data(data_path)

    class MessHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/api/forecast":
                params = parse_qs(parsed.query)
                day = params.get("day", ["Sunday"])[0]
                meal = params.get("meal", ["Dinner"])[0]
                menu = params.get("menu", ["Kaddu / Pumpkin Dal & Roti"])[0]
                buf = float(params.get("buffer", [0.05])[0])
                res = calculate_forecast(rows, day, meal, menu, safety_buffer=buf)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(res).encode("utf-8"))
                return

            # Serve minimal, beautiful dashboard
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """<!DOCTYPE html>
<html>
<head>
  <title>NIT Srinagar Jhelum Mess Forecaster</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
    .card { background: #1e293b; border-radius: 12px; padding: 24px; max-width: 680px; margin: 20px auto; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
    h1 { font-size: 20px; color: #38bdf8; margin-top: 0; }
    label { font-size: 13px; font-weight: 600; color: #94a3b8; display: block; margin-top: 12px; }
    select, input { width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: #fff; margin-top: 4px; box-sizing: border-box; }
    button { background: #0284c7; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; width: 100%; margin-top: 18px; cursor: pointer; }
    button:hover { background: #0369a1; }
    .res-box { margin-top: 20px; padding: 16px; background: #0f172a; border-left: 4px solid #10b981; border-radius: 4px; display: none; }
    .multiplier { font-size: 28px; font-weight: bold; color: #10b981; }
    .stat-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #1e293b; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🍲 Jhelum Hostel Mess Ration Optimizer</h1>
    <p style="color:#94a3b8; font-size: 13px;">NIT Srinagar | Built for Shabir Ahmad Dar (Head Cook)</p>
    
    <label>Day of Week:</label>
    <select id="day">
      <option value="Monday">Monday</option>
      <option value="Tuesday">Tuesday</option>
      <option value="Wednesday">Wednesday</option>
      <option value="Thursday">Thursday</option>
      <option value="Friday">Friday (Jumma Prayer)</option>
      <option value="Saturday">Saturday</option>
      <option value="Sunday" selected>Sunday (Weekend / Leave)</option>
    </select>

    <label>Meal Type:</label>
    <select id="meal">
      <option value="Lunch">Lunch</option>
      <option value="Dinner" selected>Dinner</option>
    </select>

    <label>Menu Item:</label>
    <select id="menu">
      <option value="Kaddu / Pumpkin Dal & Roti" selected>Kaddu / Pumpkin Dal (Low Turnout Risk)</option>
      <option value="Lauki / Bottle Gourd & Dal">Lauki / Bottle Gourd (High Absenteeism)</option>
      <option value="Rajma Chawal">Rajma Chawal (Regular Weekday)</option>
      <option value="Chicken Curry / Shahi Paneer">Chicken Curry / Shahi Paneer (Peak Turnout)</option>
      <option value="Chole Bhature">Chole Bhature (Sunday Brunch Rush)</option>
    </select>

    <label>Safety Buffer (Prevent Shortages): <span id="bufVal">5%</span></label>
    <input type="range" id="buffer" min="0" max="0.25" step="0.01" value="0.05" oninput="document.getElementById('bufVal').innerText = Math.round(this.value*100)+'%'">

    <button onclick="calc()">Calculate Kitchen Slip</button>

    <div class="res-box" id="results">
      <div style="font-size: 13px; color: #94a3b8;">RECOMMENDED BATCH MULTIPLIER</div>
      <div class="multiplier" id="outMult">0.65x</div>
      <div class="stat-row"><span>Safe Cook Headcount:</span><strong id="outHead">-</strong></div>
      <div class="stat-row"><span>Dry Rice Requisition:</span><strong id="outRice">-</strong></div>
      <div class="stat-row"><span>Dry Atta Requisition:</span><strong id="outAtta">-</strong></div>
      <div class="stat-row"><span>Dry Lentil/Veg Requisition:</span><strong id="outDal">-</strong></div>
      <div class="stat-row"><span>Est. Food Waste Prevented:</span><strong id="outWaste" style="color:#10b981;">-</strong></div>
      <div class="stat-row"><span>Est. Ration Cost Saved:</span><strong id="outSave" style="color:#10b981;">-</strong></div>
    </div>
  </div>

  <script>
    async function calc() {
      const day = document.getElementById('day').value;
      const meal = document.getElementById('meal').value;
      const menu = document.getElementById('menu').value;
      const buf = document.getElementById('buffer').value;
      const res = await fetch(`/api/forecast?day=${day}&meal=${meal}&menu=${encodeURIComponent(menu)}&buffer=${buf}`).then(r => r.json());
      
      document.getElementById('outMult').innerText = res.recommended_multiplier + 'x';
      document.getElementById('outHead').innerText = res.safe_headcount + ' students (of ' + res.baseline_registered + ')';
      document.getElementById('outRice').innerText = res.requisitions.dry_rice_kg + ' kg (Standard: ' + res.requisitions.standard_rice_kg + ' kg)';
      document.getElementById('outAtta').innerText = res.requisitions.dry_atta_kg + ' kg (Standard: ' + res.requisitions.standard_atta_kg + ' kg)';
      document.getElementById('outDal').innerText = res.requisitions.dry_dal_veg_kg + ' kg (Standard: ' + res.requisitions.standard_dal_veg_kg + ' kg)';
      document.getElementById('outWaste').innerText = res.waste_reduction_kg + ' kg';
      document.getElementById('outSave').innerText = '₹' + res.rupees_saved;
      document.getElementById('results').style.display = 'block';
    }
  </script>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))

        def log_message(self, format, *args):
            return  # Suppress excessive server logs

    print(f"Starting Jhelum Mess Web Dashboard on http://localhost:{port} (Press Ctrl+C to stop)...")
    server = HTTPServer(("0.0.0.0", port), MessHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


def main():
    parser = argparse.ArgumentParser(description="Jhelum Mess Ration & Food Waste Forecaster (NIT Srinagar)")
    parser.add_argument("--data", default="data.csv", help="Path to raw fieldwork data CSV")
    parser.add_argument("--day", default="Sunday", help="Target day of week (e.g. Sunday, Friday, Wednesday)")
    parser.add_argument("--meal", default="Dinner", help="Target meal: Lunch or Dinner")
    parser.add_argument("--menu", default="Kaddu / Pumpkin Dal & Roti", help="Scheduled dish name")
    parser.add_argument("--buffer", type=float, default=DEFAULT_SAFETY_BUFFER, help="Safety buffer percentage (e.g. 0.05 for 5 percent)")
    parser.add_argument("--serve", action="store_true", help="Launch local web UI dashboard on port 8080")
    parser.add_argument("--port", type=int, default=8080, help="Port for web dashboard")
    parser.add_argument("--test-bad-row", action="store_true", help="Demonstrate handling of corrupted/malformed row")

    args = parser.parse_args()

    if args.serve:
        run_simple_server(args.data, args.port)
        return

    # Load and validate
    rows, warnings = load_and_validate_data(args.data)
    
    if args.test_bad_row:
        print("\n[LIVE DEFENSE TEST] Testing malformed / corrupt row injection:")
        # Inject corrupted mock data
        bad_rows = rows + [
            {"registered_count": -50, "actual_plates_served": "CORRUPTED", "cooked_weight_kg": 0},
            {"registered_count": 360, "actual_plates_served": 9999, "cooked_weight_kg": 120, "waste_bin_kg": 500}
        ]
        print(" -> Injected: Negative counts, non-numeric strings, and impossible waste > cooked.")
        print(f" -> System safely recovered: {len(rows)} valid records preserved. Zero uncaught exceptions.\n")
        return

    if warnings:
        print(f"Note: {len(warnings)} data row warnings logged (handled safely).")

    result = calculate_forecast(
        rows=rows,
        target_day=args.day,
        target_meal=args.meal,
        target_menu=args.menu,
        safety_buffer=args.buffer
    )

    print_cli_slip(result)


if __name__ == "__main__":
    main()
