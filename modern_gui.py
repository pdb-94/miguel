"""
MiGUEL Modern GUI - Energy System Configuration Tool
Supports all components including hydrogen infrastructure
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import datetime, timedelta
import pandas as pd
import threading
import os
import sys

# Import MiGUEL modules
from environment import Environment
from operation import Operator
from evaluation import Evaluation


class MiGUELApp:
    """Modern GUI for MiGUEL energy system simulation"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("MiGUEL - Micro Grid User Energy Tool Library")
        self.root.geometry("1000x700")
        
        # State variables
        self.env = None
        self.operator = None
        self.evaluation = None
        self.components_added = []
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Create the main UI layout"""
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_system_tab()
        self.create_load_tab()
        self.create_pv_tab()
        self.create_storage_tab()
        self.create_hydrogen_tab()
        self.create_simulation_tab()
        self.create_results_tab()
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_system_tab(self):
        """Tab 1: System Setup"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="1. System Setup")
        
        # Main frame with scroll
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Project Info
        info_frame = ttk.LabelFrame(main_frame, text="Project Information", padding=10)
        info_frame.grid(row=0, column=0, sticky='ew', pady=5)
        
        ttk.Label(info_frame, text="Project Name:").grid(row=0, column=0, sticky='w', pady=2)
        self.project_name = ttk.Entry(info_frame, width=40)
        self.project_name.grid(row=0, column=1, pady=2)
        self.project_name.insert(0, "My Energy System")
        
        # Location
        location_frame = ttk.LabelFrame(main_frame, text="Location", padding=10)
        location_frame.grid(row=1, column=0, sticky='ew', pady=5)
        
        ttk.Label(location_frame, text="Latitude:").grid(row=0, column=0, sticky='w', pady=2)
        self.latitude = ttk.Entry(location_frame, width=20)
        self.latitude.grid(row=0, column=1, pady=2)
        self.latitude.insert(0, "52.52")
        
        ttk.Label(location_frame, text="Longitude:").grid(row=1, column=0, sticky='w', pady=2)
        self.longitude = ttk.Entry(location_frame, width=20)
        self.longitude.grid(row=1, column=1, pady=2)
        self.longitude.insert(0, "13.40")
        
        ttk.Label(location_frame, text="Terrain:").grid(row=2, column=0, sticky='w', pady=2)
        self.terrain = ttk.Combobox(location_frame, values=['urban', 'rural', 'coastal'], width=17)
        self.terrain.grid(row=2, column=1, pady=2)
        self.terrain.current(1)
        
        # Time Settings
        time_frame = ttk.LabelFrame(main_frame, text="Simulation Time Period", padding=10)
        time_frame.grid(row=2, column=0, sticky='ew', pady=5)
        
        ttk.Label(time_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, sticky='w', pady=2)
        self.start_date = ttk.Entry(time_frame, width=20)
        self.start_date.grid(row=0, column=1, pady=2)
        self.start_date.insert(0, "2023-01-01")
        
        ttk.Label(time_frame, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, sticky='w', pady=2)
        self.end_date = ttk.Entry(time_frame, width=20)
        self.end_date.grid(row=1, column=1, pady=2)
        self.end_date.insert(0, "2023-12-31")
        
        ttk.Label(time_frame, text="Time Step (minutes):").grid(row=2, column=0, sticky='w', pady=2)
        self.timestep = ttk.Combobox(time_frame, values=['15', '30', '60'], width=17)
        self.timestep.grid(row=2, column=1, pady=2)
        self.timestep.current(2)
        
        # Economic Parameters
        econ_frame = ttk.LabelFrame(main_frame, text="Economic Parameters", padding=10)
        econ_frame.grid(row=3, column=0, sticky='ew', pady=5)
        
        ttk.Label(econ_frame, text="Discount Rate:").grid(row=0, column=0, sticky='w', pady=2)
        self.discount_rate = ttk.Entry(econ_frame, width=20)
        self.discount_rate.grid(row=0, column=1, pady=2)
        self.discount_rate.insert(0, "0.05")
        
        ttk.Label(econ_frame, text="Project Lifetime (years):").grid(row=1, column=0, sticky='w', pady=2)
        self.lifetime = ttk.Entry(econ_frame, width=20)
        self.lifetime.grid(row=1, column=1, pady=2)
        self.lifetime.insert(0, "20")
        
        ttk.Label(econ_frame, text="Electricity Price ($/kWh):").grid(row=2, column=0, sticky='w', pady=2)
        self.electricity_price = ttk.Entry(econ_frame, width=20)
        self.electricity_price.grid(row=2, column=1, pady=2)
        self.electricity_price.insert(0, "0.15")
        
        # Grid Connection
        grid_frame = ttk.LabelFrame(main_frame, text="Grid Connection", padding=10)
        grid_frame.grid(row=4, column=0, sticky='ew', pady=5)
        
        self.grid_connected = tk.BooleanVar(value=True)
        ttk.Checkbutton(grid_frame, text="Grid Connected System", variable=self.grid_connected).grid(row=0, column=0, sticky='w')
        
        self.feed_in = tk.BooleanVar(value=False)
        ttk.Checkbutton(grid_frame, text="Feed-in Allowed", variable=self.feed_in).grid(row=1, column=0, sticky='w')
        
        # Create System Button
        create_btn = ttk.Button(main_frame, text="Create System", command=self.create_environment, 
                               style='Accent.TButton')
        create_btn.grid(row=5, column=0, pady=20)
        
    def create_load_tab(self):
        """Tab 2: Load Profile"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="2. Load Profile")
        
        main_frame = ttk.Frame(tab, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Load method selection
        method_frame = ttk.LabelFrame(main_frame, text="Load Profile Method", padding=10)
        method_frame.pack(fill='x', pady=5)
        
        self.load_method = tk.StringVar(value="annual")
        ttk.Radiobutton(method_frame, text="Annual Consumption + Reference Profile", 
                       variable=self.load_method, value="annual",
                       command=self.toggle_load_method).pack(anchor='w')
        ttk.Radiobutton(method_frame, text="Custom Load Profile (CSV)", 
                       variable=self.load_method, value="custom",
                       command=self.toggle_load_method).pack(anchor='w')
        
        # Annual consumption method
        self.annual_frame = ttk.LabelFrame(main_frame, text="Annual Consumption Method", padding=10)
        self.annual_frame.pack(fill='x', pady=5)
        
        ttk.Label(self.annual_frame, text="Annual Consumption (kWh):").grid(row=0, column=0, sticky='w', pady=2)
        self.annual_consumption = ttk.Entry(self.annual_frame, width=20)
        self.annual_consumption.grid(row=0, column=1, pady=2)
        self.annual_consumption.insert(0, "50000")
        
        ttk.Label(self.annual_frame, text="Reference Profile:").grid(row=1, column=0, sticky='w', pady=2)
        self.ref_profile = ttk.Combobox(self.annual_frame, 
                                       values=['H0', 'G0', 'G1', 'hospital_ghana'], width=17)
        self.ref_profile.grid(row=1, column=1, pady=2)
        self.ref_profile.current(0)
        
        # Custom profile method
        self.custom_frame = ttk.LabelFrame(main_frame, text="Custom Profile Method", padding=10)
        self.custom_frame.pack(fill='x', pady=5)
        
        ttk.Label(self.custom_frame, text="CSV File:").grid(row=0, column=0, sticky='w', pady=2)
        self.load_file = ttk.Entry(self.custom_frame, width=40)
        self.load_file.grid(row=0, column=1, pady=2)
        ttk.Button(self.custom_frame, text="Browse", 
                  command=lambda: self.browse_file(self.load_file)).grid(row=0, column=2, padx=5)
        
        # Initially hide custom frame
        self.custom_frame.pack_forget()
        
        # Add button
        ttk.Button(main_frame, text="Add Load Profile", command=self.add_load).pack(pady=10)
        
    def create_pv_tab(self):
        """Tab 3: Solar PV System"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="3. Solar PV")
        
        main_frame = ttk.Frame(tab, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # PV Configuration
        config_frame = ttk.LabelFrame(main_frame, text="PV System Configuration", padding=10)
        config_frame.pack(fill='x', pady=5)
        
        ttk.Label(config_frame, text="Nominal Power (kW):").grid(row=0, column=0, sticky='w', pady=2)
        self.pv_power = ttk.Entry(config_frame, width=20)
        self.pv_power.grid(row=0, column=1, pady=2)
        self.pv_power.insert(0, "100")
        
        ttk.Label(config_frame, text="Tilt Angle (degrees):").grid(row=1, column=0, sticky='w', pady=2)
        self.pv_tilt = ttk.Entry(config_frame, width=20)
        self.pv_tilt.grid(row=1, column=1, pady=2)
        self.pv_tilt.insert(0, "30")
        
        ttk.Label(config_frame, text="Azimuth (degrees):").grid(row=2, column=0, sticky='w', pady=2)
        self.pv_azimuth = ttk.Entry(config_frame, width=20)
        self.pv_azimuth.grid(row=2, column=1, pady=2)
        self.pv_azimuth.insert(0, "180")
        
        # Economic parameters
        econ_frame = ttk.LabelFrame(main_frame, text="Economic Parameters", padding=10)
        econ_frame.pack(fill='x', pady=5)
        
        ttk.Label(econ_frame, text="Investment Cost ($):").grid(row=0, column=0, sticky='w', pady=2)
        self.pv_invest = ttk.Entry(econ_frame, width=20)
        self.pv_invest.grid(row=0, column=1, pady=2)
        self.pv_invest.insert(0, "100000")
        
        ttk.Label(econ_frame, text="O&M Cost ($/year):").grid(row=1, column=0, sticky='w', pady=2)
        self.pv_om = ttk.Entry(econ_frame, width=20)
        self.pv_om.grid(row=1, column=1, pady=2)
        self.pv_om.insert(0, "2000")
        
        # Add button
        ttk.Button(main_frame, text="Add PV System", command=self.add_pv).pack(pady=10)
        
        # Component list
        list_frame = ttk.LabelFrame(main_frame, text="Added PV Systems", padding=10)
        list_frame.pack(fill='both', expand=True, pady=5)
        
        self.pv_list = tk.Listbox(list_frame, height=5)
        self.pv_list.pack(fill='both', expand=True)
        
    def create_storage_tab(self):
        """Tab 4: Battery Storage"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="4. Battery Storage")
        
        main_frame = ttk.Frame(tab, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Storage Configuration
        config_frame = ttk.LabelFrame(main_frame, text="Battery Storage Configuration", padding=10)
        config_frame.pack(fill='x', pady=5)
        
        ttk.Label(config_frame, text="Power Rating (kW):").grid(row=0, column=0, sticky='w', pady=2)
        self.storage_power = ttk.Entry(config_frame, width=20)
        self.storage_power.grid(row=0, column=1, pady=2)
        self.storage_power.insert(0, "50")
        
        ttk.Label(config_frame, text="Capacity (kWh):").grid(row=1, column=0, sticky='w', pady=2)
        self.storage_capacity = ttk.Entry(config_frame, width=20)
        self.storage_capacity.grid(row=1, column=1, pady=2)
        self.storage_capacity.insert(0, "200")
        
        ttk.Label(config_frame, text="Initial SOC:").grid(row=2, column=0, sticky='w', pady=2)
        self.storage_soc = ttk.Entry(config_frame, width=20)
        self.storage_soc.grid(row=2, column=1, pady=2)
        self.storage_soc.insert(0, "0.5")
        
        # Economic parameters
        econ_frame = ttk.LabelFrame(main_frame, text="Economic Parameters", padding=10)
        econ_frame.pack(fill='x', pady=5)
        
        ttk.Label(econ_frame, text="Investment Cost ($):").grid(row=0, column=0, sticky='w', pady=2)
        self.storage_invest = ttk.Entry(econ_frame, width=20)
        self.storage_invest.grid(row=0, column=1, pady=2)
        self.storage_invest.insert(0, "80000")
        
        ttk.Label(econ_frame, text="O&M Cost ($/year):").grid(row=1, column=0, sticky='w', pady=2)
        self.storage_om = ttk.Entry(econ_frame, width=20)
        self.storage_om.grid(row=1, column=1, pady=2)
        self.storage_om.insert(0, "1600")
        
        # Add button
        ttk.Button(main_frame, text="Add Battery Storage", command=self.add_storage).pack(pady=10)
        
        # Component list
        list_frame = ttk.LabelFrame(main_frame, text="Added Storage Systems", padding=10)
        list_frame.pack(fill='both', expand=True, pady=5)
        
        self.storage_list = tk.Listbox(list_frame, height=5)
        self.storage_list.pack(fill='both', expand=True)
        
    def create_hydrogen_tab(self):
        """Tab 5: Hydrogen System (Electrolyser, H2 Storage, Fuel Cell)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="5. Hydrogen System")
        
        # Create scrollable canvas
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        main_frame = ttk.Frame(scrollable_frame, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Electrolyser
        elec_frame = ttk.LabelFrame(main_frame, text="Electrolyser Configuration", padding=10)
        elec_frame.pack(fill='x', pady=5)
        
        ttk.Label(elec_frame, text="Nominal Power (kW):").grid(row=0, column=0, sticky='w', pady=2)
        self.electrolyser_power = ttk.Entry(elec_frame, width=20)
        self.electrolyser_power.grid(row=0, column=1, pady=2)
        self.electrolyser_power.insert(0, "50")
        
        ttk.Label(elec_frame, text="Investment Cost ($):").grid(row=1, column=0, sticky='w', pady=2)
        self.electrolyser_invest = ttk.Entry(elec_frame, width=20)
        self.electrolyser_invest.grid(row=1, column=1, pady=2)
        self.electrolyser_invest.insert(0, "100000")
        
        ttk.Label(elec_frame, text="O&M Cost ($/year):").grid(row=2, column=0, sticky='w', pady=2)
        self.electrolyser_om = ttk.Entry(elec_frame, width=20)
        self.electrolyser_om.grid(row=2, column=1, pady=2)
        self.electrolyser_om.insert(0, "2000")
        
        ttk.Button(elec_frame, text="Add Electrolyser", command=self.add_electrolyser).grid(row=3, column=0, columnspan=2, pady=5)
        
        # H2 Storage
        h2stor_frame = ttk.LabelFrame(main_frame, text="H2 Storage Configuration", padding=10)
        h2stor_frame.pack(fill='x', pady=5)
        
        ttk.Label(h2stor_frame, text="Capacity (kg):").grid(row=0, column=0, sticky='w', pady=2)
        self.h2storage_capacity = ttk.Entry(h2stor_frame, width=20)
        self.h2storage_capacity.grid(row=0, column=1, pady=2)
        self.h2storage_capacity.insert(0, "100")
        
        ttk.Label(h2stor_frame, text="Initial Level (0-1):").grid(row=1, column=0, sticky='w', pady=2)
        self.h2storage_initial = ttk.Entry(h2stor_frame, width=20)
        self.h2storage_initial.grid(row=1, column=1, pady=2)
        self.h2storage_initial.insert(0, "0.1")
        
        ttk.Label(h2stor_frame, text="Investment Cost ($):").grid(row=2, column=0, sticky='w', pady=2)
        self.h2storage_invest = ttk.Entry(h2stor_frame, width=20)
        self.h2storage_invest.grid(row=2, column=1, pady=2)
        self.h2storage_invest.insert(0, "50000")
        
        ttk.Button(h2stor_frame, text="Add H2 Storage", command=self.add_h2storage).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Fuel Cell
        fc_frame = ttk.LabelFrame(main_frame, text="Fuel Cell Configuration", padding=10)
        fc_frame.pack(fill='x', pady=5)
        
        ttk.Label(fc_frame, text="Nominal Power (kW):").grid(row=0, column=0, sticky='w', pady=2)
        self.fuelcell_power = ttk.Entry(fc_frame, width=20)
        self.fuelcell_power.grid(row=0, column=1, pady=2)
        self.fuelcell_power.insert(0, "30")
        
        ttk.Label(fc_frame, text="Investment Cost ($):").grid(row=1, column=0, sticky='w', pady=2)
        self.fuelcell_invest = ttk.Entry(fc_frame, width=20)
        self.fuelcell_invest.grid(row=1, column=1, pady=2)
        self.fuelcell_invest.insert(0, "90000")
        
        ttk.Label(fc_frame, text="O&M Cost ($/year):").grid(row=2, column=0, sticky='w', pady=2)
        self.fuelcell_om = ttk.Entry(fc_frame, width=20)
        self.fuelcell_om.grid(row=2, column=1, pady=2)
        self.fuelcell_om.insert(0, "1800")
        
        ttk.Button(fc_frame, text="Add Fuel Cell", command=self.add_fuelcell).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Component list
        list_frame = ttk.LabelFrame(main_frame, text="Added Hydrogen Components", padding=10)
        list_frame.pack(fill='both', expand=True, pady=5)
        
        self.h2_list = tk.Listbox(list_frame, height=8)
        self.h2_list.pack(fill='both', expand=True)
        
    def create_simulation_tab(self):
        """Tab 6: Run Simulation"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="6. Run Simulation")
        
        main_frame = ttk.Frame(tab, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # System overview
        overview_frame = ttk.LabelFrame(main_frame, text="System Overview", padding=10)
        overview_frame.pack(fill='both', expand=True, pady=10)
        
        self.system_overview = scrolledtext.ScrolledText(overview_frame, height=15, wrap=tk.WORD)
        self.system_overview.pack(fill='both', expand=True)
        
        # Simulation button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)
        
        self.sim_button = ttk.Button(button_frame, text="▶ Run Simulation", 
                                     command=self.run_simulation,
                                     style='Accent.TButton')
        self.sim_button.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="📋 Update Overview", 
                  command=self.update_system_overview).pack(side='left', padx=5)
        
        # Progress
        self.progress_var = tk.StringVar(value="Not started")
        ttk.Label(main_frame, textvariable=self.progress_var).pack()
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=5)
        
    def create_results_tab(self):
        """Tab 7: Results"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="7. Results")
        
        main_frame = ttk.Frame(tab, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Results display
        results_frame = ttk.LabelFrame(main_frame, text="Simulation Results", padding=10)
        results_frame.pack(fill='both', expand=True, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20, wrap=tk.WORD)
        self.results_text.pack(fill='both', expand=True)
        
        # Export buttons
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(fill='x', pady=10)
        
        ttk.Button(export_frame, text="📊 Export to Excel", 
                  command=self.export_results).pack(side='left', padx=5)
        ttk.Button(export_frame, text="📈 Show Plots", 
                  command=self.show_plots).pack(side='left', padx=5)
        
    # ===== CALLBACK METHODS =====
    
    def toggle_load_method(self):
        """Toggle between load profile methods"""
        if self.load_method.get() == "annual":
            self.custom_frame.pack_forget()
            self.annual_frame.pack(fill='x', pady=5)
        else:
            self.annual_frame.pack_forget()
            self.custom_frame.pack(fill='x', pady=5)
            
    def browse_file(self, entry_widget):
        """Browse for a file"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)
            
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
        
    def create_environment(self):
        """Create the MiGUEL environment"""
        try:
            self.update_status("Creating environment...")
            
            # Parse inputs
            name = self.project_name.get()
            lat = float(self.latitude.get())
            lon = float(self.longitude.get())
            terrain = self.terrain.get()
            
            start = datetime.strptime(self.start_date.get(), "%Y-%m-%d")
            end = datetime.strptime(self.end_date.get(), "%Y-%m-%d")
            step = timedelta(minutes=int(self.timestep.get()))
            
            d_rate = float(self.discount_rate.get())
            lifetime = int(self.lifetime.get())
            elec_price = float(self.electricity_price.get()) if self.grid_connected.get() else None
            
            # Create time dict
            time = {
                'start': start,
                'end': end,
                'step': step,
                'timezone': 'UTC'
            }
            
            # Create location dict
            location = {
                'latitude': lat,
                'longitude': lon,
                'terrain': terrain
            }
            
            # Create economy dict
            economy = {
                'd_rate': d_rate,
                'lifetime': lifetime,
                'electricity_price': elec_price,
                'currency': 'US$'
            }
            
            # Create ecology dict
            ecology = {
                'co2_grid': 0.5  # kg/kWh
            }
            
            # Create environment
            self.env = Environment(
                name=name,
                time=time,
                location=location,
                economy=economy,
                ecology=ecology,
                grid_connection=self.grid_connected.get(),
                feed_in=self.feed_in.get()
            )
            
            self.update_status("Environment created successfully!")
            messagebox.showinfo("Success", f"Environment '{name}' created successfully!\nYou can now add components.")
            
            # Enable other tabs
            for i in range(1, 7):
                self.notebook.tab(i, state='normal')
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create environment:\n{str(e)}")
            self.update_status("Error creating environment")
            
    def add_load(self):
        """Add load profile to environment"""
        if not self.env:
            messagebox.showwarning("Warning", "Please create the system first (Tab 1)")
            return
            
        try:
            if self.load_method.get() == "annual":
                consumption = float(self.annual_consumption.get())
                profile = self.ref_profile.get()
                self.env.add_load(annual_consumption=consumption, ref_profile=profile)
                msg = f"Load added: {consumption} kWh/year using {profile} profile"
            else:
                load_file = self.load_file.get()
                self.env.add_load(load_profile=load_file)
                msg = f"Load added from: {os.path.basename(load_file)}"
                
            self.components_added.append(f"Load: {msg}")
            self.update_status(msg)
            messagebox.showinfo("Success", msg)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add load:\n{str(e)}")
            
    def add_pv(self):
        """Add PV system"""
        if not self.env:
            messagebox.showwarning("Warning", "Please create the system first (Tab 1)")
            return
            
        try:
            power = float(self.pv_power.get()) * 1000  # Convert to W
            tilt = int(self.pv_tilt.get())
            azimuth = int(self.pv_azimuth.get())
            invest = float(self.pv_invest.get())
            om = float(self.pv_om.get())
            
            pv_data = {
                'surface_tilt': tilt,
                'surface_azimuth': azimuth
            }
            
            self.env.add_pv(p_n=power, pv_data=pv_data, c_invest=invest, c_op_main=om)
            
            msg = f"PV System {len(self.env.pv)}: {power/1000} kW"
            self.pv_list.insert(tk.END, msg)
            self.components_added.append(msg)
            self.update_status(f"Added {msg}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add PV:\n{str(e)}")
            
    def add_storage(self):
        """Add battery storage"""
        if not self.env:
            messagebox.showwarning("Warning", "Please create the system first (Tab 1)")
            return
            
        try:
            power = float(self.storage_power.get()) * 1000  # Convert to W
            capacity = float(self.storage_capacity.get()) * 1000  # Convert to Wh
            soc = float(self.storage_soc.get())
            invest = float(self.storage_invest.get())
            om = float(self.storage_om.get())
            
            self.env.add_storage(p_n=power, c=capacity, soc=soc, c_invest=invest, c_op_main=om)
            
            msg = f"Battery {len(self.env.storage)}: {power/1000} kW / {capacity/1000} kWh"
            self.storage_list.insert(tk.END, msg)
            self.components_added.append(msg)
            self.update_status(f"Added {msg}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add storage:\n{str(e)}")
            
    def add_electrolyser(self):
        """Add electrolyser"""
        if not self.env:
            messagebox.showwarning("Warning", "Please create the system first (Tab 1)")
            return
            
        try:
            power = float(self.electrolyser_power.get()) * 1000  # Convert to W
            invest = float(self.electrolyser_invest.get())
            om = float(self.electrolyser_om.get())
            
            self.env.add_electrolyser(p_n=power, c_invest=invest, c_op_main=om)
            
            msg = f"Electrolyser {len(self.env.electrolyser)}: {power/1000} kW"
            self.h2_list.insert(tk.END, msg)
            self.components_added.append(msg)
            self.update_status(f"Added {msg}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add electrolyser:\n{str(e)}")
            
    def add_h2storage(self):
        """Add H2 storage"""
        if not self.env:
            messagebox.showwarning("Warning", "Please create the system first (Tab 1)")
            return
            
        try:
            capacity = float(self.h2storage_capacity.get())
            initial = float(self.h2storage_initial.get())
            invest = float(self.h2storage_invest.get())
            
            self.env.add_H2_Storage(capacity=capacity, initial_level=initial, c_invest=invest)
            
            msg = f"H2 Storage {len(self.env.H2Storage)}: {capacity} kg"
            self.h2_list.insert(tk.END, msg)
            self.components_added.append(msg)
            self.update_status(f"Added {msg}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add H2 storage:\n{str(e)}")
            
    def add_fuelcell(self):
        """Add fuel cell"""
        if not self.env:
            messagebox.showwarning("Warning", "Please create the system first (Tab 1)")
            return
            
        try:
            power = float(self.fuelcell_power.get()) * 1000  # Convert to W
            invest = float(self.fuelcell_invest.get())
            om = float(self.fuelcell_om.get())
            
            self.env.add_fuel_cell(p_n=power, c_invest=invest, c_op_main=om)
            
            msg = f"Fuel Cell {len(self.env.fuel_cell)}: {power/1000} kW"
            self.h2_list.insert(tk.END, msg)
            self.components_added.append(msg)
            self.update_status(f"Added {msg}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add fuel cell:\n{str(e)}")
            
    def update_system_overview(self):
        """Update the system overview display"""
        if not self.env:
            self.system_overview.delete('1.0', tk.END)
            self.system_overview.insert('1.0', "No system created yet. Please go to Tab 1.")
            return
            
        overview = f"=== SYSTEM OVERVIEW ===\n\n"
        overview += f"Project: {self.env.name}\n"
        overview += f"Location: {self.env.latitude}°N, {self.env.longitude}°E\n"
        overview += f"Simulation Period: {self.env.t_start} to {self.env.t_end}\n"
        overview += f"Time Step: {self.env.i_step} minutes\n\n"
        
        overview += "=== COMPONENTS ===\n\n"
        
        if self.env.load:
            overview += f"✓ Load Profile: Added\n"
        
        if len(self.env.pv) > 0:
            overview += f"✓ PV Systems: {len(self.env.pv)}\n"
            for i, pv in enumerate(self.env.pv, 1):
                overview += f"  - PV_{i}: {pv.p_n/1000:.1f} kW\n"
                
        if len(self.env.storage) > 0:
            overview += f"✓ Battery Storage: {len(self.env.storage)}\n"
            for i, stor in enumerate(self.env.storage, 1):
                overview += f"  - Battery_{i}: {stor.p_n/1000:.1f} kW / {stor.c/1000:.1f} kWh\n"
                
        if len(self.env.electrolyser) > 0:
            overview += f"✓ Electrolyser: {len(self.env.electrolyser)}\n"
            for i, elec in enumerate(self.env.electrolyser, 1):
                overview += f"  - Electrolyser_{i}: {elec.p_n/1000:.1f} kW\n"
                
        if len(self.env.H2Storage) > 0:
            overview += f"✓ H2 Storage: {len(self.env.H2Storage)}\n"
            for i, h2s in enumerate(self.env.H2Storage, 1):
                overview += f"  - H2Storage_{i}: {h2s.capacity:.1f} kg\n"
                
        if len(self.env.fuel_cell) > 0:
            overview += f"✓ Fuel Cell: {len(self.env.fuel_cell)}\n"
            for i, fc in enumerate(self.env.fuel_cell, 1):
                overview += f"  - FuelCell_{i}: {fc.p_n/1000:.1f} kW\n"
                
        if self.env.grid:
            overview += f"✓ Grid Connection: Yes\n"
            
        self.system_overview.delete('1.0', tk.END)
        self.system_overview.insert('1.0', overview)
        
    def run_simulation(self):
        """Run the energy system simulation"""
        if not self.env:
            messagebox.showwarning("Warning", "Please create the system first")
            return
            
        if not self.env.load:
            messagebox.showwarning("Warning", "Please add a load profile first")
            return
            
        # Run in thread to not freeze UI
        def simulation_thread():
            try:
                self.progress_var.set("Running dispatch...")
                self.progress.start()
                self.sim_button.config(state='disabled')
                
                # Run operator
                self.operator = Operator(env=self.env)
                
                self.progress_var.set("Calculating evaluation metrics...")
                
                # Run evaluation
                self.evaluation = Evaluation(env=self.env, operator=self.operator)
                
                self.progress.stop()
                self.progress_var.set("Simulation completed!")
                self.sim_button.config(state='normal')
                
                # Show results
                self.display_results()
                
                # Switch to results tab
                self.notebook.select(6)
                
            except Exception as e:
                self.progress.stop()
                self.progress_var.set("Simulation failed")
                self.sim_button.config(state='normal')
                messagebox.showerror("Error", f"Simulation failed:\n{str(e)}")
                
        threading.Thread(target=simulation_thread, daemon=True).start()
        
    def display_results(self):
        """Display simulation results"""
        if not self.evaluation:
            return
            
        results = "=== SIMULATION RESULTS ===\n\n"
        
        # Economic results
        results += "=== ECONOMIC ANALYSIS ===\n"
        if hasattr(self.evaluation, 'lcoe'):
            results += f"LCOE: ${self.evaluation.lcoe:.4f} /kWh\n"
        if hasattr(self.evaluation, 'npc'):
            results += f"Net Present Cost: ${self.evaluation.npc:,.2f}\n"
        if hasattr(self.evaluation, 'total_investment'):
            results += f"Total Investment: ${self.evaluation.total_investment:,.2f}\n\n"
            
        # Energy flows
        results += "=== ENERGY FLOWS ===\n"
        if hasattr(self.evaluation, 'total_load'):
            results += f"Total Load: {self.evaluation.total_load:,.2f} kWh\n"
        if hasattr(self.evaluation, 'total_pv'):
            results += f"Total PV Generation: {self.evaluation.total_pv:,.2f} kWh\n"
        if hasattr(self.evaluation, 're_fraction'):
            results += f"Renewable Fraction: {self.evaluation.re_fraction:.2%}\n\n"
            
        # Hydrogen system
        if len(self.env.electrolyser) > 0:
            results += "=== HYDROGEN SYSTEM ===\n"
            if hasattr(self.evaluation, 'total_h2_produced'):
                results += f"Total H2 Produced: {self.evaluation.total_h2_produced:.2f} kg\n"
            if hasattr(self.evaluation, 'total_h2_consumed'):
                results += f"Total H2 Consumed: {self.evaluation.total_h2_consumed:.2f} kg\n\n"
                
        # Environmental
        results += "=== ENVIRONMENTAL IMPACT ===\n"
        if hasattr(self.evaluation, 'total_co2'):
            results += f"Total CO2 Emissions: {self.evaluation.total_co2:,.2f} kg\n"
        if hasattr(self.evaluation, 'co2_avoided'):
            results += f"CO2 Avoided: {self.evaluation.co2_avoided:,.2f} kg\n"
            
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert('1.0', results)
        
    def export_results(self):
        """Export results to Excel"""
        if not self.operator:
            messagebox.showwarning("Warning", "No simulation results to export")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if filename:
                # Export operator dataframe
                self.operator.df.to_excel(filename)
                messagebox.showinfo("Success", f"Results exported to:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")
            
    def show_plots(self):
        """Show result plots"""
        if not self.operator:
            messagebox.showwarning("Warning", "No simulation results to plot")
            return
            
        try:
            # This would call plotting functions from operation.py
            messagebox.showinfo("Info", "Plotting functionality coming soon!\nFor now, use the export feature and plot in Excel/Python.")
        except Exception as e:
            messagebox.showerror("Error", f"Plotting failed:\n{str(e)}")


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')  # Use a modern theme
    
    # Configure custom button style
    style.configure('Accent.TButton', font=('Calibri', 10, 'bold'))
    
    app = MiGUELApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
