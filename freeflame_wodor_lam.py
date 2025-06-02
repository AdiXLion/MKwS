import cantera as ct
import pandas as pd
import matplotlib.pyplot as plt

# Definicja mieszanki
phi_values = [0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 2.0, 3.0, 4.0]  # Wartości współczynnika ekwiwalencji
pressure = ct.one_atm
temperature = 300  # Początkowa temperatura [K]
fuel = "H2"
oxidizer = "O2:1, N2:3.76"

# Lista do przechowywania wyników
data_list = []

# Symulacja dla różnych wartości współczynnika ekwiwalencji
for i, phi in enumerate(phi_values, start=1):
    print(f"Obliczanie dla φ = {phi} ({i}/{len(phi_values)})...")

    gas = ct.Solution("gri30.yaml")
    gas.set_equivalence_ratio(phi, fuel, oxidizer)
    gas.TP = temperature, pressure

    flame = ct.FreeFlame(gas)
    flame.solve(loglevel=0)

    # Pobranie danych
    z = flame.grid  # Pozycja [m]
    concentration_H2 = flame.X[gas.species_index(fuel)]  # Stężenie H2 [-]
    heat_release = flame.heat_release_rate  # Wydzielanie ciepła [W/m³]
    viscosity = flame.viscosity  # Lepkość [Pa·s]
    temperature_profile = flame.T  # Temperatura [K]
    
    # Obliczenie laminarniej prędkości spalania
    laminar_burning_velocity = flame.velocity[0]  # Pierwsza wartość prędkości płomienia
    print(f"Laminarną prędkość spalania dla φ = {phi}: {laminar_burning_velocity:.4f} m/s")

    # Szacowanie długości płomienia
    flame_length = z[temperature_profile.argmax()]
    
    # Tworzenie DataFrame
    df = pd.DataFrame({
        "Pozycja w płomieniu [m]": z,
        "Stężenie H2 [-]": concentration_H2,
        "Wydzielanie ciepła [W/m³]": heat_release,
        "Lepkość [Pa·s]": viscosity,
        "Temperatura [K]": temperature_profile
    })
    df["Współczynnik ekwiwalencji"] = phi
    df["Długość płomienia [m]"] = flame_length
    df["Laminarną prędkość spalania [m/s]"] = laminar_burning_velocity
    data_list.append(df)

# Łączenie wszystkich wyników w jeden DataFrame
results_df = pd.concat(data_list, ignore_index=True)
print("Obliczenia zakończone! Generowanie wykresów...")

# Tworzenie pojedynczych wykresów dla każdej analizy
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
