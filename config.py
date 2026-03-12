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

# --- Scoring: pesos (suman 1.0) ---
WEIGHT_VOL_ANOMALY = 0.25     # Volumen vs media histórica del ticker
WEIGHT_VOL_OI = 0.20          # Posiciones nuevas (vol >> OI)
WEIGHT_NOTIONAL = 0.20        # Tamaño de la apuesta en $
WEIGHT_NEAR_EXPIRY = 0.15     # Near-term = más apalancamiento = más sospechoso
WEIGHT_OTM_DEPTH = 0.10       # OTM profundo con volumen = apuesta direccional fuerte
WEIGHT_CLUSTERING = 0.10      # Múltiples strikes inusuales en el mismo ticker

# Umbral mínimo de score (0-100) para generar alerta
ALERT_THRESHOLD = 50

# --- Rate limiting para Yahoo Finance ---
BATCH_SIZE = 10               # Tickers por lote
DELAY_BETWEEN_BATCHES = 2.0   # Segundos entre lotes
DELAY_BETWEEN_TICKERS = 0.3   # Segundos entre tickers individuales

# --- Monitoreo ---
SCAN_INTERVAL_MINUTES = 15
