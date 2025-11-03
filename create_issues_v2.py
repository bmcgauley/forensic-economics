#!/usr/bin/env python3
"""
Parse tasks.md and output task data for issue creation.
This script parses tasks and outputs JSON for manual processing.
"""
import re
import json

# Map task numbers to milestone numbers
TASK_TO_MILESTONE = {
    # Phase 1: T001-T005 → Milestone 1
    **{f"T{i:03d}": 1 for i in range(1, 6)},
    # Phase 2: T006-T013 → Milestone 2
    **{f"T{i:03d}": 2 for i in range(6, 14)},
    # Phase 3: T014-T025 → Milestone 3
    **{f"T{i:03d}": 3 for i in range(14, 26)},
    # Phase 4: T039-T044 → Milestone 4
    **{f"T{i:03d}": 4 for i in range(39, 45)},
    # Phase 5: T045-T048 → Milestone 5
    **{f"T{i:03d}": 5 for i in range(45, 49)},
    # Phase 6: T049-T052 → Milestone 6
    **{f"T{i:03d}": 6 for i in range(49, 53)},
    # Phase 7: T053-T056 → Milestone 7
    **{f"T{i:03d}": 7 for i in range(53, 57)},
    # Phase 8: T057-T060 → Milestone 8
    **{f"T{i:03d}": 8 for i in range(57, 61)},
    # Phase 9: T061-T065 → Milestone 9
    **{f"T{i:03d}": 9 for i in range(61, 66)},
    # Phase 10: T066-T069 → Milestone 10
    **{f"T{i:03d}": 10 for i in range(66, 70)},
    # Phase 11: T026-T029 → Milestone 11
    **{f"T{i:03d}": 11 for i in range(26, 30)},
    # Phase 12: T030-T033 → Milestone 12
    **{f"T{i:03d}": 12 for i in range(30, 34)},
    # Phase N: T034-T038 → Milestone 13
    **{f"T{i:03d}": 13 for i in range(34, 39)},
}

def parse_tasks(file_path):
    """Parse tasks from tasks.md file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    tasks = []
    # Pattern to match task lines
    pattern = r'^- \[([ x])\] (T\d+) (\[.*?\] )?(.+?)(?:✅.*)?$'

    for line in content.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            completed = match.group(1) == 'x'
            task_id = match.group(2)
            tags = match.group(3).strip() if match.group(3) else ""
            description = match.group(4).strip()

            # Extract priority from tags
            priority = None
            if '[P0]' in tags:
                priority = 'P0'
            elif '[P1]' in tags:
                priority = 'P1'
            elif '[P2]' in tags:
                priority = 'P2'
            elif '[P3]' in tags:
                priority = 'P3'
            elif '[P]' in tags:
                priority = 'P'

            # Extract user story from tags
            user_story = None
            if '[US1]' in tags:
                user_story = 'US1'
            elif '[US2]' in tags:
                user_story = 'US2'
            elif '[US3]' in tags:
                user_story = 'US3'

            tasks.append({
                'id': task_id,
                'completed': completed,
                'priority': priority,
                'user_story': user_story,
                'description': description,
                'milestone': TASK_TO_MILESTONE.get(task_id),
            })

    return tasks

def main():
    """Main execution."""
    tasks_file = r'c:\GitHub\test3\forensic-economics\specs\1-wrongful-death-econ\tasks.md'

    print("Parsing tasks from tasks.md...")
    tasks = parse_tasks(tasks_file)
    print(f"Found {len(tasks)} tasks")

    # Output as JSON
    output_file = r'c:\GitHub\test3\forensic-economics\tasks_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2)

    print(f"Task data written to: {output_file}")

    # Print summary
    completed = sum(1 for t in tasks if t['completed'])
    print(f"\nSummary:")
    print(f"  Total tasks: {len(tasks)}")
    print(f"  Completed: {completed}")
    print(f"  Open: {len(tasks) - completed}")

if __name__ == '__main__':
    main()
