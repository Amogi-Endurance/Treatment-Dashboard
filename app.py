from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    # Path to the CSV file
    file_path = r"C:\Users\APINPC\Desktop\Linelist\Ogun_Merged_Line_list_as_at_31-08-2024_Regenerated.csv"

    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Convert 'ARTStartDate' and 'DateofCurrentViralLoad' to datetime
    df['ARTStartDate'] = pd.to_datetime(df['ARTStartDate'], errors='coerce')
    df['DateofCurrentViralLoad'] = pd.to_datetime(df['DateofCurrentViralLoad'], errors='coerce')

    # Get the list of unique facilities for the dropdown
    facilities = df['FacilityName'].unique()

    # Get the selected facility from the dropdown (POST request) or default to the first facility
    selected_facility = request.form.get('facility', facilities[0])

    # Filter the DataFrame based on the selected facility
    facility_df = df[df['FacilityName'] == selected_facility]

    # Get the date range for Treatment New from the form
    start_date = request.form.get('start_date', '2024-08-01')
    end_date = request.form.get('end_date', '2024-08-31')

    # Convert the date range to datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Treatment New (patients who started ART within the selected date range and are not TI)
    filtered_df = facility_df[(facility_df['ARTStartDate'] >= start_date) &
                              (facility_df['ARTStartDate'] <= end_date) &
                              (facility_df['TI'] == 'No')]
    treatment_new = filtered_df.shape[0]

    # Treatment Current (patients who are active on ART)
    treatment_current = facility_df[facility_df['CurrentARTStatus_Pharmacy'] == 'Active'].shape[0]

    # Active and eligible for viral load (DaysOnART > 180 and Active)
    active_eligible_vl = facility_df[(facility_df['CurrentARTStatus_Pharmacy'] == 'Active') &
                                     (facility_df['DaysOnART'] >= 180)].shape[0]

    # Viral Load Results Documented (within one year from today)
    CurrentViralLoad = facility_df[(facility_df['CurrentARTStatus_Pharmacy'] == 'Active') &
                                   (facility_df['DaysOnART'] >= 180) &
                                   (facility_df['DateofCurrentViralLoad'] >= '2023-09-01') &
                                   (facility_df['DateofCurrentViralLoad'] <= '2024-08-31')].shape[0]

    # VL Suppressed (patients with current viral load < 1000)
    vl_suppressed = facility_df[(facility_df['CurrentARTStatus_Pharmacy'] == 'Active') &
                                   (facility_df['DaysOnART'] >= 180) &
                                   (facility_df['DateofCurrentViralLoad'] >= '2023-09-01') &
                                   (facility_df['DateofCurrentViralLoad'] <= '2024-08-31') &
                                   (facility_df['CurrentViralLoad'] < 1000)].shape[0]

    # Coverage: % of eligible patients with documented viral load
    coverage = (CurrentViralLoad / active_eligible_vl) * 100 if active_eligible_vl > 0 else 0

    # Suppression: % of patients with VL documented and suppressed
    suppression = (vl_suppressed / CurrentViralLoad) * 100 if CurrentViralLoad > 0 else 0

    # Render the data into different containers
    return render_template('dashboard.html',
                           facilities=facilities,
                           selected_facility=selected_facility,
                           treatment_new=treatment_new,
                           treatment_current=treatment_current,
                           active_eligible_vl=active_eligible_vl,
                           CurrentViralLoad=CurrentViralLoad,
                           vl_suppressed=vl_suppressed,
                           coverage=coverage,
                           suppression=suppression,
                           start_date=start_date.strftime('%Y-%m-%d'),
                           end_date=end_date.strftime('%Y-%m-%d'))

if __name__ == '__main__':
    app.run(debug=True)
