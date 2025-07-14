"""
data_analysis - Data Analysis Lesson
A lesson that demonstrates data analysis concepts using basic Python
"""

import json
import time
import random
import math
from collections import defaultdict

# Lesson configuration
LESSON_NAME = "Data Analysis with Gestures"
DATA_POINTS = 100
ANALYSIS_TYPES = ["descriptive", "correlation", "distribution", "trends"]

# Generate sample data using basic Python
random.seed(42)  # For reproducible results
data = [random.gauss(0, 1) for _ in range(DATA_POINTS)]

# Create simple data structure (like a basic DataFrame)
dataset = {
    'values': data,
    'squared': [x ** 2 for x in data],
    'cubed': [x ** 3 for x in data],
    'absolute': [abs(x) for x in data]
}

# Lesson state
analyses_performed = 0
current_analysis = None
analysis_results = {}

def calculate_mean(values):
    """Calculate mean of a list of values"""
    return sum(values) / len(values)

def calculate_std(values):
    """Calculate standard deviation of a list of values"""
    mean = calculate_mean(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance)

def calculate_percentile(values, percentile):
    """Calculate percentile of a list of values"""
    sorted_values = sorted(values)
    index = (percentile / 100) * (len(sorted_values) - 1)
    if index.is_integer():
        return sorted_values[int(index)]
    else:
        lower = sorted_values[int(index)]
        upper = sorted_values[int(index) + 1]
        return lower + (upper - lower) * (index - int(index))

def calculate_correlation(x_values, y_values):
    """Calculate correlation coefficient between two lists"""
    n = len(x_values)
    mean_x = calculate_mean(x_values)
    mean_y = calculate_mean(y_values)
    
    numerator = sum((x_values[i] - mean_x) * (y_values[i] - mean_y) for i in range(n))
    denominator_x = sum((x - mean_x) ** 2 for x in x_values)
    denominator_y = sum((y - mean_y) ** 2 for y in y_values)
    
    if denominator_x == 0 or denominator_y == 0:
        return 0
    
    return numerator / math.sqrt(denominator_x * denominator_y)

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
    values = dataset['values']
    basic_stats = {
        "mean": calculate_mean(values),
        "std": calculate_std(values),
        "min": min(values),
        "max": max(values),
        "median": calculate_percentile(values, 50),
        "count": len(values)
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
        
        values = dataset['values']
        
        # Calculate percentiles
        percentiles = [25, 50, 75, 90, 95]
        percentile_values = [calculate_percentile(values, p) for p in percentiles]
        
        # Calculate quartiles and IQR
        q1 = calculate_percentile(values, 25)
        q3 = calculate_percentile(values, 75)
        iqr = q3 - q1
        
        # Count outliers
        outliers = sum(1 for x in values if x > q3 + 1.5*iqr or x < q1 - 1.5*iqr)
        
        analysis_results["descriptive"] = {
            "percentiles": dict(zip(percentiles, percentile_values)),
            "quartiles": {"Q1": q1, "Q3": q3, "IQR": iqr},
            "outliers": outliers
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
        correlations = {}
        columns = list(dataset.keys())
        
        for i, col1 in enumerate(columns):
            for j, col2 in enumerate(columns):
                if i != j:
                    corr = calculate_correlation(dataset[col1], dataset[col2])
                    correlations[f"{col1}_vs_{col2}"] = corr
        
        # Find strongest correlations
        corr_pairs = [(k, v) for k, v in correlations.items()]
        corr_pairs.sort(key=lambda x: abs(x[1]), reverse=True)
        strongest_correlations = corr_pairs[:3]
        
        analysis_results["correlation"] = {
            "all_correlations": correlations,
            "strongest_correlations": strongest_correlations,
            "mean_correlation": calculate_mean(list(correlations.values()))
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
        
        values = dataset['values']
        
        # Generate histogram data
        bins = 10
        min_val, max_val = min(values), max(values)
        bin_width = (max_val - min_val) / bins
        
        histogram = [0] * bins
        bin_edges = [min_val + i * bin_width for i in range(bins + 1)]
        
        for value in values:
            bin_index = min(int((value - min_val) / bin_width), bins - 1)
            histogram[bin_index] += 1
        
        # Calculate distribution statistics
        mean = calculate_mean(values)
        std = calculate_std(values)
        
        # Simple normality check (coefficient of variation)
        cv = std / abs(mean) if mean != 0 else float('inf')
        is_normal = cv < 1.0  # Simplified check
        
        analysis_results["distribution"] = {
            "histogram": {
                "counts": histogram,
                "bin_edges": bin_edges,
                "bin_width": bin_width
            },
            "mean": mean,
            "std": std,
            "cv": cv,
            "is_normal_like": is_normal,
            "unique_values": len(set(values))
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
        
        values = dataset['values']
        
        # Calculate moving averages
        window_sizes = [5, 10, 20]
        moving_averages = {}
        
        for window in window_sizes:
            if len(values) >= window:
                ma = []
                for i in range(window - 1, len(values)):
                    window_values = values[i - window + 1:i + 1]
                    ma.append(calculate_mean(window_values))
                moving_averages[f"ma_{window}"] = ma
        
        # Calculate trend direction
        quarter_size = len(values) // 4
        first_quarter = calculate_mean(values[:quarter_size])
        last_quarter = calculate_mean(values[-quarter_size:])
        trend_direction = "increasing" if last_quarter > first_quarter else "decreasing"
        trend_strength = abs(last_quarter - first_quarter)
        
        analysis_results["trends"] = {
            "moving_averages": moving_averages,
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "first_quarter_mean": first_quarter,
            "last_quarter_mean": last_quarter
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
                "total_points": len(dataset['values']),
                "columns": list(dataset.keys()),
                "missing_values": 0  # No missing values in our generated data
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
        basic_stats = state.get("basic_stats", {})
        
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
        
        if "trends" in analysis_results:
            trends = analysis_results["trends"]
            direction = trends.get("trend_direction", "unknown")
            summary["insights"].append(f"Overall trend is {direction}")
        
        analysis_results["summary"] = summary
        
        state.set("analyses_performed", analyses_performed)
        state.set("current_analysis", current_analysis)
        state.set("analysis_results", analysis_results)
        
        emit("analysis_complete", {
            "type": "summary",
            "results": analysis_results["summary"]
        })
    
    # Update progress
    progress = min(100.0, analyses_performed * 20.0)  # 5 analyses = 100%
    
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