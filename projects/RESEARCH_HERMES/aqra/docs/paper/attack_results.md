# Cheating-Generator Attack Suite (M2)

All-null world (20 reps). Any certification = false discovery.
Cells: mean false certifications (rate of >=1 false cert).

| Defense | Attacker | m=25 | m=50 | m=100 | m=200 | m=400 |
|---|---|---|---|---|---|---|
| naive | hillclimb | 4.10 (95%) | 15.25 (100%) | 37.70 (100%) | 93.90 (100%) | 215.90 (100%) |
| naive | random | 1.65 (75%) | 1.90 (85%) | 4.75 (100%) | 10.75 (100%) | 17.55 (100%) |
| no_wall | hillclimb | 1.25 (15%) | 1.95 (40%) | 6.25 (65%) | 16.00 (75%) | 74.50 (80%) |
| no_wall | random | 0.25 (15%) | 0.00 (0%) | 0.05 (5%) | 0.15 (15%) | 0.05 (5%) |
| metered | hillclimb | 0.25 (15%) | 0.85 (35%) | 0.75 (30%) | 0.65 (15%) | 1.50 (25%) |
| metered | random | 0.00 (0%) | 0.05 (5%) | 0.05 (5%) | 0.00 (0%) | 0.00 (0%) |
| protocol | hillclimb | 0.00 (0%) | 0.05 (5%) | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) |
| protocol | random | 0.05 (5%) | 0.05 (5%) | 0.10 (10%) | 0.00 (0%) | 0.00 (0%) |
