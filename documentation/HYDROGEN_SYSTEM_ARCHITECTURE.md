# MiGUEL Hydrogen System Architecture

## Overview

This document describes the hydrogen system architecture implemented in MiGUEL, enabling seasonal energy storage through power-to-gas-to-power cycles.

## Component Overview

### Three-Component Hydrogen System

```
┌─────────────────────────────────────────────────────────────────┐
│                    HYDROGEN ENERGY CYCLE                        │
└─────────────────────────────────────────────────────────────────┘

  1. ELECTROLYSER          2. H2 STORAGE           3. FUEL CELL
  ┌──────────────┐        ┌──────────────┐       ┌──────────────┐
  │  Electrical  │        │   Hydrogen   │       │   Hydrogen   │
  │    Power     │  ───▶  │    Tank      │ ───▶  │  Electrical  │
  │      ↓       │        │              │       │    Power     │
  │   Water      │        │  Capacity:   │       │      ↑       │
  │   + Energy   │        │   XX kg H2   │       │  Fuel Cell   │
  │      ↓       │        │              │       │   Stack      │
  │  Hydrogen    │        │  SOC: XX%    │       │              │
  │   Output     │        │              │       │              │
  └──────────────┘        └──────────────┘       └──────────────┘
    50-500 kW                50-500 kg              30-300 kW
```

## Energy Flow Diagram

### Daily Cycle (Summer - High Solar)

```
Hour   00:00          06:00          12:00          18:00          24:00
       │              │              │              │              │
PV     │──────────────│████████████████████████████│──────────────│
Load   │████████████████████████████████████████████████████████████│
       │              │              │              │              │
Action │   Grid       │  PV→Load     │  PV→Load     │  Battery     │
       │  Import      │  +Battery    │  +Battery    │  Discharge   │
       │              │              │  +Electrolyser│              │
       │              │              │  ↓ H2 Storage│              │
```

### Daily Cycle (Winter - Low Solar)

```
Hour   00:00          06:00          12:00          18:00          24:00
       │              │              │              │              │
PV     │──────────────│████████│──────────────────│──────────────│
Load   │████████████████████████████████████████████████████████████│
       │              │              │              │              │
Action │   Grid       │  PV→Load     │  PV→Load     │  H2→FC→Load  │
       │  Import      │  +FC         │  +FC         │  +Grid       │
       │  +FC         │  ↑ H2 Storage│  ↑ H2 Storage│  ↑ H2 Storage│
```

### Seasonal Cycle

```
SUMMER (Jun-Aug)                    WINTER (Dec-Feb)
High PV Generation                  Low PV Generation

┌─────────────┐                     ┌─────────────┐
│   Excess    │                     │ H2 Storage  │
│   Solar     │                     │   (Full)    │
│   Energy    │                     │             │
└──────┬──────┘                     └──────┬──────┘
       │                                   │
       ▼                                   ▼
┌─────────────┐  H2 Production      ┌─────────────┐
│Electrolyser │ ──────────────────▶ │  Fuel Cell  │
│   Active    │    Stored as H2     │   Active    │
└─────────────┘                     └─────────────┘
       │                                   │
       ▼                                   ▼
┌─────────────┐                     ┌─────────────┐
│ H2 Storage  │                     │  Power to   │
│  Charging   │                     │    Load     │
│ (0% → 95%)  │                     │             │
└─────────────┘                     └─────────────┘
```

## Component Classes

### 1. Electrolyser Class

**File:** `components/electrolyser.py`

**Purpose:** Converts electrical energy to hydrogen through PEM electrolysis

**Key Attributes:**
- `p_n`: Nominal power (W)
- `p_min`: Minimum operating power (% of nominal)
- `efficiency_electrolyser`: Variable efficiency curve
- `df_electrolyser`: DataFrame tracking power, H2 production, LCOH

**Key Methods:**
- `electrolyser_operate()`: Calculate H2 production from input power
- `get_efficiency()`: Interpolate efficiency based on load
- `update()`: Update operating state for timestep

**Energy Conversion:**
```
Input:  Electrical Power (W)
Process: 2H2O + Electricity → 2H2 + O2
Output: Hydrogen (kg/h)

Efficiency: 50-70% (HHV basis)
H2 Output Rate: ~0.02 kg H2 per kWh electricity
```

### 2. H2 Storage Class

**File:** `components/H2_Storage.py`

**Purpose:** Store hydrogen in compressed form for later use

**Key Attributes:**
- `capacity`: Maximum storage (kg H2)
- `current_level`: Current H2 inventory (kg)
- `soc_min`, `soc_max`: Operating limits
- `df_H2Storage`: DataFrame tracking inflow, outflow, level, SOC

**Key Methods:**
- `charge()`: Add H2 from electrolyser
- `discharge()`: Remove H2 for fuel cell
- `update()`: Update storage level and SOC

**Storage Dynamics:**
```
State of Charge (SOC) = current_level / capacity

Constraints:
- SOC_min ≤ SOC ≤ SOC_max  (typically 0.01 to 0.95)
- Inflow rate: Limited by electrolyser capacity
- Outflow rate: Limited by fuel cell demand

Storage Type: Compressed H2 (350-700 bar)
```

### 3. Fuel Cell Class

**File:** `components/fuel_cell.py`

**Purpose:** Convert hydrogen to electrical power via PEM fuel cell

**Key Attributes:**
- `p_n`: Nominal electrical power output (W)
- `efficiency_curve`: Variable efficiency vs. load
- `df_fc`: DataFrame tracking power, H2 consumption, efficiency

**Key Methods:**
- `fc_operate()`: Generate power from H2 consumption
- `get_efficiency()`: Interpolate efficiency based on load
- `update()`: Update operating state

**Energy Conversion:**
```
Input:  Hydrogen (kg/h)
Process: 2H2 + O2 → 2H2O + Electricity + Heat
Output: Electrical Power (W)

Efficiency: 40-60% (electrical)
Power Output: ~33 kWh per kg H2 consumed
```

## Dispatch Priority

### With Hydrogen System

```
┌─────────────────────────────────────────────────────────────┐
│                    POWER DISPATCH LOGIC                      │
└─────────────────────────────────────────────────────────────┘

FOR EACH TIMESTEP:

1. Calculate Available Generation:
   ├─ PV Generation
   ├─ Wind Generation
   └─ Fuel Cell (if H2 available)

2. Calculate Power Balance:
   Power_Balance = Generation - Load

3. IF Power_Balance > 0 (EXCESS POWER):
   │
   ├─ Priority 1: Charge Battery (up to max SOC, max power)
   │
   ├─ Priority 2: Electrolyser Operation
   │   ├─ IF Excess > Electrolyser_Min_Power:
   │   │   ├─ Operate Electrolyser
   │   │   ├─ Produce H2
   │   │   └─ Store in H2 Storage (if SOC < max)
   │   │
   │   └─ ELSE: Skip electrolyser
   │
   └─ Priority 3: Grid Export (if feed_in enabled)

4. IF Power_Balance < 0 (DEFICIT):
   │
   ├─ Priority 1: Discharge Battery (down to min SOC)
   │
   ├─ Priority 2: Fuel Cell Operation
   │   ├─ IF H2_Storage SOC > min:
   │   │   ├─ Operate Fuel Cell
   │   │   ├─ Consume H2 from storage
   │   │   └─ Generate power
   │   │
   │   └─ ELSE: Skip fuel cell
   │
   ├─ Priority 3: Diesel Generator (if available)
   │
   └─ Priority 4: Grid Import (if connected)

5. Update All Component States:
   ├─ Battery SOC
   ├─ H2 Storage Level
   ├─ Component DataFrames
   └─ Cost Tracking
```

## Integration with MiGUEL Core

### Environment Class Integration

**Component Lists in Environment:**
```python
class Environment:
    def __init__(self):
        # Hydrogen components
        self.electrolyser = []      # List of Electrolyser objects
        self.H2Storage = []         # List of H2Storage objects
        self.fuel_cell = []         # List of FuelCell objects
        
        # Traditional components
        self.pv = []
        self.storage = []           # Battery storage
        self.grid = None
        self.load = None
```

**Add Component Methods:**
```python
env.add_electrolyser(p_n=50000, c_invest=100000, ...)
env.add_H2_Storage(capacity=100, initial_level=0.1, ...)
env.add_fuel_cell(p_n=30000, c_invest=90000, ...)
```

### Operator Class Integration

**Hydrogen Dispatch Methods:**
```python
class Operator:
    def dispatch(self):
        for timestep in time_series:
            # ... PV, Load, Battery dispatch ...
            
            # Electrolyser operation
            if excess_power > 0:
                self.electrolyser_operate(excess_power)
            
            # Fuel cell operation
            if power_deficit > 0:
                self.fuel_cell_operate(power_deficit)
            
            # Update H2 storage levels
            self.update_H2_storage()
```

### Evaluation Class Integration

**Hydrogen Metrics:**
```python
class Evaluation:
    def calculate_hydrogen_metrics(self):
        # Total H2 produced
        self.total_h2_produced = sum(electrolyser.df['H2_Production [kg]'])
        
        # Total H2 consumed
        self.total_h2_consumed = sum(fuel_cell.df['H2_Consumed [kg]'])
        
        # H2 storage efficiency
        self.h2_storage_efficiency = h2_consumed / h2_produced
        
        # Levelized Cost of Hydrogen (LCOH)
        self.lcoh = calculate_lcoh(electrolyser, h2_storage)
```

## Performance Characteristics

### Typical System Sizing

For a **50 MWh/year** load (e.g., small commercial building):

```
Component           | Size      | Purpose
--------------------|-----------|----------------------------------------
PV System           | 100-150 kW| Primary generation
Battery Storage     | 50 kW     | Daily storage (4-6 hours)
                    | 200 kWh   |
--------------------|-----------|----------------------------------------
Electrolyser        | 50 kW     | Convert excess PV to H2
H2 Storage          | 50-100 kg | Seasonal storage (weeks to months)
Fuel Cell           | 30 kW     | Re-electrification of stored H2
```

### Round-Trip Efficiency

```
Electricity → H2 → Electricity Round-Trip Efficiency:

Electrolyser Efficiency:     60%  (electrical to H2 HHV)
Storage Losses:              ~2%  (compression, leakage)
Fuel Cell Efficiency:        50%  (H2 to electrical)
──────────────────────────────────────────────────────
Total Round-Trip:            ~29% (0.60 × 0.98 × 0.50)

Note: Despite lower efficiency compared to batteries (85-95%),
hydrogen enables much longer storage duration (weeks/months vs hours/days)
```

### Cost Breakdown Example

```
Component           | Investment | Annual O&M | Lifetime | Notes
--------------------|------------|------------|----------|------------------
Electrolyser 50kW   | $92,730   | $927      | 20 years | $1854.6/kW
H2 Storage 100kg    | $53,494   | $0        | 25 years | $534.94/kg
Fuel Cell 30kW      | $90,000   | $900      | 10 years | $3000/kW (stack)
--------------------|------------|------------|----------|------------------
Total H2 System     | $236,224  | $1,827/yr |          | Decreasing rapidly
```

## Use Cases

### 1. Seasonal Energy Storage
**Problem:** Solar generation peaks in summer but consumption is constant
**Solution:** Store summer excess as H2, use in winter
**Benefit:** 30-50% increase in solar self-consumption

### 2. Off-Grid Systems
**Problem:** Battery-only systems need huge capacity for multi-day autonomy
**Solution:** Battery for daily cycles, H2 for weekly/seasonal backup
**Benefit:** Lower total storage cost, higher reliability

### 3. Grid Services
**Problem:** Need long-duration storage for grid stabilization
**Solution:** H2 system provides days-to-weeks storage
**Benefit:** Support high renewable grid penetration

### 4. Industrial Applications
**Problem:** Industrial site with high seasonal variation
**Solution:** Co-optimize electricity and H2 production
**Benefit:** Use H2 for both re-electrification and industrial processes

## Key Advantages of Hydrogen System

✅ **Long Duration:** Weeks to months of storage (vs hours for batteries)  
✅ **Seasonal Shifting:** Store summer solar for winter use  
✅ **Scalability:** Energy capacity scales independently from power  
✅ **Multi-Use:** H2 can be used for electricity, heat, fuel, industrial processes  
✅ **No Degradation:** H2 storage doesn't degrade over time like batteries  

## Limitations to Consider

⚠️ **Lower Efficiency:** ~29% round-trip (vs 85-95% for batteries)  
⚠️ **Higher Capital Cost:** Currently more expensive than batteries per kWh  
⚠️ **Complexity:** More components, more maintenance  
⚠️ **Safety:** H2 requires proper safety measures  
⚠️ **Technology Maturity:** Still evolving, costs decreasing but not as mature as batteries  

## Future Development

Planned enhancements for hydrogen system:
- [ ] Thermal integration (CHP from fuel cell waste heat)
- [ ] H2 demand modeling (industrial use cases)
- [ ] Multiple electrolyser/FC units with degradation tracking
- [ ] Optimization algorithms for component sizing
- [ ] Real-time cost tracking with dynamic electricity prices
- [ ] Safety analysis and compliance checking

---

**For more information:**
- Main README: Architecture overview
- `components/electrolyser.py`: Electrolyser implementation
- `components/H2_Storage.py`: H2 storage implementation  
- `components/fuel_cell.py`: Fuel cell implementation
- `operation.py`: Dispatch logic with H2 integration
