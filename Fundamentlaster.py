import pandas as pd
import streamlit as st
import xml.etree.ElementTree as ET
ET.register_namespace('', 'urn:strusoft')

st.title("Hent fundamentlaster")

resultcsvpath_neg = st.file_uploader("Velg out_neg-fil", type="csv", accept_multiple_files=False)
resultcsvpath_neg_perm = st.file_uploader("Velg out_neg_perm-fil", type="csv", accept_multiple_files=False)
resultcsvpath_neg_var = st.file_uploader("Velg out_neg_var-fil", type="csv", accept_multiple_files=False)
file_path = st.file_uploader("Velg femdesign-fil", type="struxml", accept_multiple_files=False)


def extract_foundations_and_axis(resultcsvpath_neg_perm,resultcsvpath_neg_var, resultcsvpath_neg, file_path):

    resultcsv_neg_perm = pd.read_csv(resultcsvpath_neg_perm, delimiter='\t', skiprows=1)
    resultcsv_neg_var = pd.read_csv(resultcsvpath_neg_var, delimiter='\t', skiprows=1)
    resultcsv_neg = pd.read_csv(resultcsvpath_neg, delimiter='\t', skiprows=1)
    tree = ET.parse(file_path)
    rootlist = tree.getroot()
    root = rootlist[0]

    # Parse XML-filen
    sup_ID, sup_x, sup_y, sup_z = [], [], [], []
    for pointsupport in root.iter('{urn:strusoft}point_support'):
        position = pointsupport.find('{urn:strusoft}position')
        #if float(position.attrib['z']) < 12:
        sup_x.append(round(float(position.attrib['x']), 3))
        sup_y.append(round(float(position.attrib['y']), 3))
        sup_z.append(round(float(position.attrib['z']), 3))
        sup_ID.append(pointsupport.attrib["name"])

    sup_forces_neg, sup_forces_neg_y, sup_forces_neg_x = [], [], []
    sup_in_res,i_not_in_res = [], []
    for support in resultcsv_neg_perm["ID"]:
        if support not in sup_in_res:
            sup_in_res.append(support)

    for sup in sup_ID:
        if sup not in sup_in_res:
            i = sup_ID.index(sup)
            i_not_in_res.append(i)
    for i in range(len(i_not_in_res)):
        sup_ID.pop(i_not_in_res[i]-i)
        sup_x.pop(i_not_in_res[i]-i)
        sup_y.pop(i_not_in_res[i]-i)
        sup_z.pop(i_not_in_res[i]-i)
    
    for i in range(len(resultcsv_neg["ID"])):
        if resultcsv_neg["ID"][i] in sup_ID and resultcsv_neg["Max."][i] == "Fz'":
            sup_forces_neg.append(abs(round(float(resultcsv_neg["Fz'"][i]))))
        if resultcsv_neg["ID"][i] in sup_ID and resultcsv_neg["Max."][i] == "Fx'":
            sup_forces_neg_x.append(abs(float(resultcsv_neg["Fx'"][i])))
        if resultcsv_neg["ID"][i] in sup_ID and resultcsv_neg["Max."][i] == "Fy'":
            sup_forces_neg_y.append(abs(float(resultcsv_neg["Fy'"][i])))
 
    sup_forces_neg_perm, sup_forces_neg_var = [], []
    for i in range(len(resultcsv_neg_perm["ID"])):
        if resultcsv_neg_perm["ID"][i] in sup_ID and resultcsv_neg_perm["Max."][i] == "Fz'":
            sup_forces_neg_perm.append(abs(round(float(resultcsv_neg_perm["Fz'"][i]))))
    for i in range(len(resultcsv_neg_var["ID"])):
        if resultcsv_neg_var["ID"][i] in sup_ID and resultcsv_neg_var["Max."][i] == "Fz'":
            sup_forces_neg_var.append(abs(round(float(resultcsv_neg_var["Fz'"][i]))))

    data = {
        "ID": sup_ID,
        "x": sup_x,
        "y": sup_y,
        "z": sup_z,
        "N-[kN]": sup_forces_neg,
        "N perm [kN]": sup_forces_neg_perm,
        "N var [kN]": sup_forces_neg_var,
    }

    df_punktfundamenter = pd.DataFrame(data)
    return df_punktfundamenter


if st.button("hent laster"):
    try:
        df_punktfundamenter = extract_foundations_and_axis(resultcsvpath_neg_perm, resultcsvpath_neg_var, resultcsvpath_neg,  file_path)
        df_punktfundamenter
        st.download_button(
            label="Download data as CSV",
            data=df_punktfundamenter.to_csv(sep=";", index=False).encode("utf-8"),
            file_name="df_punktfundamenter.csv",
            mime="text/csv",
        )
    except:
        st.write("last opp filer")
