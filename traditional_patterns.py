"""
ChendAI CANONICAL PATTERNS - REAL PROFESSIONAL THALAM
Strict traditional structures: Pathu, Koora, Kalasam.
"""

# PANCHARI MELAM - CANONICAL STRUCTURE
# The hierarchy is precise:
# 1. Nerkol (The Promenade - Base Cycle)
# 2. Koora (The Development - Triplet variations)
# 3. Theermanam (The Cadence)

PANCHARI_PATTERNS = {
    "pathikaalam": {
        "base_bpm": 85, # Slightly faster start for professional feel
        "pattern": [
            # NERKOL (The Foundation) - 1st Cycle
            "Ta", ".", "ka", ".", "Ta", ".", "ka", ".", "Ta", "Ka", "Ta", ".", "Na", ".", "ka", ".",
            "Ta", ".", "Ka", ".", "Ta", ".", "Na", ".", "Ta", "Ka", "ta", "Ka", "Na", ".", "Ta", ".",
            
            # KOORA START (Triplet Feel Injection)
            "Ta", "Ki", "Ta", "Ta", "Ki", "Ta", ".", ".", "Ta", "Ki", "Ta", "Ta", "Ki", "Ta", ".", ".",
            
            # NERKOL RETURN
            "Ta", ".", "Ka", "Ta", "ka", ".", "Na", ".", "Ta", "Ka", "Ta", "Na", "Ta", ".", "Ka", ".",
            
            # KOORA DEVELOPMENT (Dense)
            "Ta", "Ki", "Ta", "Ta", "Ki", "Ta", "Ta", "Ki", "Ta", "Dheem", ".", "Dheem", ".", "Dheem", ".", ".",
            "Ta", "Ka", "Ta", "Ka", "Ta", "Ka", "Ta", "Ka", "Ta", "Ka", "Ta", "Ka", "Ta", "Ka", "Ta", "Ka"
        ],
        "illathaalam": "1...1...1...1...1.1.1.1.1.1.1.1."
    },
    
    "randam_kaalam": {
        "base_bpm": 170,
        "pattern": [
            # IDAKKAALAM (Middle Density)
            "Ta", "Ka", "Ta", "Na", "Ta", "Ka", "Ta", "Ka",
            "Ta", "Ka", "Na", "Ta", "Ta", "Ki", "Ta", ".",
            # VARIATION
            "Ta", "Ka", "Dheem", "Ta", "Ka", "Dheem", "Ta", "Ka",
            "Ta", "Ka", "Na", "Ta", "Dha", "Ka", "Na", "Ta"
        ],
        "illathaalam": "1.1.1.1.1.1.1.1."
    },
    
    "moonam_kaalam": {
        "base_bpm": 240, 
        "pattern": [
            # URUTTU START (Rolling)
            "Ta", "Ka", "Na", "Ta", "Ka", "Na", "Ta", "Ka",
            "Ta", "Ki", "Ta", "Ta", "Ki", "Ta", "Ta", "Ki", "Ta",
            "Ta", "Ka", "Ta", "Na", "Ta", "Ka", "Na", "Ta"
        ],
        "illathaalam": "11111111"
    },
    
    "naalam_kaalam": {
        "base_bpm": 320,
        "pattern": [
            # FAST URUTTU
            "Ta", "Ka", "Na", "Ta", "Ka", "Na", "Ta", "Ka", "Na", "Ta", "Ka", "Na",
            "Dheem", "Ta", "Ka", "Dheem", "Ta", "Ka", "Dheem", "Ta", "Ka"
        ],
        "illathaalam": "11111111"
    },
    
    "anchaam_kaalam": {
        "base_bpm": 400,
        "pattern": [
            # KALASAM (The Finishing Cadence)
            "Ta", "Na", "Ta", "Na", "Ta", "Na", "Ta", "Na",
            "Ta", "Ka", "Ta", "Ka", "Ta", "Ka", "Ta", "Ka",
            # THEERMANAM (3-Hit Stop)
            "Ta", ".", "Ta", ".", "Ta", ".",
            "Ta", ".", "Ta", ".", "Ta", "."
        ],
        "illathaalam": "111111",
        "add_uruttu": True,
        "triple_hits": True
    }
}

# STROKE LIBRARY (Pure Spectral Mappings)
STROKE_LIBRARY = {
    # Mapped to the new Spectral Categories (THAAM, DHEEM, NAM, CHAPU)
    "Ta": "THAAM",
    "Ka": "CHAPU", 
    "Na": "NAM",
    "Dha": "DHEEM",
    "Dheem": "DHEEM",
    "Chapu": "CHAPU",
    
    "ka": "CHAPU", # Soft
    "ta": "THAAM", # Soft
    
    # Rolls map to simple strokes but executed fast
    "TaTa": "THAAM",
    "KaKa": "CHAPU",
    "TaKiTa": "THAAM",
    
    # Cymbals
    "1": "NAM", # Used for metal for now
    ".": "REST"
}

# OTHER MODES MAPPED TO PANCHARI FOR NOW (To ensure canon stability)
PANDI_PATTERNS = PANCHARI_PATTERNS
THAYAMBAKA_PATTERNS = PANCHARI_PATTERNS
PANCHAVADYAM_PATTERNS = PANCHARI_PATTERNS
MANGALAM_PATTERN = PANCHARI_PATTERNS["anchaam_kaalam"]
