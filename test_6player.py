"""Quick test of 6-player system"""
import sys
sys.dont_write_bytecode = True  # Disable .pyc creation

from chendai_6player import ChendAI6Player

# Initialize
chendai = ChendAI6Player(enable_spatial=False, orchestration_strategy="traditional")

# Generate short test
print("\n🎵 Generating 5-second test...")
output = chendai.generate_melam("test panchari", duration=5, orchestration_strategy="traditional")
print(f"\n✅ Success! Output: {output}")
