# Cheating-Generator Attack Suite (M2)

All-null world (20 reps). Any certification = false discovery.
Cells: mean false certifications (rate of >=1 false cert).

| Defense | Attacker | m=25 | m=50 | m=100 | m=200 | m=400 |
|---|---|---|---|---|---|---|
| naive | hillclimb | 4.95 (90%) | 13.55 (100%) | 36.80 (100%) | 86.05 (100%) | 211.40 (100%) |
| naive | random | 1.20 (50%) | 2.45 (95%) | 5.80 (100%) | 10.05 (100%) | 17.90 (100%) |
| no_wall | hillclimb | 1.40 (35%) | 4.05 (35%) | 5.40 (30%) | 24.10 (60%) | 43.85 (70%) |
| no_wall | random | 0.10 (5%) | 0.05 (5%) | 0.10 (10%) | 0.05 (5%) | 0.00 (0%) |
| metered | hillclimb | 0.75 (35%) | 0.40 (15%) | 0.80 (35%) | 0.90 (25%) | 2.50 (25%) |
| metered | random | 0.10 (10%) | 0.10 (10%) | 0.10 (5%) | 0.20 (5%) | 0.05 (5%) |
| protocol | hillclimb | 0.05 (5%) | 0.00 (0%) | 0.15 (10%) | 0.10 (5%) | 0.00 (0%) |
| protocol | random | 0.10 (10%) | 0.00 (0%) | 0.00 (0%) | 0.05 (5%) | 0.00 (0%) |
| conformal | hillclimb | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) |
| conformal | random | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) |
| online_by | hillclimb | 0.10 (5%) | 0.40 (15%) | 0.00 (0%) | 0.10 (10%) | 0.00 (0%) |
| online_by | random | 0.00 (0%) | 0.15 (15%) | 0.10 (10%) | 0.05 (5%) | 0.00 (0%) |
| online_lond | hillclimb | 0.25 (20%) | 0.25 (15%) | 0.05 (5%) | 0.15 (15%) | 0.45 (30%) |
| online_lond | random | 0.25 (25%) | 0.10 (10%) | 0.25 (20%) | 0.10 (10%) | 0.10 (10%) |
