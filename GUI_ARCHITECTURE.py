"""
MiGUEL Modern GUI - Architecture Overview
This file documents the GUI structure and data flow
"""

# ==============================================================================
# GUI ARCHITECTURE
# ==============================================================================

"""
┌─────────────────────────────────────────────────────────────────────┐
│                         MiGUEL Modern GUI                            │
│                    (modern_gui.py - Main Window)                     │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │      Notebook (Tabs)        │
                    └──────────────┬──────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
    ┌────▼─────┐             ┌────▼─────┐            ┌─────▼──────┐
    │  Tab 1:  │             │  Tab 2:  │            │   Tab 3:   │
    │  System  │             │   Load   │            │    PV      │
    │  Setup   │             │ Profile  │            │  System    │
    └──────────┘             └──────────┘            └────────────┘
         │                         │                         │
         │ Creates:                │ Adds to:                │ Adds to:
         ▼                         ▼                         ▼
    Environment ──────────────> Load ────────────────> PV Components
    
    
    ┌─────────────┬─────────────┬─────────────┬─────────────┐
    │   Tab 4:    │   Tab 5:    │   Tab 6:    │   Tab 7:    │
    │  Battery    │  Hydrogen   │    Run      │  Results    │
    │  Storage    │   System    │ Simulation  │   Display   │
    └─────────────┴─────────────┴─────────────┴─────────────┘
         │             │               │               │
         │             │               │               │
         ▼             ▼               ▼               ▼
    Storage      Electrolyser     Operator       Evaluation
    Components   H2 Storage       (dispatch)     (metrics)
                 Fuel Cell

"""

# ==============================================================================
# DATA FLOW
# ==============================================================================

"""
USER INPUT (GUI Tabs)
         │
         ▼
┌─────────────────────┐
│   Environment       │  ← Created in Tab 1
│   - Location        │
│   - Time            │
│   - Economics       │
│   - Grid settings   │
└──────┬──────────────┘
       │
       │ .add_load()          ← Tab 2
       │ .add_pv()            ← Tab 3
       │ .add_storage()       ← Tab 4
       │ .add_electrolyser()  ← Tab 5
       │ .add_H2_Storage()    ← Tab 5
       │ .add_fuel_cell()     ← Tab 5
       │
       ▼
┌─────────────────────┐
│  Environment with   │
│  all components     │
└──────┬──────────────┘
       │
       │ Run Simulation (Tab 6)
       ▼
┌─────────────────────┐
│    Operator         │  ← Runs dispatch algorithm
│    - Timestep loop  │
│    - Energy flows   │
│    - Component ops  │
└──────┬──────────────┘
       │
       │ Calculate metrics
       ▼
┌─────────────────────┐
│   Evaluation        │  ← Computes LCOE, emissions, etc.
│   - LCOE            │
│   - Costs           │
│   - Energy metrics  │
│   - H2 metrics      │
│   - CO2 emissions   │
└──────┬──────────────┘
       │
       │ Display (Tab 7)
       ▼
┌─────────────────────┐
│   Results Display   │
│   + Excel Export    │
└─────────────────────┘
"""

# ==============================================================================
# HYDROGEN SYSTEM ENERGY FLOW
# ==============================================================================

"""
POWER GENERATION:
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Solar PV   │      │     Grid     │      │  Fuel Cell   │
│              │      │              │      │  (H2 → e⁻)   │
└──────┬───────┘      └──────┬───────┘      └──────┬───────┘
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Power Balance   │
                    │   Distribution   │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌────────┐          ┌──────────┐        ┌──────────────┐
   │  Load  │          │ Battery  │        │ Electrolyser │
   │        │          │ Storage  │        │  (e⁻ → H2)   │
   └────────┘          └──────────┘        └──────┬───────┘
                                                   │
                                                   ▼
                                            ┌─────────────┐
                                            │ H2 Storage  │
                                            │             │
                                            └─────────────┘

TYPICAL DAILY CYCLE (Summer):
00:00-06:00: Grid → Load
06:00-10:00: PV → Load + Battery charging
10:00-14:00: PV → Load + Battery + Electrolyser → H2
14:00-18:00: PV → Load + Battery charging
18:00-24:00: Battery → Load + Grid → Load

TYPICAL DAILY CYCLE (Winter):
00:00-06:00: Grid → Load
06:00-10:00: PV (limited) + H2 Storage → Fuel Cell → Load
10:00-14:00: PV + Fuel Cell → Load
14:00-18:00: PV (limited) + Battery → Load
18:00-24:00: H2 Storage → Fuel Cell → Load + Grid → Load
"""

# ==============================================================================
# GUI CLASS STRUCTURE
# ==============================================================================

"""
MiGUELApp (main class)
│
├── __init__()              # Initialize GUI
│   └── setup_ui()          # Create all tabs
│
├── Tab Creation Methods:
│   ├── create_system_tab()       # Tab 1: System configuration
│   ├── create_load_tab()         # Tab 2: Load profile
│   ├── create_pv_tab()           # Tab 3: PV systems
│   ├── create_storage_tab()      # Tab 4: Battery storage
│   ├── create_hydrogen_tab()     # Tab 5: H2 components
│   ├── create_simulation_tab()   # Tab 6: Run simulation
│   └── create_results_tab()      # Tab 7: Display results
│
├── Component Addition Methods:
│   ├── create_environment()      # Create Environment object
│   ├── add_load()                # Add load profile
│   ├── add_pv()                  # Add PV system
│   ├── add_storage()             # Add battery
│   ├── add_electrolyser()        # Add electrolyser
│   ├── add_h2storage()           # Add H2 storage
│   └── add_fuelcell()            # Add fuel cell
│
├── Simulation Methods:
│   ├── run_simulation()          # Execute dispatch + evaluation
│   ├── update_system_overview()  # Show current configuration
│   └── display_results()         # Format and show results
│
└── Utility Methods:
    ├── toggle_load_method()      # Switch load input methods
    ├── browse_file()             # File picker dialog
    ├── update_status()           # Status bar updates
    └── export_results()          # Save to Excel

State Variables:
- self.env            : Environment object (None until created)
- self.operator       : Operator object (None until simulation)
- self.evaluation     : Evaluation object (None until simulation)
- self.components_added : List of added components (for tracking)
"""

# ==============================================================================
# KEY METHODS FLOW
# ==============================================================================

"""
1. USER CLICKS "Create System" (Tab 1)
   │
   ├─> create_environment()
   │   ├─> Parse GUI inputs (location, time, economics)
   │   ├─> Create time/location/economy dictionaries
   │   ├─> self.env = Environment(...)
   │   └─> Enable other tabs
   │
   └─> Status: Environment created ✓

2. USER ADDS COMPONENTS (Tabs 2-5)
   │
   ├─> add_load()
   │   └─> self.env.add_load(...)
   │
   ├─> add_pv()
   │   ├─> Parse GUI inputs
   │   ├─> self.env.add_pv(p_n=..., pv_data={...}, ...)
   │   └─> Update component list in GUI
   │
   ├─> add_storage()
   │   └─> self.env.add_storage(...)
   │
   ├─> add_electrolyser()
   │   └─> self.env.add_electrolyser(...)
   │
   ├─> add_h2storage()
   │   └─> self.env.add_H2_Storage(...)
   │
   └─> add_fuelcell()
       └─> self.env.add_fuel_cell(...)

3. USER RUNS SIMULATION (Tab 6)
   │
   ├─> update_system_overview()
   │   └─> Display all components in text widget
   │
   └─> run_simulation()
       ├─> Start progress bar
       ├─> Launch thread (don't freeze GUI)
       │   ├─> self.operator = Operator(env=self.env)  # Dispatch
       │   ├─> self.evaluation = Evaluation(...)       # Metrics
       │   └─> display_results()
       ├─> Stop progress bar
       └─> Switch to Results tab

4. USER VIEWS RESULTS (Tab 7)
   │
   ├─> display_results()
   │   ├─> Format LCOE, costs, energy flows
   │   ├─> Format H2 metrics (if applicable)
   │   ├─> Format CO2 emissions
   │   └─> Display in ScrolledText widget
   │
   └─> export_results()
       └─> self.operator.df.to_excel('results.xlsx')
"""

# ==============================================================================
# WIDGET HIERARCHY
# ==============================================================================

"""
Root (tk.Tk)
│
├─ Notebook (ttk.Notebook) [main tabs]
│  │
│  ├─ System Tab (ttk.Frame)
│  │  ├─ Project Info (ttk.LabelFrame)
│  │  │  └─ project_name (ttk.Entry)
│  │  ├─ Location (ttk.LabelFrame)
│  │  │  ├─ latitude (ttk.Entry)
│  │  │  ├─ longitude (ttk.Entry)
│  │  │  └─ terrain (ttk.Combobox)
│  │  ├─ Time (ttk.LabelFrame)
│  │  │  ├─ start_date (ttk.Entry)
│  │  │  ├─ end_date (ttk.Entry)
│  │  │  └─ timestep (ttk.Combobox)
│  │  ├─ Economics (ttk.LabelFrame)
│  │  └─ Create Button (ttk.Button)
│  │
│  ├─ Load Tab (ttk.Frame)
│  │  ├─ Method Selection (Radio buttons)
│  │  ├─ Annual Frame (ttk.LabelFrame)
│  │  ├─ Custom Frame (ttk.LabelFrame)
│  │  └─ Add Button (ttk.Button)
│  │
│  ├─ PV Tab (ttk.Frame)
│  │  ├─ Configuration (ttk.LabelFrame)
│  │  ├─ Economics (ttk.LabelFrame)
│  │  ├─ Add Button (ttk.Button)
│  │  └─ List (tk.Listbox)
│  │
│  ├─ Storage Tab (ttk.Frame)
│  │  └─ [Similar structure to PV Tab]
│  │
│  ├─ Hydrogen Tab (ttk.Frame)
│  │  ├─ Electrolyser Frame (ttk.LabelFrame)
│  │  ├─ H2 Storage Frame (ttk.LabelFrame)
│  │  ├─ Fuel Cell Frame (ttk.LabelFrame)
│  │  └─ Component List (tk.Listbox)
│  │
│  ├─ Simulation Tab (ttk.Frame)
│  │  ├─ Overview (scrolledtext.ScrolledText)
│  │  ├─ Run Button (ttk.Button)
│  │  └─ Progress Bar (ttk.Progressbar)
│  │
│  └─ Results Tab (ttk.Frame)
│     ├─ Results Display (scrolledtext.ScrolledText)
│     └─ Export Buttons (ttk.Button)
│
└─ Status Bar (tk.Label) [bottom]
"""

# ==============================================================================
# ERROR HANDLING
# ==============================================================================

"""
VALIDATION CHECKS:

1. Environment Creation:
   - Check: Latitude/longitude are valid floats
   - Check: Dates are parseable
   - Check: Timestep is valid
   - Action: Show error messagebox if invalid

2. Component Addition:
   - Check: Environment exists (self.env is not None)
   - Check: Numeric inputs are valid floats/ints
   - Action: Show warning if environment not created

3. Simulation:
   - Check: Environment exists
   - Check: Load profile added (required)
   - Action: Show warning if prerequisites missing

4. Export:
   - Check: Simulation has run (self.operator exists)
   - Action: Show warning if no results

Exception Handling:
- All user actions wrapped in try/except
- Exceptions show messagebox with error details
- Status bar updated with error state
"""

# ==============================================================================
# CUSTOMIZATION POINTS
# ==============================================================================

"""
EASY MODIFICATIONS:

1. Add New Component Type:
   - Create new tab with create_<component>_tab()
   - Add input widgets for parameters
   - Create add_<component>() method
   - Call self.env.add_<component>() with parameters

2. Change Default Values:
   - Find widget creation (e.g., ttk.Entry)
   - Modify .insert(0, "value") to desired default

3. Add More Metrics to Results:
   - Modify display_results()
   - Access self.evaluation.<metric>
   - Add to results string

4. Customize Layout:
   - Modify LabelFrame configurations
   - Adjust grid() or pack() parameters
   - Change padding/spacing values

5. Add Plots:
   - Import matplotlib.pyplot
   - Create Figure and Canvas
   - Embed in tab using tk.Canvas

ADVANCED MODIFICATIONS:

1. Save/Load Projects:
   - Serialize self.env to JSON
   - Recreate Environment from saved data

2. Batch Simulations:
   - Loop over parameter ranges
   - Run operator for each configuration
   - Collect results in DataFrame

3. Optimization:
   - Define objective function (minimize LCOE)
   - Use scipy.optimize
   - Vary component sizes

4. Real-time Plots:
   - After simulation, plot operator.df columns
   - Update plots in Results tab
"""

if __name__ == "__main__":
    print(__doc__)
    print("\nThis file documents the GUI architecture.")
    print("Run 'python modern_gui.py' to start the GUI application.")
