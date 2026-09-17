import numpy as np
import matplotlib.pyplot as plt
protons = np.arange(1, 93)
neutrons = np.array([
    0, 2, 4, 5, 6, 6, 7, 8, 10, 10, 12, 12, 14, 14, 16, 16, 18, 22, 20, 20,
    22, 24, 26, 28, 30, 30, 32, 34, 36, 36, 38, 40, 42, 44, 46, 48, 50, 50,
    52, 54, 52, 54, 56, 58, 60, 62, 62, 64, 66, 68, 70, 72, 74, 74, 78, 80,
    82, 82, 82, 82, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106,
    108, 110, 112, 114, 116, 118, 120, 122, 124, 126, 128, 130, 132, 134,
    136, 138, 140, 142, 146
])
nucleons = protons+neutrons
# change atoms and the way the work tmrw cos my brain is fried today


def binding_data(protons, neutrons):
    nucleons = protons+neutrons
    volume_term = 15.67*(nucleons)
    surface_term = 17.23*(nucleons**(2/3))
    coulomb_term = 0.75*(protons*(protons-1)/nucleons**(1/3))
    assymetry_term = 23.2*(((neutrons-protons)**2)/nucleons)
    even_protons = (protons % 2 == 0)
    odd_protons = ~(even_protons)
    even_neutrons = (neutrons % 2 == 0)
    odd_neutrons = ~(even_neutrons)
    nucleons_odd = ~(nucleons % 2 == 0)
    pairing_term = np.zeros(len(protons))
    conditions = [
        (even_protons & even_neutrons),
        (odd_protons & odd_neutrons)
    ]
    choices = [
        12 * (nucleons**(-0.5)),
        -12 * (nucleons**(-0.5))
    ]
    pairing_term = np.select(conditions, choices, default=0)
    pairing_term[nucleons_odd] = 0
    binding_energy = volume_term - surface_term - \
        coulomb_term - assymetry_term + pairing_term
    return binding_energy


wth = binding_data(protons, neutrons)
binding_energy_fr = wth/nucleons
plt.plot(protons, binding_energy_fr, 'o')

# 2. Add labels (crucial so you don't get lost)
plt.xlabel('Number of Protons (Z)')
plt.ylabel('Binding Energy per Nucleon (MeV)')
plt.title('Nuclear Binding Energy Curve')
plt.ylim(7, 10)
# 3. Show it
plt.grid(True)  # Optional: makes it easier to read
plt.show()
