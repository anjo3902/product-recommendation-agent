"""
Price Chart Generator - Visual Price History Charts

Generates:
1. ASCII charts for console (testing)
2. JSON data for web charts (Chart.js, Recharts)

For Beginners:
- Charts help visualize price changes over time
- Makes it easy to see if price is going up or down
- Professional e-commerce feature
"""

from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PriceChartGenerator:
    """Generate price history charts and insights"""
    
    def generate_chart_data(
        self,
        price_history: List[Dict[str, Any]],
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Generate rich chart data with visual enhancements like pricehistory.app
        
        Features:
        - Smooth gradient lines
        - Price zone highlights (good/average/expensive)
        - Lowest/highest price markers
        - Trend line overlay
        - Interactive tooltips data
        - Responsive sizing
        
        Args:
            price_history: List of {price, date} dicts
            days: Number of days to show
            
        Returns:
            Enhanced chart data for Chart.js/Recharts with visual appeal
        """
        if not price_history:
            return {"error": "No price history available"}
        
        # Sort by date (oldest first for chart)
        sorted_history = sorted(price_history, key=lambda x: x['date'])
        
        # Extract data
        dates = [datetime.fromisoformat(h['date']) for h in sorted_history]
        prices = [h['price'] for h in sorted_history]
        
        # Calculate statistics
        current_price = prices[-1]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        # Find key price points
        min_price_idx = prices.index(min_price)
        max_price_idx = prices.index(max_price)
        min_price_date = dates[min_price_idx]
        max_price_date = dates[max_price_idx]
        
        # Calculate trend
        trend, trend_emoji, trend_pct = self._calculate_trend(prices)
        
        # Generate insights
        insights = self._generate_insights(
            current_price, min_price, max_price, avg_price, trend, trend_pct
        )
        
        # Generate recommendation
        recommendation = self._get_recommendation(
            current_price, min_price, avg_price, trend
        )
        
        # Calculate price zones for visual highlights
        price_zones = self._calculate_price_zones(min_price, max_price, avg_price)
        
        # Create annotations for key points
        annotations = [
            {
                "type": "point",
                "xValue": min_price_idx,
                "yValue": min_price,
                "backgroundColor": "rgba(34, 197, 94, 0.8)",
                "borderColor": "rgb(34, 197, 94)",
                "borderWidth": 2,
                "radius": 6,
                "label": {
                    "content": f"Lowest: ₹{min_price:,.0f}",
                    "enabled": True,
                    "position": "top"
                }
            },
            {
                "type": "point",
                "xValue": max_price_idx,
                "yValue": max_price,
                "backgroundColor": "rgba(239, 68, 68, 0.8)",
                "borderColor": "rgb(239, 68, 68)",
                "borderWidth": 2,
                "radius": 6,
                "label": {
                    "content": f"Highest: ₹{max_price:,.0f}",
                    "enabled": True,
                    "position": "bottom"
                }
            },
            {
                "type": "point",
                "xValue": len(prices) - 1,
                "yValue": current_price,
                "backgroundColor": "rgba(59, 130, 246, 0.8)",
                "borderColor": "rgb(59, 130, 246)",
                "borderWidth": 2,
                "radius": 6,
                "label": {
                    "content": f"Current: ₹{current_price:,.0f}",
                    "enabled": True,
                    "position": "right"
                }
            },
            {
                "type": "line",
                "yMin": avg_price,
                "yMax": avg_price,
                "borderColor": "rgba(156, 163, 175, 0.5)",
                "borderWidth": 2,
                "borderDash": [5, 5],
                "label": {
                    "content": f"Average: ₹{avg_price:,.0f}",
                    "enabled": True,
                    "position": "end"
                }
            }
        ]
        
        # Enhanced dataset with gradient
        chart_data = {
            "labels": [d.strftime("%b %d") for d in dates],
            "fullDates": [d.strftime("%Y-%m-%d") for d in dates],  # For tooltips
            "datasets": [
                {
                    "label": "Price History",
                    "data": prices,
                    "borderColor": "rgb(59, 130, 246)",
                    "backgroundColor": "rgba(59, 130, 246, 0.1)",
                    "fill": True,
                    "tension": 0.4,
                    "borderWidth": 3,
                    "pointRadius": 0,  # Hide points by default
                    "pointHoverRadius": 6,  # Show on hover
                    "pointBackgroundColor": "rgb(59, 130, 246)",
                    "pointBorderColor": "#fff",
                    "pointBorderWidth": 2
                }
            ],
            "annotations": annotations,
            "priceZones": price_zones,
            "statistics": {
                "current_price": current_price,
                "min_price": min_price,
                "max_price": max_price,
                "average_price": round(avg_price, 2),
                "min_price_date": min_price_date.strftime("%b %d, %Y"),
                "max_price_date": max_price_date.strftime("%b %d, %Y"),
                "trend": trend,
                "trend_emoji": trend_emoji,
                "trend_percentage": round(trend_pct, 1),
                "price_range": round(max_price - min_price, 2),
                "volatility": round(((max_price - min_price) / avg_price) * 100, 1)
            },
            "insights": insights,
            "recommendation": recommendation,
            "chartOptions": {
                "responsive": True,
                "maintainAspectRatio": False,
                "interaction": {
                    "mode": "index",
                    "intersect": False
                },
                "plugins": {
                    "legend": {
                        "display": True,
                        "position": "top"
                    },
                    "title": {
                        "display": True,
                        "text": f"Price Trend - Last {days} Days",
                        "font": {"size": 16, "weight": "bold"}
                    },
                    "tooltip": {
                        "enabled": True,
                        "callbacks": {
                            "label": "Price: ₹{value}"
                        }
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": False,
                        "ticks": {
                            "callback": "₹{value}"
                        },
                        "title": {
                            "display": True,
                            "text": "Price (₹)"
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": "Date"
                        }
                    }
                }
            }
        }
        
        return chart_data
    
    def _calculate_price_zones(
        self,
        min_price: float,
        max_price: float,
        avg_price: float
    ) -> List[Dict[str, Any]]:
        """
        Calculate price zones for visual highlighting
        Green zone: Good prices (below average)
        Yellow zone: Average prices
        Red zone: Expensive (above average)
        """
        return [
            {
                "name": "Excellent Deal",
                "min": min_price,
                "max": min_price + (avg_price - min_price) * 0.3,
                "color": "rgba(34, 197, 94, 0.1)",
                "borderColor": "rgb(34, 197, 94)"
            },
            {
                "name": "Good Price",
                "min": min_price + (avg_price - min_price) * 0.3,
                "max": avg_price,
                "color": "rgba(132, 204, 22, 0.1)",
                "borderColor": "rgb(132, 204, 22)"
            },
            {
                "name": "Average Price",
                "min": avg_price,
                "max": avg_price + (max_price - avg_price) * 0.5,
                "color": "rgba(251, 191, 36, 0.1)",
                "borderColor": "rgb(251, 191, 36)"
            },
            {
                "name": "Expensive",
                "min": avg_price + (max_price - avg_price) * 0.5,
                "max": max_price,
                "color": "rgba(239, 68, 68, 0.1)",
                "borderColor": "rgb(239, 68, 68)"
            }
        ]
    
    def _calculate_trend(self, prices: List[float]) -> tuple:
        """
        Calculate price trend
        
        Returns:
            (trend_name, emoji, percentage_change)
        """
        if len(prices) < 30:
            return "insufficient_data", "❓", 0
        
        # Compare last 30 days vs previous 30 days
        last_month_avg = sum(prices[-30:]) / 30
        prev_month_avg = sum(prices[-60:-30]) / 30 if len(prices) >= 60 else sum(prices) / len(prices)
        
        trend_pct = ((last_month_avg - prev_month_avg) / prev_month_avg) * 100
        
        if trend_pct < -5:
            return "decreasing", "📉", trend_pct
        elif trend_pct > 5:
            return "increasing", "📈", trend_pct
        else:
            return "stable", "➡️", trend_pct
    
    def _generate_insights(
        self,
        current: float,
        min_price: float,
        max_price: float,
        avg: float,
        trend: str,
        trend_pct: float
    ) -> List[str]:
        """Generate human-readable insights"""
        insights = []
        
        # Price drop insight
        if max_price > current:
            drop_pct = ((max_price - current) / max_price) * 100
            if drop_pct >= 40:
                insights.append(f"💡 Massive price drop! {drop_pct:.0f}% off from peak!")
            elif drop_pct >= 20:
                insights.append(f"📉 Price down {drop_pct:.0f}% from highest")
        
        # Trend insight
        if trend == "decreasing":
            insights.append(f"📉 Prices trending downward ({abs(trend_pct):.1f}% last month)")
        elif trend == "increasing":
            insights.append(f"📈 Prices going up ({trend_pct:.1f}% last month)")
        
        # Current vs average
        if current < avg * 0.95:
            diff_pct = ((avg - current) / avg) * 100
            insights.append(f"✅ {diff_pct:.0f}% below average price")
        elif current > avg * 1.05:
            diff_pct = ((current - avg) / avg) * 100
            insights.append(f"⚠️ {diff_pct:.0f}% above average price")
        
        # Near lowest price
        if current <= min_price * 1.05:
            insights.append("🎯 Near all-time low price!")
        
        return insights
    
    def _get_recommendation(
        self,
        current: float,
        min_price: float,
        avg: float,
        trend: str
    ) -> Dict[str, str]:
        """Generate buy/wait recommendation"""
        
        if current <= min_price * 1.05:
            return {
                "action": "buy_now",
                "emoji": "✅",
                "text": "Excellent time to buy!",
                "reason": "Price is at or near all-time low"
            }
        elif trend == "decreasing":
            return {
                "action": "wait",
                "emoji": "⏳",
                "text": "Consider waiting",
                "reason": "Prices are trending downward"
            }
        elif current < avg:
            return {
                "action": "good_deal",
                "emoji": "👍",
                "text": "Fair deal",
                "reason": "Price is below average"
            }
        else:
            return {
                "action": "wait",
                "emoji": "⏳",
                "text": "Wait for better price",
                "reason": "Price is currently above average"
            }
    
    def generate_ascii_chart(
        self,
        price_history: List[Dict[str, Any]],
        width: int = 60,
        height: int = 10
    ) -> str:
        """
        Generate ASCII art price chart for console
        
        Args:
            price_history: List of price data
            width: Chart width in characters
            height: Chart height in lines
            
        Returns:
            ASCII chart string
            
        Example:
        Price History (Last 30 days)
        
        ₹2499 │           ●
              │          ╱ ╲
        ₹2300 │         ╱   ╲
              │        ╱     ●
        ₹2100 │   ●───●       
              │  ╱            
        ₹1899 │●──────────────►
              Jan  Feb  Mar
        """
        if not price_history:
            return "No price history available"
        
        sorted_history = sorted(price_history, key=lambda x: x['date'])
        prices = [h['price'] for h in sorted_history]
        dates = [datetime.fromisoformat(h['date']) for h in sorted_history]
        
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            price_range = 1
        
        # Build chart
        chart = []
        chart.append(f"\n📊 Price History (Last {len(prices)} days)")
        chart.append("")
        
        # Y-axis and data points
        for i in range(height, -1, -1):
            y_value = min_price + (price_range * i / height)
            line = f"₹{y_value:>5.0f} │"
            
            # Plot prices
            for price in prices:
                normalized = (price - min_price) / price_range
                if abs(normalized - (i / height)) < (1 / height / 2):
                    line += "●"
                else:
                    line += " "
            
            chart.append(line)
        
        # X-axis
        chart.append("      └" + "─" * len(prices) + "►")
        
        # Date labels
        if len(dates) >= 3:
            start_date = dates[0].strftime('%b')
            mid_date = dates[len(dates)//2].strftime('%b')
            end_date = dates[-1].strftime('%b')
            chart.append(f"       {start_date}      {mid_date}      {end_date}")
        
        chart.append("")
        
        # Add insights
        current_price = prices[-1]
        drop_pct = ((max_price - current_price) / max_price) * 100
        
        if drop_pct >= 20:
            chart.append(f"💡 Price dropped {drop_pct:.0f}% from peak!")
        
        recommendation = self._get_recommendation(
            current_price, min_price, sum(prices)/len(prices), "stable"
        )
        chart.append(f"{recommendation['emoji']} {recommendation['text']}")
        chart.append("")
        
        return "\n".join(chart)


# Global instance
price_chart_generator = PriceChartGenerator()
