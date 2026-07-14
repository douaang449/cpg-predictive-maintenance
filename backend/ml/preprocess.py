import pandas as pd 

RENAME_MAP ={
    "Air temperature [K]": "ambient_temp_k",
    "Process temperature [K]": "motor_temp_k",
    "Rotational speed [rpm]": "shaft_rpm",
    "Torque [Nm]": "load_torque_nm",
    "Tool wear [min]": "operating_minutes",
    "Machine failure": "failure",
    "Type": "equipment_class",
    "Product ID": "asset_id",

}

FEATURES = ["ambient_temp_k","motor_temp_k", "shaft_rpm", "load_torque_nm", "operating_minutes"]

def load_and_clean(csv_path: str = "data/ai4i2020.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df = df.rename(columns=RENAME_MAP)
    keep = ["asset_id", "equipment_class"] + FEATURES + ["failure"]
    return df[keep].copy()    

if __name__ == "__main__":
    df = load_and_clean()
    print(df.head())
    print(f"\nTotal lignes : {len(df)}")
    print(f"Taux de panne : {df['failure'].mean():.2%}")
    print(f"\nRépartiton par equipment_class:\n{df['equipment_class'].value_counts()}")
    print(f"\nStatistique descriptives :\n {df[FEATURES].describe()}")

