
# Student Task and Deadline Scheduler

## Overview
A Python-based student task management application that uses
a Binary Max Heap to prioritize academic tasks based on deadline,
importance and estimated completion duration.

## DSA Concepts
1. Binary Max Heap - priority queue.
2. Hash Table - task storage and lookup.
3. Sorting - ranking tasks.
4. Searching - title, category and ID search.
5. Greedy approach - recommend the highest-priority pending task.

## Requirements
- Python 3.10 or newer
- uv (optional)

## Execution

Using Python:
python3 main.py

Using uv:
uv run python main.py

## Run tests
python3 -m unittest discover -s tests -v

## Data storage
All tasks are stored locally in data/tasks.json.

## Priority formula
Priority = 0.50(U) + 0.30(I) + 0.20(D)

U = Urgency score
I = Importance score
D = Duration/preparation score
