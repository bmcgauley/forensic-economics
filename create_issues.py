#!/usr/bin/env python3
"""
Script to create GitHub issues from tasks_data.json
"""
import json
import subprocess
import sys
import time

def truncate_string(s, max_length=80):
    """Truncate string to max_length characters"""
    if len(s) <= max_length:
        return s
    return s[:max_length]

def create_issue(task, repo="bmcgauley/forensic-economics"):
    """Create a GitHub issue for a task"""
    task_id = task['id']
    description = task['description']
    completed = task['completed']
    priority = task.get('priority')
    user_story = task.get('user_story')
    milestone = task['milestone']

    # Create title (task_id + first 80 chars of description)
    title = f"{task_id}: {truncate_string(description, 80)}"

    # Create body
    body_parts = [f"**Description:**\n{description}\n"]

    if priority:
        body_parts.append(f"**Priority:** {priority}\n")

    if user_story:
        body_parts.append(f"**User Story:** {user_story}\n")

    status_emoji = ":white_check_mark:" if completed else ":hourglass:"
    status_text = "Completed" if completed else "Incomplete"
    body_parts.append(f"**Completion Status:** {status_emoji} {status_text}")

    body = "\n".join(body_parts)

    # Create the issue using gh CLI (without milestone first)
    cmd = [
        'gh', 'issue', 'create',
        '-R', repo,
        '--title', title,
        '--body', body
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        issue_url = result.stdout.strip()

        # Extract issue number from URL
        issue_number = issue_url.split('/')[-1]

        # Now assign milestone using gh API
        milestone_cmd = [
            'gh', 'api',
            f'repos/{repo}/issues/{issue_number}',
            '-X', 'PATCH',
            '-f', f'milestone={milestone}'
        ]
        subprocess.run(milestone_cmd, capture_output=True, text=True, check=True)

        print(f"[OK] Created issue #{issue_number} for {task_id} (milestone {milestone})")

        return issue_number, completed
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error creating issue for {task_id}: {e.stderr}", file=sys.stderr)
        return None, completed

def close_issue(issue_number, repo="bmcgauley/forensic-economics"):
    """Close a GitHub issue"""
    cmd = ['gh', 'issue', 'close', issue_number, '-R', repo]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"  [OK] Closed issue #{issue_number} (completed task)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Error closing issue #{issue_number}: {e.stderr}", file=sys.stderr)
        return False

def main():
    # Load tasks
    tasks_file = r'c:\GitHub\test3\forensic-economics\tasks_data.json'
    with open(tasks_file, 'r', encoding='utf-8') as f:
        tasks = json.load(f)

    print(f"Processing {len(tasks)} tasks...\n")

    created_count = 0
    closed_count = 0
    open_count = 0
    errors = []

    for i, task in enumerate(tasks, 1):
        task_id = task['id']
        print(f"[{i}/{len(tasks)}] Processing {task_id}...")

        issue_number, completed = create_issue(task)

        if issue_number:
            created_count += 1

            if completed:
                # Add small delay to avoid rate limiting
                time.sleep(0.5)
                # Close the issue
                if close_issue(issue_number):
                    closed_count += 1
                else:
                    errors.append(f"Failed to close issue #{issue_number} for {task_id}")
                    open_count += 1
            else:
                open_count += 1
        else:
            errors.append(f"Failed to create issue for {task_id}")

        # Small delay between requests to avoid rate limiting
        time.sleep(0.5)
        print()  # Empty line between tasks

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY REPORT")
    print("="*60)
    print(f"Total tasks processed: {len(tasks)}")
    print(f"Issues created: {created_count}")
    print(f"Issues closed (completed): {closed_count}")
    print(f"Issues left open (incomplete): {open_count}")

    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n[SUCCESS] All tasks processed successfully!")

if __name__ == '__main__':
    main()
