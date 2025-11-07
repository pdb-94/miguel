# MiGUEL Modern GUI - User Guide

## Overview

The new Modern GUI provides an intuitive interface for configuring and simulating energy systems with MiGUEL, including support for the latest hydrogen components (Electrolyser, H2 Storage, Fuel Cell).

## Key Features

✅ **Modern Interface**: Clean, tab-based design using tkinter  
✅ **Hydrogen System Support**: Full support for electrolyser, H2 storage, and fuel cells  
✅ **All Traditional Components**: PV, Battery Storage, Grid, Load profiles  
✅ **Real-time Feedback**: Progress indicators and status updates  
✅ **Export Results**: Save simulation results to Excel  

## How to Use

### Starting the GUI

Run the launcher script:
```bash
python launch_gui.py
```

Or directly:
```bash
python modern_gui.py
```

### Workflow

#### Step 1: System Setup (Tab 1)
1. Enter your **Project Name**
2. Set **Location** (latitude, longitude, terrain type)
3. Define **Simulation Time Period** (start date, end date, time step)
4. Configure **Economic Parameters** (discount rate, lifetime, electricity price)
5. Choose **Grid Connection** options
6. Click **"Create System"** button

✅ This creates the Environment object and enables other tabs.

#### Step 2: Load Profile (Tab 2)
Choose one method:

**Method A - Annual Consumption:**
- Enter annual consumption in kWh
- Select a reference profile (H0, G0, hospital_ghana, etc.)
- Click "Add Load Profile"

**Method B - Custom Profile:**
- Select "Custom Load Profile (CSV)" radio button
- Browse to your CSV file
- Click "Add Load Profile"

#### Step 3: Solar PV (Tab 3)
1. Enter **Nominal Power** in kW
2. Set **Tilt Angle** and **Azimuth** (degrees)
3. Enter **Investment Cost** and **O&M Cost**
4. Click **"Add PV System"**

You can add multiple PV systems - each will appear in the list below.

#### Step 4: Battery Storage (Tab 4)
1. Enter **Power Rating** (kW) and **Capacity** (kWh)
2. Set **Initial State of Charge** (0-1)
3. Enter **Investment Cost** and **O&M Cost**
4. Click **"Add Battery Storage"**

#### Step 5: Hydrogen System (Tab 5)
This tab contains three sections:

**Electrolyser:**
- Set nominal power (kW)
- Enter investment and O&M costs
- Click "Add Electrolyser"

**H2 Storage:**
- Set capacity (kg)
- Set initial level (0-1)
- Enter investment cost
- Click "Add H2 Storage"

**Fuel Cell:**
- Set nominal power (kW)
- Enter investment and O&M costs
- Click "Add Fuel Cell"

#### Step 6: Run Simulation (Tab 6)
1. Click **"📋 Update Overview"** to review your system configuration
2. Click **"▶ Run Simulation"** to start the dispatch calculation
3. Watch the progress bar - simulation runs in background
4. Results will automatically display when complete

#### Step 7: Results (Tab 7)
View simulation results including:
- **Economic Analysis**: LCOE, Net Present Cost, Total Investment
- **Energy Flows**: Total load, PV generation, renewable fraction
- **Hydrogen System**: H2 produced and consumed
- **Environmental Impact**: CO2 emissions and avoided emissions

**Export Options:**
- Click **"📊 Export to Excel"** to save detailed results
- Click **"📈 Show Plots"** for visualization (future feature)

## Component Compatibility

### Supported Components
| Component | Tab | Status |
|-----------|-----|--------|
| Load Profile | 2 | ✅ Fully Supported |
| Solar PV | 3 | ✅ Fully Supported |
| Battery Storage | 4 | ✅ Fully Supported |
| Electrolyser | 5 | ✅ **NEW** - Hydrogen System |
| H2 Storage | 5 | ✅ **NEW** - Hydrogen System |
| Fuel Cell | 5 | ✅ **NEW** - Hydrogen System |
| Grid Connection | 1 | ✅ Configured in System Setup |

### Not Yet Implemented
- Wind Turbine (can be added manually via code)
- Diesel Generator (can be added manually via code)

## Tips & Tricks

### 💡 Quick Start
1. Create System → Add Load → Add PV → Run Simulation
2. This minimal setup will give you results immediately

### 💡 Hydrogen System
- Add components in order: Electrolyser → H2 Storage → Fuel Cell
- Electrolyser uses excess PV power to produce hydrogen
- H2 Storage stores produced hydrogen
- Fuel Cell converts stored hydrogen back to electricity

### 💡 Grid Connection
- **Grid Connected**: System can import/export to grid
- **Feed-in**: Enable if you want to sell excess power
- **Off-grid**: Uncheck "Grid Connected" for standalone systems

### 💡 Economic Analysis
- Higher discount rate → lower NPV
- Longer lifetime → better economics for high upfront costs
- Adjust electricity price to match your local market

## Troubleshooting

### "Please create the system first"
→ You need to complete Tab 1 (System Setup) before adding components

### "Failed to create environment"
→ Check your input values (dates, numbers must be valid)
→ Ensure latitude/longitude are realistic coordinates

### "No simulation results to export"
→ Run the simulation first (Tab 6)

### Simulation takes a long time
→ Normal for full-year simulations with 15-minute timesteps
→ Try shorter period or larger timestep for testing

### Import errors
→ Make sure you're in the correct Python environment
→ Run: `pip install -r requirements.txt`

## Advanced Usage

### Manual Component Addition
You can still use the Python API alongside the GUI:

```python
from modern_gui import MiGUELApp
import tkinter as tk

# Start GUI
root = tk.Tk()
app = MiGUELApp(root)

# Access the environment object after creating system in GUI
# app.env.add_wind_turbine(...)  # Add components programmatically

root.mainloop()
```

### Accessing Results Programmatically
After running simulation:
```python
# app.operator.df contains all timestep data
# app.evaluation contains summary metrics
```

## Comparison with Old GUI

| Feature | Old GUI (PyQt5) | New GUI (tkinter) |
|---------|----------------|-------------------|
| Dependencies | PyQt5, Many modules | Standard library (tkinter) |
| Hydrogen Support | ❌ No | ✅ Yes |
| Diesel Generator | ✅ Yes | ⚠️ Manual only |
| Wind Turbine | ✅ Yes | ⚠️ Manual only |
| Maintenance | High complexity | Simple & maintainable |
| Database Integration | Full pvlib/windpowerlib | Simplified |

## Future Enhancements

Planned features:
- [ ] Wind turbine tab integration
- [ ] Diesel generator tab integration
- [ ] Interactive plots within GUI
- [ ] Real-time parameter sensitivity analysis
- [ ] Save/Load project configurations
- [ ] Batch simulation support

## Support

For issues or questions:
1. Check this README
2. Review the console output for error messages
3. Check main.py for working code examples
4. Refer to MiGUEL documentation

## License

Same as MiGUEL project license.
