import io
import base64
import logging
import traceback
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# Use non-interactive backend for server environments
matplotlib.use('Agg')

logger = logging.getLogger(__name__)

# Pre-import all safe modules we'll allow in chart code
_SAFE_MODULES = {
    'np': np,
    'numpy': np,
    'pd': pd,
    'pandas': pd,
    'plt': plt,
    'matplotlib': matplotlib,
}

def execute_chart_code(code: str, df: pd.DataFrame) -> tuple[str | None, str | None]:
    """
    Safely executes matplotlib Python code to generate a chart.
    Captures the resulting figure into a BytesIO buffer and returns it as a base64 string.

    Args:
        code: The Python code containing matplotlib commands.
        df: The pandas DataFrame for the code to operate on.

    Returns:
        Tuple of (base64_image_string or None, chart_type or None)
    """
    if not code or code.strip().lower() in ("null", "none", ""):
        return None, None

    # Security guard: block OS/system access attempts
    blocked = ['import os', 'import sys', 'import subprocess', 'import socket',
               '__class__', '__subclasses__', 'open(', 'exec(', 'eval(']
    for term in blocked:
        if term in code:
            logger.warning(f"Blocked suspicious term in chart code: {term}")
            return None, None

    # Remove plt.show() — we capture the figure ourselves
    code = code.replace("plt.show()", "").strip()

    # Clear any previous matplotlib state
    plt.clf()
    plt.close('all')

    # Execution namespace: real __builtins__ so matplotlib internals work,
    # plus all safe data/plotting libraries pre-imported
    exec_globals = {
        '__builtins__': __builtins__,   # full builtins so numpy/matplotlib internals work
        **_SAFE_MODULES,
    }
    exec_locals = {'df': df}

    try:
        logger.info("Executing generated chart code")
        exec(code, exec_globals, exec_locals)  # noqa: S102

        # Grab whatever figure is current (code may use plt or df.plot())
        fig = plt.gcf()

        # Detect chart type from axes contents
        chart_type: str = "chart"
        if fig.axes:
            ax = fig.axes[0]
            if ax.patches:
                # Count distinct x positions to distinguish bar from histogram
                xvals = [p.get_x() for p in ax.patches]
                chart_type = "histogram" if len(set(round(x, 6) for x in xvals)) > 10 else "bar"
            elif ax.lines:
                chart_type = "line"
            elif ax.collections:
                chart_type = "scatter"

        # Save to buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=120)
        buf.seek(0)
        base64_str = base64.b64encode(buf.read()).decode('utf-8')

        plt.close(fig)
        logger.info(f"Chart generated successfully, type={chart_type}, size={len(base64_str)} chars")
        return base64_str, chart_type

    except Exception as e:
        logger.error(f"Chart execution error: {e}")
        logger.error(traceback.format_exc())
        plt.close('all')
        return None, None
