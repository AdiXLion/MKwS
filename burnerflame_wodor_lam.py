import cantera as ct
import pandas as pd
import matplotlib.pyplot as plt

# Definicja mieszanki
phi_values = [0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 2.0, 3.0, 4.0]  
pressure = ct.one_atm
temperature = 300  # Początkowa temperatura [K]
fuel = "H2"
oxidizer = "O2:1, N2:3.76"

# Prędkość dopływu paliwa
burner_velocity = 0.5 # [m/s] Prędkość dopływu mieszanki

# Lista do przechowywania wyników
data_list = []

# Symulacja dla różnych wartości współczynnika ekwiwalencji
for i, phi in enumerate(phi_values, start=1):
    print(f"Obliczanie dla φ = {phi} ({i}/{len(phi_values)})...")

    gas = ct.Solution("gri30.yaml")
    gas.set_equivalence_ratio(phi, fuel, oxidizer)
    gas.TP = temperature, pressure

    # Definicja warunków palnika
    flame = ct.BurnerFlame(gas)
    flame.burner.mdot = burner_velocity * gas.density  # Ustalona masa przepływu
    flame.solve(loglevel=0, refine_grid=True, auto=True)
    flame.set_refine_criteria(ratio=2, slope=0.1, curve=0.1)
    flame.set_time_step_factor(0.0001)

    # Pobranie danych
    z = flame.grid
    concentration_H2 = flame.X[gas.species_index(fuel)]
    heat_release = flame.heat_release_rate
    viscosity = flame.viscosity
    temperature_profile = flame.T
    
    # Laminarną prędkość spalania
    laminar_burning_velocity = flame.velocity[-1]  
    print(f"Laminarną prędkość spalania dla φ = {phi}: {laminar_burning_velocity:.4f} m/s")

    # Tworzenie DataFrame
    df = pd.DataFrame({
    "Pozycja w płomieniu [m]": z,
    "Stężenie H2 [-]": flame.X[gas.species_index(fuel)],
    "Wydzielanie ciepła [W/m³]": flame.heat_release_rate,
    "Lepkość [Pa·s]": flame.viscosity,
    "Temperatura [K]": flame.T,
    "Prędkość płomienia [m/s]": flame.velocity[:]
    })
    df["Współczynnik ekwiwalencji"] = phi
    df["Laminarną prędkość spalania [m/s]"] = laminar_burning_velocity
    data_list.append(df)

# Łączenie wszystkich wyników w jeden DataFrame
results_df = pd.concat(data_list, ignore_index=True)
print("koniec obliczeń, generowanie wykresów")

def plot_single_chart(x, y, title, xlabel, ylabel):
    plt.figure(figsize=(8, 6))
    for phi in phi_values:
        subset = results_df[results_df["Współczynnik ekwiwalencji"] == phi]
        plt.plot(subset[x], subset[y], label=f"φ = {phi}")
    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.show()

# Generowanie pojedynczych wykresów
plot_single_chart("Pozycja w płomieniu [m]", "Stężenie H2 [-]", "Profil stężenia H2", "Pozycja w płomieniu [m]", "Stężenie H2 [-]")
plot_single_chart("Pozycja w płomieniu [m]", "Wydzielanie ciepła [W/m³]", "Maksymalna szybkość wydzielania ciepła", "Pozycja w płomieniu [m]", "Wydzielanie ciepła [W/m³]")
plot_single_chart("Pozycja w płomieniu [m]", "Lepkość [Pa·s]", "Zmienność lepkości dynamicznej", "Pozycja w płomieniu [m]", "Lepkość [Pa·s]")
plot_single_chart("Pozycja w płomieniu [m]", "Temperatura [K]", "Profil temperatury", "Pozycja w płomieniu [m]", "Temperatura [K]")
plt.figure(figsize=(8, 6))
for phi in phi_values:
    subset = results_df[results_df["Współczynnik ekwiwalencji"] == phi]
    plt.plot(subset["Pozycja w płomieniu [m]"], subset["Prędkość płomienia [m/s]"], label=f"φ = {phi}")

plt.title("Profil prędkości płomienia")
plt.xlabel("Pozycja w płomieniu [m]")
plt.ylabel("Prędkość płomienia [m/s]")
plt.legend()
plt.grid(True)
plt.show()
