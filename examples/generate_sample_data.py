"""Generate synthetic datasets for testing causal discovery."""

import numpy as np
import pandas as pd
import os


def generate_health_data(n_samples: int = 500, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic health dataset with known causal structure.
    
    Causal Structure:
        Smoking → Blood_Pressure
        Smoking → Diabetes
        Exercise → BMI
        Exercise → Blood_Pressure
        BMI → Diabetes
        BMI → Blood_Pressure
    
    Args:
        n_samples: Number of samples to generate
        seed: Random seed for reproducibility
        
    Returns:
        DataFrame with synthetic health data
    """
    np.random.seed(seed)
    
    # Root causes (exogenous variables)
    smoking = np.random.poisson(10, n_samples)  # Cigarettes per day
    exercise = np.random.gamma(3, 2, n_samples)  # Hours per week
    
    # Intermediate variables
    bmi = (
        22 +  # Base BMI
        0.1 * smoking +  # Smoking slightly increases BMI
        -0.8 * exercise +  # Exercise decreases BMI
        np.random.normal(0, 2, n_samples)  # Noise
    )
    bmi = np.clip(bmi, 15, 40)  # Realistic range
    
    # Outcome variables
    blood_pressure = (
        110 +  # Base blood pressure
        0.5 * smoking +  # Smoking increases BP
        -0.3 * exercise +  # Exercise decreases BP
        1.5 * (bmi - 22) +  # BMI affects BP
        np.random.normal(0, 5, n_samples)
    )
    blood_pressure = np.clip(blood_pressure, 80, 180)
    
    # Binary outcome (diabetes)
    diabetes_logit = (
        -5 +  # Base rate
        0.05 * smoking +  # Smoking increases risk
        0.15 * (bmi - 22) +  # BMI strongly increases risk
        np.random.normal(0, 0.5, n_samples)
    )
    diabetes_prob = 1 / (1 + np.exp(-diabetes_logit))
    diabetes = (np.random.random(n_samples) < diabetes_prob).astype(int)
    
    return pd.DataFrame({
        'Smoking': smoking,
        'Exercise': exercise,
        'BMI': bmi,
        'Blood_Pressure': blood_pressure,
        'Diabetes': diabetes
    })


def generate_economic_data(n_samples: int = 500, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic economic dataset.
    
    Causal Structure:
        Education → Income
        Education → Job_Satisfaction
        Income → Savings
        Income → Job_Satisfaction
        Age → Income
        Age → Savings
    
    Args:
        n_samples: Number of samples
        seed: Random seed
        
    Returns:
        DataFrame with synthetic economic data
    """
    np.random.seed(seed)
    
    # Root causes
    education = np.random.normal(14, 3, n_samples)  # Years of education
    education = np.clip(education, 8, 22)
    
    age = np.random.normal(40, 12, n_samples)
    age = np.clip(age, 22, 70)
    
    # Derived variables
    income = (
        20000 +
        3000 * education +
        500 * age +
        np.random.normal(0, 5000, n_samples)
    )
    income = np.clip(income, 20000, 150000)
    
    savings = (
        1000 +
        0.15 * income +
        200 * age +
        np.random.normal(0, 5000, n_samples)
    )
    savings = np.clip(savings, 0, 100000)
    
    job_satisfaction = (
        3 +
        0.15 * education +
        0.00003 * income +
        np.random.normal(0, 1, n_samples)
    )
    job_satisfaction = np.clip(job_satisfaction, 1, 10)
    
    return pd.DataFrame({
        'Education': education,
        'Age': age,
        'Income': income,
        'Savings': savings,
        'Job_Satisfaction': job_satisfaction
    })


def generate_climate_data(n_samples: int = 500, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic climate dataset.
    
    Causal Structure:
        CO2_Emissions → Temperature
        Temperature → Sea_Level
        Temperature → Extreme_Weather
        Deforestation → CO2_Emissions
        Deforestation → Biodiversity_Loss
    
    Args:
        n_samples: Number of samples
        seed: Random seed
        
    Returns:
        DataFrame with synthetic climate data
    """
    np.random.seed(seed)
    
    # Root causes
    deforestation = np.random.gamma(2, 10, n_samples)  # Million hectares per year
    
    # Derived variables
    co2_emissions = (
        350 +
        5 * deforestation +
        np.random.normal(0, 20, n_samples)
    )
    
    temperature = (
        14 +  # Base global temp (°C)
        0.01 * co2_emissions +
        np.random.normal(0, 0.3, n_samples)
    )
    
    sea_level = (
        0 +  # Baseline
        2 * (temperature - 14) +
        np.random.normal(0, 0.5, n_samples)
    )
    
    extreme_weather = (
        10 +  # Base events per year
        15 * (temperature - 14) +
        np.random.poisson(5, n_samples)
    )
    
    biodiversity_loss = (
        100 +  # Species per year
        8 * deforestation +
        np.random.poisson(10, n_samples)
    )
    
    return pd.DataFrame({
        'Deforestation': deforestation,
        'CO2_Emissions': co2_emissions,
        'Temperature': temperature,
        'Sea_Level': sea_level,
        'Extreme_Weather': extreme_weather,
        'Biodiversity_Loss': biodiversity_loss
    })


def main():
    """Generate and save all synthetic datasets."""
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    print("Generating synthetic datasets...")
    
    # Generate datasets
    health_data = generate_health_data()
    economic_data = generate_economic_data()
    climate_data = generate_climate_data()
    
    # Save to CSV
    health_data.to_csv('data/health_data.csv', index=False)
    print(f"✓ Saved health_data.csv ({len(health_data)} samples)")
    
    economic_data.to_csv('data/economic_data.csv', index=False)
    print(f"✓ Saved economic_data.csv ({len(economic_data)} samples)")
    
    climate_data.to_csv('data/climate_data.csv', index=False)
    print(f"✓ Saved climate_data.csv ({len(climate_data)} samples)")
    
    print("\nDataset summaries:")
    print("\nHealth Data:")
    print(health_data.describe())
    
    print("\nEconomic Data:")
    print(economic_data.describe())
    
    print("\nClimate Data:")
    print(climate_data.describe())


if __name__ == "__main__":
    main()

