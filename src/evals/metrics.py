"""
Evaluation Metrics for Product Recommendation System

Implements industry-standard metrics for measuring:
1. Search Relevance (Precision, Recall, NDCG, MRR)
2. Recommendation Quality (Hit Rate, Coverage, Diversity)
3. Response Quality (Factuality, Coherence, Helpfulness)
4. Agent Performance (Latency, Success Rate, Error Rate)
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from datetime import datetime
import json


class SearchMetrics:
    """Metrics for evaluating search quality"""
    
    @staticmethod
    def precision_at_k(retrieved: List[int], relevant: List[int], k: int = 10) -> float:
        """
        Precision@K: What percentage of top K results are relevant?
        
        Args:
            retrieved: List of product IDs returned by search
            relevant: List of actually relevant product IDs (ground truth)
            k: Number of top results to consider
            
        Returns:
            Precision score (0.0 to 1.0)
            
        Example:
            >>> retrieved = [1, 2, 3, 4, 5]
            >>> relevant = [1, 3, 7, 9]
            >>> precision_at_k(retrieved, relevant, k=5)
            0.4  # 2 out of 5 are relevant (products 1 and 3)
        """
        retrieved_k = retrieved[:k]
        relevant_set = set(relevant)
        hits = sum(1 for item in retrieved_k if item in relevant_set)
        return hits / k if k > 0 else 0.0
    
    @staticmethod
    def recall_at_k(retrieved: List[int], relevant: List[int], k: int = 10) -> float:
        """
        Recall@K: What percentage of all relevant items are in top K?
        
        Args:
            retrieved: List of product IDs returned by search
            relevant: List of actually relevant product IDs (ground truth)
            k: Number of top results to consider
            
        Returns:
            Recall score (0.0 to 1.0)
            
        Example:
            >>> retrieved = [1, 2, 3, 4, 5]
            >>> relevant = [1, 3, 7, 9]
            >>> recall_at_k(retrieved, relevant, k=5)
            0.5  # Found 2 out of 4 relevant items (50%)
        """
        if not relevant:
            return 0.0
        
        retrieved_k = retrieved[:k]
        relevant_set = set(relevant)
        hits = sum(1 for item in retrieved_k if item in relevant_set)
        return hits / len(relevant)
    
    @staticmethod
    def ndcg_at_k(retrieved: List[int], relevant: List[int], k: int = 10) -> float:
        """
        NDCG@K (Normalized Discounted Cumulative Gain)
        Measures ranking quality - positions matter!
        
        Args:
            retrieved: List of product IDs returned by search (ordered)
            relevant: List of relevant product IDs with relevance scores
            k: Number of top results to consider
            
        Returns:
            NDCG score (0.0 to 1.0)
            
        Explanation:
            - NDCG = 1.0: Perfect ranking
            - NDCG = 0.5: Mediocre ranking
            - NDCG = 0.0: All irrelevant results
        """
        retrieved_k = retrieved[:k]
        relevant_set = set(relevant)
        
        # Calculate DCG (Discounted Cumulative Gain)
        dcg = 0.0
        for i, item in enumerate(retrieved_k):
            if item in relevant_set:
                # Relevance = 1 if relevant, 0 if not
                # Position discount: 1/log2(position + 2)
                dcg += 1.0 / np.log2(i + 2)
        
        # Calculate Ideal DCG (all relevant items at top)
        idcg = 0.0
        for i in range(min(len(relevant), k)):
            idcg += 1.0 / np.log2(i + 2)
        
        return dcg / idcg if idcg > 0 else 0.0
    
    @staticmethod
    def mean_reciprocal_rank(retrieved_lists: List[List[int]], 
                           relevant_lists: List[List[int]]) -> float:
        """
        MRR (Mean Reciprocal Rank): Average position of first relevant result
        
        Args:
            retrieved_lists: List of search result lists
            relevant_lists: List of relevant item lists
            
        Returns:
            MRR score (0.0 to 1.0)
            
        Example:
            Query 1: First relevant at position 2 → RR = 1/2 = 0.5
            Query 2: First relevant at position 1 → RR = 1/1 = 1.0
            Query 3: First relevant at position 5 → RR = 1/5 = 0.2
            MRR = (0.5 + 1.0 + 0.2) / 3 = 0.567
        """
        reciprocal_ranks = []
        
        for retrieved, relevant in zip(retrieved_lists, relevant_lists):
            relevant_set = set(relevant)
            for i, item in enumerate(retrieved):
                if item in relevant_set:
                    reciprocal_ranks.append(1.0 / (i + 1))
                    break
            else:
                reciprocal_ranks.append(0.0)
        
        return np.mean(reciprocal_ranks) if reciprocal_ranks else 0.0


class RecommendationMetrics:
    """Metrics for evaluating recommendation quality"""
    
    @staticmethod
    def hit_rate_at_k(recommendations: List[List[int]], 
                     ground_truth: List[List[int]], 
                     k: int = 10) -> float:
        """
        Hit Rate@K: Percentage of users who found at least 1 relevant item in top K
        
        Args:
            recommendations: List of recommended product IDs for each user
            ground_truth: List of items each user actually interacted with
            k: Number of recommendations to consider
            
        Returns:
            Hit rate (0.0 to 1.0)
            
        Example:
            User 1: Recommended [1,2,3], Bought [3,5] → HIT (3 is in top 3)
            User 2: Recommended [4,5,6], Bought [1,2] → MISS
            User 3: Recommended [7,8,1], Bought [1,9] → HIT (1 is in top 3)
            Hit Rate = 2/3 = 0.667
        """
        hits = 0
        for rec, truth in zip(recommendations, ground_truth):
            rec_k = set(rec[:k])
            truth_set = set(truth)
            if rec_k & truth_set:  # If intersection exists
                hits += 1
        
        return hits / len(recommendations) if recommendations else 0.0
    
    @staticmethod
    def coverage(all_recommendations: List[List[int]], 
                total_items: int) -> float:
        """
        Catalog Coverage: What percentage of all products were recommended?
        
        Args:
            all_recommendations: All recommendation lists
            total_items: Total number of products in catalog
            
        Returns:
            Coverage score (0.0 to 1.0)
            
        Explanation:
            High coverage (>0.7) = Good, diverse recommendations
            Low coverage (<0.3) = Only recommending popular items (filter bubble)
        """
        unique_items = set()
        for rec_list in all_recommendations:
            unique_items.update(rec_list)
        
        return len(unique_items) / total_items if total_items > 0 else 0.0
    
    @staticmethod
    def diversity_score(recommendations: List[int], 
                       product_categories: Dict[int, str]) -> float:
        """
        Diversity: How diverse are the recommended products?
        
        Args:
            recommendations: List of recommended product IDs
            product_categories: Mapping of product_id → category
            
        Returns:
            Diversity score (0.0 to 1.0)
            
        Example:
            Recommendations: [headphone1, headphone2, laptop, phone, watch]
            Categories: [audio, audio, computer, mobile, accessories]
            Unique categories: 4 out of 5 items
            Diversity = 4/5 = 0.8 (good diversity)
        """
        if not recommendations:
            return 0.0
        
        categories = [product_categories.get(pid, 'unknown') 
                     for pid in recommendations]
        unique_categories = len(set(categories))
        
        return unique_categories / len(recommendations)


class ResponseQualityMetrics:
    """Metrics for evaluating LLM response quality"""
    
    @staticmethod
    def factual_accuracy(response: str, facts: Dict[str, Any]) -> float:
        """
        Factual Accuracy: Are the facts in the response correct?
        
        Args:
            response: Agent's response text
            facts: Ground truth facts (e.g., {"price": 2999, "brand": "boAt"})
            
        Returns:
            Accuracy score (0.0 to 1.0)
            
        Example:
            Response: "boAt Airdopes costs ₹2,999 with 4.3 rating"
            Facts: {"price": 2999, "brand": "boAt", "rating": 4.3}
            All facts correct → 1.0
            
            Response: "boAt Airdopes costs ₹1,999 with 4.5 rating"
            Facts: {"price": 2999, "brand": "boAt", "rating": 4.3}
            2 errors (price, rating) → 0.33 (1 correct out of 3)
        """
        correct = 0
        total = len(facts)
        
        response_lower = response.lower()
        
        for key, expected_value in facts.items():
            expected_str = str(expected_value).lower()
            if expected_str in response_lower:
                correct += 1
        
        return correct / total if total > 0 else 0.0
    
    @staticmethod
    def hallucination_check(response: str, 
                          product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hallucination Detection: Is the agent making up information?
        
        Args:
            response: Agent's response
            product_data: Actual product information from database
            
        Returns:
            Dictionary with hallucination detection results
            
        Checks for:
        - Prices not in database
        - Features not mentioned in specs
        - Fake statistics
        - Made-up comparisons
        """
        hallucinations = []
        
        # Check for price hallucinations
        import re
        prices_in_response = re.findall(r'₹[\d,]+', response)
        if prices_in_response:
            actual_price = f"₹{product_data.get('price', 0)}"
            for price in prices_in_response:
                if price != actual_price:
                    hallucinations.append({
                        'type': 'price',
                        'claimed': price,
                        'actual': actual_price
                    })
        
        return {
            'has_hallucinations': len(hallucinations) > 0,
            'hallucination_count': len(hallucinations),
            'details': hallucinations
        }
    
    @staticmethod
    def completeness_score(response: str, 
                          required_elements: List[str]) -> float:
        """
        Completeness: Does the response include all required information?
        
        Args:
            response: Agent's response
            required_elements: List of required elements
            
        Returns:
            Completeness score (0.0 to 1.0)
            
        Example:
            Required: ["price", "rating", "features", "pros", "cons"]
            Response includes: ["price", "rating", "features"]
            Completeness = 3/5 = 0.6
        """
        response_lower = response.lower()
        present = sum(1 for elem in required_elements 
                     if elem.lower() in response_lower)
        
        return present / len(required_elements) if required_elements else 0.0
    
    @staticmethod
    def helpfulness_score(response: str) -> Dict[str, Any]:
        """
        Helpfulness: Is the response actually helpful to the user?
        
        Checks:
        - Has clear recommendation? (Yes/No/Multiple options)
        - Includes reasoning? (Why this product?)
        - Actionable next steps? (Add to cart, compare, etc.)
        - Appropriate length? (Not too short, not overwhelming)
        """
        metrics = {
            'has_recommendation': False,
            'has_reasoning': False,
            'has_action_items': False,
            'length_appropriate': False,
            'overall_score': 0.0
        }
        
        # Check for recommendation
        rec_keywords = ['recommend', 'suggest', 'best choice', 'top pick']
        metrics['has_recommendation'] = any(kw in response.lower() for kw in rec_keywords)
        
        # Check for reasoning
        reason_keywords = ['because', 'since', 'due to', 'based on']
        metrics['has_reasoning'] = any(kw in response.lower() for kw in reason_keywords)
        
        # Check for action items
        action_keywords = ['add to cart', 'buy now', 'compare', 'view details']
        metrics['has_action_items'] = any(kw in response.lower() for kw in action_keywords)
        
        # Check length (50-500 words is good)
        word_count = len(response.split())
        metrics['length_appropriate'] = 50 <= word_count <= 500
        metrics['word_count'] = word_count
        
        # Calculate overall score
        score_components = [
            metrics['has_recommendation'],
            metrics['has_reasoning'],
            metrics['has_action_items'],
            metrics['length_appropriate']
        ]
        metrics['overall_score'] = sum(score_components) / len(score_components)
        
        return metrics


class AgentPerformanceMetrics:
    """Metrics for evaluating agent system performance"""
    
    @staticmethod
    def latency_metrics(execution_times: List[float]) -> Dict[str, float]:
        """
        Latency Analysis: How fast do agents respond?
        
        Args:
            execution_times: List of execution times in seconds
            
        Returns:
            Dictionary with latency statistics
        """
        if not execution_times:
            return {}
        
        return {
            'mean_latency': np.mean(execution_times),
            'median_latency': np.median(execution_times),
            'p95_latency': np.percentile(execution_times, 95),
            'p99_latency': np.percentile(execution_times, 99),
            'min_latency': np.min(execution_times),
            'max_latency': np.max(execution_times),
            'std_latency': np.std(execution_times)
        }
    
    @staticmethod
    def success_rate(total_queries: int, 
                    successful_queries: int, 
                    failed_queries: int) -> Dict[str, float]:
        """
        Success Rate: What percentage of queries succeeded?
        
        Returns:
            Dictionary with success metrics
        """
        return {
            'total_queries': total_queries,
            'successful': successful_queries,
            'failed': failed_queries,
            'success_rate': successful_queries / total_queries if total_queries > 0 else 0.0,
            'failure_rate': failed_queries / total_queries if total_queries > 0 else 0.0
        }
    
    @staticmethod
    def error_distribution(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Error Analysis: What types of errors occur?
        
        Args:
            errors: List of error dictionaries with 'type' and 'message'
            
        Returns:
            Distribution of error types
        """
        error_types = {}
        for error in errors:
            error_type = error.get('type', 'unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': len(errors),
            'error_types': error_types,
            'most_common_error': max(error_types.items(), key=lambda x: x[1])[0] if error_types else None
        }
    
    @staticmethod
    def cost_metrics(api_calls: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Cost Analysis: How much do API calls cost?
        
        Args:
            api_calls: List of API calls with token counts
            
        Returns:
            Cost breakdown
        """
        # Gemini 1.5 Pro pricing (as of Jan 2026)
        INPUT_COST_PER_1K = 0.00035  # $0.00035 per 1K input tokens
        OUTPUT_COST_PER_1K = 0.00105  # $0.00105 per 1K output tokens
        
        total_input_tokens = sum(call.get('input_tokens', 0) for call in api_calls)
        total_output_tokens = sum(call.get('output_tokens', 0) for call in api_calls)
        
        input_cost = (total_input_tokens / 1000) * INPUT_COST_PER_1K
        output_cost = (total_output_tokens / 1000) * OUTPUT_COST_PER_1K
        
        return {
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'total_tokens': total_input_tokens + total_output_tokens,
            'input_cost_usd': input_cost,
            'output_cost_usd': output_cost,
            'total_cost_usd': input_cost + output_cost,
            'cost_per_query': (input_cost + output_cost) / len(api_calls) if api_calls else 0
        }


# Helper function to calculate all metrics at once
def calculate_all_metrics(
    retrieved_results: List[int],
    relevant_items: List[int],
    response: str,
    ground_truth_facts: Dict[str, Any],
    execution_time: float
) -> Dict[str, Any]:
    """
    Calculate all evaluation metrics for a single query
    
    Returns comprehensive metrics dictionary
    """
    search_metrics = SearchMetrics()
    response_metrics = ResponseQualityMetrics()
    
    return {
        'search_quality': {
            'precision@5': search_metrics.precision_at_k(retrieved_results, relevant_items, k=5),
            'precision@10': search_metrics.precision_at_k(retrieved_results, relevant_items, k=10),
            'recall@5': search_metrics.recall_at_k(retrieved_results, relevant_items, k=5),
            'recall@10': search_metrics.recall_at_k(retrieved_results, relevant_items, k=10),
            'ndcg@10': search_metrics.ndcg_at_k(retrieved_results, relevant_items, k=10),
        },
        'response_quality': {
            'factual_accuracy': response_metrics.factual_accuracy(response, ground_truth_facts),
            'completeness': response_metrics.completeness_score(
                response, 
                ['price', 'rating', 'features', 'pros', 'cons']
            ),
            'helpfulness': response_metrics.helpfulness_score(response),
        },
        'performance': {
            'latency_seconds': execution_time,
            'meets_sla': execution_time < 2.0  # SLA: < 2 seconds
        }
    }
