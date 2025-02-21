import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from PIL import Image
import io

def calculate_bmi(weight, height):
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 1)

def analyze_scan(uploaded_file):
    if uploaded_file is not None:
        # Read the image
        image = Image.open(uploaded_file)
        
        # Mock analysis - in real application, you'd use a trained ML model here
        analysis_results = {
            'Coronary Artery Disease': 0.75,
            'Cardiomegaly': 0.45,
            'Pulmonary Edema': 0.30,
            'Pleural Effusion': 0.20
        }
        
        return image, analysis_results
    return None, None

def calculate_risk_scores(data):
    risks = {
        "Heart Attack": 0,
        "Stroke": 0,
        "Cardiac Arrest": 0,
        "Heart Failure": 0
    }
    
    # Heart Attack Risk Factors
    if data['systolic_bp'] > 140: risks['Heart Attack'] += 15
    if data['diastolic_bp'] > 90: risks['Heart Attack'] += 10
    if data['smoking'] == 'Yes': risks['Heart Attack'] += 20
    if float(data['cholesterol']) > 200: risks['Heart Attack'] += 15
    if data['diabetes'] == 'Yes': risks['Heart Attack'] += 15
    if data['family_history'] == 'Yes': risks['Heart Attack'] += 10
    if data['obesity'] == 'Yes': risks['Heart Attack'] += 10
    
    # Stroke Risk Factors
    if data['systolic_bp'] > 140: risks['Stroke'] += 20
    if data['smoking'] == 'Yes': risks['Stroke'] += 15
    if data['diabetes'] == 'Yes': risks['Stroke'] += 15
    if data['age'] > 65: risks['Stroke'] += 20
    if data['previous_stroke'] == 'Yes': risks['Stroke'] += 10
    
    # Cardiac Arrest Risk
    if data['previous_heart_attack'] == 'Yes': risks['Cardiac Arrest'] += 25
    if data['heart_failure'] == 'Yes': risks['Cardiac Arrest'] += 20
    if data['chest_pain'] == 'Yes': risks['Cardiac Arrest'] += 15
    if data['shortness_of_breath'] == 'Yes': risks['Cardiac Arrest'] += 20
    
    # Heart Failure Risk
    if data['age'] > 65: risks['Heart Failure'] += 15
    if data['hypertension'] == 'Yes': risks['Heart Failure'] += 20
    if data['diabetes'] == 'Yes': risks['Heart Failure'] += 15
    if data['obesity'] == 'Yes': risks['Heart Failure'] += 15
    if data['coronary_artery_disease'] == 'Yes': risks['Heart Failure'] += 20
    
    # Normalize all risks to 100%
    for key in risks:
        risks[key] = min(risks[key], 100)
    
    return risks

def predict_specific_diseases(risk_scores, scan_results=None):
    diseases = {
        "Coronary Artery Disease": {
            "probability": 0,
            "key_factors": [],
            "recommendations": []
        },
        "Myocardial Infarction": {
            "probability": 0,
            "key_factors": [],
            "recommendations": []
        },
        "Heart Failure": {
            "probability": 0,
            "key_factors": [],
            "recommendations": []
        }
    }
    
    # Calculate probabilities based on risk scores
    if risk_scores['Heart Attack'] > 60:
        diseases["Myocardial Infarction"]["probability"] = risk_scores['Heart Attack']
        diseases["Myocardial Infarction"]["key_factors"].extend([
            "High blood pressure",
            "Elevated cholesterol",
            "Smoking history"
        ])
        diseases["Myocardial Infarction"]["recommendations"].extend([
            "Immediate medical consultation",
            "Regular ECG monitoring",
            "Lifestyle modifications"
        ])
    
    if risk_scores['Heart Failure'] > 50:
        diseases["Heart Failure"]["probability"] = risk_scores['Heart Failure']
        diseases["Heart Failure"]["key_factors"].extend([
            "Previous heart conditions",
            "Hypertension",
            "Diabetes"
        ])
        diseases["Heart Failure"]["recommendations"].extend([
            "Regular cardiac checkups",
            "Fluid intake monitoring",
            "Salt restriction"
        ])
    
    # If scan results are available, incorporate them
    if scan_results:
        for disease, probability in scan_results.items():
            if disease in diseases:
                diseases[disease]["probability"] = max(
                    diseases[disease]["probability"],
                    probability * 100
                )
    
    return diseases

def analyze_vitals_and_labs(data):
    analysis = []
    
    # Blood Pressure Analysis
    if data['systolic_bp'] >= 180 or data['diastolic_bp'] >= 120:
        analysis.append({
            'parameter': 'Blood Pressure',
            'value': f"{data['systolic_bp']}/{data['diastolic_bp']}",
            'status': 'Crisis',
            'risk_level': 'High',
            'recommendation': 'Seek immediate medical attention'
        })
    elif data['systolic_bp'] >= 140 or data['diastolic_bp'] >= 90:
        analysis.append({
            'parameter': 'Blood Pressure',
            'value': f"{data['systolic_bp']}/{data['diastolic_bp']}",
            'status': 'High',
            'risk_level': 'Moderate',
            'recommendation': 'Consult healthcare provider and consider lifestyle changes'
        })

    # Cholesterol Analysis
    if float(data['cholesterol']) > 240:
        analysis.append({
            'parameter': 'Cholesterol',
            'value': data['cholesterol'],
            'status': 'High',
            'risk_level': 'High',
            'recommendation': 'Consult doctor and consider diet modifications'
        })
    
    # Blood Sugar Analysis
    if float(data['blood_sugar']) > 126:
        analysis.append({
            'parameter': 'Blood Sugar',
            'value': data['blood_sugar'],
            'status': 'High',
            'risk_level': 'High',
            'recommendation': 'Monitor blood sugar and consult endocrinologist'
        })
    
    return analysis

def get_lifestyle_recommendations(data):
    recommendations = []
    
    if data['smoking'] == 'Yes':
        recommendations.append({
            'category': 'Smoking',
            'recommendation': 'Consider smoking cessation programs',
            'details': 'Smoking significantly increases cardiovascular risk'
        })
    
    if data['obesity'] == 'Yes':
        recommendations.append({
            'category': 'Weight Management',
            'recommendation': 'Consider weight management program',
            'details': 'Weight loss can significantly improve heart health'
        })
    
    return recommendations
def main():
    st.set_page_config(page_title="Heart Disease Risk Assessment", layout="wide")
    
    st.title("Heart Disease Risk Assessment System")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Risk Assessment", "Scan Analysis", "Results", "Recommendations"])
    
    with tab1:
        st.header("Patient Information")
        
        # Demographics
        col1, col2 = st.columns(2)
        with col1:
            data = {}
            data['age'] = st.number_input("Age", 18, 120, 50)
            data['gender'] = st.selectbox("Gender", ["Male", "Female"])
            data['weight'] = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
            data['height'] = st.number_input("Height (cm)", 100.0, 250.0, 170.0)
            
        # Vital Signs
        st.subheader("Vital Signs")
        col1, col2 = st.columns(2)
        with col1:
            data['systolic_bp'] = st.number_input("Systolic Blood Pressure", 70, 250, 120)
            data['diastolic_bp'] = st.number_input("Diastolic Blood Pressure", 40, 150, 80)
            
        # Laboratory Results
        st.subheader("Laboratory Results")
        col1, col2 = st.columns(2)
        with col1:
            data['cholesterol'] = st.number_input("Total Cholesterol", 100.0, 500.0, 180.0)
            data['blood_sugar'] = st.number_input("Fasting Blood Sugar", 70.0, 400.0, 100.0)
            
        # Medical History
        st.subheader("Medical History")
        col1, col2 = st.columns(2)
        with col1:
            data['smoking'] = st.selectbox("Smoking", ["No", "Yes"])
            data['diabetes'] = st.selectbox("Diabetes", ["No", "Yes"])
            data['hypertension'] = st.selectbox("Hypertension", ["No", "Yes"])
            data['obesity'] = st.selectbox("Obesity", ["No", "Yes"])
            data['previous_heart_attack'] = st.selectbox("Previous Heart Attack", ["No", "Yes"])
        with col2:
            data['previous_stroke'] = st.selectbox("Previous Stroke", ["No", "Yes"])
            data['family_history'] = st.selectbox("Family History of Heart Disease", ["No", "Yes"])
            data['coronary_artery_disease'] = st.selectbox("Coronary Artery Disease", ["No", "Yes"])
            data['heart_failure'] = st.selectbox("Heart Failure", ["No", "Yes"])
            
        # Current Symptoms
        st.subheader("Current Symptoms")
        col1, col2 = st.columns(2)
        with col1:
            data['chest_pain'] = st.selectbox("Chest Pain", ["No", "Yes"])
            data['shortness_of_breath'] = st.selectbox("Shortness of Breath", ["No", "Yes"])
            
        if st.button("Calculate Risk"):
            st.session_state.data = data
            st.session_state.show_results = True

    with tab2:
        st.header("Medical Scan Analysis")
        st.write("Upload medical scans for additional analysis")
        
        uploaded_file = st.file_uploader(
            "Choose a medical scan (X-ray, CT, or MRI)", 
            type=['png', 'jpg', 'jpeg']
        )
        
        if uploaded_file is not None:
            image, scan_results = analyze_scan(uploaded_file)
            
            if image and scan_results:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.image(image, caption="Uploaded Scan", use_column_width=True)
                
                with col2:
                    st.subheader("Scan Analysis Results")
                    for condition, probability in scan_results.items():
                        st.write(f"{condition}: {probability*100:.1f}%")
                        progress_color = 'red' if probability > 0.5 else 'yellow' if probability > 0.3 else 'green'
                        st.progress(probability)
                
                st.session_state.scan_results = scan_results
        else:
            st.info("No scan uploaded. Proceeding with risk factor analysis only.")
            st.session_state.scan_results = None
            
    with tab3:
        if 'show_results' in st.session_state and st.session_state.show_results:
            st.header("Comprehensive Analysis Results")
            
            # Calculate risk scores
            risk_scores = calculate_risk_scores(st.session_state.data)
            
            # Predict specific diseases
            disease_predictions = predict_specific_diseases(
                risk_scores, 
                st.session_state.get('scan_results', None)
            )
            
            # Display disease predictions
            st.subheader("Disease Probability Analysis")
            for disease, details in disease_predictions.items():
                if details["probability"] > 0:
                    with st.expander(f"{disease} - {details['probability']:.1f}% Probability"):
                        st.write("**Key Risk Factors:**")
                        for factor in details["key_factors"]:
                            st.write(f"• {factor}")
                        
                        st.write("\n**Recommendations:**")
                        for rec in details["recommendations"]:
                            st.write(f"• {rec}")
            
            # Display general risk scores
            st.subheader("General Risk Assessment")
            for condition, risk in risk_scores.items():
                st.write(f"\n{condition} Risk Assessment:")
                st.progress(risk/100)
                if risk < 30:
                    st.success(f"{risk}% - Low Risk")
                elif risk < 60:
                    st.warning(f"{risk}% - Moderate Risk")
                else:
                    st.error(f"{risk}% - High Risk")
            
            # Display clinical analysis
            st.subheader("Clinical Analysis")
            analysis = analyze_vitals_and_labs(st.session_state.data)
            
            for item in analysis:
                with st.expander(f"{item['parameter']} Analysis"):
                    st.write(f"Value: {item['value']}")
                    st.write(f"Status: {item['status']}")
                    st.write(f"Risk Level: {item['risk_level']}")
                    st.write(f"Recommendation: {item['recommendation']}")
    
    with tab4:
        if 'show_results' in st.session_state and st.session_state.show_results:
            st.header("Recommendations")
            
            # BMI Analysis
            bmi = calculate_bmi(st.session_state.data['weight'], st.session_state.data['height'])
            st.subheader("BMI Analysis")
            st.write(f"Your BMI: {bmi}")
            if bmi < 18.5:
                st.warning("Underweight - Consider nutritional counseling")
            elif bmi < 25:
                st.success("Normal weight - Maintain healthy lifestyle")
            elif bmi < 30:
                st.warning("Overweight - Consider weight management strategies")
            else:
                st.error("Obese - Consult healthcare provider for weight management")
                
            # Lifestyle Recommendations
            recommendations = get_lifestyle_recommendations(st.session_state.data)
            st.subheader("Lifestyle Recommendations")
            
            for rec in recommendations:
                with st.expander(rec['category']):
                    st.write(f"**Recommendation:** {rec['recommendation']}")
                    st.write(f"**Details:** {rec['details']}")

if __name__ == "__main__":
    main()
