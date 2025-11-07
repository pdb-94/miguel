"""
Quick Start Example for MiGUEL Modern GUI
Demonstrates how to configure and run a simple energy system simulation
"""

from environment import Environment
from operation import Operator
from evaluation import Evaluation
from datetime import datetime, timedelta

def simple_example():
    """
    Simple example: Grid-connected PV system with battery storage
    """
    print("=" * 60)
    print("MiGUEL - Simple Example")
    print("=" * 60)
    
    # 1. Create Environment
    print("\n1. Creating environment...")
    
    time = {
        'start': datetime(2023, 1, 1),
        'end': datetime(2023, 1, 31),  # One month for quick test
        'step': timedelta(minutes=60),
        'timezone': 'UTC'
    }
    
    location = {
        'latitude': 52.52,
        'longitude': 13.40,
        'terrain': 'urban'
    }
    
    economy = {
        'd_rate': 0.05,
        'lifetime': 20,
        'electricity_price': 0.15,
        'currency': 'US$'
    }
    
    ecology = {
        'co2_grid': 0.5
    }
    
    env = Environment(
        name='Simple Example',
        time=time,
        location=location,
        economy=economy,
        ecology=ecology,
        grid_connection=True,
        feed_in=False
    )
    
    print(f"   ✓ Environment created: {env.name}")
    
    # 2. Add Load Profile
    print("\n2. Adding load profile...")
    env.add_load(annual_consumption=50000, ref_profile='H0')
    print(f"   ✓ Load added: 50,000 kWh/year")
    
    # 3. Add PV System
    print("\n3. Adding PV system...")
    pv_data = {
        'surface_tilt': 30,
        'surface_azimuth': 180
    }
    env.add_pv(p_n=100000, pv_data=pv_data, c_invest=100000, c_op_main=2000)
    print(f"   ✓ PV system added: 100 kW")
    
    # 4. Add Battery Storage
    print("\n4. Adding battery storage...")
    env.add_storage(p_n=50000, c=200000, soc=0.5, c_invest=80000, c_op_main=1600)
    print(f"   ✓ Battery added: 50 kW / 200 kWh")
    
    # 5. Run Simulation
    print("\n5. Running dispatch simulation...")
    print("   (This may take a minute...)")
    operator = Operator(env=env)
    print(f"   ✓ Dispatch completed")
    
    # 6. Calculate Evaluation
    print("\n6. Calculating evaluation metrics...")
    evaluation = Evaluation(env=env, operator=operator)
    print(f"   ✓ Evaluation completed")
    
    # 7. Display Results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if hasattr(evaluation, 'lcoe'):
        print(f"\nLCOE: ${evaluation.lcoe:.4f} /kWh")
    
    if hasattr(evaluation, 'total_investment'):
        print(f"Total Investment: ${evaluation.total_investment:,.2f}")
    
    if hasattr(evaluation, 'total_load'):
        print(f"\nTotal Load: {evaluation.total_load:,.2f} kWh")
    
    if hasattr(evaluation, 'total_pv'):
        print(f"Total PV Generation: {evaluation.total_pv:,.2f} kWh")
    
    if hasattr(evaluation, 're_fraction'):
        print(f"Renewable Fraction: {evaluation.re_fraction:.2%}")
    
    # Export results
    print("\n7. Exporting results...")
    try:
        operator.df.to_excel('simple_example_results.xlsx')
        print("   ✓ Results exported to: simple_example_results.xlsx")
    except Exception as e:
        print(f"   ⚠ Export failed: {e}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    
    return env, operator, evaluation


def hydrogen_example():
    """
    Advanced example: PV + Battery + Hydrogen System (Electrolyser, H2 Storage, Fuel Cell)
    """
    print("=" * 60)
    print("MiGUEL - Hydrogen System Example")
    print("=" * 60)
    
    # 1. Create Environment
    print("\n1. Creating environment...")
    
    time = {
        'start': datetime(2023, 1, 1),
        'end': datetime(2023, 1, 31),
        'step': timedelta(minutes=60),
        'timezone': 'UTC'
    }
    
    location = {
        'latitude': 52.52,
        'longitude': 13.40,
        'terrain': 'urban'
    }
    
    economy = {
        'd_rate': 0.05,
        'lifetime': 20,
        'electricity_price': 0.15,
        'currency': 'US$'
    }
    
    ecology = {
        'co2_grid': 0.5
    }
    
    env = Environment(
        name='Hydrogen Example',
        time=time,
        location=location,
        economy=economy,
        ecology=ecology,
        grid_connection=True,
        feed_in=False
    )
    
    print(f"   ✓ Environment created: {env.name}")
    
    # 2. Add Components
    print("\n2. Adding components...")
    env.add_load(annual_consumption=50000, ref_profile='H0')
    print(f"   ✓ Load: 50,000 kWh/year")
    
    env.add_pv(p_n=150000, pv_data={'surface_tilt': 30, 'surface_azimuth': 180}, 
               c_invest=150000, c_op_main=3000)
    print(f"   ✓ PV: 150 kW")
    
    env.add_storage(p_n=50000, c=200000, soc=0.5, c_invest=80000, c_op_main=1600)
    print(f"   ✓ Battery: 50 kW / 200 kWh")
    
    # Hydrogen components
    env.add_electrolyser(p_n=50000, c_invest=100000, c_op_main=2000)
    print(f"   ✓ Electrolyser: 50 kW")
    
    env.add_H2_Storage(capacity=100, initial_level=0.1, c_invest=50000)
    print(f"   ✓ H2 Storage: 100 kg")
    
    env.add_fuel_cell(p_n=30000, c_invest=90000, c_op_main=1800)
    print(f"   ✓ Fuel Cell: 30 kW")
    
    # 3. Run Simulation
    print("\n3. Running dispatch simulation...")
    print("   (This may take a minute...)")
    operator = Operator(env=env)
    print(f"   ✓ Dispatch completed")
    
    # 4. Calculate Evaluation
    print("\n4. Calculating evaluation metrics...")
    evaluation = Evaluation(env=env, operator=operator)
    print(f"   ✓ Evaluation completed")
    
    # 5. Display Results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if hasattr(evaluation, 'lcoe'):
        print(f"\nLCOE: ${evaluation.lcoe:.4f} /kWh")
    
    if hasattr(evaluation, 'total_investment'):
        print(f"Total Investment: ${evaluation.total_investment:,.2f}")
    
    print(f"\n--- Energy Flows ---")
    if hasattr(evaluation, 'total_load'):
        print(f"Total Load: {evaluation.total_load:,.2f} kWh")
    if hasattr(evaluation, 'total_pv'):
        print(f"Total PV Generation: {evaluation.total_pv:,.2f} kWh")
    if hasattr(evaluation, 're_fraction'):
        print(f"Renewable Fraction: {evaluation.re_fraction:.2%}")
    
    print(f"\n--- Hydrogen System ---")
    if hasattr(evaluation, 'total_h2_produced'):
        print(f"H2 Produced: {evaluation.total_h2_produced:.2f} kg")
    if hasattr(evaluation, 'total_h2_consumed'):
        print(f"H2 Consumed: {evaluation.total_h2_consumed:.2f} kg")
    
    # Export
    print("\n5. Exporting results...")
    try:
        operator.df.to_excel('hydrogen_example_results.xlsx')
        print("   ✓ Results exported to: hydrogen_example_results.xlsx")
    except Exception as e:
        print(f"   ⚠ Export failed: {e}")
    
    print("\n" + "=" * 60)
    print("Hydrogen example completed successfully!")
    print("=" * 60)
    
    return env, operator, evaluation


if __name__ == "__main__":
    print("\nChoose example to run:")
    print("1. Simple Example (PV + Battery)")
    print("2. Hydrogen System Example (PV + Battery + H2)")
    print("3. Both")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        simple_example()
    elif choice == "2":
        hydrogen_example()
    elif choice == "3":
        simple_example()
        print("\n\n")
        hydrogen_example()
    else:
        print("Running simple example by default...")
        simple_example()
