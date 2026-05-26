"""
Azure AI Agent workflow orchestrator.

This module defines the BacklogWorkflowOrchestrator, which acts as the main
adapter between the application domain and Azure AI Agents.

It is responsible for:
- Managing the full multi-step backlog generation workflow
- Registering and exposing domain tools to the Azure agent runtime
- Handling streaming execution and tool-call orchestration
- Supporting verification loops (market intelligence + backlog)
- Coordinating interaction between LLM reasoning and domain services

The orchestrator ensures a strict, controlled execution flow while delegating
business logic to domain tools.
"""

import asyncio
import logging

import json
from typing import AsyncGenerator

from azure.core.exceptions import AzureError, ClientAuthenticationError, ServiceRequestError

from backend.src.domain.exceptions.azure.azure_agent_runtime_exception import AzureAgentRuntimeException
from backend.src.domain.exceptions.azure.azure_stream_exception import AzureStreamException
from backend.src.domain.exceptions.tool.invalid_tool_argument_exception import InvalidToolArgumentException
from backend.src.domain.exceptions.stream.stream_cancelled_exception import StreamCancelledException
from backend.src.domain.exceptions.stream.stream_execution_exception import StreamExecutionException
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.domain.ports.services.backlog_generation.orchestrator.i_backlog_workflow_orchestrator import \
    IBacklogWorkflowOrchestrator
from backend.src.domain.ports.services.backlog_generation.tools.i_backlog_generator_tool import IBacklogGeneratorTool
from backend.src.domain.ports.services.backlog_generation.tools.i_delivery_planner_tool import IDeliveryPlannerTool
from backend.src.domain.ports.services.backlog_generation.tools.i_market_query_generator_tool import \
    IMarketQueryGeneratorTool
from backend.src.domain.ports.services.backlog_generation.tools.i_market_summarizer_tool import IMarketSummarizerTool
from backend.src.domain.ports.services.backlog_generation.tools.i_market_validator_tool import IMarketValidatorTool
from backend.src.domain.ports.services.backlog_generation.tools.i_product_context_builder_tool import IProductContextTool
from backend.src.domain.ports.services.backlog_generation.tools.i_user_backlog_fixer_tool import IUserBacklogFixerTool
from backend.src.domain.ports.services.backlog_generation.tools.i_web_search_tool import IWebSearchTool
from backend.src.infrastructure.external.backlog_generation.common.base_azure_project_agent import BaseAzureProjectAgent
from backend.src.infrastructure.external.backlog_generation.orchestrator.event_handler import EventHandler


logger = logging.getLogger(__name__)


class BacklogWorkflowOrchestrator(BaseAzureProjectAgent, IBacklogWorkflowOrchestrator):
    """
    Orchestrator for Azure AI Agent-based backlog generation workflow.

    This class:
    - Initializes and configures the Azure AI agent
    - Registers domain tools as callable functions
    - Manages streaming execution of agent runs
    - Handles tool execution via function calling
    - Implements verification loops for:
        - Market intelligence validation
        - User backlog correction
    - Ensures strict sequential workflow execution

    Attributes:
        product_context_tool (IProductContextTool): Builds structured product context from raw input.
        query_generator_tool (IMarketQueryGeneratorTool): Generates market research queries.
        web_search_tool (IWebSearchTool): Executes backlog workflow orchestrator queries.
        market_summarizer_tool (IMarketSummarizerTool): Summarizes market intelligence.
        market_validator_tool (IMarketValidatorTool): Validates market intelligence consistency.
        backlog_generator_tool (IBacklogGeneratorTool): Generates structured backlog (epics/user stories/tasks).
        user_backlog_fixer_tool (IUserBacklogFixerTool): Fixes user-modified backlogs.
        delivery_planner_tool (IDeliveryPlannerTool): Produces sprint planning and delivery structure.
    """

    def __init__(
            self,
            product_context_tool: IProductContextTool,
            query_generator_tool: IMarketQueryGeneratorTool,
            web_search_tool: IWebSearchTool,
            market_summarizer_tool: IMarketSummarizerTool,
            market_validator_tool: IMarketValidatorTool,
            backlog_generator_tool: IBacklogGeneratorTool,
            user_backlog_fixer_tool: IUserBacklogFixerTool,
            delivery_planner_tool: IDeliveryPlannerTool
    ):
        """
        Initialize the orchestrator with all required domain tools.

        Args:
            product_context_tool: Builds product context.
            query_generator_tool: Generates market queries.
            web_search_tool: Executes backlog workflow orchestrator.
            market_summarizer_tool: Summarizes market data.
            market_validator_tool: Validates market intelligence.
            backlog_generator_tool: Generates backlog structure.
            user_backlog_fixer_tool: Fixes user-modified backlog.
            delivery_planner_tool: Creates sprint planning.
        """
        self.product_context_tool = product_context_tool
        self.query_generator_tool = query_generator_tool
        self.web_search_tool = web_search_tool
        self.market_summarizer_tool = market_summarizer_tool
        self.market_validator_tool = market_validator_tool
        self.backlog_generator_tool = backlog_generator_tool
        self.user_backlog_fixer_tool = user_backlog_fixer_tool
        self.delivery_planner_tool = delivery_planner_tool

        super().__init__("TASK_CREATOR_AGENT_ID")

    @classmethod
    async def create(
            cls,
            product_context_tool: IProductContextTool,
            query_generator_tool: IMarketQueryGeneratorTool,
            web_search_tool: IWebSearchTool,
            market_summarizer_tool: IMarketSummarizerTool,
            market_validator_tool: IMarketValidatorTool,
            backlog_generator_tool: IBacklogGeneratorTool,
            user_backlog_fixer_tool: IUserBacklogFixerTool,
            delivery_planner_tool: IDeliveryPlannerTool
    ) -> "BacklogWorkflowOrchestrator":
        """
        Factory method to initialize and load the Azure agent.

        Returns:
            Fully initialized orchestrator instance.
        """
        logger.info("Creating BacklogWorkflowOrchestrator instance.")

        instance = cls(
            product_context_tool,
            query_generator_tool,
            web_search_tool,
            market_summarizer_tool,
            market_validator_tool,
            backlog_generator_tool,
            user_backlog_fixer_tool,
            delivery_planner_tool
        )
        await instance.load_agent()

        logger.info("Azure agent loaded successfully for BacklogWorkflowOrchestrator.")

        return instance

    async def start_stream(self, description: str) -> AsyncGenerator[str, None]:
        """
        Start the backlog generation workflow in streaming mode.

        This method initializes a new Azure agent thread and triggers the first
        step of the workflow by sending the user project description.

        It enforces the first tool call to be `build_product_context` in order
        to guarantee a structured starting point for the pipeline.

        Workflow:
        - Create a new Azure agent thread
        - Send the raw project description as user input
        - Trigger streaming execution of the agent
        - Yield the thread ID and progressive response chunks

        Args:
            description (str): Raw project description provided by the user.

        Yields:
            AsyncGenerator[str, None]:
                Streaming output including:
                - Thread creation metadata
                - Incremental agent responses

        Raises:
            AzureAgentRuntimeException: If thread creation or message creation fails, or Azure SDK error occurs.
            StreamExecutionException: If an unexpected error occurs during stream execution.
            StreamCancelledException: If the stream is cancelled.
            AzureStreamException: If an Azure streaming SDK error occurs.
        """
        logger.info(
            "Starting backlog generation stream: description_length=%s.",
            len(description),
        )

        if not self.agent:
            logger.warning("Backlog Workflow Orchestrator Agent not loaded, attempting lazy load.")
            await self.load_agent()

        try:
            thread = await self.project_client.agents.threads.create()

            logger.info("Azure thread created successfully: thread_id=%s.", thread.id)

            await self.project_client.agents.messages.create(
                thread_id=thread.id, role="user", content=description
            )
        except (AzureAgentRuntimeException, StreamExecutionException, StreamCancelledException):
            raise
        except AzureError as e:
            raise AzureAgentRuntimeException(
                message="The AI service encountered an unexpected error. Please try again."
            ) from e
        except Exception as e:
            logger.exception("start_stream failed unexpectedly.")
            raise StreamExecutionException(message="The generation could not be started. Please try again.") from e

        yield f"data: {json.dumps({'thread_id': thread.id})}\n\n"

        async for chunk in self._run_stream(
                thread.id,
                tool_choice={"type": "function", "function": {"name": "build_product_context"}},
        ):
            yield f"data: {json.dumps({'text': chunk})}\n\n"

    async def reply_stream(
        self,
        thread_id: str,
        tool_result: str,
        user_result: str
    ) -> AsyncGenerator[str, None]:
        """
        Handle the verification loop for market intelligence refinement.

        This method is triggered when the user provides feedback on the
        generated market intelligence. It ensures consistency between:
        - The original tool output
        - The user-modified result

        Workflow:
        - Sends both results to the agent
        - Allows the agent to validate or refine the context
        - Continues streaming updated reasoning/output

        Args:
            thread_id (str): Identifier of the active Azure agent thread.
            tool_result (str): JSON string produced by the market intelligence tool.
            user_result (str): JSON string modified or confirmed by the user.

        Yields:
            AsyncGenerator[str, None]: Streaming chunks of updated agent response.

        Raises:
            AzureAgentRuntimeException: If message creation fails or Azure SDK error occurs.
            StreamExecutionException: If an unexpected error occurs during execution.
            StreamCancelledException: If the stream is cancelled.
            AzureStreamException: If an Azure streaming SDK error occurs.
    """
        logger.info(
            "Processing market intelligence verification reply: thread_id=%s.",
            thread_id,
        )

        if not self.agent:
            logger.warning("Backlog Workflow Orchestrator Agent not loaded, attempting lazy load.")
            await self.load_agent()

        content = f"""
        [VERIFICATION LOOP RESPONSE]
        This is a user response during the verification loop — do NOT restart from STEP 1.

        Tool result (from previous validation step):
        {tool_result}

        User modified result (or confirmation):
        {user_result}

        Instructions:
        - If tool_result and user_result are not equivalent, call validate_market_intelligence again with the user_result as context.
          If is_valid is true in result of validate_market_intelligence tool, proceed DIRECTLY to generate_backlog with the result of validate_market_intelligence.
          Else return it to user to verify.
        - If tool_result and user_result are semantically equivalent JSON (not string comparison), proceed DIRECTLY to generate_backlog with tool_result.
        """

        try:
            await self.project_client.agents.messages.create(
                thread_id=thread_id, role="user", content=content
            )
        except (AzureAgentRuntimeException, StreamExecutionException, StreamCancelledException):
            raise
        except AzureError as e:
            raise AzureAgentRuntimeException(
                message="The AI service encountered an unexpected error. Please try again."
            ) from e
        except Exception as e:
            logger.exception("reply_stream failed unexpectedly.")
            raise StreamExecutionException(message="Your response could not be processed. Please try again.") from e

        async for chunk in self._run_stream(thread_id):
            yield f"data: {json.dumps({'text': chunk})}\n\n"

    async def reply_backlog_stream(
        self,
        thread_id: str,
        user_result: str,
        tool_result: str
    ) -> AsyncGenerator[str, None]:
        """
        Handle the backlog verification loop.

        This method manages user feedback on a generated backlog and ensures
        structural and semantic correctness before proceeding to delivery planning.

        Workflow:
        - Compares original backlog with user modifications
        - If differences exist, triggers fix_user_backlog tool
        - If valid, proceeds to delivery planning stage
        - Streams updated agent responses in real time

        Args:
            thread_id (str): Identifier of the active Azure agent thread.
            user_result (str): User-modified or confirmed backlog JSON string.
            tool_result (str): Original backlog JSON string generated by generate_backlog tool.

        Yields:
            AsyncGenerator[str, None]: Streaming chunks of updated backlog validation and response.

        Raises:
            AzureAgentRuntimeException: If message creation fails or Azure SDK error occurs.
            StreamExecutionException: If an unexpected error occurs during execution.
            StreamCancelledException: If the stream is cancelled.
            AzureStreamException: If an Azure streaming SDK error occurs.
        """
        logger.info(
            "Processing backlog verification reply: thread_id=%s.",
            thread_id,
        )

        if not self.agent:
            logger.warning("Backlog Workflow Orchestrator Agent not loaded, attempting lazy load.")
            await self.load_agent()

        content = f"""
        [BACKLOG VERIFICATION LOOP RESPONSE]
        This is a user response during the backlog verification loop — do NOT restart from STEP 1.

        Backlog reference (immutable output of generate_backlog tool):
        {tool_result}

        User modified backlog (or confirmation):
        {user_result}

        Instructions:
        - If tool_result and user_result are semantically equivalent JSON (not string comparison):
          Proceed DIRECTLY to delivery_planning using tool_result as the backlog.
        - If tool_result and user_result are NOT equivalent (user modified the backlog):
          Call fix_user_backlog with:
            - backlog_reference = tool_result
            - backlog_to_validate = user_result
          Then:
            - If fix_user_backlog returns is_valid: true → proceed DIRECTLY to delivery_planning.
            - If fix_user_backlog returns is_valid: false → present the fixed backlog with an explanation derived from the `corrections` field,
              ask the user to review again. Wait for the next [BACKLOG VERIFICATION LOOP RESPONSE].
        """

        try:
            await self.project_client.agents.messages.create(
                thread_id=thread_id, role="user", content=content
            )
        except (AzureAgentRuntimeException, StreamExecutionException, StreamCancelledException):
            raise
        except AzureError as e:
            raise AzureAgentRuntimeException(
                message="The AI service encountered an unexpected error. Please try again."
            ) from e
        except Exception as e:
            logger.exception("reply_backlog_stream failed unexpectedly.")
            raise StreamExecutionException(
                message="Your backlog response could not be processed. Please try again."
            ) from e

        async for chunk in self._run_stream(thread_id):
            yield f"data: {json.dumps({'text': chunk})}\n\n"

    async def _run_stream(self, thread_id: str, tool_choice=None) -> AsyncGenerator[str, None]:
        """
        Core execution engine for Azure AI Agent streaming runs.

        This internal method is responsible for:
        - Executing the agent run in streaming mode
        - Handling tool invocation requests
        - Dispatching tool execution results back to Azure
        - Managing event-driven response streaming
        - Coordinating the full multi-step workflow lifecycle

        Workflow:
        - Starts an Azure agent run stream
        - Listens for streaming events
        - Executes required tool calls dynamically
        - Submits tool outputs back to the agent
        - Yields intermediate and final response chunks

        Args:
            thread_id (str): Identifier of the active Azure thread.
            tool_choice (optional): Optional constraint to force initial tool execution.

        Yields:
            AsyncGenerator[str, None]: Streaming text chunks from the agent and event handler.

        Raises:
            AzureAgentRuntimeException: If stream initialization or tool output submission fails.
            StreamExecutionException: If the Azure agent run fails or unexpected error occurs.
            StreamCancelledException: If the stream is cancelled.
            AzureStreamException: If an Azure SDK streaming error occurs.
        """
        logger.info(
            "Starting Azure agent run stream: thread_id=%s, agent_id=%s.",
            thread_id,
            self.agent_id,
        )

        functions = {
            "build_product_context": self.product_context_tool,
            "generate_market_queries": self.query_generator_tool,
            "web_search": self.web_search_tool,
            "summarize_market_intelligence": self.market_summarizer_tool,
            "validate_market_intelligence": self.market_validator_tool,
            "generate_backlog": self.backlog_generator_tool,
            "fix_user_backlog": self.user_backlog_fixer_tool,
            "delivery_planning": self.delivery_planner_tool,
        }

        event_handler = EventHandler()

        run_kwargs = {
            "thread_id": thread_id,
            "agent_id": self.agent_id,
            "event_handler": event_handler,
        }

        if tool_choice is not None:
            run_kwargs["tool_choice"] = tool_choice

        try:
            stream_coro = await self.project_client.agents.runs.stream(**run_kwargs)
        except AzureError as e:
            raise AzureAgentRuntimeException(message="The AI service could not be reached. Please try again.") from e

        async with stream_coro as stream:
            try:
                async for event_type, event_data, _ in stream:
                    for chunk in event_handler.get_stream_chunks():
                        yield chunk

                    if event_type == "thread.run.requires_action":
                        run_data = event_data
                        tool_calls = run_data.required_action.submit_tool_outputs.tool_calls
                        tool_outputs = []

                        for tool_call in tool_calls:
                            function_name = tool_call.function.name
                            try:
                                function_args = json.loads(tool_call.function.arguments or "{}")
                            except json.JSONDecodeError as e:
                                logger.error(
                                    "Invalid JSON tool arguments: %s | error=%s.",
                                    tool_call.function.arguments,
                                    str(e),
                                )
                                output = json.dumps({
                                    "success": False,
                                    "error_type": "invalid_json",
                                    "message": "Invalid JSON arguments for tool",
                                    "tool": function_name
                                })
                                tool_outputs.append(
                                    {"tool_call_id": tool_call.id, "output": output}
                                )
                                continue

                            logger.info("Tool call received: name=%s, thread_id=%s.", function_name, thread_id)

                            if function_name in functions:
                                try:
                                    result = await functions[function_name](**function_args)
                                    if isinstance(result, dict):
                                        if "success" not in result:
                                            result = {
                                                "success": True,
                                                "data": result
                                            }
                                    else:
                                        result = {
                                            "success": True,
                                            "data": str(result)
                                        }

                                    output = json.dumps(result)
                                except InvalidToolArgumentException as e:
                                    logger.warning("Invalid tool arguments: %s.", function_name)
                                    output = json.dumps({
                                        "success": False,
                                        "error_type": "invalid_arguments",
                                        "message": str(e),
                                        "tool": function_name
                                    })

                                except ToolExecutionException as e:
                                    logger.error("Tool execution failed: %s.", function_name)
                                    raise StreamExecutionException(
                                        message="Something went wrong while generating your project. Please try again."
                                    ) from e
                                except Exception as e:
                                    logger.exception("Unexpected tool error: %s.", function_name)
                                    output = json.dumps({
                                        "success": False,
                                        "error_type": "unexpected",
                                        "message": str(e),
                                        "tool": function_name
                                    })
                            else:
                                output = json.dumps({
                                    "success": False,
                                    "error_type": "unknown_tool",
                                    "message": f"Unknown tool: {function_name}",
                                    "tool": function_name
                                })

                            parsed_output = json.loads(output)

                            if not parsed_output.get("success", True):
                                logger.warning(
                                    "Tool returned error: name=%s, error_type=%s, message=%s.",
                                    function_name,
                                    parsed_output.get("error_type"),
                                    parsed_output.get("message")
                                )
                            else:
                                logger.info("Tool executed successfully: name=%s.", function_name)

                            tool_outputs.append(
                                {"tool_call_id": tool_call.id, "output": output}
                            )

                        try:
                            await self.project_client.agents.runs.submit_tool_outputs_stream(
                                thread_id=thread_id,
                                run_id=run_data.id,
                                tool_outputs=tool_outputs,
                                event_handler=event_handler,
                            )
                        except StreamExecutionException:
                            raise
                        except AzureError as e:
                            logger.exception(
                                "Azure error while submitting tool outputs: thread_id=%s, run_id=%s, agent_id=%s.",
                                thread_id,
                                run_data.id,
                                self.agent_id,
                            )
                            raise AzureAgentRuntimeException(
                                message="The AI service encountered an error while processing your request. Please try again."
                            ) from e

                        except Exception as e:
                            logger.exception(
                                "Unexpected error while submitting tool outputs: thread_id=%s, run_id=%s, agent_id=%s.",
                                thread_id,
                                run_data.id,
                                self.agent_id,
                            )
                            raise StreamExecutionException(
                                message="An unexpected error occurred while processing your request. Please try again."
                            ) from e

                    elif event_type == "thread.run.failed":
                        last_error = getattr(event_data, "last_error", None)
                        logger.error(
                            "Agent run failed: thread_id=%s, error=%s.", thread_id, last_error
                        )
                        raise StreamExecutionException(
                            message="The generation process failed unexpectedly. Please try again."
                        )

                    elif event_type == "thread.run.step.failed":
                        step_error = getattr(event_data, 'last_error', None)
                        logger.error(
                            "Step failed: code=%s, message=%s.",
                            getattr(step_error, 'code', None),
                            getattr(step_error, 'message', None),
                        )
                        raise StreamExecutionException(
                            message="The generation process failed unexpectedly. Please try again."
                        )

                for chunk in event_handler.get_stream_chunks():
                    yield chunk

            except asyncio.CancelledError:
                logger.warning(
                    "Stream cancelled by user/system: thread_id=%s, agent_id=%s.",
                    thread_id,
                    self.agent_id,
                )
                raise StreamCancelledException()
            except (AzureAgentRuntimeException, StreamExecutionException, AzureStreamException, StreamCancelledException):
                raise
            except AzureError as e:
                raise AzureStreamException(message="The AI service stream was interrupted. Please try again.") from e
            except Exception as e:
                logger.exception("Stream execution failed.")
                raise StreamExecutionException(
                    message="An unexpected error occurred during generation. Please try again."
                ) from e

    async def update_agent_tools(self, instructions: str) -> None:
        """
        Dynamically update Azure AI Agent tools and system instructions.

        This method synchronizes the Azure agent configuration with the latest
        domain-level tool definitions and updates the system prompt controlling
        the agent behavior.

        It performs the following operations:
        - Rebuilds the tool schema from domain tool implementations
        - Converts tools into Azure-compatible function definitions
        - Updates the agent instructions (system prompt)
        - Preserves runtime configuration such as temperature

        This ensures that any changes in business logic or workflow rules
        are immediately reflected in the running Azure AI Agent.

        Args:
            instructions (str): The updated system prompt that defines the agent's behavior,
                workflow rules, and execution constraints.

        Raises:
            AzureAgentRuntimeException: If agent update fails due to Azure SDK error,
                authentication error, or unexpected runtime issue.
        """
        logger.info("Updating Azure agent tools and instructions: agent_id=%s.", self.agent_id)

        new_tools = await self._get_tools()
        tools_payload = []

        for tool in new_tools:
            if tool.get("type") == "function":
                tools_payload.append({
                    "type": "function",
                    "function": tool["function"],
                })
        try:
            self.agent = await self.project_client.agents.update_agent(
                self.agent_id,
                tools=tools_payload,
                instructions=instructions,
                temperature=self.agent.temperature if self.agent else 0.09,
            )

            logger.info(
                "Azure agent updated successfully: agent_id=%s, tools_count=%s.",
                self.agent_id, len(tools_payload)
            )

        except (AzureError, ClientAuthenticationError, ServiceRequestError) as e:
            logger.exception("Azure SDK error updating tools.")
            raise AzureAgentRuntimeException(
                message=f"Azure error updating backlog workflow orchestrator tools: {str(e)}."
            ) from e

        except Exception as e:
            logger.exception("Failed to update backlog workflow orchestrator agent tools.")
            raise AzureAgentRuntimeException(
                message=f"Failed to update backlog workflow orchestrator agent tools: {str(e)}."
            ) from e

    async def _get_tools(self) -> list[dict]:
        """
        Build and return the Azure agent tool schema and system instructions.

        This method defines:
        - All function tools exposed to the Azure AI Agent
        - Their JSON schema (name, description, parameters)
        - Python callable bindings
        - The full system prompt controlling agent behavior

        Responsibilities:
        - Define tool contracts for the agent runtime
        - Ensure strict workflow ordering (context → market → backlog → delivery)
        - Provide detailed instructions for Flow 1 and Flow 2 execution paths
        - Enforce verification loops (market + backlog correction)

        Returns:
            - tools_json (list[dict]): List of tool definitions compatible with Azure OpenAI function calling.

        Notes:
            This method is critical for:
            - Workflow determinism
            - Tool orchestration consistency
            - Enforcing strict multi-step reasoning pipelines
        """
        tools_json = [
            {
                "type": "function",
                "function": {
                    "name": "build_product_context",
                    "description": (
                        "Transforms a raw project description into a structured product brief. "
                        "Call this FIRST to build the product context before any other tool."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "The raw project description provided by the user.",
                            }
                        },
                        "required": ["description"],
                    },
                },
                "callable": self.product_context_tool,
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_market_queries",
                    "description": (
                        "Generates targeted backlog workflow orchestrator queries from a structured product brief. "
                        "Call this ONLY if backlog workflow orchestrator is needed (flow 1). "
                        "Input must be the JSON output of build_product_context."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "detailed_description": {
                                "type": "string",
                                "description": "The structured product brief as a JSON string (output of build_product_context).",
                            }
                        },
                        "required": ["detailed_description"],
                    },
                },
                "callable": self.query_generator_tool,
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": (
                        "Searches the web for market trends, competitors, and industry data. "
                        "Use this in Flow 1 STEP 3 after generate_market_queries."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "questions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of search queries to execute.",
                            }
                        },
                        "required": ["questions"],
                    },
                },
                "callable": self.web_search_tool,
            },
            {
                "type": "function",
                "function": {
                    "name": "summarize_market_intelligence",
                    "description": (
                        "Produces a structured market intelligence summary from the product brief "
                        "and optional backlog workflow orchestrator results."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "detailed_description": {
                                "type": "string",
                                "description": "The structured product brief as a JSON string.",
                            },
                            "web_result": {
                                "type": "string",
                                "description": "Raw backlog workflow orchestrator results as a string. Omit if no backlog workflow orchestrator was performed.",
                            },
                        },
                        "required": ["detailed_description"],
                    },
                },
                "callable": self.market_summarizer_tool,
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_market_intelligence",
                    "description": (
                        "Validates and refines the market intelligence summary. "
                        "Call this AFTER summarize_market_intelligence."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "detailed_description": {
                                "type": "string",
                                "description": "The structured product brief as a JSON string.",
                            },
                            "context": {
                                "type": "string",
                                "description": "The market intelligence summary as a JSON string.",
                            },
                        },
                        "required": ["detailed_description", "context"],
                    },
                },
                "callable": self.market_validator_tool,
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_backlog",
                    "description": (
                        "Generates a full structured backlog (Epics → User Stories → Tasks). "
                        "Call this LAST, after validate_market_intelligence."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "detailed_description": {
                                "type": "string",
                                "description": "The structured product brief as a JSON string.",
                            },
                            "context": {
                                "type": "string",
                                "description": "The refined market intelligence as a JSON string.",
                            },
                        },
                        "required": ["detailed_description", "context"],
                    },
                },
                "callable": self.backlog_generator_tool,
            },
            {
                "type": "function",
                "function": {
                    "name": "fix_user_backlog",
                    "description": (
                        "Validates and fixes a user-modified backlog by comparing it with the original backlog. "
                        "This tool preserves user intent while correcting structural, logical, and consistency issues. "
                        "It must ONLY be used when a user modifies an already generated backlog."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "backlog_reference": {
                                "type": "string",
                                "description": (
                                    "Immutable backlog JSON string generated by generate_backlog tool. This is the reference baseline used to compare user modifications."
                                ),
                            },
                            "backlog_to_validate": {
                                "type": "string",
                                "description": (
                                    "User-modified backlog JSON string that must be validated and corrected."
                                ),
                            }
                        },
                        "required": [
                            "backlog_reference",
                            "backlog_to_validate"
                        ],
                    },
                },
                "callable": self.user_backlog_fixer_tool,
            },
            {
                "type": "function",
                "function": {
                    "name": "delivery_planning",
                    "description": (
                        "Generates prioritized backlog and sprint planning. "
                        "Call this ONLY after backlog is fully validated and approved by user."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "backlog": {
                                "type": "string",
                                "description": "Final validated backlog JSON string.",
                            }
                        },
                        "required": ["backlog"],
                    },
                },
                "callable": self.delivery_planner_tool,
            },
        ]

        return tools_json

    async def list_agent_tools(self) -> None:
        """
        Display all tools currently registered on the Azure AI agent.

        This method retrieves and logs:
        - The agent system instructions (if available)
        - The list of tools currently registered in the Azure agent runtime

        It is mainly used for debugging, verification, and development purposes
        to ensure that the agent is correctly configured with all expected tools
        and that tool definitions are properly synchronized.

        The output includes:
            - Tool index (1-based)
            - Tool name (for function tools)
            - Tool description (if available)
            - Tool type (for non-function tools)
        Raises:
            AzureAgentRuntimeException: If agent loading fails due to an Azure SDK or
                configuration error.

        Notes:
            - This method does not modify the agent state.
            - It is intended for debugging and observability only.
            - In production environments, this should typically be replaced
              by structured logging instead of `logs` statements.
        """
        logger.info("Listing Azure agent tools.")

        if not self.agent:
            logger.warning("Backlog Workflow Orchestrator Agent not loaded, attempting lazy load.")
            await self.load_agent()

        instructions = getattr(self.agent, "instructions", None)
        logger.info(instructions[200:] if instructions else "Agent without instructions.")

        tools = self.agent.tools
        if not tools:
            logger.info("Agent has no tools registered.")
            return

        for i, tool in enumerate(tools, 1):
            tool_type = tool.get("type", "unknown")
            if tool_type == "function":
                name = tool.get("function", {}).get("name", "Unknown")
                desc = tool.get("function", {}).get("description", "")

                logger.info("Tool %d: name=%s description=%s.", i, name, desc)
            else:
                logger.info("Tool %d: type=%s.", i, tool_type)