import json
from datetime import datetime

class AlphaGBMClient:
    """
    Mock client for AlphaGBM skills API.
    Simulates fetching data from alphagbm-vix-status, alphagbm-market-sentiment,
    alphagbm-macro-view, and alphagbm-options-strategy.
    """
    def __init__(self):
        pass

    def get_vix_status(self):
        # Simulating a call to GET /api/options/vix-status
        # For demonstration, we'll return a "Sweet Spot" environment,
        # which is great for Bull Put Spreads.
        return {
            "success": True,
            "vix": 22.5,
            "mean_1y": 18.3,
            "percentile_1y": 68.5,
            "level": "sweet_spot",
            "color": "yellow",
            "label": "Seller Sweet Spot",
            "strategy_hint": "BPS premiums get juicy — actively open positions",
            "timestamp": datetime.now().isoformat()
        }

    def get_market_sentiment(self):
        # Simulating GET /api/analytics/market-sentiment
        return {
            "success": True,
            "fear_greed_index": 45,
            "regime": "risk-on",
            "regime_confidence": 0.75,
            "sector_rotation": "mid_cycle",
            "timestamp": datetime.now().isoformat()
        }

    def get_macro_view(self):
        # Simulating GET /api/analytics/macro-view
        return {
            "success": True,
            "growth_trend": "slowing",
            "inflation_trend": "sticky",
            "fed_stance": "higher_for_longer",
            "macro_regime": "late_cycle",
            "timestamp": datetime.now().isoformat()
        }

    def get_options_strategy(self, ticker, market_view, vix_level):
        # Simulating POST /api/options/tools/strategy/build
        
        recommendations = []
        
        if market_view == "bullish":
            if vix_level in ["sweet_spot", "caution"]:
                # High IV: favor selling premium
                recommendations.append({
                    "strategy": "Bull Put Spread",
                    "rank": 1,
                    "legs": [
                        {"action": "sell", "type": "put", "strike": "ATM-2%"},
                        {"action": "buy", "type": "put", "strike": "ATM-5%"}
                    ],
                    "rationale": f"Bullish view with {vix_level} VIX favors selling premium via credit spreads."
                })
            else:
                # Low IV: favor buying premium
                recommendations.append({
                    "strategy": "Bull Call Spread",
                    "rank": 1,
                    "legs": [
                        {"action": "buy", "type": "call", "strike": "ATM"},
                        {"action": "sell", "type": "call", "strike": "OTM+3%"}
                    ],
                    "rationale": f"Bullish view with {vix_level} VIX favors buying debit spreads."
                })
                
        elif market_view == "bearish":
            if vix_level in ["sweet_spot", "caution"]:
                recommendations.append({
                    "strategy": "Bear Call Spread",
                    "rank": 1,
                    "legs": [
                        {"action": "sell", "type": "call", "strike": "ATM+2%"},
                        {"action": "buy", "type": "call", "strike": "ATM+5%"}
                    ],
                    "rationale": f"Bearish view with elevated VIX favors selling call spreads."
                })
            else:
                recommendations.append({
                    "strategy": "Bear Put Spread",
                    "rank": 1,
                    "legs": [
                        {"action": "buy", "type": "put", "strike": "ATM"},
                        {"action": "sell", "type": "put", "strike": "OTM-3%"}
                    ],
                    "rationale": f"Bearish view with low VIX favors buying put spreads."
                })
        else:
            recommendations.append({
                "strategy": "Iron Condor",
                "rank": 1,
                "legs": [
                    {"action": "sell", "type": "put", "strike": "OTM-3%"},
                    {"action": "buy", "type": "put", "strike": "OTM-5%"},
                    {"action": "sell", "type": "call", "strike": "OTM+3%"},
                    {"action": "buy", "type": "call", "strike": "OTM+5%"},
                ],
                "rationale": "Neutral view favors non-directional premium collection."
            })
            
        return {
            "ticker": ticker,
            "market_view": market_view,
            "iv_environment": vix_level,
            "recommendations": recommendations
        }
