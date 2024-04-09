#!/usr/bin/env bash

python3 scripts/topogenerator.py '/Users/sm/Library/CloudStorage/OneDrive-AHTGlobal/Projects/25865 Stonehill - Ganahl SJC/AHT-Topo.CSV' > '/Users/sm/Library/CloudStorage/OneDrive-AHTGlobal/Projects/25865 Stonehill - Ganahl SJC/AHT-Topo.dot'; dot -Tsvg '/Users/sm/Library/CloudStorage/OneDrive-AHTGlobal/Projects/25865 Stonehill - Ganahl SJC/AHT-Topo.dot' > '/Users/sm/Library/CloudStorage/OneDrive-AHTGlobal/Projects/25865 Stonehill - Ganahl SJC/AHT-Topo.svg'


