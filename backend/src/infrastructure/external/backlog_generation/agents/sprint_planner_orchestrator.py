"""
Sprint planner agent.

This module defines the SprintPlannerAgent, responsible for generating sprint
planning structures from a structured backlog using an LLM. It transforms a
prioritized backlog into time-based sprint distributions suitable for agile planning.
"""

import logging

from backend.src.domain.entities.backlog.structure import BacklogStructure, EpicBacklog
from backend.src.domain.entities.sprint.planning import SprintPlanning
from backend.src.domain.entities.sprint.sprint import UserStorySprint
from backend.src.domain.ports.services.backlog_generation.agents.i_sprint_planner import ISprintPlanner
from backend.src.domain.ports.services.backlog_generation.agents.i_task_estimator import ITaskEstimator
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent
from backend.src.infrastructure.external.backlog_generation.helpers.backlog_formatter import format_backlog


logger = logging.getLogger(__name__)


class SprintPlannerAgent(BaseAgent[SprintPlanning], ISprintPlanner):
    """
    LLM-based implementation of ISprintPlanner.

    This agent is responsible for:
    - Transforming a structured backlog into sprint plans
    - Distributing epics/user stories into time-boxed iterations
    - Ensuring realistic sprint allocation based on backlog complexity
    """

    def __init__(self, prompt_loader: IPromptLoader, task_estimator: ITaskEstimator):
        """
        Initialize the SprintPlannerAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)
        self._task_estimator = task_estimator

    def generate_sprints(self, backlog: BacklogStructure) -> SprintPlanning:
        """
        Generate sprint planning from a backlog using an LLM.

        This method sends the formatted backlog to the LLM prompt pipeline and
        returns a structured sprint planning output.

        Args:
            backlog (BacklogStructure): The prioritized and cleaned backlog.

        Returns:
            SprintPlanning: The generated sprint plan structure.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: May raise underlying LLM or parsing errors from OpenAI client.
        """
        logger.info("Starting sprint planning generation.")

        context = SprintPlanning._build_context(backlog)
        # appel parallelde estimate tasks


        logger.info("Sprint planning generation completed successfully.")

        return result

    def _estimate_tasks_per_epic(self, context: str, epic: EpicBacklog) -> str:
        epic_summary = []
        result = self._task_estimator.estimate_tasks(context, epic)


    @staticmethod
    def _build_context(backlog:BacklogStructure) -> str:
        context = []

        for epic_block in backlog.epics:
            epic = epic_block.epic
            context.append(f"EPIC: {epic.title} — {epic.description}")
            context.append("")

        return "\n".join(context)



if __name__ == "__main__":
    import logging
    from backend.src.domain.entities.backlog.structure import BacklogStructure
    from backend.src.infrastructure.prompts.prompt_loader import PromptLoader

    logging.basicConfig(level=logging.INFO)

    print("\n" + "=" * 80)
    print(" SPRINT PLANNER AGENT TEST RUN ")
    print("=" * 80)

    # ---------------------------
    # INPUT BACKLOG
    # ---------------------------
    def get_input_backlog() -> BacklogStructure:
        return BacklogStructure(**{
            "epics": [
                {
                    "epic": {
                        "title": "Customer Retention Features",
                        "description": "Implement features to improve customer retention such as personalized recommendations and loyalty programs."
                    },
                    "user_stories": [
                        {
                            "user_story": {
                                "title": "Loyalty Program Enrollment",
                                "description": "As an online shopper, I want to enroll in a loyalty program so that I can earn rewards on my purchases."
                            },
                            "tasks": [
                                {"title": "Design loyalty program data model",
                                 "description": "Create DB schema for loyalty points."},
                                {"title": "Implement loyalty enrollment API",
                                 "description": "Build enrollment endpoint."},
                                {"title": "Build loyalty program UI", "description": "Create loyalty UI."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Personalized Recommendations",
                                "description": "As an online shopper, I want to see personalized product recommendations so that I can discover items relevant to my interests."
                            },
                            "tasks": [
                                {"title": "Implement recommendation engine",
                                 "description": "Build recommendation logic."},
                                {"title": "Integrate recommendations into product pages",
                                 "description": "Show recommendations on product page."},
                                {"title": "Test recommendation accuracy",
                                 "description": "Validate recommendation quality."}
                            ]
                        }
                    ]
                },
                {
                    "epic": {
                        "title": "Order Tracking",
                        "description": "Allow users to track the status of their orders in real-time, ensuring transparency and improving customer satisfaction."
                    },
                    "user_stories": [
                        {
                            "user_story": {
                                "title": "Provide Feedback on Delivery",
                                "description": "As an online shopper, I want to provide feedback on the delivery experience so that the platform can improve its service quality."
                            },
                            "tasks": [
                                {"title": "Design feedback submission UI", "description": "Build feedback form."},
                                {"title": "Implement feedback submission API endpoint",
                                 "description": "Create feedback endpoint."},
                                {"title": "Add feedback data model", "description": "Create feedback schema."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "View Order Status",
                                "description": "As an online shopper, I want to view the real-time status of my order so that I can stay informed about its progress and expected delivery time."
                            },
                            "tasks": [
                                {"title": "Design and implement the order status API endpoint",
                                 "description": "Create order status endpoint."},
                                {"title": "Develop frontend UI for order status display",
                                 "description": "Build order status page."},
                                {"title": "Implement real-time order status updates",
                                 "description": "Add real-time updates."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Track Delivery Location",
                                "description": "As an online shopper, I want to track the delivery location of my order in real-time so that I can anticipate its arrival."
                            },
                            "tasks": [
                                {"title": "Design delivery location tracking API",
                                 "description": "Create tracking endpoint."},
                                {"title": "Develop frontend UI for real-time delivery tracking",
                                 "description": "Build tracking UI."},
                                {"title": "Integrate map service for location visualization",
                                 "description": "Add map integration."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Access Order History",
                                "description": "As an online shopper, I want to access my past order details so that I can review my purchases and manage returns easily."
                            },
                            "tasks": [
                                {"title": "Design database schema for order history",
                                 "description": "Create order history schema."},
                                {"title": "Implement backend API for order history",
                                 "description": "Build order history endpoint."},
                                {"title": "Develop frontend UI for order history",
                                 "description": "Build order history page."}
                            ]
                        }
                    ]
                },
                {
                    "epic": {
                        "title": "Shopping Cart Functionality",
                        "description": "Provide users with the ability to add, remove, and manage items in their shopping cart."
                    },
                    "user_stories": [
                        {
                            "user_story": {
                                "title": "Save Cart for Later",
                                "description": "As an online shopper, I want to save my shopping cart for later so that I can return and complete my purchase at a convenient time."
                            },
                            "tasks": [
                                {"title": "Design backend API for saving cart",
                                 "description": "Create save cart endpoint."},
                                {"title": "Update database schema for saved carts",
                                 "description": "Add saved carts table."},
                                {"title": "Implement frontend UI for saving cart",
                                 "description": "Build save cart button."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Add Items to Cart",
                                "description": "As an online shopper, I want to add items to my shopping cart so that I can easily purchase multiple products in one transaction."
                            },
                            "tasks": [
                                {"title": "Design and implement Add to Cart API endpoint",
                                 "description": "Create endpoint for adding items to cart."},
                                {"title": "Update shopping cart data model",
                                 "description": "Update DB schema for cart items."},
                                {"title": "Develop frontend UI for Add to Cart",
                                 "description": "Build add to cart button and logic."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Mobile-Optimized Cart Management",
                                "description": "As an online shopper, I want the shopping cart interface to be optimized for mobile devices so that I can manage my cart easily on my smartphone."
                            },
                            "tasks": [
                                {"title": "Design mobile-responsive cart UI",
                                 "description": "Design responsive cart layout."},
                                {"title": "Implement mobile-responsive cart layout",
                                 "description": "Build responsive cart."},
                                {"title": "Optimize cart API for mobile performance",
                                 "description": "Optimize API response times."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "View Cart Summary",
                                "description": "As an online shopper, I want to view a summary of my shopping cart so that I can review items and total cost before checkout."
                            },
                            "tasks": [
                                {"title": "Design and implement cart summary API endpoint",
                                 "description": "Create cart summary endpoint."},
                                {"title": "Develop frontend UI for cart summary display",
                                 "description": "Build cart summary page."},
                                {"title": "Write unit and integration tests for cart summary",
                                 "description": "Test cart summary."}
                            ]
                        }
                    ]
                },
                {
                    "epic": {
                        "title": "Payment Processing",
                        "description": "Support secure and efficient payment processing to facilitate transactions and enhance user trust."
                    },
                    "user_stories": [
                        {
                            "user_story": {
                                "title": "Refund Processing",
                                "description": "As an online shopper, I want a clear and efficient refund process so that I can resolve issues with my purchases without hassle."
                            },
                            "tasks": [
                                {"title": "Design refund request data model",
                                 "description": "Create refund data model."},
                                {"title": "Implement refund request API endpoint",
                                 "description": "Build refund endpoint."},
                                {"title": "Build refund request UI", "description": "Create refund UI."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Secure Payment Options",
                                "description": "As an online shopper, I want secure payment options so that I can confidently complete my purchases without worrying about fraud."
                            },
                            "tasks": [
                                {"title": "Design and implement secure payment API endpoints",
                                 "description": "Create secure payment endpoints."},
                                {"title": "Integrate third-party payment gateway",
                                 "description": "Integrate payment provider."},
                                {"title": "Validate payment inputs", "description": "Validate all payment fields."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Multiple Payment Methods",
                                "description": "As an online shopper, I want access to multiple payment methods so that I can choose the one that best suits my preferences."
                            },
                            "tasks": [
                                {"title": "Design database schema for payment methods",
                                 "description": "Create schema for payment methods."},
                                {"title": "Implement backend logic for payment method selection",
                                 "description": "Handle payment method selection."},
                                {"title": "Create frontend UI for payment method selection",
                                 "description": "Build payment method selector."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Transaction Confirmation",
                                "description": "As an online shopper, I want immediate transaction confirmation so that I know my payment was successful."
                            },
                            "tasks": [
                                {"title": "Implement backend endpoint for transaction confirmation",
                                 "description": "Create confirmation endpoint."},
                                {"title": "Design and implement transaction confirmation UI",
                                 "description": "Build confirmation page."},
                                {"title": "Write unit and integration tests for transaction confirmation",
                                 "description": "Test confirmation flow."}
                            ]
                        }
                    ]
                },
                {
                    "epic": {
                        "title": "Product Catalog Management",
                        "description": "Enable users to browse and search through a comprehensive catalog of fashion products."
                    },
                    "user_stories": [
                        {
                            "user_story": {
                                "title": "Save Favorites",
                                "description": "As an online shopper, I want to save products to a favorites list so that I can revisit them later without searching again."
                            },
                            "tasks": [
                                {"title": "Design database schema for favorites list",
                                 "description": "Create DB schema for user favorites."},
                                {"title": "Develop backend API endpoints for favorites",
                                 "description": "Implement CRUD endpoints for favorites."},
                                {"title": "Implement frontend UI for favorites",
                                 "description": "Build favorites list UI."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Browse and Search Products",
                                "description": "As an online shopper, I want to browse and search through a visually appealing catalog so that I can easily find fashion items that interest me."
                            },
                            "tasks": [
                                {"title": "Design and implement product catalog and search API",
                                 "description": "Create RESTful endpoints for browsing and searching products."},
                                {"title": "Develop frontend UI for product catalog and search",
                                 "description": "Build responsive UI components for product listing."},
                                {"title": "Optimize database queries for catalog and search",
                                 "description": "Add indexes and optimize queries for performance."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "View Product Details",
                                "description": "As an online shopper, I want to view detailed information and high-quality images of fashion products so that I can make informed purchasing decisions."
                            },
                            "tasks": [
                                {"title": "Design and implement product details API endpoint",
                                 "description": "Create endpoint to retrieve full product details."},
                                {"title": "Develop frontend UI for product details page",
                                 "description": "Build product detail page with images and info."},
                                {"title": "Implement image carousel for product images",
                                 "description": "Add interactive image carousel component."}
                            ]
                        }
                    ]
                },
                {
                    "epic": {
                        "title": "Authentication / Identity / Access Control (RBAC)",
                        "description": "Ensure secure access through authentication and role-based permissions for both shoppers and retailers."
                    },
                    "user_stories": [
                        {
                            "user_story": {
                                "title": "Account activity tracking for retailers",
                                "description": "As a fashion retailer, I want to view account activity logs so that I can monitor and ensure secure usage of my team's accounts."
                            },
                            "tasks": [
                                {"title": "Design account activity log database schema",
                                 "description": "Create activity log schema."},
                                {"title": "Develop backend API for activity logs",
                                 "description": "Build activity log endpoint."},
                                {"title": "Implement frontend UI for activity logs",
                                 "description": "Build activity log UI."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Secure shopper authentication",
                                "description": "As an online shopper, I want to securely log into my account so that my personal and payment information is protected."
                            },
                            "tasks": [
                                {"title": "Design and implement secure login API endpoint",
                                 "description": "Build secure login endpoint."},
                                {"title": "Implement frontend login form", "description": "Build login form UI."},
                                {"title": "Secure sensitive data transmission",
                                 "description": "Use HTTPS for data security."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Multi-factor authentication for shoppers",
                                "description": "As an online shopper, I want multi-factor authentication options so that I can add an extra layer of security to my account."
                            },
                            "tasks": [
                                {"title": "Design database schema for MFA", "description": "Create MFA schema."},
                                {"title": "Implement backend logic for MFA", "description": "Build MFA logic."},
                                {"title": "Create frontend UI for MFA", "description": "Build MFA UI."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Retailer role-based access",
                                "description": "As a fashion retailer, I want role-based access controls for my team so that sensitive business data is only accessible to authorized personnel."
                            },
                            "tasks": [
                                {"title": "Design role-based access control schema",
                                 "description": "Define RBAC data model."},
                                {"title": "Implement backend RBAC logic", "description": "Build RBAC logic."},
                                {"title": "Create role management API endpoints",
                                 "description": "Build role management endpoints."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Password recovery for shoppers",
                                "description": "As an online shopper, I want a simple password recovery process so that I can regain access to my account if I forget my credentials."
                            },
                            "tasks": [
                                {"title": "Design password recovery API endpoint",
                                 "description": "Build password recovery endpoint."},
                                {"title": "Implement email notification for password recovery",
                                 "description": "Send recovery emails."},
                                {"title": "Develop password recovery UI flow", "description": "Build recovery UI."}
                            ]
                        }
                    ]
                },
                {
                    "epic": {
                        "title": "User Account Management",
                        "description": "Enable users to create and manage their accounts, including personal information and order history."
                    },
                    "user_stories": [
                        {
                            "user_story": {
                                "title": "Order History Access",
                                "description": "As an online shopper, I want to view my order history in my account so that I can track past purchases and manage returns effectively."
                            },
                            "tasks": [
                                {"title": "Design database schema for order history",
                                 "description": "Create order history schema."},
                                {"title": "Implement backend API for order history",
                                 "description": "Build order history endpoint."},
                                {"title": "Develop frontend UI for order history display",
                                 "description": "Build order history UI."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Account Creation",
                                "description": "As an online shopper, I want to create an account easily so that I can save my preferences and streamline future purchases."
                            },
                            "tasks": [
                                {"title": "Design and implement user registration API",
                                 "description": "Build registration endpoint."},
                                {"title": "Develop frontend registration form",
                                 "description": "Build registration form."},
                                {"title": "Integrate email verification process",
                                 "description": "Add email verification."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Account Security Features",
                                "description": "As an online shopper, I want secure login and account recovery options so that my personal data is protected."
                            },
                            "tasks": [
                                {"title": "Implement secure login endpoint", "description": "Build secure login."},
                                {"title": "Design and implement account recovery endpoint",
                                 "description": "Build recovery endpoint."},
                                {"title": "Integrate email service for account recovery",
                                 "description": "Add email for recovery."}
                            ]
                        },
                        {
                            "user_story": {
                                "title": "Personal Information Management",
                                "description": "As an online shopper, I want to update my personal information in my account so that my profile remains accurate and personalized."
                            },
                            "tasks": [
                                {"title": "Design and implement personal information update API",
                                 "description": "Build profile update endpoint."},
                                {"title": "Implement frontend UI for personal information management",
                                 "description": "Build profile edit UI."},
                                {"title": "Add security measures for personal information updates",
                                 "description": "Secure profile updates."}
                            ]
                        }
                    ]
                }
            ]
        })

    # ---------------------------
    # ASSERTIONS HELPER
    # ---------------------------
    def evaluate(result):
        print(f"\nASSERTIONS:")

        if not result or not result.sprints:
            print("  ❌ No sprints generated")
            return

        print(f"  ✅ Sprint count: {len(result.sprints)}")

        total_tasks = 0
        total_hours = 0.0

        for sprint in result.sprints:
            sprint_name = sprint.name

            # Rule: sprint must have a goal
            if not sprint.goal or not sprint.goal.strip():
                print(f"  ❌ Sprint '{sprint_name}' has no goal")
            else:
                print(f"  ✅ Sprint OK: '{sprint_name}' | Goal: '{sprint.goal}'")

            # Rule: sprint must have user stories
            if not sprint.user_stories:
                print(f"  ❌ Sprint '{sprint_name}' has no user stories")
                continue

            # Rule: total_estimated_hours must match sum of task hours
            computed_hours = sum(
                task.estimated_hours
                for us in sprint.user_stories
                for task in us.tasks
            )
            if abs(computed_hours - sprint.total_estimated_hours) > 0.1:
                print(f"  ❌ Sprint '{sprint_name}': total_estimated_hours mismatch "
                      f"(declared={sprint.total_estimated_hours}, computed={computed_hours:.1f})")
            else:
                print(f"  ✅ Hours match: {sprint.total_estimated_hours}h")

            # Rule: capacity check (120-160h range with buffer)
            if sprint.total_estimated_hours > 160:
                print(f"  ⚠️  Sprint '{sprint_name}' exceeds 160h capacity: {sprint.total_estimated_hours}h")
            elif sprint.total_estimated_hours < 20:
                print(f"  ⚠️  Sprint '{sprint_name}' seems under-loaded: {sprint.total_estimated_hours}h")

            for us_block in sprint.user_stories:
                us_title = us_block.user_story.title
                total_tasks += len(us_block.tasks)

                # Rule: every user story must have tasks
                if not us_block.tasks:
                    print(f"    ❌ Story '{us_title}' has no tasks")
                    continue

                print(f"    ✅ Story OK: '{us_title}' ({len(us_block.tasks)} tasks)")

                # Rule: every task must have estimated_hours > 0
                for task in us_block.tasks:
                    if task.estimated_hours <= 0:
                        print(f"      ❌ Task '{task.title}' has invalid hours: {task.estimated_hours}")

            total_hours += sprint.total_estimated_hours

        print(f"\n  📊 Summary: {len(result.sprints)} sprints | {total_tasks} tasks | {total_hours:.1f}h total")

    # ---------------------------
    # RUN TEST
    # ---------------------------
    agent = SprintPlannerAgent(prompt_loader=PromptLoader())

    print("\n" + "-" * 80)
    print("TEST: Sprint planning from large backlog")
    print("-" * 80)

    try:
        backlog = get_input_backlog()
        result = agent.generate_sprints(backlog=backlog)

        print(f"\nGENERATED SPRINT PLAN ({len(result.sprints)} sprints):")
        for sprint in result.sprints:
            print(f"\n  🏃 {sprint.name}")
            print(f"     Goal: {sprint.goal}")
            print(f"     Hours: {sprint.total_estimated_hours}h")
            for us_block in sprint.user_stories:
                print(f"\n    📖 {us_block.user_story.title}")
                for task in us_block.tasks:
                    print(f"      🔧 {task.title} ({task.estimated_hours}h)")

        evaluate(result)

    except Exception as e:
        print(f"\nERROR: {str(e)}")

    print("\n" + "=" * 80)
    print(" END OF TEST RUN ")
    print("=" * 80)