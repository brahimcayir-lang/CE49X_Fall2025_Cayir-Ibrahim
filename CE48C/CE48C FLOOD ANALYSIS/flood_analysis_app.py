import sys
import os
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, 
                             QSlider, QDoubleSpinBox, QSpinBox, QFileDialog,
                             QMessageBox, QGroupBox, QProgressBar, QTextEdit,
                             QScrollArea, QSplitter, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QColor
# Try to import QGIS - if not available, use fallback mode
try:
    from qgis.core import (QgsApplication, QgsRasterLayer, QgsProject, QgsMapCanvas,
                          QgsMapCanvasLayer, QgsVectorLayer, QgsField, QgsFeature,
                          QgsGeometry, QgsPointXY, QgsSymbol, QgsRendererRange,
                          QgsGraduatedSymbolRenderer, QgsColorRampShader, QgsRasterShader,
                          QgsSingleBandPseudoColorRenderer, QgsCoordinateReferenceSystem)
    from qgis.gui import QgsMapCanvas, QgsMapToolPan, QgsMapToolZoom
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False
    print("WARNING: QGIS not available. Using fallback visualization mode.")
    # Create dummy classes for fallback
    class QgsApplication:
        @staticmethod
        def setPrefixPath(path, useDefaultProviders):
            pass
        def __init__(self, argv, useGUI):
            pass
        def initQgis(self):
            pass
        def exitQgis(self):
            pass
    class QgsRasterLayer:
        def __init__(self, path, name):
            self.isValid = lambda: False
    class QgsProject:
        instance = lambda: None
        def addMapLayer(self, layer):
            pass
        def mapLayersByName(self, name):
            return []
        def removeMapLayer(self, layer_id):
            pass
    class QgsMapCanvas:
        def __init__(self):
            pass
        def setCanvasColor(self, color):
            pass
        def setExtent(self, extent):
            pass
        def setLayers(self, layers):
            pass
        def refresh(self):
            pass
        def saveAsImage(self, path):
            pass

# Try to import GDAL - if not available, provide fallback
try:
    from osgeo import gdal
    from osgeo import osr
    GDAL_AVAILABLE = True
except ImportError:
    GDAL_AVAILABLE = False
    print("WARNING: GDAL not available. Some features may be limited.")
    # Create minimal fallback
    class gdal:
        GDT_Byte = 1
        GDT_Float32 = 6
        @staticmethod
        def Open(path):
            return None
        @staticmethod
        def GetDriverByName(name):
            return None
        @staticmethod
        def GetDataTypeName(dtype):
            return "Unknown"
    class osr:
        class SpatialReference:
            def ImportFromEPSG(self, code):
                pass
            def ImportFromWkt(self, wkt):
                pass
            def GetAttrValue(self, key, idx):
                return None
        class CoordinateTransformation:
            def __init__(self, src, dst):
                pass
            def TransformPoint(self, x, y, z):
                return (x, y, z)

# Redirect stdout to both console and GUI
class ConsoleOutput:
    def __init__(self, text_widget=None):
        self.text_widget = text_widget
        self.terminal = sys.stdout
    
    def write(self, message):
        self.terminal.write(message)
        if self.text_widget:
            self.text_widget.append(message.rstrip())
    
    def flush(self):
        self.terminal.flush()


class FloodSimulationThread(QThread):
    """Thread for running flood simulation without freezing GUI"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)
    status_message = pyqtSignal(str)
    
    def __init__(self, simulator, duration, time_step, rainfall_intensity):
        super().__init__()
        self.simulator = simulator
        self.duration = duration
        self.time_step = time_step
        self.rainfall_intensity = rainfall_intensity
    
    def run(self):
        print(f"\n{'='*60}")
        print(f"Starting Flood Simulation")
        print(f"{'='*60}")
        print(f"Duration: {self.duration} hours")
        print(f"Time Step: {self.time_step} minutes")
        print(f"Rainfall Intensity: {self.rainfall_intensity} mm/hr")
        print(f"{'='*60}\n")
        
        self.status_message.emit("Starting simulation...")
        results = self.simulator.run_simulation(
            self.duration, 
            self.time_step, 
            self.rainfall_intensity,
            self.progress,
            self.status_message
        )
        
        print(f"\n{'='*60}")
        print(f"Simulation Complete!")
        print(f"Total Time Steps: {len(results['water_depth'])}")
        print(f"Max Water Depth: {np.max(results['water_depth'][-1]):.2f} m")
        print(f"{'='*60}\n")
        
        self.finished.emit(results)


class FloodAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dem_path = None
        self.dem_data = None
        self.dem_transform = None
        self.dem_crs = None
        self.regulator_coords = None
        self.simulator = None
        self.simulation_results = None
        self.current_time_step = 0
        self.animation_timer = None
        self.animation_playing = False
        
        # Setup console output FIRST (before UI so it's available in create_control_panel)
        self.setup_console()
        
        # Initialize QGIS
        self.init_qgis()
        
        # Setup UI
        self.init_ui()
        
    def setup_console(self):
        """Setup console output to both terminal and GUI"""
        self.console_output = ConsoleOutput()
        sys.stdout = self.console_output
        
    def find_qgis_path(self):
        """Auto-detect QGIS installation path"""
        possible_paths = [
            r'C:\OSGeo4W64\apps\qgis',
            r'C:\OSGeo4W\apps\qgis',
            r'C:\Program Files\QGIS 3.28\apps\qgis',
            r'C:\Program Files\QGIS 3.30\apps\qgis',
            r'C:\Program Files\QGIS 3.32\apps\qgis',
            r'C:\Program Files (x86)\QGIS 3.28\apps\qgis',
            r'C:\Program Files (x86)\QGIS 3.30\apps\qgis',
        ]
        
        # Check environment variable first
        env_path = os.environ.get('QGIS_PREFIX_PATH')
        if env_path and os.path.exists(env_path):
            return env_path
        
        # Check common paths
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
        
    def init_qgis(self):
        """Initialize QGIS application"""
        if not QGIS_AVAILABLE:
            print("WARNING: QGIS not available. Using fallback visualization mode.")
            print("For full functionality, please install QGIS from https://qgis.org")
            self.qgs = None
            self.use_qgis = False
            return
        
        qgis_path = self.find_qgis_path()
        
        if qgis_path is None:
            print("WARNING: QGIS installation not found.")
            print("Using fallback visualization mode.")
            print("To use QGIS features, install QGIS from https://qgis.org")
            print("or set QGIS_PREFIX_PATH environment variable.")
            self.qgs = None
            self.use_qgis = False
            return
        
        try:
            print(f"Initializing QGIS from: {qgis_path}")
            QgsApplication.setPrefixPath(qgis_path, True)
            self.qgs = QgsApplication([], False)
            self.qgs.initQgis()
            print("QGIS initialized successfully")
            self.use_qgis = True
        except Exception as e:
            print(f"WARNING: Failed to initialize QGIS: {str(e)}")
            print("Using fallback visualization mode.")
            self.qgs = None
            self.use_qgis = False
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Flood Analysis Simulation App - Kuzey 2 Regulator")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Central widget with splitter for resizable panels
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Controls (with scroll area)
        control_panel = self.create_control_panel()
        
        # Wrap control panel in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(control_panel)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(400)
        scroll_area.setMaximumWidth(600)
        scroll_area.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        splitter.addWidget(scroll_area)
        
        # Right panel - Map canvas or matplotlib fallback
        map_widget = QWidget()
        map_layout = QVBoxLayout(map_widget)
        map_layout.setContentsMargins(0, 0, 0, 0)
        
        if self.use_qgis:
            self.map_canvas = QgsMapCanvas()
            self.map_canvas.setCanvasColor(QColor(255, 255, 255))
            self.map_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            map_layout.addWidget(self.map_canvas)
        else:
            # Use matplotlib as fallback
            try:
                from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
                from matplotlib.figure import Figure
                import matplotlib.pyplot as plt
                
                self.fig = Figure(figsize=(10, 8))
                self.canvas = FigureCanvas(self.fig)
                self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.ax = self.fig.add_subplot(111)
                self.ax.set_title("Flood Analysis Map\n(QGIS not available - using matplotlib)", 
                                fontsize=12, pad=20)
                self.ax.axis('off')
                # Use subplots_adjust instead of tight_layout to prevent shrinking
                self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
                map_layout.addWidget(self.canvas)
                self.use_matplotlib = True
            except ImportError:
                # If matplotlib not available, use simple label
                fallback_label = QLabel("Map visualization requires QGIS or matplotlib.\n"
                                       "Please install QGIS from https://qgis.org\n"
                                       "or install matplotlib: pip install matplotlib")
                fallback_label.setAlignment(Qt.AlignCenter)
                fallback_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                map_layout.addWidget(fallback_label)
                self.use_matplotlib = False
        
        splitter.addWidget(map_widget)
        
        # Set splitter proportions (30% left, 70% right)
        splitter.setSizes([400, 1200])
        splitter.setStretchFactor(0, 0)  # Left panel doesn't stretch
        splitter.setStretchFactor(1, 1)  # Right panel stretches
        
        # Menu bar
        self.create_menu_bar()
        
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        load_dem_action = file_menu.addAction('Load DEM (TIF)')
        load_dem_action.triggered.connect(self.load_dem)
        
        file_menu.addSeparator()
        
        export_action = file_menu.addAction('Export Current View')
        export_action.triggered.connect(self.export_current_view)
        
        export_all_action = file_menu.addAction('Export All Time Steps')
        export_all_action.triggered.connect(self.export_all_timesteps)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)
        
    def create_control_panel(self):
        """Create control panel with all inputs"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # DEM Info
        dem_group = QGroupBox("DEM Information")
        dem_layout = QVBoxLayout()
        dem_layout.setSpacing(5)
        self.dem_label = QLabel("No DEM loaded")
        self.dem_label.setWordWrap(True)
        self.dem_label.setMinimumHeight(60)
        self.dem_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        dem_layout.addWidget(self.dem_label)
        dem_group.setLayout(dem_layout)
        dem_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addWidget(dem_group)
        
        # Regulator Coordinates
        regulator_group = QGroupBox("Regulator Location - Kuzey 2")
        regulator_layout = QVBoxLayout()
        
        # Pixel coordinates (for manual input when georeferencing is not available)
        pixel_coord_label = QLabel("Pixel Coordinates (Manual Override):")
        pixel_coord_label.setStyleSheet("font-weight: bold;")
        regulator_layout.addWidget(pixel_coord_label)
        
        self.regulator_pixel_x_input = QSpinBox()
        self.regulator_pixel_x_input.setRange(0, 10000)
        self.regulator_pixel_x_input.setValue(0)
        self.regulator_pixel_x_input.setEnabled(False)
        self.regulator_pixel_x_input.setToolTip("Column (X) pixel coordinate - enable to manually set")
        regulator_layout.addWidget(QLabel("Pixel X (Column):"))
        regulator_layout.addWidget(self.regulator_pixel_x_input)
        
        self.regulator_pixel_y_input = QSpinBox()
        self.regulator_pixel_y_input.setRange(0, 10000)
        self.regulator_pixel_y_input.setValue(0)
        self.regulator_pixel_y_input.setEnabled(False)
        self.regulator_pixel_y_input.setToolTip("Row (Y) pixel coordinate - enable to manually set")
        regulator_layout.addWidget(QLabel("Pixel Y (Row):"))
        regulator_layout.addWidget(self.regulator_pixel_y_input)
        
        # World coordinates
        world_coord_label = QLabel("World Coordinates (UTM):")
        world_coord_label.setStyleSheet("font-weight: bold;")
        regulator_layout.addWidget(world_coord_label)
        
        self.regulator_x = QDoubleSpinBox()
        self.regulator_x.setRange(0, 1000000)
        self.regulator_x.setValue(369012.0)  # UTM Zone 6 Easting
        self.regulator_x.setDecimals(3)
        regulator_layout.addWidget(QLabel("UTM Zone 6 Easting:"))
        regulator_layout.addWidget(self.regulator_x)
        
        self.regulator_y = QDoubleSpinBox()
        self.regulator_y.setRange(0, 10000000)
        self.regulator_y.setValue(4513388.0)  # UTM Zone 6 Northing
        self.regulator_y.setDecimals(3)
        regulator_layout.addWidget(QLabel("UTM Zone 6 Northing:"))
        regulator_layout.addWidget(self.regulator_y)
        
        utm_label = QLabel("UTM Zone: 6N (WGS84)")
        regulator_layout.addWidget(utm_label)
        
        # Dam height parameter (for backward compatibility)
        self.dam_height = QDoubleSpinBox()
        self.dam_height.setRange(0, 100)
        self.dam_height.setValue(5.0)
        self.dam_height.setDecimals(2)
        self.dam_height.setSuffix(" m")
        regulator_layout.addWidget(QLabel("Dam Height (Legacy):"))
        regulator_layout.addWidget(self.dam_height)
        
        # Initial water level at regulator
        self.initial_water_level = QDoubleSpinBox()
        self.initial_water_level.setRange(0, 50)
        self.initial_water_level.setValue(1.0)
        self.initial_water_level.setDecimals(2)
        self.initial_water_level.setSuffix(" m")
        regulator_layout.addWidget(QLabel("Initial Water Level at Regulator:"))
        regulator_layout.addWidget(self.initial_water_level)
        
        regulator_group.setLayout(regulator_layout)
        layout.addWidget(regulator_group)
        
        # Structure Dimensions
        structure_group = QGroupBox("Structure Dimensions - Kuzey 2")
        structure_layout = QVBoxLayout()
        
        # Spillway width
        self.spillway_width = QDoubleSpinBox()
        self.spillway_width.setRange(1, 100)
        self.spillway_width.setValue(25.0)  # 25 meters
        self.spillway_width.setDecimals(2)
        self.spillway_width.setSuffix(" m")
        structure_layout.addWidget(QLabel("Spillway Width (Crest Length):"))
        structure_layout.addWidget(self.spillway_width)
        
        # Overflow elevation
        self.overflow_elevation = QDoubleSpinBox()
        self.overflow_elevation.setRange(0, 1000)
        self.overflow_elevation.setValue(412.00)  # 412 meters
        self.overflow_elevation.setDecimals(2)
        self.overflow_elevation.setSuffix(" m")
        structure_layout.addWidget(QLabel("Overflow Elevation (Crest):"))
        structure_layout.addWidget(self.overflow_elevation)
        
        # Weir coefficient
        self.weir_coefficient = QDoubleSpinBox()
        self.weir_coefficient.setRange(1.0, 3.0)
        self.weir_coefficient.setValue(1.7)  # Standard broad-crested weir
        self.weir_coefficient.setDecimals(2)
        structure_layout.addWidget(QLabel("Weir Coefficient (C):"))
        structure_layout.addWidget(self.weir_coefficient)
        
        structure_group.setLayout(structure_layout)
        layout.addWidget(structure_group)
        
        # Rainfall Scenarios
        rainfall_group = QGroupBox("Rainfall Scenario")
        rainfall_layout = QVBoxLayout()
        
        self.rainfall_combo = QComboBox()
        self.rainfall_combo.addItems([
            "Light Rain (5 mm/hr)",
            "Moderate Rain (10 mm/hr)",
            "Heavy Rain (25 mm/hr)",
            "Very Heavy Rain (50 mm/hr)",
            "Extreme Rain (100 mm/hr)",
            "Custom Intensity"
        ])
        self.rainfall_combo.currentIndexChanged.connect(self.on_rainfall_combo_changed)
        rainfall_layout.addWidget(QLabel("Select Scenario:"))
        rainfall_layout.addWidget(self.rainfall_combo)
        
        # Custom rainfall input
        self.custom_rainfall = QDoubleSpinBox()
        self.custom_rainfall.setRange(0, 500)
        self.custom_rainfall.setValue(10)
        self.custom_rainfall.setSuffix(" mm/hr")
        self.custom_rainfall.setSingleStep(5)
        self.custom_rainfall.setEnabled(False)
        rainfall_layout.addWidget(QLabel("Custom Intensity:"))
        rainfall_layout.addWidget(self.custom_rainfall)
        
        rainfall_group.setLayout(rainfall_layout)
        layout.addWidget(rainfall_group)
        
        # Simulation Parameters
        sim_group = QGroupBox("Simulation Parameters")
        sim_layout = QVBoxLayout()
        
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 48)
        self.duration_spin.setValue(6)
        self.duration_spin.setSuffix(" hours")
        sim_layout.addWidget(QLabel("Simulation Duration:"))
        sim_layout.addWidget(self.duration_spin)
        
        self.time_step_spin = QDoubleSpinBox()
        self.time_step_spin.setRange(0.1, 60)
        self.time_step_spin.setValue(1.0)
        self.time_step_spin.setSuffix(" minutes")
        sim_layout.addWidget(QLabel("Time Step:"))
        sim_layout.addWidget(self.time_step_spin)
        
        sim_group.setLayout(sim_layout)
        layout.addWidget(sim_group)
        
        # Soil Parameters
        soil_group = QGroupBox("Soil Characteristics (Old Streambed in Forest)")
        soil_layout = QVBoxLayout()
        
        self.manning_n = QDoubleSpinBox()
        self.manning_n.setRange(0.01, 0.1)
        self.manning_n.setValue(0.04)
        self.manning_n.setDecimals(3)
        self.manning_n.setSingleStep(0.005)
        soil_layout.addWidget(QLabel("Manning's Roughness (n):"))
        soil_layout.addWidget(self.manning_n)
        
        self.infiltration_rate = QDoubleSpinBox()
        self.infiltration_rate.setRange(0, 50)
        self.infiltration_rate.setValue(7.5)
        self.infiltration_rate.setSuffix(" mm/hr")
        soil_layout.addWidget(QLabel("Infiltration Rate:"))
        soil_layout.addWidget(self.infiltration_rate)
        
        self.curve_number = QSpinBox()
        self.curve_number.setRange(30, 100)
        self.curve_number.setValue(65)
        soil_layout.addWidget(QLabel("SCS Curve Number:"))
        soil_layout.addWidget(self.curve_number)
        
        soil_group.setLayout(soil_layout)
        layout.addWidget(soil_group)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load DEM")
        self.load_btn.setMinimumHeight(35)
        self.load_btn.clicked.connect(self.load_dem_from_desktop)
        button_layout.addWidget(self.load_btn)
        
        self.auto_regulator_btn = QPushButton("Auto-Detect Regulator")
        self.auto_regulator_btn.setMinimumHeight(35)
        self.auto_regulator_btn.setEnabled(False)
        self.auto_regulator_btn.clicked.connect(self.auto_detect_regulator)
        button_layout.addWidget(self.auto_regulator_btn)
        layout.addLayout(button_layout)
        
        self.run_btn = QPushButton("Run Simulation")
        self.run_btn.setMinimumHeight(35)
        self.run_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.run_btn.clicked.connect(self.run_simulation)
        self.run_btn.setEnabled(False)
        layout.addWidget(self.run_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setMinimumHeight(20)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addWidget(self.status_label)
        
        # Console output in GUI
        console_group = QGroupBox("Console Output")
        console_layout = QVBoxLayout()
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setMinimumHeight(100)
        self.console_text.setMaximumHeight(200)
        self.console_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        console_layout.addWidget(self.console_text)
        console_group.setLayout(console_layout)
        console_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addWidget(console_group)
        
        # Update console output widget (if console_output exists)
        if hasattr(self, 'console_output'):
            self.console_output.text_widget = self.console_text
        
        # Time Slider
        time_group = QGroupBox("Time Navigation")
        time_layout = QVBoxLayout()
        time_layout.setSpacing(5)
        
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setEnabled(False)
        self.time_slider.setMinimumHeight(25)
        self.time_slider.valueChanged.connect(self.update_time_display)
        time_layout.addWidget(self.time_slider)
        
        time_info_layout = QHBoxLayout()
        self.time_label = QLabel("Time: 0:00")
        self.time_label.setMinimumWidth(100)
        time_info_layout.addWidget(self.time_label)
        time_info_layout.addStretch()
        
        self.play_btn = QPushButton("Play Animation")
        self.play_btn.setEnabled(False)
        self.play_btn.setMinimumHeight(30)
        self.play_btn.clicked.connect(self.toggle_animation)
        time_info_layout.addWidget(self.play_btn)
        time_layout.addLayout(time_info_layout)
        
        time_group.setLayout(time_layout)
        time_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addWidget(time_group)
        
        # Add stretch at the end to push everything up
        layout.addStretch()
        
        # Set size policy for panel
        panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        
        return panel
    
    def on_rainfall_combo_changed(self, index):
        """Enable/disable custom rainfall input"""
        if self.rainfall_combo.currentText() == "Custom Intensity":
            self.custom_rainfall.setEnabled(True)
        else:
            self.custom_rainfall.setEnabled(False)
    
    def load_dem_from_desktop(self):
        """Load DEM from desktop (ikinci_data.tif)"""
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        dem_file = os.path.join(desktop_path, "ikinci_data.tif")
        
        print(f"\nAttempting to load DEM from: {dem_file}")
        if os.path.exists(dem_file):
            self.load_dem_file(dem_file)
        else:
            print(f"File not found. Opening file dialog...")
            QMessageBox.warning(self, "File Not Found", 
                              f"Could not find {dem_file}\nPlease select the file manually.")
            self.load_dem()
    
    def load_dem(self):
        """Load DEM file dialog"""
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load DEM File", desktop_path, "TIF Files (*.tif *.tiff);;All Files (*)")
        if file_path:
            self.load_dem_file(file_path)
    
    def load_dem_file(self, file_path):
        """Load and display DEM file"""
        try:
            print(f"\nLoading DEM file: {os.path.basename(file_path)}")
            
            if not GDAL_AVAILABLE:
                # Try to load with rasterio or other method
                try:
                    import rasterio
                    with rasterio.open(file_path) as src:
                        self.dem_data = src.read(1).astype(np.float64)
                        # Convert transform to GDAL format
                        transform = src.transform
                        self.dem_transform = (transform[2], transform[0], transform[1],
                                            transform[5], transform[3], transform[4])
                        # Get CRS
                        self.dem_crs = None
                        if src.crs:
                            try:
                                epsg = src.crs.to_epsg()
                                if epsg:
                                    self.dem_crs = osr.SpatialReference()
                                    self.dem_crs.ImportFromEPSG(epsg)
                            except:
                                pass
                except ImportError:
                    # Last resort: try to load as image
                    try:
                        from PIL import Image
                        img = Image.open(file_path)
                        self.dem_data = np.array(img).astype(np.float64)
                        # Create dummy geotransform
                        self.dem_transform = (0, 1, 0, 0, 0, -1)
                        self.dem_crs = None
                        print("WARNING: Loaded as image. Georeferencing may be incorrect.")
                    except ImportError:
                        raise Exception("GDAL not available. Please install GDAL, rasterio, or Pillow.")
            else:
                # Load DEM using GDAL
                dataset = gdal.Open(file_path)
                if dataset is None:
                    raise Exception("Could not open DEM file")
                
                # Get DEM data
                band = dataset.GetRasterBand(1)
                
                # Check data type
                data_type = band.DataType
                print(f"DEM Data Type: {gdal.GetDataTypeName(data_type)}")
                
                # Read data
                self.dem_data = band.ReadAsArray()
                
                # Handle BYTE data type - convert to float
                if data_type == gdal.GDT_Byte:
                    print("Converting BYTE data to float (0-255 -> elevation)")
                    # Assume BYTE represents elevation in meters (or convert as needed)
                    # You may need to adjust this conversion based on your data
                    self.dem_data = self.dem_data.astype(np.float64)
                    # If BYTE is actually elevation, use as-is
                    # If BYTE needs scaling, uncomment: self.dem_data = self.dem_data * scale_factor
                else:
                    self.dem_data = self.dem_data.astype(np.float64)
                
                # Get geotransform
                self.dem_transform = dataset.GetGeoTransform()
                
                # Get CRS
                proj = dataset.GetProjection()
                self.dem_crs = None
                if proj:
                    srs = osr.SpatialReference()
                    srs.ImportFromWkt(proj)
                    self.dem_crs = srs
            
            # Create QGIS raster layer or matplotlib display
            if self.use_qgis:
                layer = QgsRasterLayer(file_path, "DEM")
                if not layer.isValid():
                    raise Exception("Invalid raster layer")
                
                # Add to project
                QgsProject.instance().addMapLayer(layer)
                
                # Set up map canvas
                self.map_canvas.setExtent(layer.extent())
                self.map_canvas.setLayers([layer])
                self.map_canvas.refresh()
                crs_info = layer.crs().authid() if layer.crs().isValid() else "Unknown"
            elif self.use_matplotlib:
                # Display DEM using matplotlib
                self.ax.clear()
                im = self.ax.imshow(self.dem_data, cmap='terrain', aspect='auto', origin='upper')
                self.ax.set_title(f"DEM: {os.path.basename(file_path)}", 
                                fontsize=12, pad=10)
                if hasattr(self, 'dem_colorbar'):
                    try:
                        self.dem_colorbar.remove()
                        self.dem_colorbar = None
                    except:
                        pass
                self.dem_colorbar = self.fig.colorbar(im, ax=self.ax, fraction=0.046, pad=0.04)
                self.dem_colorbar.set_label('Elevation (m)', fontsize=10)
                # FIXED: Use fixed subplots_adjust to prevent shrinking
                self.fig.subplots_adjust(left=0.05, right=0.92, top=0.95, bottom=0.05)
                self.canvas.draw()
                crs_info = "Displayed (matplotlib)"
            else:
                crs_info = "Unknown"
            
            # Update UI
            self.dem_path = file_path
            cell_size = abs(self.dem_transform[1]) if self.dem_transform else 1.0
            
            info_text = (
                f"DEM: {os.path.basename(file_path)}\n"
                f"Size: {self.dem_data.shape[1]} x {self.dem_data.shape[0]} pixels\n"
                f"Cell Size: {cell_size:.2f} m\n"
                f"CRS: {crs_info}\n"
                f"Elevation Range: {np.nanmin(self.dem_data):.2f} - {np.nanmax(self.dem_data):.2f} m"
            )
            self.dem_label.setText(info_text)
            
            print(f"DEM loaded successfully:")
            print(f"  Dimensions: {self.dem_data.shape[1]} x {self.dem_data.shape[0]} pixels")
            print(f"  Cell Size: {cell_size:.2f} meters")
            print(f"  CRS: {crs_info}")
            print(f"  Elevation Range: {np.nanmin(self.dem_data):.2f} - {np.nanmax(self.dem_data):.2f} m")
            
            self.run_btn.setEnabled(True)
            self.auto_regulator_btn.setEnabled(True)
            
            # Auto-detect regulator location
            self.auto_detect_regulator()
            
        except Exception as e:
            error_msg = f"Failed to load DEM:\n{str(e)}"
            print(f"ERROR: {error_msg}")
            QMessageBox.critical(self, "Error", error_msg)
    
    def convert_regulator_coords_to_dem_crs(self):
        """Convert UTM Zone 6 coordinates to DEM's coordinate system"""
        try:
            print("\nConverting regulator coordinates...")
            
            if not GDAL_AVAILABLE or not hasattr(osr, 'SpatialReference'):
                # No transformation available
                self.regulator_x_dem = self.regulator_x.value()
                self.regulator_y_dem = self.regulator_y.value()
                print("  Using coordinates directly (GDAL/osr not available)")
                return
            
            # UTM Zone 6N (WGS84)
            utm_srs = osr.SpatialReference()
            utm_srs.ImportFromEPSG(32606)  # UTM Zone 6N
            
            # Get DEM CRS
            if self.dem_crs is None:
                # Try to get from QGIS layer
                if self.use_qgis:
                    layers = QgsProject.instance().mapLayersByName("DEM")
                    if layers:
                        dem_crs_qgis = layers[0].crs()
                        if dem_crs_qgis.isValid():
                            epsg_code = dem_crs_qgis.authid()
                            if epsg_code:
                                try:
                                    epsg_num = int(epsg_code.split(':')[1])
                                    self.dem_crs = osr.SpatialReference()
                                    self.dem_crs.ImportFromEPSG(epsg_num)
                                except:
                                    pass
            
            if self.dem_crs is None:
                # Assume same CRS
                self.regulator_x_dem = self.regulator_x.value()
                self.regulator_y_dem = self.regulator_y.value()
                print("  Using coordinates directly (assuming same CRS as DEM)")
                return
            
            # Create coordinate transformation
            transform = osr.CoordinateTransformation(utm_srs, self.dem_crs)
            
            # Transform UTM coordinates
            utm_x = self.regulator_x.value()
            utm_y = self.regulator_y.value()
            
            print(f"  UTM Coordinates: {utm_x:.3f} E, {utm_y:.3f} N")
            
            # Transform
            x, y, z = transform.TransformPoint(utm_x, utm_y, 0)
            
            # Store transformed coordinates
            self.regulator_x_dem = x
            self.regulator_y_dem = y
            
            print(f"  Transformed to DEM CRS: {x:.3f}, {y:.3f}")
            
            # Check if coordinates are within DEM extent (if QGIS available)
            if self.use_qgis:
                layers = QgsProject.instance().mapLayersByName("DEM")
                if layers:
                    extent = layers[0].extent()
                    if extent.xMinimum() <= x <= extent.xMaximum() and \
                       extent.yMinimum() <= y <= extent.yMaximum():
                        print("  ✓ Coordinates are within DEM extent")
                    else:
                        warning = (
                            f"Regulator coordinates may be outside DEM extent!\n"
                            f"DEM: X[{extent.xMinimum():.2f}, {extent.xMaximum():.2f}], "
                            f"Y[{extent.yMinimum():.2f}, {extent.yMaximum():.2f}]\n"
                            f"Regulator: X[{x:.2f}], Y[{y:.2f}]"
                        )
                        print(f"  WARNING: {warning}")
                        QMessageBox.warning(self, "Coordinates", warning)
        
        except Exception as e:
            # If transformation fails, use direct coordinates
            self.regulator_x_dem = self.regulator_x.value()
            self.regulator_y_dem = self.regulator_y.value()
            print(f"  WARNING: Coordinate transformation failed: {str(e)}")
            print(f"  Using coordinates directly")
    
    def get_rainfall_intensity(self):
        """Get selected rainfall intensity in mm/hr"""
        if self.rainfall_combo.currentText() == "Custom Intensity":
            return self.custom_rainfall.value()
        
        selection = self.rainfall_combo.currentText()
        if "Light" in selection:
            return 5
        elif "Moderate" in selection:
            return 10
        elif "Heavy" in selection:
            return 25
        elif "Very Heavy" in selection:
            return 50
        elif "Extreme" in selection:
            return 100
        return 10
    
    def run_simulation(self):
        """Run flood simulation"""
        if self.dem_data is None:
            QMessageBox.warning(self, "Error", "Please load DEM first!")
            return
        
        # Get parameters
        rainfall_intensity = self.get_rainfall_intensity()  # mm/hr
        duration = self.duration_spin.value()  # hours
        time_step = self.time_step_spin.value()  # minutes
        manning_n = self.manning_n.value()
        infiltration_rate = self.infiltration_rate.value()  # mm/hr
        curve_number = self.curve_number.value()
        dam_height = self.dam_height.value()  # meters (legacy)
        initial_water_level = self.initial_water_level.value()  # meters
        
        # Get structure dimensions
        spillway_width = self.spillway_width.value()  # meters
        overflow_elevation = self.overflow_elevation.value()  # meters
        weir_coefficient = self.weir_coefficient.value()
        
        # Get regulator coordinates - prefer pixel coordinates if available
        pixel_x = None
        pixel_y = None
        
        # Check manual pixel input first
        if hasattr(self, 'regulator_pixel_x_input') and self.regulator_pixel_x_input.isEnabled():
            pixel_x = self.regulator_pixel_x_input.value()
            pixel_y = self.regulator_pixel_y_input.value()
            print(f"Using manual pixel coordinates: ({pixel_x}, {pixel_y})")
        
        # Use stored pixel coordinates if available
        if pixel_x is None and hasattr(self, 'regulator_pixel_x') and hasattr(self, 'regulator_pixel_y'):
            if self.regulator_pixel_x is not None and self.regulator_pixel_y is not None:
                pixel_x = int(self.regulator_pixel_x)
                pixel_y = int(self.regulator_pixel_y)
                print(f"Using stored pixel coordinates: ({pixel_x}, {pixel_y})")
        
        # Try to convert world coordinates to pixels
        if pixel_x is None:
            if hasattr(self, 'regulator_x_dem') and self.regulator_x_dem is not None:
                regulator_x = self.regulator_x_dem
                regulator_y = self.regulator_y_dem
                pixel_x, pixel_y = self.world_to_pixel(regulator_x, regulator_y)
                if pixel_x is not None and pixel_y is not None:
                    print(f"Converted world coordinates to pixels: ({pixel_x}, {pixel_y})")
        
        # Try to convert from spin box values
        if pixel_x is None:
            regulator_x = self.regulator_x.value()
            regulator_y = self.regulator_y.value()
            pixel_x, pixel_y = self.world_to_pixel(regulator_x, regulator_y)
            if pixel_x is not None and pixel_y is not None:
                print(f"Converted spin box coordinates to pixels: ({pixel_x}, {pixel_y})")
        
        # If still no valid coordinates, auto-detect
        if pixel_x is None or pixel_y is None:
            print("No valid regulator coordinates found. Auto-detecting...")
            # Auto-detect
            self.auto_detect_regulator()
            # Get the detected coordinates
            if hasattr(self, 'regulator_pixel_x') and hasattr(self, 'regulator_pixel_y'):
                pixel_x = int(self.regulator_pixel_x)
                pixel_y = int(self.regulator_pixel_y)
                print(f"Auto-detected regulator at: ({pixel_x}, {pixel_y})")
            else:
                # Last resort: use center
                pixel_x = self.dem_data.shape[1] // 2
                pixel_y = self.dem_data.shape[0] // 2
                print(f"Using DEM center as fallback: ({pixel_x}, {pixel_y})")
        
        # Validate pixel coordinates are within bounds
        if not (0 <= pixel_x < self.dem_data.shape[1] and 0 <= pixel_y < self.dem_data.shape[0]):
            # Clamp to valid range
            old_x, old_y = pixel_x, pixel_y
            pixel_x = max(0, min(int(pixel_x), self.dem_data.shape[1] - 1))
            pixel_y = max(0, min(int(pixel_y), self.dem_data.shape[0] - 1))
            print(f"WARNING: Pixel coordinates ({old_x}, {old_y}) clamped to: ({pixel_x}, {pixel_y})")
            QMessageBox.warning(
                self, "Coordinate Warning",
                f"Regulator coordinates were out of bounds and have been adjusted:\n"
                f"From: ({old_x}, {old_y})\n"
                f"To: ({pixel_x}, {pixel_y})"
            )
        
        # Ensure coordinates are integers
        pixel_x = int(pixel_x)
        pixel_y = int(pixel_y)
        
        # Store for future use
        self.regulator_pixel_x = pixel_x
        self.regulator_pixel_y = pixel_y
        
        # Get ground elevation at regulator location for validation
        ground_elevation = self.dem_data[pixel_y, pixel_x]
        print(f"\n{'='*60}")
        print(f"Simulation Setup")
        print(f"{'='*60}")
        print(f"Regulator pixel location: ({pixel_x}, {pixel_y})")
        print(f"Ground elevation at regulator: {ground_elevation:.2f} m")
        print(f"Structure dimensions:")
        print(f"  Spillway width: {spillway_width:.2f} m")
        print(f"  Overflow elevation: {overflow_elevation:.2f} m")
        print(f"  Weir coefficient: {weir_coefficient:.2f}")
        print(f"  Initial water level: {initial_water_level:.2f} m")
        print(f"{'='*60}")
        
        # Validate overflow elevation is reasonable
        if overflow_elevation < ground_elevation - 10 or overflow_elevation > ground_elevation + 100:
            warning = (
                f"Warning: Overflow elevation ({overflow_elevation:.2f} m) seems unusual "
                f"compared to ground elevation ({ground_elevation:.2f} m).\n"
                f"Please verify this is correct."
            )
            print(f"WARNING: {warning}")
            reply = QMessageBox.question(
                self, "Elevation Warning", 
                warning + "\n\nContinue anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.run_btn.setEnabled(True)
                return
        
        # Disable run button
        self.run_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Initializing simulation...")
        
        try:
            # Create simulator with proper geotransform (use dummy if None)
            geotransform = self.dem_transform
            if geotransform is None:
                # Create dummy geotransform
                geotransform = (0, 1, 0, 0, 0, -1)
                print("WARNING: Using dummy geotransform (DEM not georeferenced)")
            
            from flood_simulator import FloodSimulator2D
            self.simulator = FloodSimulator2D(
                self.dem_data,
                geotransform,
                manning_n=manning_n,
                infiltration_rate=infiltration_rate,
                curve_number=curve_number,
                dam_height=dam_height,
                initial_water_level=initial_water_level,
                spillway_width=spillway_width,
                overflow_elevation=overflow_elevation,
                weir_coefficient=weir_coefficient
            )
            
            # Set regulator location (use pixel coordinates directly)
            self.simulator.set_regulator(pixel_x, pixel_y)
            print(f"Regulator set at pixel coordinates: ({pixel_x}, {pixel_y})")
            
            # Run simulation in thread
            self.sim_thread = FloodSimulationThread(
                self.simulator, duration, time_step, rainfall_intensity
            )
            self.sim_thread.progress.connect(self.progress_bar.setValue)
            self.sim_thread.status_message.connect(self.status_label.setText)
            self.sim_thread.finished.connect(self.simulation_finished)
            self.sim_thread.start()
            
        except Exception as e:
            error_msg = f"Failed to start simulation:\n{str(e)}"
            print(f"ERROR: {error_msg}")
            QMessageBox.critical(self, "Simulation Error", error_msg)
            self.run_btn.setEnabled(True)
            self.status_label.setText("Simulation failed")
    
    def world_to_pixel(self, x, y):
        """Convert world coordinates to pixel coordinates"""
        if self.dem_transform is None:
            print("WARNING: No geotransform available for coordinate conversion")
            return None, None
        
        try:
            # Check if geotransform is valid (not dummy values)
            # Dummy geotransform is typically (0, 1, 0, 0, 0, -1)
            if (abs(self.dem_transform[0]) < 0.001 and abs(self.dem_transform[1] - 1.0) < 0.001 and 
                abs(self.dem_transform[3]) < 0.001 and abs(abs(self.dem_transform[5]) - 1.0) < 0.001):
                # This is a dummy/unreferenced geotransform
                print("WARNING: DEM appears to have dummy geotransform (not georeferenced)")
                return None, None
            
            # Validate geotransform values
            if abs(self.dem_transform[1]) < 0.001 or abs(self.dem_transform[5]) < 0.001:
                print("WARNING: Invalid geotransform cell size")
                return None, None
            
            # Convert coordinates
            pixel_x = int((x - self.dem_transform[0]) / self.dem_transform[1])
            pixel_y = int((y - self.dem_transform[3]) / self.dem_transform[5])
            
            # Check if result is reasonable (within DEM bounds or close)
            if abs(pixel_x) > 1000000 or abs(pixel_y) > 1000000:
                print(f"WARNING: Calculated pixel coordinates seem invalid: ({pixel_x}, {pixel_y})")
                return None, None
            
            # Check if within DEM bounds (with some tolerance)
            if self.dem_data is not None:
                rows, cols = self.dem_data.shape
                if pixel_x < -cols or pixel_x > cols * 2 or pixel_y < -rows or pixel_y > rows * 2:
                    print(f"WARNING: Pixel coordinates ({pixel_x}, {pixel_y}) are far outside DEM bounds ({cols}, {rows})")
                    # Still return them, but warn - they might be clamped later
            
            return pixel_x, pixel_y
            
        except Exception as e:
            print(f"ERROR: Coordinate conversion failed: {str(e)}")
            return None, None
    
    def auto_detect_regulator(self):
        """Automatically detect regulator location - simple elevation-based method"""
        if self.dem_data is None:
            QMessageBox.warning(self, "Error", "Please load DEM first!")
            return
        
        print("\nDetecting regulator location...")
        rows, cols = self.dem_data.shape
        
        # Simple method: Find lowest elevation point in upper-left quadrant
        # This is where regulators/dams are typically located (in valleys)
        search_rows = max(10, int(rows * 0.4))  # First 40% of rows
        search_cols = max(10, int(cols * 0.4))  # First 40% of columns
        
        # Extract search area
        search_area = self.dem_data[:search_rows, :search_cols]
        
        # Find minimum elevation (valley/low point)
        min_idx = np.unravel_index(np.argmin(search_area), search_area.shape)
        pixel_y = int(min_idx[0])
        pixel_x = int(min_idx[1])
        
        print(f"Found regulator at lowest elevation in upper-left area: ({pixel_x}, {pixel_y})")
        print(f"Elevation: {self.dem_data[pixel_y, pixel_x]:.2f} m")
        
        # Ensure coordinates are within bounds
        pixel_x = max(10, min(pixel_x, cols - 10))
        pixel_y = max(10, min(pixel_y, rows - 10))
        
        print(f"Regulator location set to pixel coordinates: ({pixel_x}, {pixel_y})")
        
        try:
            # Check if geotransform is valid
            is_valid_geotransform = False
            if self.dem_transform is not None:
                # Check if geotransform values are reasonable (not dummy values)
                if (abs(self.dem_transform[1]) > 0.001 and abs(self.dem_transform[5]) > 0.001 and
                    abs(self.dem_transform[0]) < 1e10 and abs(self.dem_transform[3]) < 1e10):
                    is_valid_geotransform = True
            
            # Convert pixel coordinates back to world coordinates if geotransform is valid
            if is_valid_geotransform:
                world_x = self.dem_transform[0] + pixel_x * self.dem_transform[1]
                world_y = self.dem_transform[3] + pixel_y * self.dem_transform[5]
                
                # Update the coordinate spin boxes
                self.regulator_x.setValue(world_x)
                self.regulator_y.setValue(world_y)
                
                # Store pixel coordinates directly
                self.regulator_x_dem = world_x
                self.regulator_y_dem = world_y
                self.regulator_pixel_x = pixel_x
                self.regulator_pixel_y = pixel_y
                
                # Update pixel coordinate inputs
                if hasattr(self, 'regulator_pixel_x_input'):
                    self.regulator_pixel_x_input.setValue(pixel_x)
                    self.regulator_pixel_x_input.setEnabled(True)
                if hasattr(self, 'regulator_pixel_y_input'):
                    self.regulator_pixel_y_input.setValue(pixel_y)
                    self.regulator_pixel_y_input.setEnabled(True)
                
                print(f"Regulator location set to world coordinates: ({world_x:.2f}, {world_y:.2f})")
                print(f"Pixel coordinates: ({pixel_x}, {pixel_y})")
            else:
                # No valid geotransform - use pixel coordinates directly
                self.regulator_x.setValue(pixel_x)
                self.regulator_y.setValue(pixel_y)
                self.regulator_x_dem = pixel_x
                self.regulator_y_dem = pixel_y
                self.regulator_pixel_x = pixel_x
                self.regulator_pixel_y = pixel_y
                
                # Update pixel coordinate inputs
                if hasattr(self, 'regulator_pixel_x_input'):
                    self.regulator_pixel_x_input.setValue(pixel_x)
                    self.regulator_pixel_x_input.setEnabled(True)
                if hasattr(self, 'regulator_pixel_y_input'):
                    self.regulator_pixel_y_input.setValue(pixel_y)
                    self.regulator_pixel_y_input.setEnabled(True)
                
                print(f"Regulator location set to pixel coordinates: ({pixel_x}, {pixel_y})")
                print("Note: DEM appears to have no georeferencing - using pixel coordinates")
            
            # Show on map if matplotlib is available
            if self.use_matplotlib and hasattr(self, 'ax'):
                try:
                    self.ax.clear()
                    if self.dem_data is not None:
                        im = self.ax.imshow(self.dem_data, cmap='terrain', aspect='auto', origin='upper')
                        # Mark regulator location (note: Y-axis is inverted in image coordinates)
                        self.ax.plot(pixel_x, pixel_y, 'r*', markersize=20, 
                                   label='Regulator Location', markeredgecolor='black', markeredgewidth=2)
                        self.ax.legend()
                        # Remove old colorbar if exists
                        if hasattr(self, 'dem_colorbar') and self.dem_colorbar is not None:
                            try:
                                self.dem_colorbar.remove()
                            except:
                                pass
                        # Create new colorbar with fixed position
                        if hasattr(self, 'dem_colorbar') and self.dem_colorbar is not None:
                            try:
                                self.dem_colorbar.remove()
                                self.dem_colorbar = None
                            except:
                                pass
                        self.dem_colorbar = self.fig.colorbar(im, ax=self.ax, fraction=0.046, pad=0.04)
                        self.dem_colorbar.set_label('Elevation (m)', fontsize=10)
                        # FIXED: Use fixed subplots_adjust to prevent shrinking
                        self.fig.subplots_adjust(left=0.05, right=0.92, top=0.95, bottom=0.05)
                        self.canvas.draw()
                except Exception as plot_error:
                    print(f"Warning: Could not update map display: {str(plot_error)}")
                    # Continue anyway - detection was successful
            
            # Show success message (only if no critical errors)
            try:
                QMessageBox.information(
                    self, "Regulator Location Set",
                    f"Regulator location set to:\n"
                    f"Pixel coordinates: ({pixel_x}, {pixel_y})\n\n"
                    f"To change, edit lines 1038-1039 in flood_analysis_app.py"
                )
            except:
                # If message box fails, just print
                print(f"Regulator location detected: ({pixel_x}, {pixel_y})")
            
        except Exception as e:
            print(f"Error in auto-detection: {str(e)}")
            # Fallback to center
            pixel_x = self.dem_data.shape[1] // 2
            pixel_y = self.dem_data.shape[0] // 2
            
            self.regulator_pixel_x = pixel_x
            self.regulator_pixel_y = pixel_y
            
            if self.dem_transform is not None:
                world_x = self.dem_transform[0] + pixel_x * self.dem_transform[1]
                world_y = self.dem_transform[3] + pixel_y * self.dem_transform[5]
                self.regulator_x.setValue(world_x)
                self.regulator_y.setValue(world_y)
                self.regulator_x_dem = world_x
                self.regulator_y_dem = world_y
            else:
                self.regulator_x.setValue(pixel_x)
                self.regulator_y.setValue(pixel_y)
                self.regulator_x_dem = pixel_x
                self.regulator_y_dem = pixel_y
            
            QMessageBox.warning(
                self, "Auto-Detection Failed",
                f"Using DEM center as fallback:\n"
                f"Pixel coordinates: ({pixel_x}, {pixel_y})\n\n"
                f"Error: {str(e)}"
            )
    
    def simulation_finished(self, results):
        """Handle simulation completion"""
        self.simulation_results = results
        self.run_btn.setEnabled(True)
        self.status_label.setText("Simulation complete!")
        
        # Setup time slider
        num_steps = len(results['water_depth'])
        self.time_slider.setMaximum(max(0, num_steps - 1))
        self.time_slider.setValue(0)
        self.time_slider.setEnabled(True)
        self.play_btn.setEnabled(True)
        
        # Display first time step
        self.update_time_display(0)
        
        max_depth = np.max(results['water_depth'][-1])
        success_msg = (
            f"Simulation finished with {num_steps} time steps.\n"
            f"Max water depth: {max_depth:.2f} m"
        )
        print(f"\n{success_msg}")
        QMessageBox.information(self, "Simulation Complete", success_msg)
    
    def update_time_display(self, step):
        """Update display for given time step"""
        if self.simulation_results is None:
            return
        
        self.current_time_step = step
        time_hours = step * self.time_step_spin.value() / 60.0
        hours = int(time_hours)
        minutes = int((time_hours - hours) * 60)
        self.time_label.setText(f"Time: {hours}:{minutes:02d}")
        
        # Update map with water depth
        water_depth = self.simulation_results['water_depth'][step]
        self.display_water_depth(water_depth)
    
    def display_water_depth(self, water_depth):
        """Display water depth as raster layer"""
        if self.use_qgis:
            # Remove old water depth layer
            old_layers = QgsProject.instance().mapLayersByName("Water Depth")
            for layer in old_layers:
                QgsProject.instance().removeMapLayer(layer.id())
            
            # Create temporary raster file
            temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp")
            os.makedirs(temp_dir, exist_ok=True)
            temp_file = os.path.join(temp_dir, "temp_water_depth.tif")
            
            # Save water depth to GeoTIFF
            if GDAL_AVAILABLE:
                driver = gdal.GetDriverByName("GTiff")
                dataset = driver.Create(
                    temp_file, 
                    water_depth.shape[1], 
                    water_depth.shape[0], 
                    1, 
                    gdal.GDT_Float32
                )
                
                dataset.SetGeoTransform(self.dem_transform)
                if self.dem_path:
                    source_ds = gdal.Open(self.dem_path)
                    if source_ds:
                        dataset.SetProjection(source_ds.GetProjection())
                
                band = dataset.GetRasterBand(1)
                band.WriteArray(water_depth)
                band.SetNoDataValue(-9999)
                dataset.FlushCache()
                dataset = None
                
                # Load as QGIS layer
                layer = QgsRasterLayer(temp_file, "Water Depth")
                
                if layer.isValid():
                    # Apply color ramp
                    shader = QgsColorRampShader()
                    shader.setColorRampType(QgsColorRampShader.Interpolated)
                    
                    items = [
                        QgsColorRampShader.ColorRampItem(0, QColor(0, 0, 0, 0), "No Water"),
                        QgsColorRampShader.ColorRampItem(0.05, QColor(255, 200, 200, 200), "0.05 m"),
                        QgsColorRampShader.ColorRampItem(0.1, QColor(255, 150, 150, 200), "0.1 m"),
                        QgsColorRampShader.ColorRampItem(0.5, QColor(255, 100, 100, 200), "0.5 m"),
                        QgsColorRampShader.ColorRampItem(1.0, QColor(255, 0, 0, 200), "1.0 m"),
                        QgsColorRampShader.ColorRampItem(2.0, QColor(200, 0, 0, 200), "2.0 m"),
                        QgsColorRampShader.ColorRampItem(5.0, QColor(139, 0, 0, 200), "5.0+ m"),
                    ]
                    shader.setColorRampItemList(items)
                    
                    renderer = QgsSingleBandPseudoColorRenderer(
                        layer.dataProvider(), 1, shader
                    )
                    layer.setRenderer(renderer)
                    
                    # Add to project
                    QgsProject.instance().addMapLayer(layer)
                    
                    # Update canvas
                    dem_layer = QgsProject.instance().mapLayersByName("DEM")[0]
                    self.map_canvas.setLayers([dem_layer, layer])
                    self.map_canvas.refresh()
        elif self.use_matplotlib:
            # Display using matplotlib
            self.ax.clear()
            # Create overlay: DEM in background, water depth on top
            if self.dem_data is not None:
                self.ax.imshow(self.dem_data, cmap='gray', alpha=0.5, aspect='auto', origin='upper')
            
            # Display water depth with transparency - RED color for flood
            masked_water = np.ma.masked_where(water_depth < 0.01, water_depth)
            im = self.ax.imshow(masked_water, cmap='Reds', alpha=0.7, aspect='auto', 
                              vmin=0, vmax=max(5.0, np.max(water_depth)), origin='upper')
            self.ax.set_title(f"Water Depth - Time Step {self.current_time_step}", 
                            fontsize=12, pad=10)
            # Remove old colorbar properly
            if hasattr(self, 'colorbar') and self.colorbar is not None:
                try:
                    self.colorbar.remove()
                    self.colorbar = None
                except:
                    pass
            self.colorbar = self.fig.colorbar(im, ax=self.ax, fraction=0.046, pad=0.04)
            self.colorbar.set_label('Water Depth (m)', fontsize=10)
            # FIXED: Use fixed subplots_adjust to prevent shrinking
            self.fig.subplots_adjust(left=0.05, right=0.92, top=0.95, bottom=0.05)
            self.canvas.draw()
    
    def toggle_animation(self):
        """Toggle animation playback"""
        if not hasattr(self, 'animation_timer') or self.animation_timer is None:
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self.animate_step)
            self.animation_playing = False
        
        if self.animation_playing:
            self.animation_timer.stop()
            self.play_btn.setText("Play Animation")
            self.animation_playing = False
        else:
            interval = int(1000 / 2)  # 2 frames per second
            self.animation_timer.start(interval)
            self.play_btn.setText("Pause Animation")
            self.animation_playing = True
    
    def animate_step(self):
        """Step through animation"""
        if self.simulation_results is None:
            return
        
        max_step = self.time_slider.maximum()
        current = self.time_slider.value()
        
        if current < max_step:
            self.time_slider.setValue(current + 1)
        else:
            self.animation_timer.stop()
            self.play_btn.setText("Play Animation")
            self.animation_playing = False
    
    def export_current_view(self):
        """Export current map view"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Map", "", "PNG Files (*.png);;JPEG Files (*.jpg)")
        if file_path:
            if self.use_qgis:
                self.map_canvas.saveAsImage(file_path)
            elif self.use_matplotlib:
                self.fig.savefig(file_path, dpi=150, bbox_inches='tight')
            print(f"Map exported to: {file_path}")
            QMessageBox.information(self, "Export", f"Map exported to {file_path}")
    
    def export_all_timesteps(self):
        """Export all time steps as GeoTIFF files"""
        if self.simulation_results is None:
            QMessageBox.warning(self, "Error", "No simulation results to export!")
            return
        
        # Ask for output directory
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select Output Directory for GeoTIFF Files")
        
        if not output_dir:
            return
        
        print(f"\nExporting {len(self.simulation_results['water_depth'])} time steps...")
        print(f"Output directory: {output_dir}")
        
        if not GDAL_AVAILABLE:
            QMessageBox.warning(self, "Error", 
                              "GDAL not available. Cannot export GeoTIFF files.\n"
                              "Please install GDAL or use QGIS.")
            return
        
        # Export each time step
        driver = gdal.GetDriverByName("GTiff")
        
        for i, water_depth in enumerate(self.simulation_results['water_depth']):
            time_hours = self.simulation_results['time_steps'][i]
            filename = f"flood_depth_t{time_hours:06.2f}hr.tif"
            filepath = os.path.join(output_dir, filename)
            
            # Create GeoTIFF
            dataset = driver.Create(
                filepath,
                water_depth.shape[1],
                water_depth.shape[0],
                1,
                gdal.GDT_Float32
            )
            
            if self.dem_transform:
                dataset.SetGeoTransform(self.dem_transform)
            if self.dem_path:
                source_ds = gdal.Open(self.dem_path)
                if source_ds:
                    dataset.SetProjection(source_ds.GetProjection())
            
            band = dataset.GetRasterBand(1)
            band.WriteArray(water_depth)
            band.SetNoDataValue(-9999)
            band.SetDescription("Water Depth (m)")
            dataset.FlushCache()
            dataset = None
            
            if (i + 1) % 10 == 0:
                print(f"  Exported {i + 1}/{len(self.simulation_results['water_depth'])} files...")
        
        print(f"Export complete! {len(self.simulation_results['water_depth'])} files saved.")
        QMessageBox.information(
            self, "Export Complete",
            f"Exported {len(self.simulation_results['water_depth'])} GeoTIFF files to:\n{output_dir}"
        )
    
    def closeEvent(self, event):
        """Clean up on close"""
        if self.animation_timer:
            self.animation_timer.stop()
        print("\nClosing application...")
        if self.qgs:
            self.qgs.exitQgis()
        super().closeEvent(event)


def main():
    print("="*60)
    print("Flood Analysis Simulation App")
    print("="*60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    app = QApplication(sys.argv)
    window = FloodAnalysisApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

