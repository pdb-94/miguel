# MiGUEL Modern GUI - Quick Start

## 🎯 What's New

Your updated MiGUEL tool now has a **brand new modern GUI** that supports all the latest features, including:

- ✅ **Hydrogen Components**: Electrolyser, H2 Storage, Fuel Cell
- ✅ **Traditional Components**: PV, Battery Storage, Load, Grid
- ✅ **Simple Interface**: Easy-to-use tab-based design
- ✅ **No Heavy Dependencies**: Uses built-in tkinter (comes with Python)

## 🚀 Quick Start

### Option 1: Use the GUI (Recommended)

1. **Launch the GUI:**
   ```bash
   python launch_gui.py
   ```

2. **Follow the tabs in order:**
   - Tab 1: System Setup (location, time period, economics)
   - Tab 2: Load Profile (energy consumption)
   - Tab 3: Solar PV (optional)
   - Tab 4: Battery Storage (optional)
   - Tab 5: Hydrogen System (optional - Electrolyser, H2 Storage, Fuel Cell)
   - Tab 6: Run Simulation
   - Tab 7: View Results

### Option 2: Run Example Code

```bash
python gui_example.py
```

Choose:
- **1**: Simple example (PV + Battery)
- **2**: Hydrogen example (PV + Battery + H2 system)
- **3**: Run both

### Option 3: Use Python API Directly

```python
from environment import Environment
from operation import Operator
from evaluation import Evaluation
from datetime import datetime, timedelta

# See gui_example.py for complete working examples
```

## 📋 GUI Workflow

### Step-by-Step Guide

#### 1️⃣ System Setup (Tab 1)

Fill in basic information:
- **Project Name**: "My Energy System"
- **Location**: Latitude (e.g., 52.52), Longitude (e.g., 13.40)
- **Time Period**: Start date, End date, Time step (15/30/60 minutes)
- **Economics**: Discount rate (0.05), Lifetime (20 years), Electricity price ($/kWh)
- **Grid**: Check if grid-connected

Click **"Create System"** ✅

#### 2️⃣ Load Profile (Tab 2)

Choose one method:

**Method A - Annual Consumption + Reference:**
- Annual Consumption: 50000 (kWh)
- Reference Profile: H0 (residential), G0 (commercial), hospital_ghana, etc.

**Method B - Custom CSV File:**
- Browse to your load profile CSV file

Click **"Add Load Profile"** ✅

#### 3️⃣ Solar PV (Tab 3) - Optional

- Nominal Power: 100 (kW)
- Tilt Angle: 30 (degrees)
- Azimuth: 180 (degrees, south-facing)
- Investment Cost: 100000 ($)
- O&M Cost: 2000 ($/year)

Click **"Add PV System"** ✅

You can add multiple PV systems!

#### 4️⃣ Battery Storage (Tab 4) - Optional

- Power Rating: 50 (kW)
- Capacity: 200 (kWh)
- Initial SOC: 0.5 (50%)
- Investment Cost: 80000 ($)
- O&M Cost: 1600 ($/year)

Click **"Add Battery Storage"** ✅

#### 5️⃣ Hydrogen System (Tab 5) - Optional but POWERFUL! 💪

**Electrolyser** (converts excess power to hydrogen):
- Nominal Power: 50 (kW)
- Investment Cost: 100000 ($)
- O&M Cost: 2000 ($/year)
- Click **"Add Electrolyser"**

**H2 Storage** (stores hydrogen):
- Capacity: 100 (kg)
- Initial Level: 0.1 (10%)
- Investment Cost: 50000 ($)
- Click **"Add H2 Storage"**

**Fuel Cell** (converts hydrogen back to power):
- Nominal Power: 30 (kW)
- Investment Cost: 90000 ($)
- O&M Cost: 1800 ($/year)
- Click **"Add Fuel Cell"**

#### 6️⃣ Run Simulation (Tab 6)

1. Click **"📋 Update Overview"** to review your system
2. Check all components are listed
3. Click **"▶ Run Simulation"**
4. Wait for progress bar (may take 1-5 minutes depending on simulation length)
5. Results will appear automatically!

#### 7️⃣ Results (Tab 7)

View:
- **LCOE** (Levelized Cost of Energy)
- **Total Investment**
- **Energy Flows** (load, generation, renewable fraction)
- **Hydrogen Metrics** (H2 produced/consumed)
- **CO2 Emissions**

Export:
- Click **"📊 Export to Excel"** to save detailed timestep data

## 🔧 What Changed from Old GUI?

| Feature | Old GUI (PyQt5) | New GUI (tkinter) |
|---------|----------------|-------------------|
| **Hydrogen Support** | ❌ Not supported | ✅ Full support |
| **Dependencies** | PyQt5, many libs | ✅ Only tkinter (built-in) |
| **Diesel Generator** | ✅ GUI tab | ⚠️ Use API directly |
| **Wind Turbine** | ✅ GUI tab | ⚠️ Use API directly |
| **PV System** | ✅ Supported | ✅ Supported |
| **Battery** | ✅ Supported | ✅ Supported |
| **Load** | ✅ Supported | ✅ Supported |
| **Complexity** | High | ✅ Simple & clean |

## 💡 Tips & Tricks

### Quick Test Configuration
For fast testing:
- **Time period**: 1 month (instead of full year)
- **Time step**: 60 minutes (instead of 15)
- **Location**: Use default values (52.52, 13.40 - Berlin)

### Hydrogen System Benefits
The hydrogen system creates a **seasonal energy storage** capability:
1. ☀️ **Summer**: Excess PV → Electrolyser → H2 Storage
2. ❄️ **Winter**: H2 Storage → Fuel Cell → Electricity
3. 🎯 **Result**: Better renewable energy utilization!

### Recommended Component Sizes
For a **50,000 kWh/year** load (typical small commercial):
- PV: 100-150 kW
- Battery: 50 kW / 200 kWh
- Electrolyser: 50 kW
- H2 Storage: 100 kg
- Fuel Cell: 30 kW

### Grid vs Off-Grid
- **Grid-connected**: More flexible, cheaper LCOE
- **Off-grid**: Needs larger battery/H2 storage, higher costs, but fully independent!

## 🐛 Troubleshooting

### "Please create the system first"
→ Complete Tab 1 (System Setup) before adding components

### GUI doesn't open
→ tkinter is built-in with Python, but if missing:
```bash
# On Ubuntu/Debian:
sudo apt-get install python3-tk

# On macOS:
# tkinter comes with Python from python.org

# On Windows:
# tkinter is included by default
```

### Simulation is slow
→ Normal! A full year with 15-min timesteps = 35,040 timesteps
→ Try: 1 month + 60-min timestep for testing (~720 timesteps)

### Import errors
```bash
pip install -r requirements.txt
```

### pvlib/h5py errors
```bash
pip install --upgrade numpy==1.24.4
pip install --upgrade h5py==3.8.0
pip install --upgrade pvlib
```

## 📚 File Overview

| File | Purpose |
|------|---------|
| `modern_gui.py` | Main GUI application |
| `launch_gui.py` | Simple launcher script |
| `gui_example.py` | Working code examples (no GUI) |
| `GUI_README.md` | Detailed user guide |
| `QUICKSTART.md` | This file! |

## 🎓 Learning Path

1. **Beginner**: Use `gui_example.py` to see working code
2. **Intermediate**: Use `modern_gui.py` for interactive design
3. **Advanced**: Edit `environment.py`, `operation.py` directly

## 📞 Support

If you encounter issues:
1. ✅ Check console output for error messages
2. ✅ Try the examples in `gui_example.py`
3. ✅ Review `GUI_README.md` for detailed help
4. ✅ Check that all components are added (especially Load!)

## 🎉 Next Steps

Try this:
1. Launch GUI: `python launch_gui.py`
2. Create a simple system (PV + Load)
3. Run simulation
4. Export to Excel
5. **Add hydrogen components** and compare results!

---

**Happy simulating! 🚀⚡🔋**
