"""
Evaluator Classes for Testing Agent Quality

Provides end-to-end evaluation of:
- Search agents
- Recommendation agents
- Complete agent system
"""

from typing import List, Dict, Any, Tuple
import time
import json
from datetime import datetime
from .metrics import (
    SearchMetrics,
    RecommendationMetrics,
    ResponseQualityMetrics,
    AgentPerformanceMetrics,
    calculate_all_metrics
)


class SearchEvaluator:
    """Evaluate search agent quality"""
    
    def __init__(self):
        self.metrics = SearchMetrics()
        self.results = []
    
    def evaluate_query(self, 
                      query: str,
                      retrieved_products: List[int],
                      relevant_products: List[int],
                      execution_time: float) -> Dict[str, Any]:
        """
        Evaluate a single search query
        
        Args:
            query: User's search query
            retrieved_products: Products returned by search agent
            relevant_products: Ground truth relevant products
            execution_time: Time taken to execute (seconds)
            
        Returns:
            Evaluation results
        """
        result = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'precision@5': self.metrics.precision_at_k(retrieved_products, relevant_products, k=5),
                'precision@10': self.metrics.precision_at_k(retrieved_products, relevant_products, k=10),
                'recall@5': self.metrics.recall_at_k(retrieved_products, relevant_products, k=5),
                'recall@10': self.metrics.recall_at_k(retrieved_products, relevant_products, k=10),
                'ndcg@10': self.metrics.ndcg_at_k(retrieved_products, relevant_products, k=10),
            },
            'performance': {
                'latency': execution_time,
                'meets_sla': execution_time < 2.0,
                'results_returned': len(retrieved_products),
                'relevant_found': len(set(retrieved_products) & set(relevant_products))
            }
        }
        
        self.results.append(result)
        return result
    
    def get_aggregate_metrics(self) -> Dict[str, Any]:
        """Calculate average metrics across all queries"""
        if not self.results:
            return {}
        
        import numpy as np
        
        return {
            'total_queries': len(self.results),
            'average_precision@10': np.mean([r['metrics']['precision@10'] for r in self.results]),
            'average_recall@10': np.mean([r['metrics']['recall@10'] for r in self.results]),
            'average_ndcg@10': np.mean([r['metrics']['ndcg@10'] for r in self.results]),
            'average_latency': np.mean([r['performance']['latency'] for r in self.results]),
            'sla_compliance': sum(1 for r in self.results if r['performance']['meets_sla']) / len(self.results)
        }
    
    def generate_report(self, filepath: str = None) -> str:
        """Generate evaluation report"""
        agg_metrics = self.get_aggregate_metrics()
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║        SEARCH AGENT EVALUATION REPORT                    ║
╚══════════════════════════════════════════════════════════╝

📊 OVERALL METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Queries Evaluated: {agg_metrics.get('total_queries', 0)}

🎯 ACCURACY METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average Precision@10:    {agg_metrics.get('average_precision@10', 0):.3f}
Average Recall@10:       {agg_metrics.get('average_recall@10', 0):.3f}
Average NDCG@10:         {agg_metrics.get('average_ndcg@10', 0):.3f}

⚡ PERFORMANCE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average Latency:         {agg_metrics.get('average_latency', 0):.3f}s
SLA Compliance (<2s):    {agg_metrics.get('sla_compliance', 0)*100:.1f}%

✅ QUALITY ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Add quality grade
        avg_ndcg = agg_metrics.get('average_ndcg@10', 0)
        if avg_ndcg >= 0.8:
            report += "Grade: EXCELLENT ⭐⭐⭐⭐⭐\n"
        elif avg_ndcg >= 0.6:
            report += "Grade: GOOD ⭐⭐⭐⭐\n"
        elif avg_ndcg >= 0.4:
            report += "Grade: FAIR ⭐⭐⭐\n"
        else:
            report += "Grade: NEEDS IMPROVEMENT ⭐⭐\n"
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(report)
        
        return report


class RecommendationEvaluator:
    """Evaluate recommendation quality"""
    
    def __init__(self):
        self.metrics = RecommendationMetrics()
        self.results = []
    
    def evaluate_recommendations(self,
                                user_id: int,
                                recommendations: List[int],
                                ground_truth: List[int],
                                total_products: int) -> Dict[str, Any]:
        """
        Evaluate recommendations for a user
        
        Args:
            user_id: User identifier
            recommendations: Recommended product IDs
            ground_truth: Products user actually liked/bought
            total_products: Total products in catalog
            
        Returns:
            Evaluation results
        """
        result = {
            'user_id': user_id,
            'metrics': {
                'hit_rate@5': int(bool(set(recommendations[:5]) & set(ground_truth))),
                'hit_rate@10': int(bool(set(recommendations[:10]) & set(ground_truth))),
                'precision@10': len(set(recommendations[:10]) & set(ground_truth)) / 10,
                'recall@10': len(set(recommendations[:10]) & set(ground_truth)) / len(ground_truth) if ground_truth else 0
            }
        }
        
        self.results.append(result)
        return result


class ResponseEvaluator:
    """Evaluate LLM response quality"""
    
    def __init__(self):
        self.metrics = ResponseQualityMetrics()
        self.results = []
    
    def evaluate_response(self,
                         query: str,
                         response: str,
                         ground_truth: Dict[str, Any],
                         product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate agent response quality
        
        Args:
            query: User query
            response: Agent's response
            ground_truth: Expected facts
            product_data: Actual product information
            
        Returns:
            Evaluation results
        """
        result = {
            'query': query,
            'response_length': len(response),
            'metrics': {
                'factual_accuracy': self.metrics.factual_accuracy(response, ground_truth),
                'completeness': self.metrics.completeness_score(
                    response,
                    ['price', 'rating', 'features', 'pros', 'cons']
                ),
                'helpfulness': self.metrics.helpfulness_score(response),
                'hallucination': self.metrics.hallucination_check(response, product_data)
            }
        }
        
        self.results.append(result)
        return result
    
    def generate_report(self) -> str:
        """Generate response quality report"""
        if not self.results:
            return "No results to report"
        
        import numpy as np
        
        avg_accuracy = np.mean([r['metrics']['factual_accuracy'] for r in self.results])
        avg_completeness = np.mean([r['metrics']['completeness'] for r in self.results])
        avg_helpfulness = np.mean([r['metrics']['helpfulness']['overall_score'] for r in self.results])
        hallucination_rate = sum(1 for r in self.results if r['metrics']['hallucination']['has_hallucinations']) / len(self.results)
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║      RESPONSE QUALITY EVALUATION REPORT                  ║
╚══════════════════════════════════════════════════════════╝

📊 EVALUATED RESPONSES: {len(self.results)}

✅ QUALITY METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Factual Accuracy:        {avg_accuracy*100:.1f}%
Completeness:            {avg_completeness*100:.1f}%
Helpfulness:             {avg_helpfulness*100:.1f}%

⚠️  HALLUCINATION RATE:  {hallucination_rate*100:.1f}%

🎯 OVERALL GRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        overall_score = (avg_accuracy + avg_completeness + avg_helpfulness) / 3
        if overall_score >= 0.8 and hallucination_rate < 0.05:
            report += "Grade: PRODUCTION READY ✅\n"
        elif overall_score >= 0.6:
            report += "Grade: NEEDS REFINEMENT ⚠️\n"
        else:
            report += "Grade: NOT PRODUCTION READY ❌\n"
        
        return report


class EndToEndEvaluator:
    """Complete end-to-end system evaluation"""
    
    def __init__(self):
        self.search_eval = SearchEvaluator()
        self.response_eval = ResponseEvaluator()
        self.performance_metrics = AgentPerformanceMetrics()
        
        self.execution_times = []
        self.api_calls = []
        self.errors = []
    
    def evaluate_complete_query(self,
                               query: str,
                               retrieved_products: List[int],
                               relevant_products: List[int],
                               response: str,
                               ground_truth_facts: Dict[str, Any],
                               product_data: Dict[str, Any],
                               execution_time: float,
                               api_call_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        End-to-end evaluation of complete query
        
        Evaluates:
        - Search quality
        - Response quality
        - Performance
        - Cost
        """
        # Track performance
        self.execution_times.append(execution_time)
        if api_call_info:
            self.api_calls.append(api_call_info)
        
        # Evaluate search
        search_result = self.search_eval.evaluate_query(
            query, retrieved_products, relevant_products, execution_time
        )
        
        # Evaluate response
        response_result = self.response_eval.evaluate_response(
            query, response, ground_truth_facts, product_data
        )
        
        return {
            'query': query,
            'search_evaluation': search_result,
            'response_evaluation': response_result,
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_complete_report(self, filepath: str = None) -> str:
        """Generate comprehensive evaluation report"""
        latency_metrics = self.performance_metrics.latency_metrics(self.execution_times)
        cost_metrics = self.performance_metrics.cost_metrics(self.api_calls) if self.api_calls else {}
        
        search_agg = self.search_eval.get_aggregate_metrics()
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║   PRODUCT RECOMMENDATION SYSTEM - COMPLETE EVALUATION    ║
╚══════════════════════════════════════════════════════════╝

📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 Total Queries: {len(self.execution_times)}

═══════════════════════════════════════════════════════════

🎯 SEARCH QUALITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Precision@10:     {search_agg.get('average_precision@10', 0):.3f}
Recall@10:        {search_agg.get('average_recall@10', 0):.3f}
NDCG@10:          {search_agg.get('average_ndcg@10', 0):.3f}

⚡ PERFORMANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mean Latency:     {latency_metrics.get('mean_latency', 0):.3f}s
Median Latency:   {latency_metrics.get('median_latency', 0):.3f}s
P95 Latency:      {latency_metrics.get('p95_latency', 0):.3f}s
P99 Latency:      {latency_metrics.get('p99_latency', 0):.3f}s
SLA Compliance:   {search_agg.get('sla_compliance', 0)*100:.1f}%

💰 COST ANALYSIS (USD)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        if cost_metrics:
            report += f"""Total Tokens:     {cost_metrics.get('total_tokens', 0):,}
Total Cost:       ${cost_metrics.get('total_cost_usd', 0):.4f}
Cost per Query:   ${cost_metrics.get('cost_per_query', 0):.4f}
"""
        else:
            report += "No cost data available\n"
        
        report += f"""
═══════════════════════════════════════════════════════════

✅ PRODUCTION READINESS CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Add checklist
        ndcg = search_agg.get('average_ndcg@10', 0)
        latency = latency_metrics.get('p95_latency', 999)
        
        report += f"[{'✓' if ndcg >= 0.7 else '✗'}] Search Quality (NDCG >= 0.7): {ndcg:.3f}\n"
        report += f"[{'✓' if latency < 2.0 else '✗'}] Latency (P95 < 2s): {latency:.3f}s\n"
        report += f"[{'✓' if not self.errors else '✗'}] No Critical Errors: {len(self.errors)} errors\n"
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(report)
        
        return report
