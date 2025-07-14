"""
data_analysis - Interactive Data Analysis Lesson
Learn data science concepts through interactive gestures using basic Python
"""

import time
import json
import math
import random
from collections import defaultdict

# Lesson configuration
LESSON_NAME = "Interactive Data Analysis"
TARGET_GESTURES = ["fist", "open_hand", "point", "victory", "thumbs_up", "ok"]
ANALYSIS_TYPES = ["descriptive", "correlation", "distribution", "regression", "clustering", "summary"]

# Generate simple dataset using basic Python
random.seed(42)
n_samples = 50

# Create a simple dataset with relationships
age = [random.randint(20, 65) for _ in range(n_samples)]
income = [30000 + age[i] * 1000 + random.randint(-5000, 5000) for i in range(n_samples)]
education = [random.randint(12, 20) for _ in range(n_samples)]
experience = [age[i] - education[i] - 4 + random.randint(-2, 2) for i in range(n_samples)]
satisfaction = [min(10, max(1, (income[i] / 10000) * 0.5 + experience[i] * 0.2 + random.randint(-2, 2))) for i in range(n_samples)]

# Create the main dataset as a list of dictionaries
dataset = []
for i in range(n_samples):
    dataset.append({
        'age': age[i],
        'income': income[i],
        'education': education[i],
        'experience': experience[i],
        'satisfaction': satisfaction[i]
    })

# Helper functions for statistical calculations
def calculate_mean(data):
    """Calculate mean of a list of numbers"""
    return sum(data) / len(data) if data else 0

def calculate_median(data):
    """Calculate median of a list of numbers"""
    if not data:
        return 0
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % 2 == 0:
        return (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
    else:
        return sorted_data[n//2]

def calculate_std(data):
    """Calculate standard deviation of a list of numbers"""
    if not data:
        return 0
    mean = calculate_mean(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return math.sqrt(variance)

def calculate_correlation(x, y):
    """Calculate correlation coefficient between two lists"""
    if len(x) != len(y) or len(x) == 0:
        return 0
    
    mean_x = calculate_mean(x)
    mean_y = calculate_mean(y)
    
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
    denominator_x = sum((x[i] - mean_x) ** 2 for i in range(len(x)))
    denominator_y = sum((y[i] - mean_y) ** 2 for i in range(len(y)))
    
    if denominator_x == 0 or denominator_y == 0:
        return 0
    
    return numerator / math.sqrt(denominator_x * denominator_y)

def simple_linear_regression(x, y):
    """Simple linear regression"""
    if len(x) != len(y) or len(x) == 0:
        return 0, 0, 0, 0
    
    mean_x = calculate_mean(x)
    mean_y = calculate_mean(y)
    
    # Calculate slope and intercept
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
    denominator = sum((x[i] - mean_x) ** 2 for i in range(len(x)))
    
    if denominator == 0:
        return 0, mean_y, 0, 0
    
    slope = numerator / denominator
    intercept = mean_y - slope * mean_x
    
    # Calculate R-squared
    y_pred = [slope * x[i] + intercept for i in range(len(x))]
    ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(len(y)))
    ss_tot = sum((y[i] - mean_y) ** 2 for i in range(len(y)))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    # Calculate RMSE
    rmse = math.sqrt(sum((y[i] - y_pred[i]) ** 2 for i in range(len(y))) / len(y))
    
    return slope, intercept, r_squared, rmse

def simple_clustering(data, k=3, max_iters=50):
    """Simple k-means clustering implementation"""
    if not data or len(data) < k:
        return [], []
    
    # Initialize centroids randomly
    centroids = random.sample(data, k)
    
    for _ in range(max_iters):
        # Assign points to closest centroid
        labels = []
        for point in data:
            distances = [abs(point - centroid) for centroid in centroids]
            labels.append(distances.index(min(distances)))
        
        # Update centroids
        new_centroids = []
        for i in range(k):
            cluster_points = [data[j] for j in range(len(data)) if labels[j] == i]
            if cluster_points:
                new_centroids.append(calculate_mean(cluster_points))
            else:
                new_centroids.append(centroids[i])
        
        # Check convergence
        if all(abs(new_centroids[i] - centroids[i]) < 0.01 for i in range(k)):
            break
            
        centroids = new_centroids
    
    return labels, centroids

# Lesson state
analyses_performed = 0
current_analysis = None
analysis_results = {}
lesson_progress = 0.0

@on_start
def lesson_start():
    """Called when the lesson starts"""
    global analyses_performed, current_analysis, analysis_results, lesson_progress
    
    log("INFO", f"Starting data analysis lesson: {LESSON_NAME}")
    log("INFO", f"Dataset shape: {len(dataset)} samples, 5 features")
    log("INFO", f"Available gestures: {TARGET_GESTURES}")
    
    # Reset state
    analyses_performed = 0
    current_analysis = None
    analysis_results = {}
    lesson_progress = 0.0
    
    # Calculate basic statistics
    ages = [d['age'] for d in dataset]
    incomes = [d['income'] for d in dataset]
    satisfactions = [d['satisfaction'] for d in dataset]
    
    basic_stats = {
        "n_samples": len(dataset),
        "n_features": 5,
        "feature_names": ['age', 'income', 'education', 'experience', 'satisfaction'],
        "age_mean": round(calculate_mean(ages), 2),
        "income_mean": round(calculate_mean(incomes), 2),
        "satisfaction_mean": round(calculate_mean(satisfactions), 2)
    }
    
    # Update lesson state
    state.update({
        "lesson_name": LESSON_NAME,
        "dataset_info": basic_stats,
        "target_gestures": TARGET_GESTURES,
        "analysis_types": ANALYSIS_TYPES,
        "analyses_performed": analyses_performed,
        "current_analysis": current_analysis,
        "analysis_results": analysis_results,
        "lesson_progress": lesson_progress,
        "start_time": time.time()
    })
    
    emit("lesson_started", {
        "lesson_name": LESSON_NAME,
        "dataset_info": basic_stats,
        "target_gestures": TARGET_GESTURES,
        "analysis_types": ANALYSIS_TYPES,
        "instructions": {
            "fist": "Perform descriptive statistics analysis",
            "open_hand": "Analyze correlations between variables",
            "point": "Explore data distributions",
            "victory": "Build regression models",
            "thumbs_up": "Perform clustering analysis",
            "ok": "Generate summary and insights"
        }
    })

@on_gesture
def handle_gesture(gesture_data):
    """Called when a gesture is detected"""
    global analyses_performed, current_analysis, analysis_results, lesson_progress
    
    gesture = gesture_data.get("gesture")
    confidence = gesture_data.get("confidence", 0)
    
    if not gesture or confidence < 0.7:
        return
    
    log("INFO", f"Processing gesture: {gesture} (confidence: {confidence:.2f})")
    
    # Map gestures to analyses
    if gesture == "fist":
        current_analysis = "descriptive"
        analyses_performed += 1
        
        # Perform descriptive statistics
        ages = [d['age'] for d in dataset]
        incomes = [d['income'] for d in dataset]
        educations = [d['education'] for d in dataset]
        experiences = [d['experience'] for d in dataset]
        satisfactions = [d['satisfaction'] for d in dataset]
        
        results = {
            "age": {
                "mean": round(calculate_mean(ages), 2),
                "median": round(calculate_median(ages), 2),
                "std": round(calculate_std(ages), 2),
                "min": min(ages),
                "max": max(ages)
            },
            "income": {
                "mean": round(calculate_mean(incomes), 2),
                "median": round(calculate_median(incomes), 2),
                "std": round(calculate_std(incomes), 2),
                "min": min(incomes),
                "max": max(incomes)
            },
            "satisfaction": {
                "mean": round(calculate_mean(satisfactions), 2),
                "median": round(calculate_median(satisfactions), 2),
                "std": round(calculate_std(satisfactions), 2),
                "min": min(satisfactions),
                "max": max(satisfactions)
            }
        }
        
        analysis_results["descriptive"] = results
        lesson_progress = min(100.0, analyses_performed * 16.67)
        
        state.update({
            "current_analysis": current_analysis,
            "analysis_results": analysis_results,
            "lesson_progress": lesson_progress
        })
        
        emit("analysis_complete", {
            "type": "descriptive",
            "results": results,
            "message": "Descriptive statistics calculated successfully!"
        })
        
    elif gesture == "open_hand":
        current_analysis = "correlation"
        analyses_performed += 1
        
        # Perform correlation analysis
        ages = [d['age'] for d in dataset]
        incomes = [d['income'] for d in dataset]
        educations = [d['education'] for d in dataset]
        experiences = [d['experience'] for d in dataset]
        satisfactions = [d['satisfaction'] for d in dataset]
        
        correlations = {
            "age_income": round(calculate_correlation(ages, incomes), 3),
            "age_satisfaction": round(calculate_correlation(ages, satisfactions), 3),
            "income_satisfaction": round(calculate_correlation(incomes, satisfactions), 3),
            "education_income": round(calculate_correlation(educations, incomes), 3),
            "experience_satisfaction": round(calculate_correlation(experiences, satisfactions), 3)
        }
        
        analysis_results["correlation"] = correlations
        lesson_progress = min(100.0, analyses_performed * 16.67)
        
        state.update({
            "current_analysis": current_analysis,
            "analysis_results": analysis_results,
            "lesson_progress": lesson_progress
        })
        
        emit("analysis_complete", {
            "type": "correlation",
            "results": correlations,
            "message": "Correlation analysis completed!"
        })
        
    elif gesture == "point":
        current_analysis = "distribution"
        analyses_performed += 1
        
        # Perform distribution analysis
        ages = [d['age'] for d in dataset]
        incomes = [d['income'] for d in dataset]
        satisfactions = [d['satisfaction'] for d in dataset]
        
        # Create simple histograms
        def create_histogram(data, bins=5):
            min_val, max_val = min(data), max(data)
            bin_size = (max_val - min_val) / bins
            histogram = [0] * bins
            
            for value in data:
                bin_index = min(int((value - min_val) / bin_size), bins - 1)
                histogram[bin_index] += 1
            
            return histogram, [min_val + i * bin_size for i in range(bins + 1)]
        
        age_hist, age_bins = create_histogram(ages, 5)
        income_hist, income_bins = create_histogram(incomes, 5)
        satisfaction_hist, satisfaction_bins = create_histogram(satisfactions, 5)
        
        distributions = {
            "age": {
                "histogram": age_hist,
                "bins": [round(b, 1) for b in age_bins],
                "mean": round(calculate_mean(ages), 2),
                "std": round(calculate_std(ages), 2)
            },
            "income": {
                "histogram": income_hist,
                "bins": [round(b, 1) for b in income_bins],
                "mean": round(calculate_mean(incomes), 2),
                "std": round(calculate_std(incomes), 2)
            },
            "satisfaction": {
                "histogram": satisfaction_hist,
                "bins": [round(b, 1) for b in satisfaction_bins],
                "mean": round(calculate_mean(satisfactions), 2),
                "std": round(calculate_std(satisfactions), 2)
            }
        }
        
        analysis_results["distribution"] = distributions
        lesson_progress = min(100.0, analyses_performed * 16.67)
        
        state.update({
            "current_analysis": current_analysis,
            "analysis_results": analysis_results,
            "lesson_progress": lesson_progress
        })
        
        emit("analysis_complete", {
            "type": "distribution",
            "results": distributions,
            "message": "Distribution analysis completed!"
        })
        
    elif gesture == "victory":
        current_analysis = "regression"
        analyses_performed += 1
        
        # Perform regression analysis
        ages = [d['age'] for d in dataset]
        incomes = [d['income'] for d in dataset]
        satisfactions = [d['satisfaction'] for d in dataset]
        
        # Age vs Income regression
        age_income_slope, age_income_intercept, age_income_r2, age_income_rmse = simple_linear_regression(ages, incomes)
        
        # Age vs Satisfaction regression
        age_satisfaction_slope, age_satisfaction_intercept, age_satisfaction_r2, age_satisfaction_rmse = simple_linear_regression(ages, satisfactions)
        
        regressions = {
            "age_vs_income": {
                "slope": round(age_income_slope, 3),
                "intercept": round(age_income_intercept, 3),
                "r_squared": round(age_income_r2, 3),
                "rmse": round(age_income_rmse, 3)
            },
            "age_vs_satisfaction": {
                "slope": round(age_satisfaction_slope, 3),
                "intercept": round(age_satisfaction_intercept, 3),
                "r_squared": round(age_satisfaction_r2, 3),
                "rmse": round(age_satisfaction_rmse, 3)
            }
        }
        
        analysis_results["regression"] = regressions
        lesson_progress = min(100.0, analyses_performed * 16.67)
        
        state.update({
            "current_analysis": current_analysis,
            "analysis_results": analysis_results,
            "lesson_progress": lesson_progress
        })
        
        emit("analysis_complete", {
            "type": "regression",
            "results": regressions,
            "message": "Regression analysis completed!"
        })
        
    elif gesture == "thumbs_up":
        current_analysis = "clustering"
        analyses_performed += 1
        
        # Perform clustering analysis
        ages = [d['age'] for d in dataset]
        incomes = [d['income'] for d in dataset]
        
        # Simple clustering on age and income
        combined_data = [(ages[i], incomes[i]) for i in range(len(ages))]
        age_income_data = [ages[i] * 0.5 + incomes[i] * 0.0001 for i in range(len(ages))]  # Combined metric
        
        labels, centroids = simple_clustering(age_income_data, k=3)
        
        # Analyze clusters
        cluster_analysis = {}
        for i in range(3):
            cluster_indices = [j for j, label in enumerate(labels) if label == i]
            if cluster_indices:
                cluster_ages = [ages[j] for j in cluster_indices]
                cluster_incomes = [incomes[j] for j in cluster_indices]
                cluster_satisfactions = [satisfactions[j] for j in cluster_indices]
                
                cluster_analysis[f"cluster_{i+1}"] = {
                    "size": len(cluster_indices),
                    "avg_age": round(calculate_mean(cluster_ages), 2),
                    "avg_income": round(calculate_mean(cluster_incomes), 2),
                    "avg_satisfaction": round(calculate_mean(cluster_satisfactions), 2)
                }
        
        clustering_results = {
            "n_clusters": 3,
            "cluster_analysis": cluster_analysis,
            "centroids": [round(c, 2) for c in centroids]
        }
        
        analysis_results["clustering"] = clustering_results
        lesson_progress = min(100.0, analyses_performed * 16.67)
        
        state.update({
            "current_analysis": current_analysis,
            "analysis_results": analysis_results,
            "lesson_progress": lesson_progress
        })
        
        emit("analysis_complete", {
            "type": "clustering",
            "results": clustering_results,
            "message": "Clustering analysis completed!"
        })
        
    elif gesture == "ok":
        current_analysis = "summary"
        analyses_performed += 1
        
        # Generate summary and insights
        ages = [d['age'] for d in dataset]
        incomes = [d['income'] for d in dataset]
        satisfactions = [d['satisfaction'] for d in dataset]
        
        # Key insights
        insights = {
            "sample_size": len(dataset),
            "age_range": f"{min(ages)} - {max(ages)} years",
            "income_range": f"${min(incomes):,} - ${max(incomes):,}",
            "satisfaction_range": f"{min(satisfactions):.1f} - {max(satisfactions):.1f}",
            "strongest_correlation": "age vs income" if abs(calculate_correlation(ages, incomes)) > 0.5 else "none found",
            "average_satisfaction": round(calculate_mean(satisfactions), 2),
            "data_quality": "Good - no missing values",
            "recommendations": [
                "Consider age-based marketing strategies",
                "Focus on income-satisfaction relationship",
                "Explore education impact on career success"
            ]
        }
        
        analysis_results["summary"] = insights
        lesson_progress = 100.0  # Complete the lesson
        
        state.update({
            "current_analysis": current_analysis,
            "analysis_results": analysis_results,
            "lesson_progress": lesson_progress
        })
        
        emit("analysis_complete", {
            "type": "summary",
            "results": insights,
            "message": "Data analysis summary completed! Lesson finished!"
        })
        
        # Mark lesson as complete
        emit("lesson_completed", {
            "final_progress": lesson_progress,
            "total_analyses": analyses_performed,
            "insights": insights
        })

@on_tick
def lesson_tick():
    """Called periodically during the lesson"""
    # Update progress based on analyses performed
    analyses = state.get("analyses_performed", 0)
    progress = min(100.0, analyses * 16.67)  # 6 analyses = 100%
    
    state.set("lesson_progress", progress)
    
    emit("lesson_tick", {
        "progress": progress,
        "analyses_performed": analyses
    })

@on_complete
def lesson_complete():
    """Called when the lesson is completed"""
    log("INFO", "Data analysis lesson completed!")
    
    final_results = {
        "total_analyses": analyses_performed,
        "final_progress": lesson_progress,
        "analysis_types_completed": list(analysis_results.keys()),
        "dataset_size": len(dataset),
        "completion_time": time.time() - state.get("start_time", time.time())
    }
    
    state.update({
        "lesson_completed": True,
        "final_results": final_results
    })
    
    emit("lesson_completed", final_results) 