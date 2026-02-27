import json
from typing import Any, Dict, List
from langchain.tools import tool
import pandas as pd
from app.services.dataset_loader import dataset_loader

# Pre-load df so it's ready for tools
df = dataset_loader.load_dataset()

@tool
def python_analysis_tool(code: str) -> str:
    """Executes pandas python code against the Titanic dataframe 'df' and returns the string output of the last statement.
    Do not use print(). Just return the value. Example code: "df['Age'].mean()".
    """
    try:
        # Create a restricted local namespace
        local_vars = {"df": df}
        
        # We try to evaluate the expression directly. If it's a multi-line statement, we execute it.
        # But generally we want to return the result of the expression.
        try:
            result = eval(code.strip(), {"pd": pd}, local_vars)
            return str(result)
        except SyntaxError:
            # If it's not a simple expression, run it as a script and capture local vars
            # To get output from exec, we can wrap it or modify it cautiously.
            # But normally for this simple tool we expect one-liners. Let's provide basic exec.
            exec(code.strip(), {"pd": pd}, local_vars)
            # Find the last assigned variable or some default output
            keys_added = [k for k in local_vars.keys() if k != "df"]
            if keys_added:
                return str(local_vars[keys_added[-1]])
            return "Command executed successfully, no explicit return value."

    except Exception as e:
        return f"Error executing code: {e}"

@tool
def statistical_tool(column_name: str, metric: str) -> str:
    """Computes a specific statistical metric ('mean', 'median', 'mode', 'min', 'max', 'count', 'unique') on a specified column in the Titanic dataframe."""
    try:
        if column_name not in df.columns:
            return f"Error: Column {column_name} does not exist."
            
        col_data = df[column_name]
        
        if metric == 'mean':
            return str(col_data.mean())
        elif metric == 'median':
            return str(col_data.median())
        elif metric == 'mode':
            return str(col_data.mode()[0])
        elif metric == 'min':
            return str(col_data.min())
        elif metric == 'max':
            return str(col_data.max())
        elif metric == 'count':
            return str(col_data.count())
        elif metric == 'unique':
            return str(col_data.nunique())
        else:
            return f"Error: Unknown metric {metric}."
    except Exception as e:
        return f"Error computing {metric} for {column_name}: {e}"
        
@tool
def get_dataset_info(query: str = "shape") -> str:
    """Get basic information about the dataset. Allowed queries: 'shape', 'columns', 'dtypes', 'head'."""
    if query == 'shape':
        return str(df.shape)
    elif query == 'columns':
        return str(list(df.columns))
    elif query == 'dtypes':
        return str(df.dtypes.to_dict())
    elif query == 'head':
        return str(df.head().to_dict())
    return "Unknown query."

TOOLS = [python_analysis_tool, statistical_tool, get_dataset_info]
