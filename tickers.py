"""Listas de tickers del S&P 500 y NASDAQ-100."""

# NASDAQ-100 (actualizado Q1 2025)
NASDAQ_100 = [
    "AAPL", "ABNB", "ADBE", "ADI", "ADP", "ADSK", "AEP", "AMAT", "AMD",
    "AMGN", "AMZN", "ANSS", "APP", "ARM", "ASML", "AVGO", "AZN", "BIIB",
    "BKNG", "BKR", "CDNS", "CDW", "CEG", "CHTR", "CMCSA", "COST", "CPRT",
    "CRWD", "CSCO", "CSGP", "CTAS", "CTSH", "DASH", "DDOG", "DLTR",
    "DXCM", "EA", "EXC", "FANG", "FAST", "FTNT", "GEHC", "GFS", "GILD",
    "GOOG", "GOOGL", "HON", "IDXX", "ILMN", "INTC", "INTU", "ISRG",
    "KDP", "KHC", "KLAC", "LIN", "LRCX", "LULU", "MAR", "MCHP", "MDB",
    "MDLZ", "MELI", "META", "MNST", "MRNA", "MRVL", "MSFT", "MU",
    "NFLX", "NVDA", "NXPI", "ODFL", "ON", "ORLY", "PANW", "PAYX", "PCAR",
    "PDD", "PEP", "PYPL", "QCOM", "REGN", "ROP", "ROST", "SBUX", "SMCI",
    "SNPS", "TEAM", "TMUS", "TSLA", "TTD", "TTWO", "TXN", "VRSK",
    "VRTX", "WBD", "WDAY", "XEL", "ZS",
]

# S&P 500 (actualizado Q1 2025)
SP500 = [
    "MMM", "AOS", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AES", "AFL",
    "A", "APD", "ABNB", "AKAM", "ALB", "ALK", "ARE", "ALGN", "ALLE",
    "LNT", "ALL", "GOOGL", "GOOG", "MO", "AMZN", "AMCR", "AEE", "AAL",
    "AEP", "AXP", "AIG", "AMT", "AWK", "AMP", "AME", "AMGN", "APH",
    "ADI", "ANSS", "AON", "APA", "AAPL", "AMAT", "APTV", "ACGL", "ADM",
    "ANET", "AJG", "AIZ", "T", "ATO", "ADSK", "ADP", "AZO", "AVB",
    "AVY", "AXON", "BKR", "BALL", "BAC", "BK", "BBWI", "BAX", "BDX",
    "BRK.B", "BBY", "BIO", "TECH", "BIIB", "BLK", "BA", "BKNG", "BWA",
    "BSX", "BMY", "AVGO", "BR", "BRO", "BF.B", "BLDR", "BG", "BXP",
    "CDNS", "CZR", "CPT", "CPB", "COF", "CAH", "KMX", "CCL", "CARR",
    "CTLT", "CAT", "CBOE", "CBRE", "CDW", "CE", "COR", "CNC", "CNP",
    "CF", "CHRW", "CRL", "SCHW", "CHTR", "CVX", "CMG", "CB", "CHD",
    "CI", "CINF", "CTAS", "CSCO", "C", "CFG", "CLX", "CME", "CMS",
    "KO", "CTSH", "CL", "CMCSA", "CAG", "COP", "ED", "STZ", "CEG",
    "COO", "CPRT", "GLW", "CPAY", "CTVA", "CSGP", "COST", "CTRA", "CCI",
    "CSX", "CMI", "CVS", "DHI", "DHR", "DRI", "DVA", "DAY", "DECK",
    "DE", "DAL", "DVN", "DXCM", "FANG", "DLR", "DFS", "DG", "DLTR",
    "D", "DPZ", "DOV", "DOW", "DHI", "DTE", "DUK", "DD", "EMN",
    "ETN", "EBAY", "ECL", "EIX", "EW", "EA", "ELV", "EMR", "ENPH",
    "ETR", "EOG", "EPAM", "EQT", "EFX", "EQIX", "EQR", "ESS", "EL",
    "ETSY", "EG", "EVRG", "ES", "EXC", "EXPE", "EXPD", "EXR", "XOM",
    "FFIV", "FDS", "FICO", "FAST", "FRT", "FDX", "FIS", "FITB", "FSLR",
    "FE", "FI", "FMC", "F", "FTNT", "FTV", "FOXA", "FOX", "BEN",
    "FCX", "GRMN", "IT", "GEHC", "GEN", "GNRC", "GD", "GE", "GIS",
    "GM", "GPC", "GILD", "GPN", "GL", "GS", "HAL", "HIG", "HAS",
    "HCA", "PEAK", "HSIC", "HSY", "HES", "HPE", "HLT", "HOLX", "HD",
    "HON", "HRL", "HST", "HWM", "HPQ", "HUBB", "HUM", "HBAN", "HII",
    "IBM", "IEX", "IDXX", "ITW", "ILMN", "INCY", "IR", "PODD", "INTC",
    "ICE", "IFF", "IP", "IPG", "INTU", "ISRG", "IVZ", "INVH", "IQV",
    "IRM", "JBHT", "JBL", "JKHY", "J", "JNJ", "JCI", "JPM", "JNPR",
    "K", "KVUE", "KDP", "KEY", "KEYS", "KMB", "KIM", "KMI", "KLAC",
    "KHC", "KR", "LHX", "LH", "LRCX", "LW", "LVS", "LDOS", "LEN",
    "LIN", "LLY", "LKQ", "LMT", "L", "LOW", "LULU", "LYB", "MTB",
    "MRO", "MPC", "MKTX", "MAR", "MMC", "MLM", "MAS", "MA", "MTCH",
    "MKC", "MCD", "MCK", "MDT", "MRK", "META", "MET", "MTD", "MGM",
    "MCHP", "MU", "MSFT", "MAA", "MRNA", "MHK", "MOH", "TAP", "MDLZ",
    "MPWR", "MNST", "MCO", "MS", "MOS", "MSI", "MSCI", "NDAQ", "NTAP",
    "NFLX", "NEM", "NWSA", "NWS", "NEE", "NKE", "NI", "NDSN", "NSC",
    "NTRS", "NOC", "NCLH", "NRG", "NUE", "NVDA", "NVR", "NXPI", "ORLY",
    "OXY", "ODFL", "OMC", "ON", "OKE", "ORCL", "OTIS", "PCAR", "PKG",
    "PANW", "PARA", "PH", "PAYX", "PAYC", "PYPL", "PNR", "PEP", "PFE",
    "PCG", "PM", "PSX", "PNW", "PXD", "PNC", "POOL", "PPG", "PPL",
    "PFG", "PG", "PGR", "PLD", "PRU", "PEG", "PTC", "PSA", "PHM",
    "QRVO", "PWR", "QCOM", "DGX", "RL", "RJF", "RTX", "O", "REG",
    "REGN", "RF", "RSG", "RMD", "RVTY", "RHI", "ROK", "ROL", "ROP",
    "ROST", "RCL", "SPGI", "CRM", "SBAC", "SLB", "STX", "SRE", "NOW",
    "SHW", "SPG", "SWKS", "SJM", "SNA", "SOLV", "SO", "LUV", "SWK",
    "SBUX", "STT", "STLD", "STE", "SYK", "SYF", "SNPS", "SYY", "TMUS",
    "TRGP", "TGT", "TEL", "TDY", "TFX", "TER", "TSLA", "TXN", "TXT",
    "TMO", "TJX", "TSCO", "TT", "TDG", "TRV", "TRMB", "TFC", "TYL",
    "TSN", "USB", "UBER", "UDR", "ULTA", "UNP", "UAL", "UPS", "URI",
    "UNH", "UHS", "VLO", "VTR", "VLTO", "VRSN", "VRSK", "VZ", "VRTX",
    "VTRS", "VICI", "V", "VMC", "WRB", "WAB", "WBA", "WMT", "DIS",
    "WBD", "WM", "WAT", "WEC", "WFC", "WELL", "WST", "WDC", "WRK",
    "WY", "WMB", "WTW", "GWW", "WYNN", "XEL", "XYL", "YUM", "ZBRA",
    "ZBH", "ZTS",
]


# Dow Jones Industrial Average (30)
DOW_JONES = [
    "AAPL", "AMGN", "AMZN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX",
    "DIS", "DOW", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO",
    "MCD", "MMM", "MRK", "MSFT", "NKE", "PG", "SHW", "TRV", "UNH",
    "V", "VZ", "WMT",
]

# Russell 2000 — Top 100 por capitalizacion (proxy representativo)
RUSSELL_2K_TOP = [
    "SMCI", "MSTR", "CELH", "ANF", "LNTH", "ENPH", "CROX", "RKLB",
    "ELF", "DUOL", "TOST", "FND", "CAVA", "PCVX", "AFRM", "CWST",
    "INSM", "GKOS", "STRL", "CARG", "HIMS", "JOBY", "CVNA", "PLNT",
    "RDFN", "UPST", "SHAK", "SOUN", "IONQ", "RXRX", "DJT", "ACHR",
    "RIOT", "MARA", "CLSK", "HUT", "BITF", "WULF", "CIFR", "IREN",
    "BTDR", "CORZ", "COIN", "HOOD", "SOFI", "AEHR", "LMND", "MNDY",
    "GTLB", "RBLX", "DKNG", "ROKU", "PINS", "SNAP", "LYFT", "ETSY",
    "CHWY", "W", "FVRR", "ZI", "PATH", "AI", "BBAI", "PLTR",
    "ASAN", "NET", "CFLT", "MDB", "ESTC", "DOCN", "DT", "BRZE",
    "SPT", "BILL", "PCOR", "CWAN", "TMDX", "AXSM", "SAIA", "ODFL",
    "XPO", "GXO", "ARCB", "WERN", "JBHT", "LSTR", "MATX", "SNDR",
    "EXEL", "ALNY", "SRPT", "BMRN", "RARE", "HALO", "INCY", "NBIX",
    "PRCT", "NUVL", "ITCI", "KRYS",
]

# Semiconductores — principales
SEMICONDUCTORS = [
    "NVDA", "AMD", "INTC", "AVGO", "QCOM", "TXN", "MU", "MRVL",
    "LRCX", "KLAC", "AMAT", "ASML", "ADI", "NXPI", "ON", "MCHP",
    "SWKS", "QRVO", "ARM", "GFS", "SMCI", "TSM",
]

# Biotech/Pharma — principales
BIOTECH = [
    "MRNA", "PFE", "JNJ", "LLY", "ABBV", "AMGN", "GILD", "BIIB",
    "REGN", "VRTX", "BMY", "MRK", "AZN", "ALNY", "SRPT", "BMRN",
    "INCY", "NBIX", "EXEL", "HALO", "INSM", "PCVX", "RXRX", "ILMN",
    "DXCM", "ISRG", "IOVA", "SGEN", "BNTX", "CRSP",
]

# Energia
ENERGY = [
    "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "VLO", "PSX", "PXD",
    "DVN", "OXY", "FANG", "HES", "HAL", "BKR", "TRGP", "OKE", "WMB",
    "KMI", "ET",
]

# Finanzas — principales
FINANCIALS = [
    "JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "SCHW", "AXP",
    "COF", "USB", "PNC", "TFC", "MTB", "FITB", "KEY", "CFG", "HBAN",
    "RF", "ALLY", "SOFI", "HOOD", "ICE", "CME", "CBOE", "NDAQ",
    "MCO", "SPGI", "V", "MA",
]

# FAANG+ / Mega cap tech
MEGACAP_TECH = [
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "NVDA", "TSLA",
    "NFLX", "AVGO", "CRM", "ORCL", "ADBE", "INTC", "AMD", "QCOM",
    "NOW", "INTU", "UBER", "ABNB", "SNAP", "PINS", "ROKU", "DKNG",
    "RBLX", "PLTR", "COIN", "SQ", "SHOP", "MELI",
]

# Meme stocks / alta volatilidad retail
MEME_VOLATILE = [
    "GME", "AMC", "BBBY", "BB", "PLTR", "SOFI", "RIVN", "LCID",
    "NIO", "XPEV", "CVNA", "UPST", "AFRM", "DJT", "SMCI", "IONQ",
    "SOUN", "RKLB", "ACHR", "JOBY", "HOOD", "COIN", "MSTR", "RIOT",
    "MARA", "CLSK", "HUT", "BITF",
]


INDICES = {
    "nasdaq100":    ("NASDAQ-100", NASDAQ_100),
    "sp500":        ("S&P 500", SP500),
    "dow":          ("Dow Jones 30", DOW_JONES),
    "semiconductors": ("Semiconductores", SEMICONDUCTORS),
    "biotech":      ("Biotech / Pharma", BIOTECH),
    "energy":       ("Energia", ENERGY),
    "financials":   ("Finanzas", FINANCIALS),
    "megacap":      ("Mega Cap Tech", MEGACAP_TECH),
    "meme":         ("Meme / Alta Volatilidad", MEME_VOLATILE),
    "russell2k":    ("Russell 2000 (Top 100)", RUSSELL_2K_TOP),
    "all":          ("S&P 500 + NASDAQ-100", []),  # special case
}


def get_index_tickers(index: str) -> list[str]:
    """Devuelve los tickers de un índice."""
    key = index.lower().replace("&", "").replace(" ", "")
    if key in ("all", "todos", "full"):
        combined = list(SP500)
        for t in NASDAQ_100:
            if t not in combined:
                combined.append(t)
        return combined
    if key in INDICES:
        return INDICES[key][1]
    return []


def list_indices() -> list[dict]:
    """Devuelve la lista de índices disponibles."""
    result = []
    for key, (name, tickers) in INDICES.items():
        count = len(get_index_tickers(key)) if key == "all" else len(tickers)
        result.append({"id": key, "name": name, "count": count})
    return result
