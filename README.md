# 🚢 Constraint Satisfaction Problem: Battleship Solitaire Solver

## 📖 Overview
This project implements a solver for Battleship Solitaire puzzles using **Constraint Satisfaction Problem (CSP)** techniques. Battleship Solitaire is a logic puzzle where you must deduce the location of ships on a grid based on given constraints.

Play Battleship Solitaire online [here](https://lukerissacher.com/battleships).

---

## 🎮 Game Rules

### 🛠️ Ship Types:
- **Submarine (1x1)**: S
- **Destroyer (1x2)**: `<` for left, `>` for right
- **Cruiser (1x3)**: `<`, `M` (middle), `>`
- **Battleship (1x4)**: `<`, `M`, `M`, `>`
- **Carrier (1x5)**: `<`, `M`, `M`, `M`, `>`

### 🔄 Constraints:
1. **Row Constraints:** Number of ship parts in each row is indicated.
2. **Column Constraints:** Number of ship parts in each column is indicated.
3. **Ship Constraints:** The puzzle specifies the number of each type of ship.
4. **No Adjacent Ships:** Ships cannot touch each other, even diagonally.
5. **Hints:** Some cells may provide hints (`S`, `<`, `M`, `>`, `^`, `v`, or water `.`).

![image](https://github.com/user-attachments/assets/fc71b785-99f1-47fc-b2a3-afa0824c6ad3)


## 💼 Features

### 🎯 Your Tasks:
- Encode the problem as a **Constraint Satisfaction Problem (CSP)**.
- Implement:
  - **Backtracking Search**
  - **Forward Checking**
  - **AC-3 Arc Consistency**
  - Any additional optimizations you choose.

---

## 🚀 How to Run

### Prerequisites
- **Python 3**: Ensure Python 3 is installed.

### Commands
To solve a Battleship puzzle:
```bash
python3 battle.py --inputfile <input file> --outputfile <output file>
```
![image](https://github.com/user-attachments/assets/13617935-900b-41cb-9f84-514fb9c31591)

## 🧩 Input & Output Format

### Input:
Row Constraints: Line 1 specifies the number of ship parts per row.
Column Constraints: Line 2 specifies the number of ship parts per column.
Ship Counts: Line 3 specifies the number of ships of each type (submarine, destroyer, cruiser, battleship, carrier).
Grid: Remaining lines represent the grid with hints (0 for empty, S for submarine, . for water, etc.).

Example Input:
211222
140212
32100
000000
0000S0
000000
000000
00000.
000000

### Output:
The grid with all ships placed correctly, adhering to constraints.
No 0 values remain in the solution.

Example Output:
<>....
....S.
.^....
.M...S
.v.^..
...v.S
