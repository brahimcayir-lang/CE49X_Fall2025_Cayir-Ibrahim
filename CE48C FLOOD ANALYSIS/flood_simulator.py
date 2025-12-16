import numpy as np
from scipy import ndimage
import warnings
warnings.filterwarnings('ignore')


class FloodSimulator2D:
    """
    2D Shallow Water Equations Solver for Flood Simulation
    Implements overflow dam behavior with actual structure dimensions
    """
    
    def __init__(self, dem_data, geotransform, manning_n=0.04, 
                 infiltration_rate=7.5, curve_number=65, dam_height=5.0,
                 initial_water_level=1.0, spillway_width=25.0, 
                 overflow_elevation=412.0, weir_coefficient=1.7):
        """
        Initialize flood simulator
        
        Parameters:
        -----------
        dem_data : numpy array
            Digital Elevation Model data (already converted to float)
        geotransform : tuple
            GDAL geotransform parameters
        manning_n : float
            Manning's roughness coefficient
        infiltration_rate : float
            Infiltration rate in mm/hr
        curve_number : int
            SCS Curve Number for runoff calculation
        dam_height : float
            Height of dam above ground level (meters) - DEPRECATED, use overflow_elevation
        initial_water_level : float
            Initial water level at regulator location (meters)
        spillway_width : float
            Width of spillway/weir crest (meters) - 25.0 m for Kuzey 2
        overflow_elevation : float
            Elevation of weir crest where overflow begins (meters) - 412.0 m for Kuzey 2
        weir_coefficient : float
            Weir discharge coefficient (C) - typically 1.7 for broad-crested weir
        """
        self.dem = dem_data.astype(np.float64)
        self.geotransform = geotransform
        self.manning_n = manning_n
        self.infiltration_rate = infiltration_rate / 1000.0  # Convert to m/hr
        self.curve_number = curve_number
        self.dam_height = dam_height  # Keep for backward compatibility
        self.initial_water_level = initial_water_level
        
        # Actual structure dimensions
        self.spillway_width = spillway_width  # meters
        self.overflow_elevation = overflow_elevation  # meters
        self.weir_coefficient = weir_coefficient
        
        # Grid dimensions
        self.ny, self.nx = self.dem.shape
        
        # Cell size (assuming square cells)
        self.dx = abs(geotransform[1])  # meters
        self.dy = abs(geotransform[5])  # meters
        
        # Initialize water depth and velocity
        self.h = np.zeros_like(self.dem)  # Water depth (m)
        self.u = np.zeros_like(self.dem)  # x-velocity (m/s)
        self.v = np.zeros_like(self.dem)  # y-velocity (m/s)
        
        # Flow accumulation for stream detection
        self.flow_accumulation = None
        self.stream_channel = None
        
        # Regulator location
        self.regulator_x = None
        self.regulator_y = None
        
        # Dam storage (water behind dam)
        self.dam_storage = 0.0  # cubic meters
        self.dam_water_level = 0.0  # meters above ground at dam location
        
        # Calculate flow accumulation
        print("Calculating flow accumulation...")
        self.calculate_flow_accumulation()
        
        # Detect stream channels
        print("Detecting stream channels...")
        self.detect_stream_channels()
        print(f"Stream channels detected: {np.sum(self.stream_channel)} cells")
    
    def calculate_flow_accumulation(self):
        """Calculate flow accumulation from DEM"""
        # Fill sinks
        filled_dem = self.fill_sinks(self.dem)
        
        # Calculate flow direction (D8)
        flow_dir = self.calculate_flow_direction(filled_dem)
        
        # Calculate flow accumulation
        self.flow_accumulation = self.calculate_accumulation(flow_dir)
    
    def fill_sinks(self, dem):
        """Fill sinks in DEM using simple approach"""
        filled = dem.copy()
        kernel = np.array([[1, 1, 1],
                          [1, 0, 1],
                          [1, 1, 1]], dtype=float) / 8.0
        
        for _ in range(5):  # Iterative filling
            neighbors = ndimage.convolve(filled, kernel, mode='constant')
            mask = (filled < neighbors) & (neighbors > 0)
            filled[mask] = neighbors[mask] + 0.01
        
        return filled
    
    def calculate_flow_direction(self, dem):
        """
        Calculate D8 flow direction
        Returns array with values 1-8 representing flow directions
        """
        flow_dir = np.zeros_like(dem, dtype=int)
        
        # Pad DEM for boundary handling
        padded_dem = np.pad(dem, 1, mode='edge')
        
        for i in range(1, self.ny + 1):
            for j in range(1, self.nx + 1):
                center = padded_dem[i, j]
                neighbors = np.array([
                    padded_dem[i-1, j-1], padded_dem[i-1, j], padded_dem[i-1, j+1],
                    padded_dem[i, j-1],                       padded_dem[i, j+1],
                    padded_dem[i+1, j-1], padded_dem[i+1, j], padded_dem[i+1, j+1]
                ])
                
                # Calculate slopes
                slopes = (center - neighbors) / (self.dx * np.sqrt([2, 1, 2, 1, 1, 2, 1, 2]))
                
                # Find maximum positive slope
                max_slope_idx = np.argmax(slopes)
                if slopes[max_slope_idx] > 0:
                    # D8 encoding: 1=E, 2=SE, 3=S, 4=SW, 5=W, 6=NW, 7=N, 8=NE
                    flow_dir[i-1, j-1] = max_slope_idx + 1
                else:
                    flow_dir[i-1, j-1] = 0  # No flow (sink)
        
        return flow_dir
    
    def calculate_accumulation(self, flow_dir):
        """Calculate flow accumulation"""
        accumulation = np.ones_like(flow_dir, dtype=float)
        
        # D8 flow directions
        dx_dirs = [1, 1, 0, -1, -1, -1, 0, 1]
        dy_dirs = [0, 1, 1, 1, 0, -1, -1, -1]
        
        # Iterative accumulation
        changed = True
        iterations = 0
        max_iterations = 100
        
        while changed and iterations < max_iterations:
            changed = False
            new_accumulation = np.ones_like(accumulation)
            
            for i in range(self.ny):
                for j in range(self.nx):
                    if flow_dir[i, j] > 0:
                        dir_idx = flow_dir[i, j] - 1
                        ni = i + dy_dirs[dir_idx]
                        nj = j + dx_dirs[dir_idx]
                        
                        if 0 <= ni < self.ny and 0 <= nj < self.nx:
                            new_accumulation[ni, nj] += accumulation[i, j]
                            changed = True
                    
                    new_accumulation[i, j] = max(new_accumulation[i, j], accumulation[i, j])
            
            accumulation = new_accumulation
            iterations += 1
        
        return accumulation
    
    def detect_stream_channels(self, threshold_percentile=85):
        """Detect stream channels from flow accumulation"""
        if self.flow_accumulation is None:
            return
        
        # Use percentile threshold to find streams
        threshold = np.percentile(self.flow_accumulation, threshold_percentile)
        self.stream_channel = self.flow_accumulation >= threshold
        
        # Apply morphological operations to clean up
        from scipy.ndimage import binary_dilation, binary_erosion
        self.stream_channel = binary_dilation(self.stream_channel, iterations=1)
        self.stream_channel = binary_erosion(self.stream_channel, iterations=1)
    
    def set_regulator(self, x, y):
        """Set regulator (dam/weir) location in pixel coordinates"""
        self.regulator_x = int(x)
        self.regulator_y = int(y)
        
        # Initialize dam water level with initial water level
        self.dam_water_level = self.initial_water_level
        reservoir_area = self.dx * self.dy * 50
        self.dam_storage = self.initial_water_level * reservoir_area
        
        ground_elevation = self.dem[self.regulator_y, self.regulator_x]
        
        print(f"Regulator set at pixel ({self.regulator_x}, {self.regulator_y})")
        print(f"Ground elevation at regulator: {ground_elevation:.2f} m")
        print(f"Overflow elevation: {self.overflow_elevation:.2f} m")
        print(f"Spillway width: {self.spillway_width:.2f} m")
        print(f"Weir coefficient: {self.weir_coefficient:.2f}")
        print(f"Initial water level: {self.initial_water_level:.2f} m")
        print(f"Height to overflow: {self.overflow_elevation - ground_elevation:.2f} m")
    
    def calculate_runoff(self, rainfall_intensity_mm_hr):
        """
        Calculate runoff using SCS Curve Number method
        Returns runoff in m/hr
        """
        # Convert rainfall to meters
        rainfall_m = rainfall_intensity_mm_hr / 1000.0
        
        # SCS Curve Number method
        S = (25400.0 / self.curve_number) - 254.0  # Potential maximum retention (mm)
        S_m = S / 1000.0  # Convert to meters
        
        # Calculate runoff
        if rainfall_m > 0.2 * S_m:
            runoff = (rainfall_m - 0.2 * S_m)**2 / (rainfall_m + 0.8 * S_m)
        else:
            runoff = 0.0
        
        return max(0.0, runoff)  # m/hr
    
    def calculate_manning_velocity(self, h, slope):
        """
        Calculate velocity using Manning's equation
        v = (1/n) * R^(2/3) * S^(1/2)
        For shallow flow, R ≈ h
        """
        if h < 0.001:  # Very shallow water
            return 0.0
        
        # Hydraulic radius approximation for shallow flow
        R = h
        
        # Slope magnitude
        S = max(abs(slope), 1e-6)
        
        # Manning's equation
        v = (1.0 / self.manning_n) * (R ** (2.0/3.0)) * (S ** 0.5)
        
        return min(v, 10.0)  # Cap at 10 m/s for stability
    
    def calculate_dam_overflow(self, dt, runoff_rate):
        """
        Calculate dam overflow behavior using actual structure dimensions
        Water accumulates behind dam until it reaches overflow_elevation, then overflows
        
        Uses broad-crested weir equation: Q = C * L * H^(3/2)
        where:
        - Q = discharge (m³/s)
        - C = weir coefficient (1.7 for broad-crested weir)
        - L = weir length (spillway width) = 25.0 m
        - H = head over weir (water level - overflow_elevation)
        """
        if self.regulator_x is None or self.regulator_y is None:
            return 0.0
        
        rx, ry = self.regulator_x, self.regulator_y
        
        # Ground elevation at dam location
        ground_elevation = self.dem[ry, rx]
        
        # Current water surface elevation at dam location
        water_surface_elevation = ground_elevation + self.h[ry, rx]
        
        # Add water to dam storage from rainfall/runoff
        # Assume catchment area around dam (simplified)
        catchment_area = self.dx * self.dy * 100  # Approximate catchment (100 cells)
        inflow_volume = runoff_rate * catchment_area * (dt / 3600.0)  # m³
        
        # Update water surface elevation based on inflow
        # Simplified: assume water accumulates in a reservoir area
        reservoir_area = self.dx * self.dy * 50  # Approximate reservoir area
        if reservoir_area > 0:
            water_level_increase = inflow_volume / reservoir_area
            water_surface_elevation += water_level_increase
        
        # Check if water exceeds overflow elevation
        overflow_depth = 0.0
        if water_surface_elevation > self.overflow_elevation:
            # Calculate head over weir
            head_over_weir = water_surface_elevation - self.overflow_elevation
            
            # Broad-crested weir equation: Q = C * L * H^(3/2)
            # Q in m³/s, C = weir coefficient, L = spillway width, H = head
            discharge = self.weir_coefficient * self.spillway_width * (head_over_weir ** 1.5)  # m³/s
            
            # Convert discharge to depth per time step
            # Volume per time step = Q * dt
            overflow_volume = discharge * dt  # m³
            
            # Convert to depth at dam location (spread over cell area)
            cell_area = self.dx * self.dy  # m²
            overflow_depth = overflow_volume / cell_area  # meters
            
            # Update water surface elevation (reduce by overflow)
            water_level_decrease = overflow_volume / reservoir_area if reservoir_area > 0 else 0.0
            water_surface_elevation = max(self.overflow_elevation, 
                                         water_surface_elevation - water_level_decrease)
            
            # Store updated water level
            self.dam_water_level = water_surface_elevation - ground_elevation
            self.dam_storage = self.dam_water_level * reservoir_area
            
            return overflow_depth
        
        # Update dam storage and water level even if no overflow
        self.dam_water_level = max(0.0, water_surface_elevation - ground_elevation)
        self.dam_storage = self.dam_water_level * reservoir_area
        
        return 0.0
    
    def solve_shallow_water(self, dt, rainfall_intensity_mm_hr):
        """
        Solve 2D shallow water equations using finite difference method
        Includes dam overflow behavior
        """
        # Calculate runoff
        runoff_rate = self.calculate_runoff(rainfall_intensity_mm_hr)  # m/hr
        runoff_dt = runoff_rate * (dt / 3600.0)  # Convert to m per time step
        
        # Calculate infiltration loss
        infiltration_dt = self.infiltration_rate * (dt / 3600.0)  # m per time step
        
        # Calculate dam overflow
        overflow_depth = self.calculate_dam_overflow(dt, runoff_rate)
        
        # Initialize new arrays
        h_new = self.h.copy()
        u_new = self.u.copy()
        v_new = self.v.copy()
        
        # Calculate water surface elevation
        eta = self.dem + self.h
        
        # Calculate gradients for velocity
        grad_x = np.gradient(eta, axis=1) / self.dx
        grad_y = np.gradient(eta, axis=0) / self.dy
        
        # Update velocities using Manning's equation
        for i in range(1, self.ny - 1):
            for j in range(1, self.nx - 1):
                if h_new[i, j] > 0.001:
                    # Calculate slope components
                    slope_x = -grad_x[i, j]
                    slope_y = -grad_y[i, j]
                    slope_mag = np.sqrt(slope_x**2 + slope_y**2)
                    
                    if slope_mag > 1e-6:
                        # Manning's velocity
                        v_mag = self.calculate_manning_velocity(h_new[i, j], slope_mag)
                        u_new[i, j] = v_mag * (slope_x / slope_mag)
                        v_new[i, j] = v_mag * (slope_y / slope_mag)
                    else:
                        u_new[i, j] = 0.0
                        v_new[i, j] = 0.0
        
        # Update water depth using continuity equation
        # ∂h/∂t + ∂(hu)/∂x + ∂(hv)/∂y = R - I + Overflow
        
        # Calculate flux divergences
        flux_x = h_new * u_new
        flux_y = h_new * v_new
        
        div_x = np.gradient(flux_x, axis=1) / self.dx
        div_y = np.gradient(flux_y, axis=0) / self.dy
        
        # Update water depth
        h_new = h_new - dt * (div_x + div_y) + runoff_dt - infiltration_dt
        
        # Add overflow from dam
        if overflow_depth > 0 and self.regulator_x is not None and self.regulator_y is not None:
            rx, ry = self.regulator_x, self.regulator_y
            if 0 <= rx < self.nx and 0 <= ry < self.ny:
                h_new[ry, rx] += overflow_depth
        
        # Ensure non-negative depth
        h_new = np.maximum(h_new, 0.0)
        
        # Apply boundary conditions (no flow at edges)
        h_new[0, :] = 0.0
        h_new[-1, :] = 0.0
        h_new[:, 0] = 0.0
        h_new[:, -1] = 0.0
        
        # Update velocities where water depth is too low
        mask = h_new < 0.001
        u_new[mask] = 0.0
        v_new[mask] = 0.0
        
        # Update state
        self.h = h_new
        self.u = u_new
        self.v = v_new
    
    def run_simulation(self, duration_hours, time_step_minutes, rainfall_intensity_mm_hr, 
                      progress_callback=None, status_callback=None):
        """
        Run simulation for specified duration
        
        Parameters:
        -----------
        duration_hours : float
            Total simulation duration in hours
        time_step_minutes : float
            Time step in minutes
        rainfall_intensity_mm_hr : float
            Rainfall intensity in mm/hr
        progress_callback : function
            Callback function for progress updates (0-100)
        status_callback : function
            Callback function for status messages
        
        Returns:
        --------
        dict with simulation results
        """
        # Convert to seconds
        dt = time_step_minutes * 60.0  # seconds
        total_time = duration_hours * 3600.0  # seconds
        num_steps = int(total_time / dt)
        
        print(f"\nSimulation Parameters:")
        print(f"  Time steps: {num_steps}")
        print(f"  Time step: {dt:.1f} seconds ({time_step_minutes:.1f} minutes)")
        print(f"  Total duration: {duration_hours:.1f} hours")
        
        # Store results
        results = {
            'water_depth': [],
            'time_steps': [],
            'flow_accumulation': self.flow_accumulation,
            'stream_channel': self.stream_channel,
            'dam_storage_history': []
        }
        
        # Reset water depth
        self.h = np.zeros_like(self.dem)
        self.u = np.zeros_like(self.dem)
        self.v = np.zeros_like(self.dem)
        
        # Initialize dam with initial water level
        self.dam_storage = 0.0
        self.dam_water_level = self.initial_water_level
        reservoir_area = self.dx * self.dy * 50
        self.dam_storage = self.initial_water_level * reservoir_area
        
        # Set initial water at regulator location
        if self.regulator_x is not None and self.regulator_y is not None:
            rx, ry = self.regulator_x, self.regulator_y
            if 0 <= rx < self.nx and 0 <= ry < self.ny:
                self.h[ry, rx] = self.initial_water_level
                print(f"Initial water level set: {self.initial_water_level:.2f} m at regulator")
        
        # Run simulation
        print(f"\nRunning simulation...")
        for step in range(num_steps):
            # Solve shallow water equations
            self.solve_shallow_water(dt, rainfall_intensity_mm_hr)
            
            # Store results
            results['water_depth'].append(self.h.copy())
            results['time_steps'].append(step * dt / 3600.0)  # hours
            results['dam_storage_history'].append(self.dam_storage)
            
            # Update progress
            if progress_callback:
                progress = int((step + 1) / num_steps * 100)
                progress_callback(progress)
            
            # Status updates every 10% or every 100 steps
            if status_callback and (step % max(1, num_steps // 10) == 0 or step % 100 == 0):
                time_hours = step * dt / 3600.0
                max_depth = np.max(self.h)
                total_water = np.sum(self.h) * self.dx * self.dy
                status = (f"Step {step+1}/{num_steps} | "
                         f"Time: {time_hours:.2f} hr | "
                         f"Max Depth: {max_depth:.2f} m | "
                         f"Dam Level: {self.dam_water_level:.2f} m")
                status_callback(status)
                print(f"  {status}")
        
        print(f"\nSimulation complete!")
        print(f"Final max water depth: {np.max(self.h):.2f} m")
        print(f"Final dam water level: {self.dam_water_level:.2f} m")
        
        return results

