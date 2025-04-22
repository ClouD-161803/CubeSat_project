import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def create_heat_shield_simulation():
    """Main function to run the CubeSat heat shield simulation"""
    
    # ===== CONSTANTS AND PARAMETERS =====
    ORBITAL_PERIOD = 92.5 * 60  # 92.5 minutes in seconds
    dt = 0.1  # seconds
    dx = 0.01  # meters
    sigma = 5.67e-8  # Stefan-Boltzmann constant (W/m²·K⁴)
    emissivity = 0.85  # Typical emissivity for heat shield materials
    
    # ===== MATERIAL PROPERTIES =====
    # [PICA, Aerogel, Aluminum 6082]
    materials = ["PICA", "Aerogel", "Aluminum 6082"]
    thicknesses = np.array([5.0, 4.0, 2.5]) * 1e-3  # mm to m
    k_values = np.array([0.18, 0.010, 170.0])  # W/(m·K)
    rho_values = np.array([290, 150, 2700])  # kg/m³
    cp_values = np.array([900, 850, 900])  # J/(kg·K)
    max_service_temps = np.array([1650, 1200, 400])  # °C
    
    # Calculate thermal diffusivity and verify stability condition
    alpha_values = k_values / (rho_values * cp_values)
    alpha_Al = alpha_values[2]  # Aluminum has highest diffusivity
    stability_threshold = dx**2 / (2 * alpha_Al)
    print(f"Stability threshold: {stability_threshold:.4f} s (given: 0.5155 s)")
    print(f"Chosen dt: {dt:.4f} s {'(stable)' if dt <= stability_threshold else '(unstable)'}")
    
    # ===== MESH GENERATION =====
    # Use finer mesh in regions with steeper gradients
    nodes_per_layer = [int(np.ceil(t / dx)) for t in thicknesses]
    total_nodes = sum(nodes_per_layer)
    
    # Initialize arrays for node properties
    x = np.zeros(total_nodes)
    k = np.zeros(total_nodes)
    rho = np.zeros(total_nodes)
    cp = np.zeros(total_nodes)
    layer_indices = np.zeros(total_nodes, dtype=int)
    
    # Assign material properties to nodes
    node_idx = 0
    for layer in range(len(thicknesses)):
        for i in range(nodes_per_layer[layer]):
            x[node_idx] = sum(thicknesses[:layer]) + i * thicknesses[layer] / nodes_per_layer[layer]
            k[node_idx] = k_values[layer]
            rho[node_idx] = rho_values[layer]
            cp[node_idx] = cp_values[layer]
            layer_indices[node_idx] = layer
            node_idx += 1
    
    # Add final node exactly at the end of the heat shield
    x[-1] = sum(thicknesses)
    
    # Calculate dx between nodes
    dx_values = np.diff(x)
    dx_values = np.append(dx_values, dx_values[-1])  # Add value for last node
    
    # ===== LOAD AND PROCESS TIME SERIES DATA =====
    time_series = parse_time_series()
    
    # Extract data columns
    time_norm = time_series['time']
    radiation_intensity = time_series['radiation_intensity']
    temperature = time_series['temperature']
    internal_temperature = time_series['internal_temperature']
    albedo_radiation = time_series['albedo_radiation']
    
    # Convert normalized time to seconds
    time_seconds = time_norm * ORBITAL_PERIOD
    
    # Create interpolation functions
    radiation_interp = interp1d(time_seconds, radiation_intensity, kind='linear', 
                               bounds_error=False, fill_value='extrapolate')
    albedo_interp = interp1d(time_seconds, albedo_radiation, kind='linear', 
                            bounds_error=False, fill_value='extrapolate')
    internal_temp_interp = interp1d(time_seconds, internal_temperature, kind='linear', 
                                   bounds_error=False, fill_value='extrapolate')
    
    # ===== SIMULATION SETTINGS =====
    num_orbits = 3  # Number of orbits to simulate
    simulation_time = num_orbits * ORBITAL_PERIOD
    num_time_steps = int(simulation_time / dt)
    
    # Initialize temperature array
    T = np.ones(total_nodes) * temperature[0]  # Start with initial surface temperature
    
    # Arrays to store results for plotting
    time_points = []
    temperature_profiles = []
    surface_temps = []
    back_temps = []
    total_heat_flux = []
    
    # ===== MAIN SIMULATION LOOP =====
    print("Starting simulation...")
    for step in range(num_time_steps):
        current_time = step * dt
        
        # Get interpolated values from time series at current time
        orbit_time = current_time % ORBITAL_PERIOD
        solar_radiation = radiation_interp(orbit_time)
        albedo = albedo_interp(orbit_time)
        back_temp = internal_temp_interp(orbit_time)
        
        # Set temperature at back boundary
        T[-1] = back_temp
        
        # Calculate total incident radiation
        q_in = solar_radiation + albedo
        
        # Store data for visualization
        if step % int(ORBITAL_PERIOD / (dt * 20)) == 0:  # ~20 points per orbit
            time_points.append(current_time)
            temperature_profiles.append(T.copy())
            surface_temps.append(T[0])
            back_temps.append(T[-1])
            total_heat_flux.append(q_in)
        
        # Create temperature array for next time step
        T_new = np.copy(T)
        
        # Update interior nodes using FTCS scheme
        for i in range(1, total_nodes - 1):
            # Calculate interface thermal properties
            if i < total_nodes - 1:
                if layer_indices[i] != layer_indices[i+1]:
                    # Interface between different materials
                    k_right = 2 * k[i] * k[i+1] / (k[i] + k[i+1])  # Harmonic mean
                else:
                    k_right = k[i]
                dx_right = dx_values[i]
            
            if i > 0:
                if layer_indices[i] != layer_indices[i-1]:
                    k_left = 2 * k[i] * k[i-1] / (k[i] + k[i-1])
                else:
                    k_left = k[i]
                dx_left = dx_values[i-1]
            
            # Apply FTCS update
            T_new[i] = T[i] + dt / (rho[i] * cp[i] * dx_values[i]) * (
                k_right * (T[i+1] - T[i]) / dx_right -
                k_left * (T[i] - T[i-1]) / dx_left
            )
        
        # Apply boundary condition at outer surface
        T_surf_K = T[0] + 273.15  # Convert to Kelvin for radiation calculation
        q_out = emissivity * sigma * T_surf_K**4  # Outgoing radiation
        q_net = q_in - q_out  # Net heat flux at surface
        
        # Update surface temperature based on heat flux
        T_new[0] = T[1] + q_net * dx_values[0] / k[0]
        
        # Update temperature array
        T = T_new
        
        # Print progress
        if step % int(num_time_steps / 10) == 0:
            progress = step / num_time_steps * 100
            print(f"Simulation progress: {progress:.1f}%")
    
    # Convert lists to arrays
    time_points = np.array(time_points)
    temperature_profiles = np.array(temperature_profiles)
    
    # ===== VISUALIZATION =====
    plot_results(time_points, temperature_profiles, x, ORBITAL_PERIOD, 
                materials, thicknesses, surface_temps, back_temps, total_heat_flux)
    
    # ===== EXPORT DATA =====
    export_data_to_file(time_points, temperature_profiles, x, ORBITAL_PERIOD,
                      surface_temps, back_temps, total_heat_flux)
    
    # ===== SUMMARY STATISTICS =====
    print_summary(time_points, temperature_profiles, surface_temps, back_temps, 
                 layer_indices, materials, max_service_temps, simulation_time, num_orbits)

def parse_time_series():
    """Parse the time series data from the provided text"""
    time_series_data = """
time	radiation_intensity	temperature	internal_temperature	albedo_radiation
0.00	1363.60	-24.30	-6.90	0.00
0.02	1363.60	-24.00	-7.10	0.00
0.04	1363.60	-23.70	-7.40	13.07
0.06	1363.60	-23.30	-7.80	45.36
0.08	1363.60	-22.50	-8.30	84.14
0.10	1363.60	-21.30	-9.10	126.85
0.12	1363.60	-20.20	-10.20	172.06
0.14	1363.60	-18.50	-11.50	216.01
0.16	1363.60	-16.00	-13.10	257.42
0.18	1363.60	-13.80	-14.80	293.61
0.20	1363.60	-11.20	-16.30	325.93
0.22	1363.60	-8.20	-17.50	353.11
0.24	1363.60	-4.70	-18.20	375.08
0.26	1363.60	-0.60	-16.90	390.56
0.28	1363.60	3.40	-14.20	402.21
0.30	1363.60	7.30	-10.80	407.00
0.32	1363.60	12.20	-7.10	404.75
0.34	1363.60	17.10	-2.90	401.85
0.36	1363.60	21.40	1.60	388.84
0.38	1363.60	27.20	6.40	366.56
0.40	1363.60	32.10	11.80	359.64
0.42	1363.60	38.40	17.50	350.50
0.44	1363.60	43.50	23.60	332.39
0.46	1363.60	50.00	29.80	308.60
0.48	1363.60	55.70	36.10	296.44
0.50	1363.60	62.40	42.50	261.12
0.52	1363.60	68.10	48.70	231.41
0.54	1363.60	74.90	54.60	201.69
0.56	1363.60	81.00	60.20	165.51
0.58	1363.60	87.20	65.90	130.71
0.60	1363.60	91.00	70.80	94.50
0.62	0.00	92.00	74.10	58.29
0.64	0.00	90.50	74.60	25.98
0.66	0.00	88.30	73.80	0.00
0.68	0.00	84.00	72.10	0.00
0.70	0.00	79.30	69.50	0.00
0.72	0.00	72.10	66.20	0.00
0.74	0.00	65.40	62.70	0.00
0.76	0.00	56.50	58.40	0.00
0.78	0.00	48.00	53.50	0.00
0.80	0.00	38.00	48.20	0.00
0.82	0.00	28.80	42.40	0.00
0.84	0.00	18.50	36.10	0.00
0.86	0.00	9.80	29.30	0.00
0.88	0.00	0.00	22.20	0.00
0.90	0.00	-8.40	14.70	0.00
0.92	0.00	-15.50	7.20	0.00
0.94	0.00	-20.80	-0.10	0.00
0.96	0.00	-22.70	-4.80	0.00
0.98	0.00	-24.10	-6.20	0.00
1.00	1363.60	-24.30	-6.90	0.00
1.02	1363.60	-24.10	-7.00	0.00
1.04	1363.60	-23.40	-7.20	13.07
1.06	1363.60	-22.90	-7.60	45.36
1.08	1363.60	-21.70	-8.10	84.14
1.10	1363.60	-20.80	-8.90	126.85
1.12	1363.60	-19.10	-9.80	172.06
1.14	1363.60	-17.60	-10.90	216.01
1.16	1363.60	-15.10	-12.30	257.42
1.18	1363.60	-12.90	-13.60	293.61
1.20	1363.60	-9.60	-14.70	325.93
1.22	1363.60	-6.90	-15.30	353.11
1.24	1363.60	-3.00	-15.50	375.08
1.26	1363.60	0.70	-14.80	390.56
1.28	1363.60	4.50	-13.50	402.21
1.30	1363.60	8.70	-11.70	407.00
1.32	1363.60	13.30	-9.60	404.75
1.34	1363.60	17.60	-6.80	401.85
1.36	1363.60	23.00	-3.50	388.84
1.38	1363.60	27.80	0.20	366.56
1.40	1363.60	34.00	4.30	359.64
1.42	1363.60	39.20	8.80	350.50
1.44	1363.60	45.70	13.60	332.39
1.46	1363.60	51.30	18.80	308.60
1.48	1363.60	58.40	24.50	296.44
1.50	1363.60	64.20	30.60	284.29
1.52	1363.60	71.10	37.30	261.12
1.54	1363.60	76.70	44.20	231.41
1.56	1363.60	83.30	51.10	201.69
1.58	1363.60	88.00	58.00	165.51
1.60	1363.60	91.60	64.70	130.71
1.62	0.00	92.00	70.80	94.50
1.64	0.00	90.30	74.20	58.29
1.66	0.00	86.60	74.60	25.98
1.68	0.00	82.80	73.20	0.00
1.70	0.00	76.70	70.80	0.00
1.72	0.00	70.60	67.40	0.00
1.74	0.00	62.40	63.10	0.00
1.76	0.00	54.60	58.20	0.00
1.78	0.00	44.90	52.60	0.00
1.80	0.00	35.90	46.50	0.00
1.82	0.00	25.60	40.10	0.00
1.84	0.00	16.70	33.60	0.00
1.86	0.00	6.70	26.90	0.00
1.88	0.00	-2.20	20.00	0.00
1.90	0.00	-9.70	12.90	0.00
1.92	0.00	-17.40	5.50	0.00
1.94	0.00	-21.50	-1.60	0.00
1.96	0.00	-23.40	-4.90	0.00
1.98	0.00	-24.20	-6.40	0.00
2.00	0.00	-24.30	-6.90	0.00
"""
    # Parse lines and extract data
    lines = time_series_data.strip().split('\n')
    headers = lines[0].split('\t')
    data = {}
    
    for header in headers:
        data[header] = []
    
    for line in lines[1:]:
        values = line.split('\t')
        for i, header in enumerate(headers):
            data[header].append(float(values[i]))
    
    for header in headers:
        data[header] = np.array(data[header])
    
    return data

def plot_results(time_points, temperature_profiles, x, orbital_period, 
                materials, thicknesses, surface_temps, back_temps, total_heat_flux):
    """Create visualization plots for the simulation results"""
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Temperature profiles at different times
    plt.subplot(2, 2, 1)
    plot_indices = np.linspace(0, len(time_points)-1, 5, dtype=int)
    for i in plot_indices:
        time_hrs = time_points[i] / 3600
        plt.plot(x * 1000, temperature_profiles[i], label=f"t = {time_hrs:.1f} hrs")
    
    # Add material boundaries
    cum_thickness = 0
    for thickness in thicknesses[:-1]:
        cum_thickness += thickness * 1000
        plt.axvline(cum_thickness, color='k', linestyle='--', alpha=0.3)
    
    plt.xlabel("Distance from outer surface (mm)")
    plt.ylabel("Temperature (°C)")
    plt.title("Temperature Profiles Through Heat Shield")
    plt.grid(True)
    plt.legend()
    
    # Plot 2: Temperature vs. normalized time for selected points
    plt.subplot(2, 2, 2)
    # Select points at different depths
    depth_indices = [0, len(x)//4, len(x)//2, 3*len(x)//4, -1]
    normalized_time = (time_points % orbital_period) / orbital_period
    
    for idx in depth_indices:
        depth_mm = x[idx] * 1000
        temp_data = [profile[idx] for profile in temperature_profiles]
        plt.plot(normalized_time, temp_data, label=f"{depth_mm:.1f} mm")
    
    plt.xlabel("Normalized Time (orbital period)")
    plt.ylabel("Temperature (°C)")
    plt.title("Temperature vs. Orbital Position")
    plt.grid(True)
    plt.legend()
    
    # Plot 3: Temperature evolution over time
    plt.subplot(2, 2, 3)
    time_hrs = time_points / 3600
    
    for idx in depth_indices:
        depth_mm = x[idx] * 1000
        temp_data = [profile[idx] for profile in temperature_profiles]
        plt.plot(time_hrs, temp_data, label=f"{depth_mm:.1f} mm")
    
    # Add orbit boundaries
    orbit_times = np.arange(1, time_hrs[-1]//(orbital_period/3600)+1) * (orbital_period/3600)
    for orbit_time in orbit_times:
        plt.axvline(orbit_time, color='gray', linestyle='--', alpha=0.3)
    
    plt.xlabel("Time (hours)")
    plt.ylabel("Temperature (°C)")
    plt.title("Temperature Evolution Over Multiple Orbits")
    plt.grid(True)
    plt.legend()
    
    # Plot 4: Heat shield material visualization with thermal gradient
    plt.subplot(2, 2, 4)
    
    # Pick a representative temperature profile
    profile_idx = len(temperature_profiles) // 2
    
    # Add colored regions for materials
    cum_thickness = 0
    colors = ['brown', 'lightblue', 'silver']
    for i, (material, thickness) in enumerate(zip(materials, thicknesses)):
        start = cum_thickness
        end = cum_thickness + thickness * 1000
        plt.axvspan(start, end, alpha=0.3, color=colors[i], label=material)
        
        # Add material label
        y_pos = (np.max(temperature_profiles[profile_idx]) - 
                np.min(temperature_profiles[profile_idx])) * 0.1
        plt.text((start + end)/2, np.min(temperature_profiles[profile_idx]) - y_pos, 
                material, ha='center', fontsize=9)
        
        cum_thickness = end
    
    # Plot temperature profile
    plt.plot(x * 1000, temperature_profiles[profile_idx], 'k-', linewidth=2, 
            label=f"T at t={time_points[profile_idx]/3600:.1f} hrs")
    
    plt.xlabel("Distance from outer surface (mm)")
    plt.ylabel("Temperature (°C)")
    plt.title("Heat Shield Materials and Temperature Gradient")
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig("cubesat_heat_shield_simulation.png", dpi=300)
    
    # Additional plot: Incoming radiation and surface temperature
    plt.figure(figsize=(10, 6))
    ax1 = plt.gca()
    ax2 = ax1.twinx()
    
    normalized_time = (time_points % orbital_period) / orbital_period
    ax1.plot(normalized_time, surface_temps, 'r-', label="Surface Temperature")
    ax2.plot(normalized_time, total_heat_flux, 'b-', label="Incoming Radiation")
    
    ax1.set_xlabel("Normalized Time (orbital period)")
    ax1.set_ylabel("Temperature (°C)", color='r')
    ax2.set_ylabel("Radiation Intensity (W/m²)", color='b')
    
    ax1.tick_params(axis='y', colors='r')
    ax2.tick_params(axis='y', colors='b')
    
    plt.title("Surface Temperature and Incoming Radiation vs. Orbital Position")
    plt.grid(True)
    
    # Add legend for both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    plt.savefig("cubesat_radiation_and_temperature.png", dpi=300)
    plt.show()

def print_summary(time_points, temperature_profiles, surface_temps, back_temps, 
                 layer_indices, materials, max_service_temps, simulation_time, num_orbits):
    """Print a summary of simulation results"""
    print("\n===== SIMULATION SUMMARY =====")
    print(f"Total simulation time: {simulation_time/3600:.2f} hours ({num_orbits} orbits)")
    print(f"Surface temperature range: {np.min(surface_temps):.1f}°C to {np.max(surface_temps):.1f}°C")
    print(f"Back-face temperature range: {np.min(back_temps):.1f}°C to {np.max(back_temps):.1f}°C")
    
    # Find maximum temperature in each material layer
    max_temps = np.zeros(len(materials))
    for i, profile in enumerate(temperature_profiles):
        for layer in range(len(materials)):
            layer_nodes = np.where(layer_indices == layer)[0]
            layer_max = np.max(profile[layer_nodes])
            max_temps[layer] = max(max_temps[layer], layer_max)
    
    # Print temperature information by material
    print("\nMaximum temperatures by material layer:")
    for i, material in enumerate(materials):
        status = "OK" if max_temps[i] < max_service_temps[i] else "EXCEEDED"
        print(f"{material}: {max_temps[i]:.1f}°C (Max service: {max_service_temps[i]}°C) - {status}")
    
    # Calculate thermal gradients
    max_gradient = 0
    for profile in temperature_profiles:
        gradient = np.abs(np.diff(profile) / np.diff(np.arange(len(profile))))
        max_gradient = max(max_gradient, np.max(gradient))
    
    print(f"\nMaximum thermal gradient: {max_gradient:.1f}°C/node")
    print("===== END SUMMARY =====")


def export_data_to_file(time_points, temperature_profiles, x, orbital_period, surface_temps, back_temps, total_heat_flux, filename="cubesat_simulation_data.txt"):
    """Export simulation data to a tab-delimited text file for two orbital periods"""
    import numpy as np
    
    # Filter data for only the first two orbital periods
    max_time = 2 * orbital_period
    indices = np.where(time_points <= max_time)[0]
    
    filtered_time = time_points[indices]
    filtered_temp_profiles = temperature_profiles[indices]
    filtered_surface_temps = np.array(surface_temps)[indices]
    filtered_back_temps = np.array(back_temps)[indices]
    filtered_heat_flux = np.array(total_heat_flux)[indices]
    
    # Normalize time to orbital period
    normalized_time = (filtered_time % orbital_period) / orbital_period
    orbital_period_num = np.floor(filtered_time / orbital_period) + 1
    
    # Select depths for output
    depth_indices = [0, len(x)//4, len(x)//2, 3*len(x)//4, -1]
    depths_mm = [x[idx] * 1000 for idx in depth_indices]
    
    # Open file for writing
    with open(filename, 'w') as f:
        # Write header row
        header = ["time(s)", "orbit_num", "normalized_time", "surface_temp(C)", "back_temp(C)", "heat_flux(W/m2)"]
        
        # Add headers for intermediate points
        for depth in depths_mm:
            header.append(f"temp_at_{depth:.1f}mm(C)")
        
        f.write("\t".join(header) + "\n")
        
        # Write data rows
        for i in range(len(filtered_time)):
            row = [
                f"{filtered_time[i]:.2f}",  # time in seconds
                f"{orbital_period_num[i]:.0f}",  # orbit number
                f"{normalized_time[i]:.4f}",  # normalized time within orbit
                f"{filtered_surface_temps[i]:.2f}",  # surface temperature
                f"{filtered_back_temps[i]:.2f}",  # back temperature
                f"{filtered_heat_flux[i]:.2f}"  # heat flux
            ]
            
            # Add temperatures at selected depths
            for idx in depth_indices:
                row.append(f"{filtered_temp_profiles[i][idx]:.2f}")
                
            f.write("\t".join(row) + "\n")
            
    print(f"Data for two orbital periods exported to {filename}")


if __name__ == "__main__":
    create_heat_shield_simulation()


