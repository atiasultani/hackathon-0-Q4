"""
Ralph Wiggum Persistent Loop Implementation
Implements the required persistent multi-step execution mechanism
"""
import os
import time
import json
from datetime import datetime
from typing import Dict, Any, Callable, Optional
import traceback

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class RalphWiggumLoop:
    """
    Implements the Ralph Wiggum persistent loop for multi-step task execution.
    This ensures that tasks requiring multiple steps are completed reliably,
    even if individual steps fail or require human intervention.
    """

    def __init__(self):
        self.plans_dir = os.path.join(BASE_PATH, "Plans")
        self.needs_action_dir = os.path.join(BASE_PATH, "Needs_Action")
        self.done_dir = os.path.join(BASE_PATH, "Done")
        self.logs_dir = os.path.join(BASE_PATH, "Logs")

        # Ensure directories exist
        os.makedirs(self.plans_dir, exist_ok=True)
        os.makedirs(self.needs_action_dir, exist_ok=True)
        os.makedirs(self.done_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

    def process_plan(self, plan_file: str) -> bool:
        """
        Process a single plan file through the Ralph loop.
        Returns True if the plan is fully completed, False if it needs more work.
        """
        plan_path = os.path.join(self.plans_dir, plan_file)

        if not os.path.exists(plan_path):
            return False

        with open(plan_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse plan metadata
        plan_metadata = self.parse_plan_metadata(content)
        plan_steps = self.parse_plan_steps(content)

        # Check if plan is already completed
        if self.is_plan_completed(plan_steps):
            # Move to done if fully completed
            done_path = os.path.join(self.done_dir, plan_file)
            os.rename(plan_path, done_path)
            self.log_action(f"Plan completed: {plan_file}")
            return True

        # Execute next step in the plan
        next_step = self.get_next_incomplete_step(plan_steps)
        if next_step:
            step_index = plan_steps.index(next_step)
            step_description = next_step['description']

            self.log_action(f"Executing step {step_index + 1}: {step_description}")

            try:
                # Execute the step
                step_result = self.execute_step(step_description)

                # Update the plan file with the execution result
                updated_content = self.update_plan_step(content, step_description, step_result)

                with open(plan_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                self.log_action(f"Step completed: {step_description}")

            except Exception as e:
                self.log_action(f"Step failed: {step_description}, Error: {str(e)}")
                self.log_action(f"Traceback: {traceback.format_exc()}")
                # Plan needs to wait for manual intervention or retry
                return False

        # Check if plan is now completed after step execution
        return self.is_plan_completed(self.parse_plan_steps(self.read_file(plan_path)))

    def parse_plan_metadata(self, content: str) -> Dict[str, Any]:
        """Parse plan metadata from content."""
        metadata = {}

        # Look for YAML front matter
        if content.startswith('---'):
            end_frontmatter = content.find('---', 3)
            if end_frontmatter != -1:
                frontmatter = content[3:end_frontmatter]
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()

        return metadata

    def parse_plan_steps(self, content: str) -> list:
        """Parse plan steps from content."""
        steps = []

        # Look for markdown-style checkboxes
        lines = content.split('\n')
        for line in lines:
            if '- [ ] ' in line or '- [x] ' in line:
                # Extract step description
                if '- [x] ' in line:
                    status = 'completed'
                    desc = line.replace('- [x] ', '').strip()
                else:
                    status = 'pending'
                    desc = line.replace('- [ ] ', '').strip()

                steps.append({
                    'description': desc,
                    'status': status
                })

        return steps

    def is_plan_completed(self, steps: list) -> bool:
        """Check if all steps in the plan are completed."""
        return all(step['status'] == 'completed' for step in steps)

    def get_next_incomplete_step(self, steps: list) -> Optional[dict]:
        """Get the next incomplete step."""
        for step in steps:
            if step['status'] == 'pending':
                return step
        return None

    def execute_step(self, step_description: str) -> Dict[str, Any]:
        """
        Execute a single step in the plan.
        This is where the actual business logic happens.
        """
        # This is a simplified implementation - in a real system, this would
        # dispatch to various services based on the step description
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'details': f"Executed step: {step_description}"
        }

        # Determine what type of step this is and execute accordingly
        step_lower = step_description.lower()

        if 'send email' in step_lower or 'email' in step_lower:
            # Simulate email sending
            result['action'] = 'email_sent'
            result['details'] = f"Email step processed: {step_description}"

        elif 'create invoice' in step_lower or 'invoice' in step_lower:
            # Simulate invoice creation
            result['action'] = 'invoice_created'
            result['details'] = f"Invoice step processed: {step_description}"

        elif 'payment' in step_lower or 'pay' in step_lower:
            # Check if payment requires approval
            amount = self.extract_amount_from_text(step_description)
            if amount and amount > 100:
                # Payment over $100 requires approval - move to pending approval
                result['requires_approval'] = True
                result['approval_threshold'] = 100
                result['amount'] = amount
                result['action'] = 'payment_requires_approval'
            else:
                # Process smaller payment
                result['action'] = 'payment_processed'
                result['details'] = f"Payment step processed: {step_description}"

        elif 'social' in step_lower or 'post' in step_lower:
            # Simulate social media posting
            result['action'] = 'social_posted'
            result['details'] = f"Social step processed: {step_description}"

        elif 'calendar' in step_lower or 'meeting' in step_lower or 'schedule' in step_lower:
            # Simulate calendar event creation
            result['action'] = 'calendar_event_created'
            result['details'] = f"Calendar step processed: {step_description}"

        else:
            # Generic step processing
            result['action'] = 'step_executed'
            result['details'] = f"Generic step processed: {step_description}"

        return result

    def extract_amount_from_text(self, text: str) -> Optional[float]:
        """Extract monetary amount from text."""
        import re
        match = re.search(r'\$(\d+(?:\.\d+)?)', text)
        if match:
            return float(match.group(1))
        return None

    def update_plan_step(self, original_content: str, step_description: str, result: Dict[str, Any]) -> str:
        """Update a plan step to mark it as completed."""
        # Replace the unchecked checkbox with a checked one
        updated_content = original_content.replace(
            f'- [ ] {step_description}',
            f'- [x] {step_description} <!-- {json.dumps(result)} -->'
        )

        return updated_content

    def read_file(self, file_path: str) -> str:
        """Read file content."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def log_action(self, message: str):
        """Log an action to the system logs."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": message,
            "component": "RalphWiggumLoop"
        }

        log_file = os.path.join(self.logs_dir, f"{datetime.now().strftime('%Y-%m-%d')}.json")

        # Read existing logs or create new
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def run_loop(self, max_iterations: int = 100):
        """
        Run the Ralph Wiggum loop continuously.
        Processes all pending plans until they are completed.
        """
        iteration = 0
        while iteration < max_iterations:
            # Get all plan files
            plan_files = [f for f in os.listdir(self.plans_dir) if f.endswith('.md')]

            if not plan_files:
                print("No plans to process, waiting...")
                time.sleep(5)  # Wait before checking again
                continue

            plans_completed = 0
            for plan_file in plan_files:
                try:
                    completed = self.process_plan(plan_file)
                    if completed:
                        plans_completed += 1
                except Exception as e:
                    self.log_action(f"Error processing plan {plan_file}: {str(e)}")
                    self.log_action(f"Traceback: {traceback.format_exc()}")

            print(f"Iteration {iteration + 1}: Completed {plans_completed} of {len(plan_files)} plans")

            # If no plans were completed this iteration, wait a bit before next check
            if plans_completed == 0:
                time.sleep(5)

            iteration += 1

    def create_plan_from_task(self, task_file: str) -> str:
        """
        Create a plan file from a task file.
        This simulates the Claude planning phase.
        """
        task_path = os.path.join(self.needs_action_dir, task_file)

        with open(task_path, 'r', encoding='utf-8') as f:
            task_content = f.read()

        # Generate a plan based on the task content
        plan_content = self.generate_plan_for_task(task_content, task_file)

        # Create plan filename
        plan_filename = f"PLAN_{task_file.replace('.md', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        plan_path = os.path.join(self.plans_dir, plan_filename)

        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)

        # Log the plan creation
        self.log_action(f"Plan created from task: {task_file} -> {plan_filename}")

        # Remove the original task file as it's now converted to a plan
        os.remove(task_path)

        return plan_filename

    def generate_plan_for_task(self, task_content: str, task_file: str) -> str:
        """
        Generate a structured plan for a given task.
        In a real system, this would involve Claude AI.
        """
        import re

        # Create plan header
        plan_content = f"""---
created: {datetime.now().isoformat()}
domain: auto-generated
status: in_progress
source_task: {task_file}
---

# Execution Plan for: {task_file.replace('.md', '')}

## Objective
Process the task: {task_file.replace('.md', '')}

## Steps
"""

        # Analyze the task content to determine appropriate steps
        task_lower = task_content.lower()

        # Add steps based on content analysis
        steps = []

        if '$' in task_content or 'payment' in task_lower or 'pay' in task_lower:
            steps.append("- [ ] Identify payment amount and recipient")
            steps.append("- [ ] Verify payment approval requirements")
            steps.append("- [ ] Process payment through appropriate channel")
            steps.append("- [ ] Record transaction in accounting system")
            steps.append("- [ ] Generate receipt and confirmation")

        if 'email' in task_lower or 'message' in task_lower:
            steps.append("- [ ] Identify recipient and message content")
            steps.append("- [ ] Draft email with appropriate content")
            steps.append("- [ ] Send email via email MCP server")
            steps.append("- [ ] Log email delivery confirmation")

        if 'invoice' in task_lower:
            steps.append("- [ ] Extract invoice details from request")
            steps.append("- [ ] Create invoice in accounting system")
            steps.append("- [ ] Send invoice to client")
            steps.append("- [ ] Track invoice status")

        if 'social' in task_lower or 'post' in task_lower:
            steps.append("- [ ] Identify target social platforms")
            steps.append("- [ ] Format content for each platform")
            steps.append("- [ ] Post content via social MCP server")
            steps.append("- [ ] Monitor engagement metrics")

        # Add default steps if no specific ones were identified
        if not steps:
            steps.append("- [ ] Analyze task requirements")
            steps.append("- [ ] Execute appropriate action based on task type")
            steps.append("- [ ] Log action results")
            steps.append("- [ ] Update system records")

        # Add steps to the plan
        for step in steps:
            plan_content += f"{step}\n"

        # Add completion verification
        plan_content += "\n## Verification\n- [ ] Confirm all steps completed successfully\n- [ ] Update dashboard with results\n- [ ] Archive plan to Done folder\n"

        return plan_content


def main():
    """Main function to run the Ralph Wiggum Loop"""
    ralph_loop = RalphWiggumLoop()

    print("Starting Ralph Wiggum Persistent Loop...")
    print("This will process plans until they are fully completed.")

    try:
        # Run indefinitely
        ralph_loop.run_loop(max_iterations=1000000)  # Effectively infinite
    except KeyboardInterrupt:
        print("\nRalph Wiggum Loop stopped by user.")
    except Exception as e:
        print(f"Error in Ralph Wiggum Loop: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()