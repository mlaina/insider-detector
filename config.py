"""Umbrales de detección para actividad inusual en opciones."""

# --- Filtros básicos ---
MIN_VOLUME = 100              # Volumen mínimo absoluto para no filtrar ruido
MAX_OTM_PCT = 0.30            # Hasta 30% OTM
MIN_DTE = 1
MAX_DTE = 45

# --- Detección de anomalías ---
# Un contrato es "inusual" si su volumen hoy supera X veces el promedio
# del volumen de opciones del ticker (estimado via total options volume)
VOL_ANOMALY_MULTIPLIER = 3.0  # Vol hoy >= 3x media → anomalía

# Vol/OI mínimo para considerar (señal de posiciones NUEVAS, no rolleo)
MIN_VOL_OI_RATIO = 1.5

# Notional mínimo ($) para que la alerta sea relevante
MIN_NOTIONAL = 50_000

# --- Directional Flow ---
# Umbral de dominancia para flujo extremo direccional (% de vol en una dirección)
DIRECTIONAL_FLOW_THRESHOLD = 0.75  # 75%+ en calls o puts = flujo direccional
EXTREME_DIRECTIONAL_THRESHOLD = 0.85  # 85%+ = flujo extremo

# --- OI Concentration ---
# Umbral de concentración de OI en un solo contrato vs total del ticker
OI_CONCENTRATION_THRESHOLD = 0.20  # 20%+ del OI total en un solo contrato
OI_CONCENTRATION_MIN = 1000  # Mínimo OI absoluto para considerar concentración

# --- Scoring: pesos (suman 1.0) ---
WEIGHT_VOL_ANOMALY = 0.20     # Volumen vs media histórica del ticker
WEIGHT_VOL_OI = 0.15          # Posiciones nuevas (vol >> OI)
WEIGHT_NOTIONAL = 0.15        # Tamaño de la apuesta en $
WEIGHT_NEAR_EXPIRY = 0.12     # Near-term = más apalancamiento = más sospechoso
WEIGHT_OTM_DEPTH = 0.08       # OTM profundo con volumen = apuesta direccional fuerte
WEIGHT_CLUSTERING = 0.08      # Múltiples strikes inusuales en el mismo ticker
WEIGHT_DIRECTIONAL_FLOW = 0.12  # Flujo extremo en una dirección (calls vs puts)
WEIGHT_OI_CONCENTRATION = 0.10  # Concentración anormal de OI en contratos específicos

# Umbral mínimo de score (0-100) para generar alerta
ALERT_THRESHOLD = 50

# --- Rate limiting para Yahoo Finance ---
BATCH_SIZE = 10               # Tickers por lote
DELAY_BETWEEN_BATCHES = 2.0   # Segundos entre lotes
DELAY_BETWEEN_TICKERS = 0.3   # Segundos entre tickers individuales

# --- Monitoreo ---
SCAN_INTERVAL_MINUTES = 15
