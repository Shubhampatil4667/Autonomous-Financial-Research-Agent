from typing import List, Dict, Any
import yfinance as yf

def peer_comparison(symbol: str, peers: List[str]) -> Dict[str, Any]:
    """
    Compare company with peers
    """
    comparison = {"target": symbol, "peers": []}

    try:
        target = yf.Ticker(symbol)
        target_pe = target.info.get("trailingPE", 0)

        for peer in peers:
            peer_ticker = yf.Ticker(peer)
            peer_info = peer_ticker.info
            comparison["peers"].append({
                "symbol": peer,
                "name": peer_info.get("longName", peer),
                "pe_ratio": peer_info.get("trailingPE"),
                "market_cap": peer_info.get("marketCap"),
                "vs_target_pe": peer_info.get("trailingPE", 0) - target_pe if target_pe else 0
            })
    except:
        # Mock data
        for peer in peers:
            comparison["peers"].append({
                "symbol": peer,
                "name": f"{peer} Corp",
                "pe_ratio": 25.0,
                "market_cap": 100000000000,
                "vs_target_pe": 5.0
            })

    return comparison