# Cheating-Generator Attack Suite (M2)

All-null world (20 reps). Any certification = false discovery.
Cells: mean false certifications (rate of >=1 false cert).

| Defense | Attacker | m=25 | m=50 | m=100 | m=200 | m=400 |
|---|---|---|---|---|---|---|
| naive | hillclimb | 4.35 (90%) | 15.15 (100%) | 33.70 (100%) | 98.55 (100%) | 216.90 (100%) |
| naive | random | 1.25 (75%) | 2.80 (95%) | 5.10 (95%) | 10.35 (100%) | 20.25 (100%) |
| no_wall | hillclimb | 3.25 (55%) | 1.90 (25%) | 4.05 (50%) | 21.35 (75%) | 68.00 (75%) |
| no_wall | random | 0.10 (10%) | 0.10 (10%) | 0.10 (10%) | 0.00 (0%) | 0.00 (0%) |
| metered | hillclimb | 0.30 (15%) | 1.15 (30%) | 0.20 (10%) | 0.20 (10%) | 2.15 (30%) |
| metered | random | 0.00 (0%) | 0.00 (0%) | 0.05 (5%) | 0.05 (5%) | 0.00 (0%) |
| protocol | hillclimb | 0.10 (5%) | 0.10 (5%) | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) |
| protocol | random | 0.10 (5%) | 0.00 (0%) | 0.30 (25%) | 0.15 (15%) | 0.00 (0%) |
| conformal | hillclimb | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) |
| conformal | random | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) | 0.00 (0%) |
