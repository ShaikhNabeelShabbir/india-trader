import os
from dataclasses import dataclass, field
from typing import Dict, List

def load_dotenv():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_dotenv()

@dataclass
class Instrument:
    symbol: str
    instrument_key: str
    name: str
    sector: str

@dataclass
class Config:
    # Upstox Credentials (Strictly Read-Only Market Analytics)
    access_token: str = field(default_factory=lambda: os.getenv("UPSTOX_ACCESS_TOKEN", ""))
    
    # Capital Baseline & Risk Governance
    initial_capital: float = float(os.getenv("INITIAL_CAPITAL", "2000.0"))
    max_risk_pct: float = float(os.getenv("MAX_RISK_PCT", "1.5"))       # 1.5% max risk per trade (₹30)
    max_allocation_pct: float = float(os.getenv("MAX_ALLOCATION_PCT", "80.0")) # Max 80% capital deployed (₹1,600)
    cash_buffer_pct: float = 20.0                                       # ₹400 safety reserve
    min_risk_reward: float = 2.0                                        # Minimum 1:2.0 R:R
    max_daily_loss_pct: float = 4.0                                     # ₹80 daily circuit stop
    
    # Ethical Negative Screening: Strictly NO tobacco, alcohol, gambling, or related entities.
    EXCLUDED_SECTORS: List[str] = field(default_factory=lambda: ["Tobacco", "Alcohol", "Gambling"])
    
    # High-Liquidity NSE Equity Watchlist (Liquid, priced under ₹1,500, Ethically Screened)
    instruments: Dict[str, Instrument] = field(default_factory=lambda: {
        "TATASTEEL": Instrument("TATASTEEL", "NSE_EQ|INE081A01020", "Tata Steel Limited", "Nifty Metal"),
        "ETERNAL": Instrument("ETERNAL", "NSE_EQ|INE758T01015", "Eternal Ltd (Zomato)", "Nifty Consumption"),
        "SBIN": Instrument("SBIN", "NSE_EQ|INE062A01020", "State Bank of India", "Nifty PSU Bank"),
        "TMPV": Instrument("TMPV", "NSE_EQ|INE155A01022", "Tata Motors Pass Veh Ltd", "Nifty Auto"),
        "WIPRO": Instrument("WIPRO", "NSE_EQ|INE075A01022", "Wipro Limited", "Nifty IT"),
        "COALINDIA": Instrument("COALINDIA", "NSE_EQ|INE522F01014", "Coal India Limited", "Nifty Energy"),
        "NTPC": Instrument("NTPC", "NSE_EQ|INE733E01010", "NTPC Limited", "Nifty Energy"),
    })

    # Benchmark Market Indices & Sectoral Trackers
    indices: Dict[str, str] = field(default_factory=lambda: {
        "NIFTY50": "NSE_INDEX|Nifty 50",
        "BANKNIFTY": "NSE_INDEX|Nifty Bank",
    })

    # Sector Indices for Relative Strength Filtering
    sector_indices: Dict[str, str] = field(default_factory=lambda: {
        "Nifty IT": "NSE_INDEX|Nifty IT",
        "Nifty PSU Bank": "NSE_INDEX|Nifty PSU Bank",
        "Nifty Metal": "NSE_INDEX|Nifty Metal",
        "Nifty Auto": "NSE_INDEX|Nifty Auto",
        "Nifty FMCG": "NSE_INDEX|Nifty FMCG",
    })

config = Config()
