"""
Weekly Cost Optimization Example

Demonstrates autonomous cost optimization using the Cost Optimizer Agent.
This script runs weekly to analyze cloud spend and implement cost-saving measures.

Usage:
    # Run cost optimization
    python weekly_review.py --environment prod

    # Dry run (no changes)
    python weekly_review.py --environment prod --dry-run

    # Auto-approve non-production changes
    python weekly_review.py --environment dev --auto-approve
"""

import argparse
import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any

from agents.infrastructure import CostOptimizerAgent
from agents.config import AgentConfig
from utils.logging import setup_logging
from utils.notifications import send_slack_notification, send_email

logger = setup_logging(__name__)


class WeeklyCostReviewer:
    """Orchestrates weekly cost review and optimization"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.cost_agent = CostOptimizerAgent(config)

    async def run_weekly_review(
        self,
        dry_run: bool = False,
        auto_approve_nonprod: bool = False
    ) -> Dict[str, Any]:
        """
        Run comprehensive weekly cost review

        Args:
            dry_run: If True, only analyze without making changes
            auto_approve_nonprod: If True, auto-approve non-production optimizations

        Returns:
            Dict containing analysis results and actions taken
        """
        logger.info("💰 Weekly Cost Optimization Review")
        logger.info(f"   Environment: {self.config.environment}")
        logger.info(f"   Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        logger.info(f"   Date: {datetime.now().strftime('%Y-%m-%d')}\n")

        # Step 1: Analyze current spend
        logger.info("Step 1/5: Analyzing current cloud spend...")
        spend_analysis = await self._analyze_spend()

        logger.info(f"   📊 Total monthly spend: ${spend_analysis['total_monthly_cost']:,.2f}")
        logger.info(f"   📈 Trend: {spend_analysis['trend']}")
        logger.info(f"   🔍 Top 5 cost drivers:")
        for i, driver in enumerate(spend_analysis['top_cost_drivers'][:5], 1):
            logger.info(f"      {i}. {driver['service']}: ${driver['cost']:,.2f}/month")

        # Step 2: Identify optimization opportunities
        logger.info("\nStep 2/5: Identifying optimization opportunities...")
        opportunities = await self.cost_agent.find_opportunities()

        total_potential_savings = sum(opp['monthly_savings'] for opp in opportunities)
        logger.info(f"   💡 Found {len(opportunities)} opportunities")
        logger.info(f"   💰 Total potential savings: ${total_potential_savings:,.2f}/month\n")

        # Display opportunities
        for i, opp in enumerate(opportunities, 1):
            logger.info(f"   {i}. {opp['title']}")
            logger.info(f"      Savings: ${opp['monthly_savings']:,.2f}/month")
            logger.info(f"      Impact: {opp['impact']}")
            logger.info(f"      Risk: {opp['risk_level']}")
            logger.info("")

        # Step 3: Categorize opportunities
        logger.info("Step 3/5: Categorizing opportunities...")
        categorized = self._categorize_opportunities(opportunities)

        logger.info(f"   🟢 Low-risk (auto-approve): {len(categorized['low_risk'])} items")
        logger.info(f"   🟡 Medium-risk (review): {len(categorized['medium_risk'])} items")
        logger.info(f"   🔴 High-risk (requires approval): {len(categorized['high_risk'])} items")

        # Step 4: Execute optimizations
        if not dry_run:
            logger.info("\nStep 4/5: Executing optimizations...")
            results = await self._execute_optimizations(
                categorized,
                auto_approve_nonprod=auto_approve_nonprod
            )

            logger.info(f"   ✅ Applied: {results['applied_count']} optimizations")
            logger.info(f"   ⏳ Pending approval: {results['pending_count']} optimizations")
            logger.info(f"   ⏭️  Skipped: {results['skipped_count']} optimizations")
            logger.info(f"   💰 Total savings (applied): ${results['actual_savings']:,.2f}/month")
        else:
            logger.info("\nStep 4/5: Skipping execution (dry run mode)")
            results = {"applied_count": 0, "pending_count": 0, "skipped_count": 0, "actual_savings": 0}

        # Step 5: Generate report and notifications
        logger.info("\nStep 5/5: Generating report...")
        report = self._generate_report(
            spend_analysis,
            opportunities,
            categorized,
            results,
            dry_run
        )

        # Send notifications
        await self._send_notifications(report)

        logger.info("\n✅ Weekly cost review complete!")
        logger.info(f"   📊 Full report: {report['report_url']}")

        return report

    async def _analyze_spend(self) -> Dict[str, Any]:
        """Analyze current cloud spending"""
        # Get cost data from Azure Cost Management API
        analysis = await self.cost_agent.analyze_spend(
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            group_by=["service", "resource_group", "tags"]
        )

        return {
            "total_monthly_cost": analysis["total_cost"],
            "trend": analysis["trend"],  # "increasing", "stable", "decreasing"
            "top_cost_drivers": analysis["cost_breakdown"],
            "anomalies": analysis["anomalies"]
        }

    def _categorize_opportunities(
        self,
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize opportunities by risk level"""
        categorized = {
            "low_risk": [],
            "medium_risk": [],
            "high_risk": []
        }

        for opp in opportunities:
            risk_level = opp["risk_level"]
            if risk_level == "low":
                categorized["low_risk"].append(opp)
            elif risk_level == "medium":
                categorized["medium_risk"].append(opp)
            else:
                categorized["high_risk"].append(opp)

        return categorized

    async def _execute_optimizations(
        self,
        categorized: Dict[str, List[Dict[str, Any]]],
        auto_approve_nonprod: bool = False
    ) -> Dict[str, Any]:
        """Execute optimizations based on risk level and approval settings"""
        applied_count = 0
        pending_count = 0
        skipped_count = 0
        actual_savings = 0

        # Auto-apply low-risk optimizations
        logger.info("\n   Applying low-risk optimizations...")
        for opp in categorized["low_risk"]:
            if self.config.environment != "prod" and auto_approve_nonprod:
                result = await self.cost_agent.apply_optimization(opp)
                if result["success"]:
                    applied_count += 1
                    actual_savings += opp["monthly_savings"]
                    logger.info(f"      ✅ {opp['title']}")
                else:
                    skipped_count += 1
                    logger.info(f"      ⏭️  {opp['title']} (failed: {result['error']})")
            else:
                pending_count += 1
                logger.info(f"      ⏳ {opp['title']} (requires approval)")

        # Medium-risk: require approval
        logger.info("\n   Medium-risk optimizations (requires review)...")
        for opp in categorized["medium_risk"]:
            pending_count += 1
            logger.info(f"      ⏳ {opp['title']}")

        # High-risk: always require explicit approval
        logger.info("\n   High-risk optimizations (requires explicit approval)...")
        for opp in categorized["high_risk"]:
            pending_count += 1
            logger.info(f"      🔴 {opp['title']}")

        return {
            "applied_count": applied_count,
            "pending_count": pending_count,
            "skipped_count": skipped_count,
            "actual_savings": actual_savings
        }

    def _generate_report(
        self,
        spend_analysis: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        categorized: Dict[str, List[Dict[str, Any]]],
        results: Dict[str, Any],
        dry_run: bool
    ) -> Dict[str, Any]:
        """Generate comprehensive cost optimization report"""

        total_potential_savings = sum(opp['monthly_savings'] for opp in opportunities)
        savings_percentage = (total_potential_savings / spend_analysis['total_monthly_cost']) * 100

        report = {
            "date": datetime.now().isoformat(),
            "environment": self.config.environment,
            "dry_run": dry_run,
            "spend_summary": {
                "total_monthly_cost": spend_analysis['total_monthly_cost'],
                "trend": spend_analysis['trend'],
                "top_cost_drivers": spend_analysis['top_cost_drivers'][:5]
            },
            "optimization_summary": {
                "opportunities_found": len(opportunities),
                "total_potential_savings": total_potential_savings,
                "savings_percentage": savings_percentage,
                "low_risk_count": len(categorized['low_risk']),
                "medium_risk_count": len(categorized['medium_risk']),
                "high_risk_count": len(categorized['high_risk'])
            },
            "actions_taken": {
                "applied_count": results['applied_count'],
                "pending_count": results['pending_count'],
                "skipped_count": results['skipped_count'],
                "actual_savings": results['actual_savings']
            },
            "opportunities": opportunities,
            "report_url": f"https://portal.azure.com/cost-reports/{datetime.now().strftime('%Y-%m-%d')}"
        }

        return report

    async def _send_notifications(self, report: Dict[str, Any]):
        """Send notifications to stakeholders"""
        # Slack notification
        slack_message = self._format_slack_message(report)
        await send_slack_notification(slack_message)

        # Email for high-savings opportunities
        if report['optimization_summary']['total_potential_savings'] > 1000:
            email_html = self._format_email(report)
            await send_email(
                to=self.config.cost_notification_emails,
                subject=f"Cost Optimization Review: ${report['optimization_summary']['total_potential_savings']:,.0f}/month savings available",
                html=email_html
            )

    def _format_slack_message(self, report: Dict[str, Any]) -> str:
        """Format Slack notification message"""
        savings = report['optimization_summary']['total_potential_savings']
        percentage = report['optimization_summary']['savings_percentage']

        message = f"""
💰 *Weekly Cost Optimization Report*

*Environment:* {report['environment']}
*Current Monthly Spend:* ${report['spend_summary']['total_monthly_cost']:,.2f}
*Potential Savings:* ${savings:,.2f}/month ({percentage:.1f}%)

*Opportunities Found:* {report['optimization_summary']['opportunities_found']}
🟢 Low-risk: {report['optimization_summary']['low_risk_count']}
🟡 Medium-risk: {report['optimization_summary']['medium_risk_count']}
🔴 High-risk: {report['optimization_summary']['high_risk_count']}

*Actions Taken:*
✅ Applied: {report['actions_taken']['applied_count']} (${report['actions_taken']['actual_savings']:,.2f} saved)
⏳ Pending Approval: {report['actions_taken']['pending_count']}

<{report['report_url']}|View Full Report>
        """
        return message

    def _format_email(self, report: Dict[str, Any]) -> str:
        """Format email notification"""
        # HTML email template
        html = f"""
        <html>
        <body>
            <h2>Weekly Cost Optimization Report</h2>
            <p><strong>Environment:</strong> {report['environment']}</p>

            <h3>Spend Summary</h3>
            <ul>
                <li>Total Monthly Cost: ${report['spend_summary']['total_monthly_cost']:,.2f}</li>
                <li>Trend: {report['spend_summary']['trend']}</li>
            </ul>

            <h3>Optimization Opportunities</h3>
            <p>
                Potential Savings: <strong>${report['optimization_summary']['total_potential_savings']:,.2f}/month</strong>
                ({report['optimization_summary']['savings_percentage']:.1f}%)
            </p>

            <table border="1" cellpadding="5">
                <tr>
                    <th>Risk Level</th>
                    <th>Count</th>
                </tr>
                <tr>
                    <td>🟢 Low-risk</td>
                    <td>{report['optimization_summary']['low_risk_count']}</td>
                </tr>
                <tr>
                    <td>🟡 Medium-risk</td>
                    <td>{report['optimization_summary']['medium_risk_count']}</td>
                </tr>
                <tr>
                    <td>🔴 High-risk</td>
                    <td>{report['optimization_summary']['high_risk_count']}</td>
                </tr>
            </table>

            <h3>Actions Taken</h3>
            <ul>
                <li>✅ Applied: {report['actions_taken']['applied_count']} (${report['actions_taken']['actual_savings']:,.2f} saved)</li>
                <li>⏳ Pending Approval: {report['actions_taken']['pending_count']}</li>
            </ul>

            <p><a href="{report['report_url']}">View Full Report in Azure Portal</a></p>
        </body>
        </html>
        """
        return html


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Weekly cost optimization review")
    parser.add_argument("--environment", default="dev", help="Environment (dev, staging, prod)")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only, don't make changes")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve non-production changes")

    args = parser.parse_args()

    # Load configuration
    config = AgentConfig.load_from_env(args.environment)

    # Create cost reviewer
    reviewer = WeeklyCostReviewer(config)

    try:
        # Run weekly review
        report = await reviewer.run_weekly_review(
            dry_run=args.dry_run,
            auto_approve_nonprod=args.auto_approve
        )

        sys.exit(0)

    except Exception as e:
        logger.error(f"❌ Cost review failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
