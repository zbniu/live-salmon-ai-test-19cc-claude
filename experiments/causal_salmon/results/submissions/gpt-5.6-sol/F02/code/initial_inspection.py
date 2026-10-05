from pathlib import Path
p=Path('upload/data(3).csv')
print('Bytes:',p.stat().st_size)
with p.open() as f:
 for _ in range(6):
  print(f.readline().rstrip())
