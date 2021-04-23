import seaborn as sns
import pandas as pd
import plotly.express as pe
import ai

def export_to_ai(data_file):
    with open(data_file, "r") as f:
            open_file = json.load(f)
            dates = open_file.keys()
            values = open_file.values()
            new_dict = {"dates": dates, "values": values}
            df = pd.DataFrame(new_dict)
    visualize_df = ai.run_ai(df)
    return visualize_df

def visualize(df):
    df_vis = sns.load_dataset(df)
    graph = sns.lineplot(data = df_vis, x = "dates")

visualize_df = export_to_ai("backend/ai/Raspberry_data/temp_dataset_3.json")




#code