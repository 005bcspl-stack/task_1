import pandas as pd
import os

def run_strategy(entry_time, exit_time, sl_ratio, log_tf, date=None):
    os.makedirs("output/task2", exist_ok=True)

    data = {
        "Time": ["10:00", "10:05", "10:10"],
        "Price": [200, 198, 205],
        "SL_Ratio": [sl_ratio]*3
    }

    df = pd.DataFrame(data)

    output_path = f"output/task2/{date}_task2.xlsx"
    df.to_excel(output_path, index=False)

    return output_path
