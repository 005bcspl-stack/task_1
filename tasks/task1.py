import pandas as pd
import os

def run_strategy(entry_time, exit_time, sl_ratio, log_tf, date=None):
    os.makedirs("output/task1", exist_ok=True)

    data = {
        "Time": ["09:30", "09:35", "09:40"],
        "Price": [100, 105, 102],
        "SL_Ratio": [sl_ratio]*3
    }

    df = pd.DataFrame(data)

    output_path = f"output/task1/{date}_task1.xlsx"
    df.to_excel(output_path, index=False)

    return output_path
