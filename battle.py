from csp import Constraint, Variable, CSP
from constraints import *
from backtracking import bt_search
import argparse


def parse_input(file_path):
  """Parse the input file and return the board and size."""
  with open(file_path, 'r') as file:
    b = file.read()
  b2 = b.split()
  size = len(b2[0]) + 2  # Account for padding
  b3 = []
  b3 += ['0' + b2[0] + '0']  # Row constraints
  b3 += ['0' + b2[1] + '0']  # Column constraints
  b3 += [b2[2] + ('0' if len(b2[2]) == 3 else '')]  # Ship constraints
  b3 += ['0' * size]  # Top padding
  for i in range(3, len(b2)):
    b3 += ['0' + b2[i] + '0']
  b3 += ['0' * size]  # Bottom padding
  return "\n".join(b3), size


def verify_solution(grid, board):
  """Verify that the solution meets row and column constraints."""
  board_rows = board.split()
  row_constraints = [int(x) for x in board_rows[0][1:-1]]  # Remove padding
  col_constraints = [int(x) for x in board_rows[1][1:-1]]  # Remove padding

  grid_rows = grid.strip().split('\n')

  # Verify row constraints
  for i, row in enumerate(grid_rows):
    row_sum = sum(int(x) for x in row)
    if row_sum != row_constraints[i]:
      print(f"Row {i} sum {row_sum} does not match constraint {row_constraints[i]}")
      return False

  # Verify column constraints
  for j in range(len(grid_rows[0])):
    col_sum = sum(int(row[j]) for row in grid_rows)
    if col_sum != col_constraints[j]:
      print(f"Column {j} sum {col_sum} does not match constraint {col_constraints[j]}")
      return False

  return True

def count_ships(grid):
  """Count the number of ships of each type in the grid."""
  grid_rows = grid.strip().split('\n')
  height = len(grid_rows)
  width = len(grid_rows[0])
  visited = [[False for _ in range(width)] for _ in range(height)]

  ship_counts = {
    "submarines": 0,  # 1x1
    "destroyers": 0,  # 1x2
    "cruisers": 0,    # 1x3
    "battleships": 0, # 1x4
    "carriers": 0     # 1x5
  }

  def dfs(x, y):
    """Perform DFS to find the size of a ship."""
    stack = [(x, y)]
    size = 0

    while stack:
      cx, cy = stack.pop()
      if 0 <= cx < height and 0 <= cy < width and not visited[cx][cy] and grid_rows[cx][cy] != '.':
        visited[cx][cy] = True
        size += 1
        stack.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])  # Explore neighbors

    return size

  # Count ships
  for i in range(height):
    for j in range(width):
      if not visited[i][j] and grid_rows[i][j] != '.':
        size = dfs(i, j)
        if size == 1:
          ship_counts["submarines"] += 1
        elif size == 2:
          ship_counts["destroyers"] += 1
        elif size == 3:
          ship_counts["cruisers"] += 1
        elif size == 4:
          ship_counts["battleships"] += 1
        elif size == 5:
          ship_counts["carriers"] += 1

  return ship_counts


def verify_ship_constraints(grid, ship_constraints):
  """Verify that the solution meets the ship count constraints."""
  ship_counts = count_ships(grid)

  # Compare the counts with the constraints
  expected_counts = {
    "submarines": ship_constraints[0],
    "destroyers": ship_constraints[1],
    "cruisers": ship_constraints[2],
    "battleships": ship_constraints[3],
    "carriers": ship_constraints[4]
  }

  for ship_type, count in expected_counts.items():
    if ship_counts[ship_type] != count:
      print(f"{ship_type.capitalize()} count {ship_counts[ship_type]} does not match constraint {count}.")
      return False

  return True


def convert_to_ship_grid(grid):
  """Convert 01 grid to ship symbol grid."""
  grid_rows = grid.strip().split('\n')
  height = len(grid_rows)
  width = len(grid_rows[0])
  result = [['.'] * width for _ in range(height)]

  for i in range(height):
    for j in range(width):
      if grid_rows[i][j] == '1':
        vertical = horizontal = False
        if i > 0 and grid_rows[i-1][j] == '1':
          vertical = True
        if i < height-1 and grid_rows[i+1][j] == '1':
          vertical = True
        if j > 0 and grid_rows[i][j-1] == '1':
          horizontal = True
        if j < width-1 and grid_rows[i][j+1] == '1':
          horizontal = True

        if not vertical and not horizontal:
          result[i][j] = 'S'  # Single cell ship
        elif vertical:
          if i == 0 or grid_rows[i-1][j] == '0':
            result[i][j] = '^'  # Top
          elif i == height-1 or grid_rows[i+1][j] == '0':
            result[i][j] = 'v'  # Bottom
          else:
            result[i][j] = 'M'  # Middle
        elif horizontal:
          if j == 0 or grid_rows[i][j-1] == '0':
            result[i][j] = '<'  # Left
          elif j == width-1 or grid_rows[i][j+1] == '0':
            result[i][j] = '>'  # Right
          else:
            result[i][j] = '='  # Middle

  return '\n'.join(''.join(row) for row in result)


def format_solution(solution, size):
  """Format the solution as a grid of 0s and 1s."""
  s_ = {int(var.name()): val for (var, val) in solution}
  rows = []
  for i in range(1, size-1):
    row = ''.join(str(s_[-1-(i*size+j)]) for j in range(1, size-1))
    rows.append(row)
  return '\n'.join(rows)


def main():
  inputf = str(input("Enter file name: "))
  input_f = "input_" + inputf + ".txt"
  output_f = "output" + input_f[5:]
  file = open(input_f, 'r')
  b = file.read()
  b2 = b.split()
  size = len(b2[0])
  size = size + 2
  b3 = []
  b3 += ['0' + b2[0] + '0']
  b3 += ['0' + b2[1] + '0']
  b3 += [b2[2] + ('0' if len(b2[2]) == 3 else '')]
  b3 += ['0' * size]
  for i in range(3, len(b2)):
    b3 += ['0' + b2[i] + '0']
  b3 += ['0' * size]
  board = "\n".join(b3)

  varlist = []
  varn = {}
  conslist = []

  # 1/0 variables
  for i in range(0,size):
    for j in range(0, size):
      v = None
      if i == 0 or i == size-1 or j == 0 or j == size-1:
        v = Variable(str(-1-(i*size+j)), [0])
      else:
        v = Variable(str(-1-(i*size+j)), [0,1])
      varlist.append(v)
      varn[str(-1-(i*size+j))] = v

  # Make 1/0 variables match board info
  ii = 0
  for i in board.split()[3:]:
    jj = 0
    for j in i:
      if j != '0' and j != '.':
        conslist.append(TableConstraint('boolean_match', [varn[str(-1-(ii*size+jj))]], [[1]]))
      elif j == '.':
        conslist.append(TableConstraint('boolean_match', [varn[str(-1-(ii*size+jj))]], [[0]]))
      jj += 1
    ii += 1

  # Row and column constraints
  row_constraint = [int(i) for i in board.split()[0]]
  for row in range(0,size):
    row_vars = [varn[str(-1-(row*size+col))] for col in range(0,size)]
    conslist.append(NValuesConstraint('row', row_vars, [1], row_constraint[row], row_constraint[row]))

  col_constraint = [int(i) for i in board.split()[1]]
  for col in range(0,size):
    col_vars = [varn[str(-1-(col+row*size))] for row in range(0,size)]
    conslist.append(NValuesConstraint('col', col_vars, [1], col_constraint[col], col_constraint[col]))

  ship_constraints = [int(x) for x in board.split()[2]]

  # Diagonal constraints - optimized to only check necessary cells
  for i in range(1, size-1):
    for j in range(1, size-1):
      center_var = varn[str(-1-(i*size+j))]
      if j > 0:
        diag_var = varn[str(-1-((i-1)*size+(j-1)))]
        conslist.append(NValuesConstraint('diag', [center_var, diag_var], [1], 0, 1))
      if j < size-2:
        diag_var = varn[str(-1-((i-1)*size+(j+1)))]
        conslist.append(NValuesConstraint('diag', [center_var, diag_var], [1], 0, 1))

  # Add water around known ships
  def add_water_surroundings(i, j):
    if 1 <= i < size-1 and 1 <= j < size-1:
      for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
          if di != 0 or dj != 0:
            neighbor_var = varn[str(-1-((i+di)*size+(j+dj)))]
            conslist.append(TableConstraint('water_around', [neighbor_var], [[0]]))

  # Process known ships
  ii = 0
  for i in board.split()[3:]:
    jj = 0
    for j in i:
      if j != '0' and j != '.':
        add_water_surroundings(ii, jj)
      jj += 1
    ii += 1

  csp = CSP('battleship', varlist, conslist)
  solutions, num_nodes = bt_search('BT', csp, 'mrv', True, True)
  print(len(solutions))

  # Write solutions to output file
  with open(output_f, 'w') as f:
    for i, solution in enumerate(solutions, 1):
      grid_01 = format_solution(solution, size)
      if verify_solution(grid_01, board):
        grid_ships = convert_to_ship_grid(grid_01)
        if verify_ship_constraints(grid_ships, ship_constraints):
          f.write(f"{grid_ships}\n")
        else:
          solutions.pop(i)
    else:
      print(f"Solution {i} failed verification!")

  print(f"Found {len(solutions)} solution(s).")

if __name__ == "__main__":
  main()
