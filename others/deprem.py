import numpy as np
import matplotlib.pyplot as plt

# Parameters
Sds = 1.170
Sd1 = 0.400

# Corner periods
TA = 0.2 * Sd1 / Sds
TB = Sd1 / Sds
TD = 6.0

# Period grid: dense to 1s
T = np.concatenate([np.arange(0, 1.00, 0.01), np.arange(1.00, 8.05, 0.05)])

# Spectrum
Sa = []
for t in T:
    if t <= TA:
        Sa.append(Sds * (0.4 + 0.6 * t / TA))  # ✅ fixed 0.6 factor
    elif t <= TB:
        Sa.append(Sds)
    elif t <= TD:
        Sa.append(Sd1 / t)
    else:
        Sa.append(Sd1 * TD / t**2)

# Save (dot-decimal)
np.savetxt("../Elastic_Design_Spectrum_Dense_FIX.txt",
           np.column_stack((T, Sa)), fmt="%.3f")

# If ETAATABS expects comma-decimal on your Windows:
with open("../Elastic_Design_Spectrum_Dense_FIX.txt", "r") as f:
    txt = f.read().replace(".", ",")
with open("../Elastic_Design_Spectrum_Dense_TR.txt", "w") as f:
    f.write(txt)

# Plot
plt.figure(figsize=(10, 6))
plt.plot(T, Sa, 'b-', linewidth=2)
plt.xlabel('Period, T (s)', fontsize=12)
plt.ylabel('Spectral Acceleration, Sa (g)', fontsize=12)
plt.title('Elastic Design Spectrum', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.xlim(0, max(T))
plt.ylim(bottom=0)
plt.tight_layout()
plt.savefig('../Elastic_Design_Spectrum.png', dpi=300)
plt.show()

print("✅ Files saved to workspace root and plot generated.")
