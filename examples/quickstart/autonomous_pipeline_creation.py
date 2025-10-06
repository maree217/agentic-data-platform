"""
Autonomous Pipeline Creation Example

This script demonstrates how to use the Agentic Data Platform to create
a complete data pipeline from scratch using autonomous agents.

Usage:
    python autonomous_pipeline_creation.py \
        --source "sqlserver-prod.dbo.sales_orders" \
        --destination "datalake-bronze.sales" \
        --schedule "daily-2am"
"""

import argparse
import asyncio
import sys
from datetime import datetime
from typing import Dict, Any

# Import agent orchestration SDK
from agents.orchestration import SupervisorAgent
from agents.config import AgentConfig
from utils.logging import setup_logging
from utils.monitoring import track_workflow

# Setup logging
logger = setup_logging(__name__)


class AutonomousPipelineCreator:
    """Orchestrates autonomous pipeline creation using multiple agents"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.supervisor = SupervisorAgent(config)

    async def create_pipeline(
        self,
        source: str,
        destination: str,
        schedule: str,
        quality_checks: bool = True,
        cost_optimize: bool = True
    ) -> Dict[str, Any]:
        """
        Create a complete data pipeline autonomously

        Args:
            source: Source system (e.g., "sqlserver-prod.dbo.sales_orders")
            destination: Destination (e.g., "datalake-bronze.sales")
            schedule: Schedule expression (e.g., "daily-2am", "hourly", "*/15 * * * *")
            quality_checks: Whether to add data quality validations
            cost_optimize: Whether to optimize for cost

        Returns:
            Dict containing pipeline details and execution summary
        """
        logger.info("🤖 Starting Autonomous Pipeline Creation")
        logger.info(f"   Source: {source}")
        logger.info(f"   Destination: {destination}")
        logger.info(f"   Schedule: {schedule}")

        # Track the entire workflow
        with track_workflow("autonomous_pipeline_creation") as workflow:
            # Step 1: Analyze requirements
            logger.info("\nStep 1/6: Analyzing requirements...")
            requirements = await self._analyze_requirements(
                source, destination, schedule
            )
            logger.info(f"   ✅ Source: {requirements['source_type']}")
            logger.info(f"   ✅ Destination: {requirements['destination_type']}")
            logger.info(f"   ✅ Mode: {requirements['load_mode']}")
            logger.info(f"   ✅ Schedule: {requirements['schedule_expression']}")

            # Step 2: Provision infrastructure (Infrastructure Agent)
            logger.info("\nStep 2/6: Provisioning infrastructure...")
            logger.info("   ⏳ Infrastructure Agent working...")

            infra_result = await self.supervisor.execute_task(
                agent="infrastructure",
                task={
                    "action": "provision",
                    "resources": requirements["required_resources"],
                    "environment": self.config.environment,
                    "estimate_cost": True
                }
            )

            logger.info(f"   ✅ {infra_result['resources_created']} resources created")
            logger.info(f"   💰 Estimated cost: ${infra_result['estimated_monthly_cost']}/month")

            # Step 3: Create pipeline (Pipeline Agent)
            logger.info("\nStep 3/6: Creating pipeline...")
            logger.info("   ⏳ Pipeline Agent working...")

            pipeline_result = await self.supervisor.execute_task(
                agent="pipeline",
                task={
                    "action": "create",
                    "source": source,
                    "destination": destination,
                    "mode": requirements["load_mode"],
                    "watermark_column": requirements.get("watermark_column"),
                    "schedule": requirements["schedule_expression"],
                    "data_factory_id": infra_result["data_factory_id"]
                }
            )

            logger.info(f"   ✅ Pipeline '{pipeline_result['pipeline_name']}' created")
            logger.info(f"   ✅ Watermark logic configured")
            logger.info(f"   ✅ Schedule trigger created")

            # Step 4: Add data quality validations (Data Quality Agent)
            if quality_checks:
                logger.info("\nStep 4/6: Adding data quality validations...")
                logger.info("   ⏳ Data Quality Agent working...")

                quality_result = await self.supervisor.execute_task(
                    agent="data-quality",
                    task={
                        "action": "create_validations",
                        "source": source,
                        "pipeline_id": pipeline_result["pipeline_id"],
                        "auto_profile": True,
                        "validation_types": [
                            "uniqueness",
                            "completeness",
                            "freshness",
                            "range"
                        ]
                    }
                )

                logger.info(f"   ✅ Data profiling complete")
                logger.info(f"   ✅ {quality_result['rules_created']} validation rules created")
                logger.info(f"   ✅ Integrated with pipeline")
            else:
                quality_result = {"rules_created": 0}
                logger.info("\nStep 4/6: Skipping data quality validations")

            # Step 5: Deploy to production (Deployment Agent)
            logger.info("\nStep 5/6: Deploying to production...")
            logger.info("   ⏳ Deployment Agent working...")

            deployment_result = await self.supervisor.execute_task(
                agent="deployment",
                task={
                    "action": "deploy",
                    "pipeline_id": pipeline_result["pipeline_id"],
                    "environment": "production",
                    "run_smoke_test": True,
                    "require_approval": self.config.environment == "prod"
                }
            )

            logger.info(f"   ✅ Deployed to production")
            logger.info(f"   ✅ Smoke test {'passed' if deployment_result['smoke_test_passed'] else 'failed'}")
            logger.info(f"   ✅ Schedule activated")

            # Step 6: Setup monitoring (Monitoring Agent)
            logger.info("\nStep 6/6: Setting up monitoring...")
            logger.info("   ⏳ Monitoring Agent working...")

            monitoring_result = await self.supervisor.execute_task(
                agent="monitoring",
                task={
                    "action": "setup_monitoring",
                    "pipeline_id": pipeline_result["pipeline_id"],
                    "alerts": [
                        {"type": "pipeline_failure", "severity": "high"},
                        {"type": "data_quality_breach", "severity": "medium"},
                        {"type": "cost_anomaly", "severity": "low"}
                    ],
                    "create_dashboard": True
                }
            )

            logger.info(f"   ✅ {monitoring_result['alerts_created']} alerts configured")
            logger.info(f"   ✅ Dashboard created")

            # Cost optimization (optional)
            if cost_optimize:
                logger.info("\nBonus: Cost Optimization...")
                logger.info("   ⏳ Cost Optimizer Agent working...")

                cost_result = await self.supervisor.execute_task(
                    agent="cost-optimizer",
                    task={
                        "action": "optimize_pipeline",
                        "pipeline_id": pipeline_result["pipeline_id"],
                        "apply_recommendations": True
                    }
                )

                if cost_result.get("savings_found"):
                    logger.info(f"   💰 Optimizations applied: ${cost_result['monthly_savings']}/month saved")
                else:
                    logger.info(f"   ✅ Pipeline already optimized")

            # Summary
            logger.info("\n🎉 Pipeline Created Successfully!\n")
            logger.info("Summary:")
            logger.info(f"  Pipeline ID: {pipeline_result['pipeline_name']}")
            logger.info(f"  Status: Active")
            logger.info(f"  Next Run: {pipeline_result['next_run_time']}")
            logger.info(f"  Estimated Monthly Cost: ${infra_result['estimated_monthly_cost']}")
            logger.info(f"  Data Quality Rules: {quality_result['rules_created']} active")
            logger.info(f"  Monitoring Dashboard: {monitoring_result['dashboard_url']}")
            logger.info(f"\nTotal Time: {workflow.duration}")
            logger.info(f"(vs. 2-3 weeks manual process)")

            return {
                "pipeline_id": pipeline_result["pipeline_id"],
                "pipeline_name": pipeline_result["pipeline_name"],
                "status": "active",
                "infrastructure": infra_result,
                "quality": quality_result,
                "monitoring": monitoring_result,
                "workflow_duration": workflow.duration
            }

    async def _analyze_requirements(
        self,
        source: str,
        destination: str,
        schedule: str
    ) -> Dict[str, Any]:
        """Analyze requirements and determine optimal configuration"""

        # Parse source and destination
        source_parts = source.split(".")
        dest_parts = destination.split(".")

        # Determine source type
        source_type = self._detect_source_type(source_parts[0])
        destination_type = self._detect_destination_type(dest_parts[0])

        # Determine load mode
        load_mode = "incremental" if source_type in ["sqlserver", "postgresql", "mysql"] else "full"

        # Determine watermark column
        watermark_column = None
        if load_mode == "incremental":
            # Use AI agent to detect best watermark column
            result = await self.supervisor.execute_task(
                agent="pipeline",
                task={
                    "action": "detect_watermark_column",
                    "source": source
                }
            )
            watermark_column = result.get("watermark_column", "modified_date")

        # Parse schedule
        schedule_expression = self._parse_schedule(schedule)

        # Determine required resources
        required_resources = self._determine_resources(source_type, destination_type)

        return {
            "source_type": source_type,
            "destination_type": destination_type,
            "load_mode": load_mode,
            "watermark_column": watermark_column,
            "schedule_expression": schedule_expression,
            "required_resources": required_resources
        }

    def _detect_source_type(self, source_prefix: str) -> str:
        """Detect source system type"""
        source_mapping = {
            "sqlserver": "sqlserver",
            "postgres": "postgresql",
            "mysql": "mysql",
            "oracle": "oracle",
            "cosmosdb": "cosmosdb",
            "blob": "blob_storage",
            "adls": "data_lake",
            "api": "rest_api"
        }
        for key, value in source_mapping.items():
            if key in source_prefix.lower():
                return value
        return "unknown"

    def _detect_destination_type(self, dest_prefix: str) -> str:
        """Detect destination type"""
        dest_mapping = {
            "datalake": "data_lake",
            "synapse": "synapse",
            "databricks": "databricks",
            "cosmos": "cosmosdb",
            "sql": "sql_database"
        }
        for key, value in dest_mapping.items():
            if key in dest_prefix.lower():
                return value
        return "data_lake"  # default

    def _parse_schedule(self, schedule: str) -> str:
        """Convert human-readable schedule to cron expression"""
        schedule_mapping = {
            "hourly": "0 * * * *",
            "daily": "0 2 * * *",
            "daily-2am": "0 2 * * *",
            "weekly": "0 2 * * 0",
            "monthly": "0 2 1 * *"
        }
        return schedule_mapping.get(schedule.lower(), schedule)

    def _determine_resources(self, source_type: str, destination_type: str) -> list:
        """Determine required Azure resources"""
        resources = ["data_factory", "storage_account"]

        if destination_type == "synapse":
            resources.append("synapse_workspace")
        elif destination_type == "databricks":
            resources.append("databricks_workspace")

        if source_type in ["sqlserver", "postgresql", "mysql"]:
            resources.append("integration_runtime")

        return resources


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Create autonomous data pipeline")
    parser.add_argument("--source", required=True, help="Source system (e.g., 'sqlserver-prod.dbo.sales_orders')")
    parser.add_argument("--destination", required=True, help="Destination (e.g., 'datalake-bronze.sales')")
    parser.add_argument("--schedule", default="daily-2am", help="Schedule (e.g., 'daily-2am', 'hourly')")
    parser.add_argument("--no-quality-checks", action="store_true", help="Skip data quality validations")
    parser.add_argument("--no-cost-optimize", action="store_true", help="Skip cost optimization")
    parser.add_argument("--environment", default="dev", help="Environment (dev, staging, prod)")

    args = parser.parse_args()

    # Load configuration
    config = AgentConfig.load_from_env(args.environment)

    # Create pipeline creator
    creator = AutonomousPipelineCreator(config)

    try:
        # Create pipeline
        result = await creator.create_pipeline(
            source=args.source,
            destination=args.destination,
            schedule=args.schedule,
            quality_checks=not args.no_quality_checks,
            cost_optimize=not args.no_cost_optimize
        )

        # Success!
        sys.exit(0)

    except Exception as e:
        logger.error(f"❌ Pipeline creation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
