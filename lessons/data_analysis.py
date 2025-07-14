"""
data_analysis - Data Analysis Lesson
A lesson that uses Python data science tools for interactive learning
"""

# Import data science libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import json
import time

# Lesson configuration
LESSON_NAME = "Data Analysis with Gestures"
DATA_POINTS = 100
ANALYSIS_TYPES = ["descriptive", "correlation", "distribution", "trends"]

# Generate sample data
np.random.seed(42)  # For reproducible results
data = np.random.normal(0, 1, DATA_POINTS)
df = pd.DataFrame({
    'values': data,
    'squared': data ** 2,
    'cubed': data ** 3,
    'absolute': np.abs(data)
})

# Lesson state
analyses_performed = 0
current_analysis = None
analysis_results = {}

@on_start
def lesson_start():
    """Called when the lesson starts"""
    global analyses_performed, current_analysis, analysis_results
    
    log("INFO", f"Starting data analysis lesson: {LESSON_NAME}")
    log("INFO", f"Dataset size: {DATA_POINTS} points")
    
    # Reset state
    analyses_performed = 0
    current_analysis = None
    analysis_results = {}
    
    # Calculate basic statistics
    basic_stats = {
        "mean": float(df['values'].mean()),
        "std": float(df['values'].std()),
        "min": float(df['values'].min()),
        "max": float(df['values'].max()),
        "median": float(df['values'].median()),
        "skewness": float(df['values'].skew()),
        "kurtosis": float(df['values'].kurtosis())
    }
    
    # Update lesson state
    state.set("lesson_name", LESSON_NAME)
    state.set("data_points", DATA_POINTS)
    state.set("analyses_performed", analyses_performed)
    state.set("current_analysis", current_analysis)
    state.set("analysis_results", analysis_results)
    state.set("basic_stats", basic_stats)
    state.set("start_time", time.time())
    
    emit("lesson_started", {
        "lesson_name": LESSON_NAME,
        "data_points": DATA_POINTS,
        "analysis_types": ANALYSIS_TYPES,
        "basic_statistics": basic_stats
    })

@on_gesture
def handle_gesture(gesture_data):
    """Called when a gesture is detected"""
    global analyses_performed, current_analysis, analysis_results
    
    gesture = gesture_data.get("gesture")
    
    if not gesture:
        return
    
    log("INFO", f"Processing gesture: {gesture}")
    
    # Different gestures trigger different analyses
    if gesture == "fist":
        # Descriptive statistics analysis
        current_analysis = "descriptive"
        analyses_performed += 1
        
        # Calculate percentiles
        percentiles = [25, 50, 75, 90, 95]
        percentile_values = [float(df['values'].quantile(p/100)) for p in percentiles]
        
        # Calculate quartiles and IQR
        q1, q3 = float(df['values'].quantile(0.25)), float(df['values'].quantile(0.75))
        iqr = q3 - q1
        
        analysis_results["descriptive"] = {
            "percentiles": dict(zip(percentiles, percentile_values)),
            "quartiles": {"Q1": q1, "Q3": q3, "IQR": iqr},
            "outliers": len(df[df['values'] > q3 + 1.5*iqr]) + len(df[df['values'] < q1 - 1.5*iqr])
        }
        
        state.set("analyses_performed", analyses_performed)
        state.set("current_analysis", current_analysis)
        state.set("analysis_results", analysis_results)
        
        emit("analysis_complete", {
            "type": "descriptive",
            "results": analysis_results["descriptive"]
        })
    
    elif gesture == "open_hand":
        # Correlation analysis
        current_analysis = "correlation"
        analyses_performed += 1
        
        # Calculate correlations between all columns
        corr_matrix = df.corr()
        correlations = {}
        
        for col1 in df.columns:
            for col2 in df.columns:
                if col1 != col2:
                    correlations[f"{col1}_vs_{col2}"] = float(corr_matrix.loc[col1, col2])
        
        # Find strongest correlations
        corr_pairs = [(k, v) for k, v in correlations.items()]
        corr_pairs.sort(key=lambda x: abs(x[1]), reverse=True)
        strongest_correlations = corr_pairs[:3]
        
        analysis_results["correlation"] = {
            "all_correlations": correlations,
            "strongest_correlations": strongest_correlations,
            "mean_correlation": float(corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean())
        }
        
        state.set("analyses_performed", analyses_performed)
        state.set("current_analysis", current_analysis)
        state.set("analysis_results", analysis_results)
        
        emit("analysis_complete", {
            "type": "correlation",
            "results": analysis_results["correlation"]
        })
    
    elif gesture == "point":
        # Distribution analysis
        current_analysis = "distribution"
        analyses_performed += 1
        
        # Generate histogram data
        hist, bins = np.histogram(df['values'], bins=10)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        # Calculate distribution statistics
        skewness = float(df['values'].skew())
        kurtosis = float(df['values'].kurtosis())
        
        # Check for normality (simplified)
        is_normal = abs(skewness) < 0.5 and abs(kurtosis) < 1.0
        
        analysis_results["distribution"] = {
            "histogram": {
                "counts": hist.tolist(),
                "bin_centers": bin_centers.tolist(),
                "bins": bins.tolist()
            },
            "skewness": skewness,
            "kurtosis": kurtosis,
            "is_normal_like": is_normal,
            "unique_values": int(df['values'].nunique())
        }
        
        state.set("analyses_performed", analyses_performed)
        state.set("current_analysis", current_analysis)
        state.set("analysis_results", analysis_results)
        
        emit("analysis_complete", {
            "type": "distribution",
            "results": analysis_results["distribution"]
        })
    
    elif gesture == "victory":
        # Trend analysis
        current_analysis = "trends"
        analyses_performed += 1
        
        # Calculate moving averages
        window_sizes = [5, 10, 20]
        moving_averages = {}
        
        for window in window_sizes:
            if len(df) >= window:
                ma = df['values'].rolling(window=window).mean()
                moving_averages[f"ma_{window}"] = ma.dropna().tolist()
        
        # Calculate trend direction
        first_quarter = df['values'].iloc[:len(df)//4].mean()
        last_quarter = df['values'].iloc[-len(df)//4:].mean()
        trend_direction = "increasing" if last_quarter > first_quarter else "decreasing"
        trend_strength = abs(last_quarter - first_quarter)
        
        analysis_results["trends"] = {
            "moving_averages": moving_averages,
            "trend_direction": trend_direction,
            "trend_strength": float(trend_strength),
            "first_quarter_mean": float(first_quarter),
            "last_quarter_mean": float(last_quarter)
        }
        
        state.set("analyses_performed", analyses_performed)
        state.set("current_analysis", current_analysis)
        state.set("analysis_results", analysis_results)
        
        emit("analysis_complete", {
            "type": "trends",
            "results": analysis_results["trends"]
        })
    
    elif gesture == "thumbs_up":
        # Summary analysis
        current_analysis = "summary"
        analyses_performed += 1
        
        # Create comprehensive summary
        summary = {
            "data_overview": {
                "total_points": len(df),
                "columns": list(df.columns),
                "memory_usage": df.memory_usage(deep=True).sum(),
                "missing_values": df.isnull().sum().to_dict()
            },
            "statistical_summary": {
                "descriptive": analysis_results.get("descriptive", {}),
                "correlation": analysis_results.get("correlation", {}),
                "distribution": analysis_results.get("distribution", {}),
                "trends": analysis_results.get("trends", {})
            },
            "insights": []
        }
        
        # Generate insights
        if "descriptive" in analysis_results:
            desc = analysis_results["descriptive"]
            if desc.get("outliers", 0) > 0:
                summary["insights"].append(f"Found {desc['outliers']} outliers in the data")
        
        if "correlation" in analysis_results:
            corr = analysis_results["correlation"]
            strongest = corr.get("strongest_correlations", [])
            if strongest:
                strongest_pair = strongest[0]
                summary["insights"].append(f"Strongest correlation: {strongest_pair[0]} ({strongest_pair[1]:.3f})")
        
        if "distribution" in analysis_results:
            dist = analysis_results["distribution"]
            if dist.get("is_normal_like"):
                summary["insights"].append("Data appears to follow a normal distribution")
            else:
                summary["insights"].append("Data shows non-normal distribution characteristics")
        
        analysis_results["summary"] = summary
        
        state.set("analyses_performed", analyses_performed)
        state.set("current_analysis", current_analysis)
        state.set("analysis_results", analysis_results)
        
        emit("analysis_complete", {
            "type": "summary",
            "results": analysis_results["summary"]
        })
    
    # Update progress
    progress = min(100.0, analyses_performed * 25.0)  # 4 analyses = 100%
    
    # Update state
    state.set("current_gesture", gesture)
    state.set("lesson_progress", progress)
    
    # Emit gesture event
    emit("gesture_processed", {
        "gesture": gesture,
        "current_analysis": current_analysis,
        "analyses_performed": analyses_performed,
        "progress": progress
    })
    
    # Check if lesson is complete
    if progress >= 100.0:
        log("INFO", "Data analysis lesson completed!")
        emit("lesson_completed", {
            "final_progress": progress,
            "total_analyses": analyses_performed,
            "analysis_results": analysis_results
        })

@on_tick
def lesson_tick():
    """Called periodically during the lesson"""
    # Update lesson duration
    start_time = state.get("start_time")
    if start_time:
        duration = time.time() - start_time
        state.set("lesson_duration", duration)
    
    # Calculate analysis efficiency
    analyses_performed = state.get("analyses_performed", 0)
    duration = state.get("lesson_duration", 0)
    
    if duration > 0:
        analysis_rate = analyses_performed / duration
        state.set("analysis_rate", analysis_rate)
    
    # Emit periodic update
    emit("lesson_tick", {
        "analyses_performed": analyses_performed,
        "progress": state.get("lesson_progress", 0),
        "current_analysis": state.get("current_analysis"),
        "lesson_duration": duration,
        "analysis_rate": state.get("analysis_rate", 0)
    })

@on_complete
def lesson_complete():
    """Called when the lesson is completed"""
    log("INFO", "Data analysis lesson cleanup and final report")
    
    # Generate final report
    analysis_results = state.get("analysis_results", {})
    basic_stats = state.get("basic_stats", {})
    
    final_report = {
        "lesson_summary": {
            "total_analyses": len(analysis_results),
            "data_points": DATA_POINTS,
            "analysis_types": list(analysis_results.keys()),
            "duration": state.get("lesson_duration", 0)
        },
        "statistical_summary": basic_stats,
        "analysis_results": analysis_results,
        "insights": []
    }
    
    # Generate insights
    if "descriptive" in analysis_results:
        desc = analysis_results["descriptive"]
        final_report["insights"].append(f"Data range: {basic_stats['min']:.3f} to {basic_stats['max']:.3f}")
        final_report["insights"].append(f"Standard deviation: {basic_stats['std']:.3f}")
    
    if "correlation" in analysis_results:
        corr = analysis_results["correlation"]
        strongest = corr.get("strongest_correlations", [])
        if strongest:
            final_report["insights"].append(f"Strongest correlation: {strongest[0][0]} ({strongest[0][1]:.3f})")
    
    if "distribution" in analysis_results:
        dist = analysis_results["distribution"]
        if dist.get("is_normal_like"):
            final_report["insights"].append("Data follows normal distribution")
        else:
            final_report["insights"].append("Data shows non-normal characteristics")
    
    log("INFO", f"Final report generated with {len(final_report['insights'])} insights")
    emit("lesson_report", final_report) 