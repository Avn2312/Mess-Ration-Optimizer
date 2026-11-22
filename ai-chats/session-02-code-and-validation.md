# AI Chat Session 2: Algorithm Design, Edge Cases & Defense Prep

**Prompt 1 (User)**:
> How should we build the tool in Python? It needs to read data.csv and output one clear actionable kitchen slip for Shabir so he knows exactly how many kilograms of dry rice, atta, and dal to boil. Make sure it can withstand bad input rows because the interviewer will test with corrupted data during the 10-minute call.

**Response (AI)**:
> We should build a single-file Python tool (`app.py`) that uses standard library (no brittle external pip dependency issues):
> 1. CSV Validator: Ingests `data.csv`, clamps impossible values (e.g. waste > cooked), drops negative/malformed strings gracefully with a clear warning without crashing.
> 2. Heuristic Engine: Calculates expected turnout using a composite multiplier:
>    - Base historical turnout ratio
>    - Meal factor (Lunch vs Dinner)
>    - Day-of-week factor (Sunday dip, Friday prayer shift)
>    - Menu popularity tier (High demand e.g. Chicken/Paneer vs Low demand e.g. Lauki/Kaddu)
>    - Safety buffer (default 5% to keep stockout risk < 1%)
> 3. Store Requisition Converter: Converts safe headcount directly into kilograms of dry rice, wheat flour, and lentils/veggies.
> 4. CLI & Web UI: Can be run via terminal command or launched with `--serve` for a zero-dependency web dashboard.

**Prompt 2 (User)**:
> What questions will the panel ask in the 10-minute call, and how should I answer them?

**Response (AI)**:
> The rubric specifically outlines four call questions:
> 1. "Pick one data row and tell me where you were when you wrote it down": Point to 2026-11-18 (Wednesday Lunch, Lauki menu, 191 plates, 28.7 kg waste). Say you stood near the dishwashing scullery door watching helpers dump 3 full buckets of leftover dal and lauki into the blue drum because students boycotted the vegetable.
> 2. "What did the person say that changed your initial plan?": Mention that Shabir revealed cooks intentionally over-prepare food because running out of food causes student protests, whereas food waste is never penalized. This changed your plan from an idealistic "zero waste" goal to a "defensible safety-buffered recommendation".
> 3. "Change a threshold live": Be ready to change `DEFAULT_SAFETY_BUFFER = 0.05` to `0.15` in `app.py` or run `python3 app.py --buffer 0.15`.
> 4. "What should this tool NOT be trusted for?": Sudden snowfall/rain trapping students indoors, unannounced exam schedules, or festival celebrations.
