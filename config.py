import os

# OpenAI Configuration
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")

# Generation Parameters
DG_TEMPERATURE = 0.95  # High for divergent generation
DG_MAX_TOKENS = 2000
DG_ARTIFACT_COUNT = 5  # Number of artifacts per cycle

CC_TEMPERATURE = 0.4  # Low for analytical critique
CC_MAX_TOKENS = 1500
CC_MAX_SELECTED = 3  # Maximum artifacts to select per cycle

# Tension Controller Thresholds
TC_MIN_KNOTS = 1  # Minimum open knots to maintain
TC_COMPRESSION_TARGET = 0.4  # Target compression ratio (0.3-0.5 ideal)
TC_NOVELTY_THRESHOLD = 0.05  # Below this triggers diminishing returns
TC_FORCED_DIVERGENCE_TEMP = 1.2  # Temperature for chaos injection

# Orchestrator Settings
MAX_CYCLES = 10
DIMINISHING_RETURNS_CYCLES = 3  # Consecutive low-novelty cycles before stop

# File Paths
MEMORY_DIR = "memory"
SCRATCH_DIR = "scratch"
PROMPTS_DIR = "prompts"
CRYSTALLIZED_FILE = f"{MEMORY_DIR}/crystallized.json"
OPEN_KNOTS_FILE = f"{MEMORY_DIR}/open_knots.json"
SCRATCH_FILE = f"{SCRATCH_DIR}/last_cycle.json"
DG_PROMPT_FILE = f"{PROMPTS_DIR}/dg_prompt.txt"
CC_PROMPT_FILE = f"{PROMPTS_DIR}/cc_prompt.txt"
