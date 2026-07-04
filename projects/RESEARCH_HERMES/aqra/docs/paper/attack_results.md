# Cheating-Generator Attack Suite (M2)

All-null world (20 reps). Any certification = false discovery.
Cells: mean false certifications (rate of >=1 false cert).

| Defense | Attacker | m=25 | m=50 | m=100 | m=200 | m=400 |
|---|---|---|---|---|---|---|
| naive | hillclimb | 6.15 (100%) | 14.55 (100%) | 37.55 (100%) | 89.95 (100%) | 216.80 (100%) |
| naive | random | 2.00 (80%) | 2.35 (90%) | 5.90 (100%) | 11.95 (100%) | 17.40 (100%) |
| no_wall | hillclimb | 0.95 (25%) | 2.40 (35%) | 9.00 (75%) | 20.50 (55%) | 79.90 (80%) |
| no_wall | random | 0.05 (5%) | 0.10 (10%) | 0.15 (15%) | 0.05 (5%) | 0.05 (5%) |
| protocol | hillclimb | 0.00 (0%) | 0.25 (5%) | 0.00 (0%) | 0.00 (0%) | 0.05 (5%) |
| protocol | random | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) |
