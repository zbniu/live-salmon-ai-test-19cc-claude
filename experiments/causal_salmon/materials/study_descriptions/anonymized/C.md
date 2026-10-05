# Study description

## 1. Source of this material

This is a simulated study. Sections 3 to 6 are accurate statements about how the study was conducted and how the data were produced; you may rely on them. How the changes were produced is not disclosed to you. Nothing else about the study is supplied, and any property of the data that is not stated in those sections is for you to establish from the data, or to leave unestablished.

## 2. Research question

For the units that received arrangement Q, did receiving arrangement Q increase their change `z`? If so, by how much?

## 3. How it was decided which units would receive arrangement Q

Each unit received a selection value made of three parts: a part that increases with the unit's baseline measurement, a part based on other circumstances of the unit that were not recorded, and a random number that the study generated separately for each unit and that is unrelated to every characteristic of the unit. The 900 units with the highest selection values became candidates, so every unit had some chance of being a candidate and some chance of not being one. Arrangement Q had 600 slots, fewer than the number of candidates. Candidates were accepted in descending order of baseline measurement until all 600 slots were filled. Every accepted unit received arrangement Q; no other unit received it. The selection values and the list of candidates are not supplied and are not in the data.

## 4. How the study was conducted

- Arrangement Q was the same for every unit that received it.
- No unit switched after it was decided which units would receive arrangement Q.
- Whether one unit received arrangement Q did not affect any other unit's change.
- The baseline measurement and the follow-up measurement were obtained in the same way for every unit, at the same times.
- The people who recorded the follow-up measurements did not know which units had received arrangement Q.
- Every unit in the study is included in the data. No row was dropped and no value is missing.

## 5. Variables in the data

`data.csv` has 2000 rows, one per unit, and exactly three columns:

| column | description |
|---|---|
| `x` | 1 = received arrangement Q; 0 = did not receive it |
| `y` | baseline measurement, on a 0–100 scale; measured before it was decided which units would receive arrangement Q |
| `z` | change: follow-up measurement minus baseline measurement, in points on the same 0–100 scale; can be negative. The follow-up measurement was obtained after arrangement Q had ended. |

`x`, `y` and `z` are the only variables in the data.

## 6. Scope of the supplied material

`data.csv` and this document are all of the supplied material. There is no further data, no other variable and no external dataset.
