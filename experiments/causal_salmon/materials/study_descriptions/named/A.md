# Study description

## 1. Source of this material

This is a simulated study. Sections 3 to 6 are accurate statements about how the study was conducted and how the data were produced; you may rely on them. How the score gains were produced is not disclosed to you. Nothing else about the study is supplied, and any property of the data that is not stated in those sections is for you to establish from the data, or to leave unestablished.

## 2. Research question

For the students who attended the tutoring class, did attending the tutoring class increase their score gain `z`? If so, by how much?

## 3. How it was decided which students would attend the tutoring class

Exactly 600 of the 2000 students were selected to attend the tutoring class by a random draw in which every student had the same chance of being selected. The draw used no information about the students. Every selected student attended the tutoring class; no other student attended it.

## 4. How the study was conducted

- The tutoring class was the same for every student who attended it.
- No student switched after it was decided which students would attend the tutoring class.
- Whether one student attended the tutoring class did not affect any other student's score gain.
- The start-of-term test score and the end-of-term test score were obtained in the same way for every student, at the same times.
- The people who recorded the end-of-term test scores did not know which students had attended the tutoring class.
- Every student in the study is included in the data. No row was dropped and no value is missing.

## 5. Variables in the data

`data.csv` has 2000 rows, one per student, and exactly three columns:

| column | description |
|---|---|
| `x` | 1 = attended the tutoring class; 0 = did not attend it |
| `y` | start-of-term test score, on a 0–100 scale; measured before it was decided which students would attend the tutoring class |
| `z` | score gain: end-of-term test score minus start-of-term test score, in points on the same 0–100 scale; can be negative. The end-of-term test score was obtained after the tutoring class had ended. |

`x`, `y` and `z` are the only variables in the data.

## 6. Scope of the supplied material

`data.csv` and this document are all of the supplied material. There is no further data, no other variable and no external dataset.
