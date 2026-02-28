import numpy as np

class AudioEncoder:
    def __init__(self):
        self.current_phase = 0.0

    def generate_tone_array(self, hz: int, sample_rate: int, duration_ms: int = 100):
        duration_sec = duration_ms #/ 1000.0
        num_samples = int(sample_rate * duration_sec)
        
        # 1. Calculate how much the phase moves per sample for this frequency
        # Phase increment = 2 * pi * frequency / sample_rate
        phase_step = 2 * np.pi * hz / sample_rate
        
        # 2. Create an array of phase steps
        phases = self.current_phase + np.arange(num_samples) * phase_step
        
        # 3. Generate the sine wave
        tone = 0.5 * np.sin(phases)
        
        # 4. Update the stored phase for the NEXT chunk
        # We use modulo 2*pi to keep the number from growing toward infinity
        self.current_phase = (phases[-1] + phase_step) % (2 * np.pi)
        
        return tone.astype(np.float32)