"""
Service de génération de solutions pour les problèmes détectés
"""
from typing import Dict, List
from models import Mention, ReasonType

class SolutionGenerator:
    """Génère des solutions basées sur le type de problème et le contexte"""
    
    # Solutions par type de raison
    SOLUTIONS_BY_REASON = {
        ReasonType.CAMERA: {
            "short": "Improve camera quality",
            "actions": [
                "Release a software update to enhance camera processing algorithms",
                "Provide camera optimization tips to users via in-app notifications",
                "Consider offering a camera module replacement program for affected devices",
                "Engage with users on camera settings and best practices"
            ],
            "priority": "high"
        },
        ReasonType.BATTERY: {
            "short": "Optimize battery performance",
            "actions": [
                "Release a battery optimization update addressing drain issues",
                "Provide power-saving mode recommendations to users",
                "Offer battery health diagnostics through customer support",
                "Consider extending warranty for battery-related issues"
            ],
            "priority": "high"
        },
        ReasonType.PERFORMANCE: {
            "short": "Enhance device performance",
            "actions": [
                "Release performance optimization update",
                "Provide RAM management tips and app optimization guides",
                "Offer device diagnostics and cleanup tools",
                "Consider offering trade-in programs for severely affected devices"
            ],
            "priority": "medium"
        },
        ReasonType.BUILD_QUALITY: {
            "short": "Address build quality concerns",
            "actions": [
                "Review quality control processes in manufacturing",
                "Offer replacement or repair for devices with build defects",
                "Improve quality assurance testing procedures",
                "Provide transparent communication about quality improvements"
            ],
            "priority": "critical"
        },
        ReasonType.PRICE: {
            "short": "Review pricing strategy",
            "actions": [
                "Consider promotional pricing or discounts for affected customers",
                "Offer trade-in programs with better value",
                "Provide transparent pricing communication",
                "Review competitive pricing in the market"
            ],
            "priority": "medium"
        },
        ReasonType.SOFTWARE: {
            "short": "Fix software issues",
            "actions": [
                "Release bug fix updates addressing reported issues",
                "Improve software testing and QA processes",
                "Provide beta testing programs for early feedback",
                "Enhance customer support for software-related queries"
            ],
            "priority": "high"
        },
        ReasonType.CUSTOMER_SUPPORT: {
            "short": "Improve customer service",
            "actions": [
                "Train support staff on common issues and solutions",
                "Reduce response times and improve communication channels",
                "Implement customer feedback loops",
                "Offer proactive support outreach for affected users"
            ],
            "priority": "high"
        },
        ReasonType.CONNECTIVITY: {
            "short": "Improve connectivity",
            "actions": [
                "Release network optimization updates",
                "Provide connectivity troubleshooting guides",
                "Improve signal strength and network compatibility",
                "Offer network diagnostic tools"
            ],
            "priority": "medium"
        },
        ReasonType.EXPERIENCE: {
            "short": "Enhance user experience",
            "actions": [
                "Gather detailed user feedback on experience issues",
                "Implement UX improvements based on feedback",
                "Provide user guides and tutorials",
                "Engage with users to understand pain points"
            ],
            "priority": "medium"
        },
        ReasonType.DELIVERY: {
            "short": "Improve delivery experience",
            "actions": [
                "Partner with reliable delivery services",
                "Provide real-time tracking and updates",
                "Offer expedited shipping options",
                "Improve packaging to prevent damage during transit"
            ],
            "priority": "medium"
        },
        ReasonType.OTHER: {
            "short": "Address customer concerns",
            "actions": [
                "Review customer feedback and identify common themes",
                "Engage directly with affected customers",
                "Implement feedback-driven improvements",
                "Provide transparent communication about resolutions"
            ],
            "priority": "medium"
        }
    }
    
    @staticmethod
    def generate_solution(mention: Mention) -> Dict:
        """
        Génère une solution basée sur la mention et sa raison
        """
        reason = mention.reason or ReasonType.OTHER
        
        # Récupérer la solution de base
        solution_template = SolutionGenerator.SOLUTIONS_BY_REASON.get(
            reason, 
            SolutionGenerator.SOLUTIONS_BY_REASON[ReasonType.OTHER]
        )
        
        # Personnaliser selon le contenu
        content_lower = mention.content.lower()
        
        # Détecter des problèmes spécifiques
        specific_issues = []
        if "hang" in content_lower or "freeze" in content_lower:
            specific_issues.append("Device freezing/hanging issues detected")
        if "heating" in content_lower or "overheat" in content_lower:
            specific_issues.append("Overheating concerns identified")
        if "slow" in content_lower or "lag" in content_lower:
            specific_issues.append("Performance lag reported")
        if "display" in content_lower or "screen" in content_lower:
            specific_issues.append("Display-related issues found")
        
        # Construire la solution
        solution = {
            "reason": reason.value if reason else "other",
            "reason_detail": mention.reason_detail or "General issue",
            "summary": solution_template["short"],
            "priority": solution_template["priority"],
            "recommended_actions": solution_template["actions"].copy(),
            "specific_issues": specific_issues,
            "estimated_impact": SolutionGenerator._estimate_impact(mention),
            "timeline": SolutionGenerator._estimate_timeline(mention, solution_template["priority"])
        }
        
        # Ajouter des actions spécifiques si des problèmes sont détectés
        if specific_issues:
            if "freezing" in specific_issues[0].lower():
                solution["recommended_actions"].insert(0, 
                    "Immediate: Release emergency patch for freezing issues")
            if "heating" in specific_issues[0].lower():
                solution["recommended_actions"].insert(0,
                    "Immediate: Provide thermal management update")
        
        return solution
    
    @staticmethod
    def _estimate_impact(mention: Mention) -> str:
        """Estime l'impact basé sur le sentiment et la source"""
        if mention.sentiment_score < -0.7:
            return "High - Negative sentiment may affect brand reputation"
        elif mention.sentiment_score < -0.5:
            return "Medium - Moderate negative impact expected"
        else:
            return "Low - Limited impact but should be addressed"
    
    @staticmethod
    def _estimate_timeline(mention: Mention, priority: str) -> str:
        """Estime le temps de résolution"""
        if priority == "critical":
            return "1-2 weeks - Urgent action required"
        elif priority == "high":
            return "2-4 weeks - High priority resolution"
        else:
            return "1-2 months - Standard resolution timeline"
    
    @staticmethod
    def generate_bulk_solutions(mentions: List[Mention]) -> Dict:
        """Génère des solutions agrégées pour plusieurs mentions"""
        solutions_by_reason = {}
        
        for mention in mentions:
            if mention.reason:
                reason_key = mention.reason.value
                if reason_key not in solutions_by_reason:
                    solutions_by_reason[reason_key] = {
                        "count": 0,
                        "mentions": [],
                        "solution": None
                    }
                solutions_by_reason[reason_key]["count"] += 1
                solutions_by_reason[reason_key]["mentions"].append(mention)
        
        # Générer une solution pour chaque raison
        aggregated_solutions = []
        for reason_key, data in solutions_by_reason.items():
            # Utiliser la première mention comme base
            base_mention = data["mentions"][0]
            solution = SolutionGenerator.generate_solution(base_mention)
            solution["affected_count"] = data["count"]
            solution["sample_quotes"] = [
                m.content[:100] + "..." if len(m.content) > 100 else m.content
                for m in data["mentions"][:3]
            ]
            aggregated_solutions.append(solution)
        
        return {
            "total_issues": len(mentions),
            "solutions": aggregated_solutions,
            "priority_order": sorted(
                aggregated_solutions,
                key=lambda x: {"critical": 0, "high": 1, "medium": 2}.get(x["priority"], 3)
            )
        }

