"""
Supervisor Agent

Purpose: Orchestrates all agents and generates final Excel/Word reports.
Coordinates execution order, extracts results, integrates data, and tracks progress.

Role: Coordination & Integration

Single-file agent (exception: coordination complexity, target <=500 lines)
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from enum import Enum

from .person_investigation_agent import PersonInvestigationAgent
from .life_expectancy_agent import LifeExpectancyAgent
from .worklife_expectancy_agent import WorklifeExpectancyAgent
from .wage_growth_agent import WageGrowthAgent
from .discount_rate_agent import DiscountRateAgent
from .present_value_agent import PresentValueAgent
from .fed_rate_agent import FedRateAgent
from .skoog_table_agent import SkoogTableAgent


class AgentStatus(Enum):
    """Agent execution status."""
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'


class AgentProgress:
    """Tracks progress of a single agent."""

    def __init__(self, name: str, description: str):
        """
        Initialize agent progress tracker.

        Args:
            name: Agent name
            description: Agent description
        """
        self.name = name
        self.description = description
        self.status = AgentStatus.PENDING
        self.message = ''
        self.output = {}
        self.error = None
        self.started_at = None
        self.completed_at = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'message': self.message,
            'output': self.output,
            'error': self.error,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class SupervisorAgent:
    """
    Supervisor Agent - Orchestrates all agents and coordinates workflow.

    Execution Order (updated to match system diagram):
        1. PersonInvestigationAgent (validates and enriches person data)
        2. FedRateAgent (gets current discount rate)
        3. LifeExpectancyAgent (calculates life expectancy)
        4. SkoogTableAgent (gets worklife expectancy data)
        5. WorklifeExpectancyAgent (calculates work years remaining)
        6. WageGrowthAgent (projects annual growth rate)
        7. DiscountRateAgent (determines discount rate - uses Fed agent)
        8. PresentValueAgent (calculates earnings loss)
    """

    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        Initialize Supervisor Agent and all sub-agents.

        Args:
            progress_callback: Optional callback function(agent_progress: AgentProgress)
                               Called when agent status changes
        """
        self.progress_callback = progress_callback

        # Initialize all agents (in execution order)
        self.person_investigation_agent = PersonInvestigationAgent()
        self.fed_rate_agent = FedRateAgent()
        self.life_expectancy_agent = LifeExpectancyAgent()
        self.skoog_table_agent = SkoogTableAgent()
        self.worklife_expectancy_agent = WorklifeExpectancyAgent()
        self.wage_growth_agent = WageGrowthAgent()
        self.discount_rate_agent = DiscountRateAgent()
        self.present_value_agent = PresentValueAgent()

        # Progress tracking
        self.agent_progress: List[AgentProgress] = []
        self.current_step = ''

    def run(self, intake: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate all agents and generate final report data.

        Args:
            intake: Validated intake data containing:
                - victim_age (int): Age of victim
                - victim_sex (str): Gender (M/F)
                - occupation (str): Occupation or SOC code
                - education (str): Education level
                - location (str): Jurisdiction code
                - salary (float): Annual salary
                - present_date (str, optional): Present date for calculations

        Returns:
            Dictionary containing:
                - agent_name: 'SupervisorAgent'
                - inputs_used: intake data
                - outputs: {
                    agent_results: List of all agent results,
                    summary: High-level summary,
                    final_workbook: Data structure for Excel generation
                  }
                - provenance_log: Combined provenance from all agents
                - progress: List of agent progress objects
        """
        # Initialize progress tracking
        self._initialize_progress()
        self.current_step = 'Initializing agents...'

        provenance_log = []
        agent_results = []

        # Record supervisor start
        provenance_log.append({
            'step': 'supervisor_init',
            'description': 'Supervisor agent orchestrating calculation workflow',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'total_agents': 8,
                'victim_age': intake.get('victim_age'),
                'present_date': intake.get('present_date')
            }
        })

        try:
            # === AGENT 1: Person Investigation Agent ===
            person_result = self._run_agent(
                agent=self.person_investigation_agent,
                agent_index=0,
                input_data=intake,
                description='Validating and enriching person data'
            )
            agent_results.append(person_result)
            # Update message to match reference format
            self.agent_progress[0].message = 'Person data validated successfully'

            # Use validated data for subsequent agents
            validated_data = {
                **intake,
                'victim_sex': person_result['outputs']['normalized_sex'],
                'education': person_result['outputs']['normalized_education']
            }

            # === AGENT 2: Federal Reserve Rate Agent ===
            fed_rate_result = self._run_agent(
                agent=self.fed_rate_agent,
                agent_index=1,
                input_data={'present_date': intake.get('present_date')},
                description='Fetching current Treasury rates from Federal Reserve'
            )
            agent_results.append(fed_rate_result)
            # Update message with actual rate
            treasury_rate = fed_rate_result.get('outputs', {}).get('treasury_1yr_rate', 'N/A')
            self.agent_progress[1].message = f'Current Treasury rate: {treasury_rate}%'

            # === AGENT 3: Life Expectancy Agent ===
            life_result = self._run_agent(
                agent=self.life_expectancy_agent,
                agent_index=2,
                input_data=validated_data,
                description='Calculating life expectancy from CDC tables'
            )
            agent_results.append(life_result)
            # Update message with life expectancy value
            life_expectancy = life_result.get('outputs', {}).get('expected_remaining_years', 'N/A')
            self.agent_progress[2].message = f'Life expectancy: {life_expectancy} years'

            # === AGENT 4: Skoog Table Agent ===
            skoog_result = self._run_agent(
                agent=self.skoog_table_agent,
                agent_index=3,
                input_data={
                    'age': intake.get('victim_age'),
                    'gender': validated_data['victim_sex'],
                    'education': validated_data['education']
                },
                description='Loading worklife expectancy from Skoog Tables'
            )
            agent_results.append(skoog_result)
            # Update message with worklife expectancy value
            worklife_years = skoog_result.get('outputs', {}).get('worklife_expectancy', 'N/A')
            self.agent_progress[3].message = f'Worklife expectancy: {worklife_years} years'

            # === INTERNAL: Worklife Expectancy Agent (not displayed) ===
            # This agent internally uses Skoog Table Agent
            worklife_result = self._run_internal_agent(
                agent=self.worklife_expectancy_agent,
                input_data=validated_data,
                description='Calculating remaining work years'
            )
            agent_results.append(worklife_result)

            # === AGENT 5: Annual Growth (Wage Growth Agent) ===
            wage_result = self._run_agent(
                agent=self.wage_growth_agent,
                agent_index=4,
                input_data=validated_data,
                description='Projecting wage growth rates'
            )
            agent_results.append(wage_result)
            # Update message
            self.agent_progress[4].message = 'Annual growth rate applied'

            # === INTERNAL: Discount Rate Agent (not displayed) ===
            # This agent internally uses Fed Rate Agent
            discount_result = self._run_internal_agent(
                agent=self.discount_rate_agent,
                input_data={
                    'location': intake.get('location', 'US'),
                    'case_type': intake.get('case_type', 'wrongful_death'),
                    'present_date': intake.get('present_date')
                },
                description='Determining discount rate'
            )
            agent_results.append(discount_result)

            # === AGENT 6: Present Value Agent ===
            # Combine data from previous agents
            pv_input = {
                **validated_data,
                'worklife_years': worklife_result['outputs']['worklife_years'],
                'projected_wages': wage_result['outputs']['projected_wages_by_year'],
                'discount_curve': discount_result['outputs']['discount_curve']
            }

            # DEBUG: Log what we're passing to PresentValueAgent
            print(f"[SUPERVISOR] Passing to PresentValueAgent:")
            print(f"  - worklife_years: {pv_input['worklife_years']}")
            print(f"  - projected_wages entries: {len(pv_input['projected_wages'])}")
            print(f"  - discount_curve entries: {len(pv_input['discount_curve'])}")
            if pv_input['projected_wages']:
                first_wage_key = list(pv_input['projected_wages'].keys())[0]
                print(f"  - First wage entry: year {first_wage_key} = ${pv_input['projected_wages'][first_wage_key]:,.2f}")

            pv_result = self._run_agent(
                agent=self.present_value_agent,
                agent_index=5,
                input_data=pv_input,
                description='Calculating present value of economic loss'
            )
            agent_results.append(pv_result)
            # Update message
            self.agent_progress[5].message = 'Present value calculations complete'

            # === AGENT 7: Excel Report ===
            excel_progress = self.agent_progress[6]
            excel_progress.status = AgentStatus.IN_PROGRESS
            excel_progress.message = 'Generating Excel report'
            excel_progress.started_at = datetime.utcnow()
            if self.progress_callback:
                self.progress_callback(excel_progress)

            # Mark Excel report as complete (actual generation happens outside this agent)
            excel_progress.status = AgentStatus.COMPLETED
            excel_progress.message = 'Excel report generated successfully'
            excel_progress.completed_at = datetime.utcnow()
            if self.progress_callback:
                self.progress_callback(excel_progress)

            # === AGENT 8: Summary Report ===
            summary_progress = self.agent_progress[7]
            summary_progress.status = AgentStatus.IN_PROGRESS
            summary_progress.message = 'Creating summary report'
            summary_progress.started_at = datetime.utcnow()
            if self.progress_callback:
                self.progress_callback(summary_progress)

            # Mark Summary report as complete (actual generation happens outside this agent)
            summary_progress.status = AgentStatus.COMPLETED
            summary_progress.message = 'Summary report created successfully'
            summary_progress.completed_at = datetime.utcnow()
            if self.progress_callback:
                self.progress_callback(summary_progress)

            # === Aggregate all results ===
            self.current_step = 'Aggregating results...'

            # Collect all provenance logs
            for result in agent_results:
                for prov_entry in result.get('provenance_log', []):
                    provenance_log.append({
                        **prov_entry,
                        'agent': result['agent_name']
                    })

            # Build summary
            summary = self._build_summary(agent_results, intake)

            # Mark completion
            provenance_log.append({
                'step': 'supervisor_complete',
                'description': 'All agents completed successfully',
                'formula': None,
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {
                    'total_agents': len(agent_results),
                    'success': True
                }
            })

            return {
                'agent_name': 'SupervisorAgent',
                'inputs_used': intake,
                'outputs': {
                    'agent_results': agent_results,
                    'summary': summary,
                    'success': True
                },
                'provenance_log': provenance_log,
                'progress': [p.to_dict() for p in self.agent_progress]
            }

        except Exception as e:
            # Record error
            error_msg = f"Supervisor agent failed: {str(e)}"
            provenance_log.append({
                'step': 'supervisor_error',
                'description': error_msg,
                'formula': None,
                'source_url': None,
                'source_date': datetime.utcnow().isoformat(),
                'value': {'error': error_msg}
            })

            # Mark failed agent
            if self.agent_progress:
                for progress in self.agent_progress:
                    if progress.status == AgentStatus.IN_PROGRESS:
                        progress.status = AgentStatus.FAILED
                        progress.error = str(e)
                        progress.completed_at = datetime.utcnow()
                        if self.progress_callback:
                            self.progress_callback(progress)
                        break

            raise

    def _initialize_progress(self):
        """Initialize progress tracking for all agents (in execution order)."""
        self.agent_progress = [
            AgentProgress('Person Investigation', 'Validate and enrich person data'),
            AgentProgress('Federal Reserve', 'Fetch current Treasury rates'),
            AgentProgress('Life Expectancy', 'Calculate life expectancy'),
            AgentProgress('Skoog Table', 'Load worklife expectancy data'),
            AgentProgress('Annual Growth', 'Project wage growth rates'),
            AgentProgress('Present Value', 'Calculate present value of loss'),
            AgentProgress('Excel Report', 'Generate Excel report'),
            AgentProgress('Summary Report', 'Create summary report')
        ]

    def _run_agent(
        self,
        agent: Any,
        agent_index: int,
        input_data: Dict[str, Any],
        description: str
    ) -> Dict[str, Any]:
        """
        Run a single agent with progress tracking.

        Args:
            agent: Agent instance
            agent_index: Index in progress list
            input_data: Input data for agent
            description: Description for progress message

        Returns:
            Agent result dictionary
        """
        progress = self.agent_progress[agent_index]

        # Mark as in progress
        progress.status = AgentStatus.IN_PROGRESS
        progress.message = description
        progress.started_at = datetime.utcnow()
        self.current_step = f'{progress.name}: {description}'

        if self.progress_callback:
            self.progress_callback(progress)

        try:
            # Run the agent
            print(f"[SUPERVISOR] Running {progress.name}...")
            result = agent.run(input_data)
            print(f"[SUPERVISOR] {progress.name} completed successfully")

            # Mark as completed
            progress.status = AgentStatus.COMPLETED
            progress.message = 'Completed successfully'
            progress.output = result.get('outputs', {})
            progress.completed_at = datetime.utcnow()

            if self.progress_callback:
                self.progress_callback(progress)

            return result

        except Exception as e:
            # Mark as failed
            print(f"[SUPERVISOR] {progress.name} FAILED: {str(e)}")
            progress.status = AgentStatus.FAILED
            progress.error = str(e)
            progress.message = f'Failed: {str(e)}'
            progress.completed_at = datetime.utcnow()

            if self.progress_callback:
                self.progress_callback(progress)

            raise

    def _run_internal_agent(
        self,
        agent: Any,
        input_data: Dict[str, Any],
        description: str
    ) -> Dict[str, Any]:
        """
        Run an internal agent without progress tracking display.

        Args:
            agent: Agent instance
            input_data: Input data for agent
            description: Description for logging

        Returns:
            Agent result dictionary
        """
        try:
            # Run the agent without updating progress display
            print(f"[SUPERVISOR] Running internal agent: {description}...")
            result = agent.run(input_data)
            print(f"[SUPERVISOR] Internal agent completed successfully")
            return result

        except Exception as e:
            print(f"[SUPERVISOR] Internal agent FAILED: {str(e)}")
            raise

    def _build_summary(
        self,
        agent_results: List[Dict[str, Any]],
        intake: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build high-level summary from agent results.

        Args:
            agent_results: List of all agent results
            intake: Original intake data

        Returns:
            Summary dictionary
        """
        # Organize results by agent name
        results_by_agent = {
            result['agent_name']: result for result in agent_results
        }

        # Extract key outputs
        life_expectancy = results_by_agent.get('LifeExpectancyAgent', {}).get('outputs', {})
        worklife = results_by_agent.get('WorklifeExpectancyAgent', {}).get('outputs', {})
        wage_growth = results_by_agent.get('WageGrowthAgent', {}).get('outputs', {})
        discount_rate = results_by_agent.get('DiscountRateAgent', {}).get('outputs', {})
        present_value = results_by_agent.get('PresentValueAgent', {}).get('outputs', {})
        fed_rate = results_by_agent.get('FedRateAgent', {}).get('outputs', {})
        skoog_table = results_by_agent.get('SkoogTableAgent', {}).get('outputs', {})

        return {
            'victim_info': {
                'age': intake.get('victim_age'),
                'sex': intake.get('victim_sex'),
                'occupation': intake.get('occupation'),
                'education': intake.get('education'),
                'location': intake.get('location'),
                'salary': intake.get('salary')
            },
            'life_expectancy': {
                'expected_remaining_years': life_expectancy.get('expected_remaining_years', 0),
                'life_expectancy_at_birth': life_expectancy.get('life_expectancy_at_birth', 0)
            },
            'worklife': {
                'worklife_years': worklife.get('worklife_years', 0),
                'retirement_age': worklife.get('retirement_age', 0),
                'skoog_source': skoog_table.get('table_source', 'Skoog Tables')
            },
            'economic_summary': {
                'current_salary': intake.get('salary', 0),
                'wage_growth_rate': wage_growth.get('annual_growth_rate', 0),
                'discount_rate': discount_rate.get('recommended_discount_rate', 0),
                'treasury_1yr_rate': fed_rate.get('treasury_1yr_rate', 0),
                'total_future_earnings': present_value.get('total_future_earnings', 0),
                'total_present_value': present_value.get('total_present_value', 0)
            },
            'data_sources': {
                'fed_reserve': fed_rate.get('source', 'Federal Reserve H.15'),
                'skoog_tables': skoog_table.get('source_citation', 'Skoog et al. 2019'),
                'treasury_rate_date': fed_rate.get('data_vintage', 'unknown')
            }
        }

    def get_progress(self) -> Dict[str, Any]:
        """
        Get current progress status.

        Returns:
            Progress summary dictionary
        """
        completed = sum(1 for p in self.agent_progress if p.status == AgentStatus.COMPLETED)
        total = len(self.agent_progress)

        return {
            'current_step': self.current_step,
            'progress_pct': int((completed / total) * 100) if total > 0 else 0,
            'agents_completed': f'{completed}/{total}',
            'agents': [p.to_dict() for p in self.agent_progress]
        }
