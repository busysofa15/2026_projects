import numpy as np
no_of_atoms = 1
no_of_protons = 79
no_of_neutrons = 118
max_atoms = 10000
protons = np.zeros(max_atoms)
neutrons = np.zeros(max_atoms)
protons_id = np.arange(max_atoms)
neutrons_id = np.arange(max_atoms)
protons[:no_of_atoms] = no_of_protons
neutrons[:no_of_atoms] = no_of_neutrons
nucleons = protons[:no_of_atoms]+neutrons[:no_of_atoms]


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
    return binding_energy, surface_term


binding_energy, surface_term = binding_data(
    protons[:no_of_atoms], neutrons[:no_of_atoms])


def daughter_atoms(protons, neutrons, nucleons, binding_energy):
    split_bias = np.random.normal(loc=0.5, scale=0.1, size=no_of_atoms)
    split_bias = np.clip(split_bias, 0, 1)
    neutrons_separated = np.random.poisson(2.00, size=no_of_atoms)
    neutrons_after_fission = (neutrons + 1 - neutrons_separated)
    new_protons_1 = (protons*split_bias).astype(int)
    new_protons_2 = protons - new_protons_1
    new_neutrons_1 = (neutrons_after_fission*split_bias).astype(int)
    new_neutrons_2 = neutrons_after_fission - new_neutrons_1
    new_nucleon_1 = new_protons_1+new_neutrons_1
    new_nucleon_2 = new_protons_2+new_neutrons_2
    binding_energy_daughter_atom_1, random_term = binding_data(
        protons=new_protons_1, neutrons=new_neutrons_1)
    binding_energy_daughter_atom_2, random_term_2 = binding_data(
        protons=new_protons_2, neutrons=new_neutrons_2)
    be_daughters = binding_energy_daughter_atom_1+binding_energy_daughter_atom_2
    q_factor = be_daughters-binding_energy
    return q_factor, new_protons_1, new_protons_2


q_factor, new_nucleon_1, new_nucleon_2 = daughter_atoms(protons[:no_of_atoms],
                                                   neutrons[:no_of_atoms], nucleons, binding_energy)
print(q_factor)

