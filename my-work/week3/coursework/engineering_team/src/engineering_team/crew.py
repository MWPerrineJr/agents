from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai import Agent, Crew, Process, Task, LLM
from .tools.sandbox_tools import sandbox_tools


# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators



@CrewBase
class EngineeringTeam():
    """EngineeringTeam crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here: 
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def engineering_lead(self) -> Agent:
        config = dict(self.agents_config['engineering_lead']) # type: ignore[index]

        llm = LLM(
            model=config.pop("llm"),
            max_completion_tokens=config.pop("max_completion_tokens"),
            # CrewAI 1.14.4 only forwards the normal field for o1 models.
            additional_params={"reasoning_effort": config.pop("reasoning_effort")},
        )
        return Agent(
            config=config,
            llm=llm,
            tools=sandbox_tools,
            verbose=True,
            mcps=['https://mcp.context7.com/mcp']
        )
            
    @agent
    def backend_engineer(self) -> Agent:
        config = dict(self.agents_config['backend_engineer']) # type: ignore[index]
        
        llm = LLM(
            model=config.pop("llm"),
            max_tokens=config.pop("max_tokens"),
        )
        return Agent(
            config=config,
            llm=llm,
            tools=sandbox_tools,
            verbose=True,
            mcps=['https://mcp.context7.com/mcp']
        )

    @agent
    def frontend_engineer(self) -> Agent:
        config = dict(self.agents_config['frontend_engineer']) # type: ignore[index]

        llm = LLM(
            model=config.pop("llm"),
            max_tokens=config.pop("max_tokens"),
        )
        return Agent(
            config=config,
            llm=llm,
            tools=sandbox_tools,
            verbose=True,
            mcps=['https://mcp.context7.com/mcp']
        )
    
    @agent
    def test_engineer(self) -> Agent:
        config = dict(self.agents_config['test_engineer']) # type: ignore[index]
        
        llm = LLM(
            model=config.pop("llm"),
            max_completion_tokens=config.pop("max_completion_tokens"),
            # CrewAI 1.14.4 only forwards the normal field for o1 models.
            additional_params={"reasoning_effort": config.pop("reasoning_effort")},
        )
        return Agent(
            config=config,
            llm=llm,
            tools=sandbox_tools,
            verbose=True,
            mcps=['https://mcp.context7.com/mcp']
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_task'], # type: ignore[index]
        )

    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_task'], # type: ignore[index]
            
        )
    @task
    def frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config['frontend_task'],

        )
    @task
    def test_task(self) -> Task:
        return Task(
            config=self.tasks_config['test_task'],
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the EngineeringTeam crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            tracing=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
