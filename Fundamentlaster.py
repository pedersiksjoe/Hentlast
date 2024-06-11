import pandas as pd
import math
import streamlit as st
import xml.etree.ElementTree as ET
import json
ET.register_namespace('', 'urn:strusoft')

st.title("Hent fundamentlaster")

#tab1,tab2,tab3,tab4 = st.tabs(["input","beregning av størrelser", "plot av løft", "plot horisontallaster"])
resultcsvpath_neg = st.file_uploader("Velg out_neg-fil", type="csv", accept_multiple_files=False)
resultcsvpath_pos= st.file_uploader("Velg out_sup-fil", type="csv", accept_multiple_files=False)
file_path = st.file_uploader("Velg femdesign-fil", type="struxml", accept_multiple_files=False)

#def extract_foundations_and_axis(json_file):
def extract_foundations_and_axis(resultcsvpath_neg, resultcsvpath_pos, file_path):
    #resultcsvpath_neg_path = json_file['OutputPath_sup_neg']
    #resultcsvpath_pos_path = json_file['OutputPath_sup_pos']
    #file_path_str_path = json_file['FilePath']

    resultcsv_neg = pd.read_csv(resultcsvpath_neg, delimiter='\t', skiprows=1)
    resultcsv_pos = pd.read_csv(resultcsvpath_pos, delimiter='\t', skiprows=1)
    #file_path = f'{file_path_str}uxml'
    tree = ET.parse(file_path)
    rootlist = tree.getroot()
    root = rootlist[0]

    # Parse XML-filen
    sup_ID, sup_x, sup_y, sup_z = [], [], [], []
    for pointsupport in root.iter('{urn:strusoft}point_support'):
        position = pointsupport.find('{urn:strusoft}position')
        if float(position.attrib['z']) < 6:
            sup_x.append(round(float(position.attrib['x']), 3))
            sup_y.append(round(float(position.attrib['y']), 3))
            sup_z.append(round(float(position.attrib['z']), 3))
            sup_ID.append(pointsupport.attrib["name"])

    sup_forces_neg, sup_forces_neg_y, sup_forces_neg_x = [], [], []
    for i in range(len(resultcsv_neg["ID"])):
        if resultcsv_neg["ID"][i] in sup_ID and resultcsv_neg["Max."][i] == "Fz'":
            sup_forces_neg.append(abs(round(float(resultcsv_neg["Fz'"][i]))))
        if resultcsv_neg["ID"][i] in sup_ID and resultcsv_neg["Max."][i] == "Fx'":
            sup_forces_neg_x.append(abs(float(resultcsv_neg["Fx'"][i])))
        if resultcsv_neg["ID"][i] in sup_ID and resultcsv_neg["Max."][i] == "Fy'":
            sup_forces_neg_y.append(abs(float(resultcsv_neg["Fy'"][i])))

    sup_forces_pos, sup_forces_pos_y, sup_forces_pos_x, N_is_pos = [], [], [], []
    for i in range(len(resultcsv_pos["ID"])):
        if resultcsv_pos["ID"][i] in sup_ID and resultcsv_pos["Max."][i] == "Fz'":
            if float(resultcsv_pos["Fz'"][i]) > 0:
                N_is_pos.append(True)
                sup_forces_pos.append(round(float(resultcsv_pos["Fz'"][i])))
            else:
                N_is_pos.append(False)
                sup_forces_pos.append(0)
        if resultcsv_pos["ID"][i] in sup_ID and resultcsv_pos["Max."][i] == "Fx'":
            sup_forces_pos_x.append(abs(float(resultcsv_pos["Fx'"][i])))
        if resultcsv_pos["ID"][i] in sup_ID and resultcsv_pos["Max."][i] == "Fy'":
            sup_forces_pos_y.append(abs(float(resultcsv_pos["Fy'"][i])))

    sup_H = []
    for i in range(len(sup_ID)):
        Fx = max(sup_forces_neg_x[i], sup_forces_pos_x[i])
        Fy = max(sup_forces_neg_y[i], sup_forces_pos_y[i])
        sup_H.append(round(math.sqrt(math.pow(Fx, 2) + math.pow(Fy, 2))))

    data = {
        "ID": sup_ID,
        "x": sup_x,
        "y": sup_y,
        "z": sup_z,
        "N-[kN]": sup_forces_neg,
        "N+[kN]": sup_forces_pos,
        "løft": N_is_pos,
        "H [kN]": sup_H
    }

    df_punktfundamenter = pd.DataFrame(data)
    return df_punktfundamenter

#json_file = json.load(st.file_uploader("Velg JSON-fil", type="json", accept_multiple_files=False))
#if json_file is not None:
if st.button("hent laster"):
    #df_punktfundamenter = extract_foundations_and_axis(json_file)
    try:
        df_punktfundamenter = extract_foundations_and_axis(resultcsvpath_neg, resultcsvpath_pos, file_path)
        st.download_button(
            label="Download data as CSV",
            data=df_punktfundamenter.to_csv().encode("utf-8"),
            file_name="large_df.csv",
            mime="text/csv",
        )
    except:
        st.write("last opp filer")
