"""Builds the three sample pdfs in sample_docs/.

All content is invented. The documents exist so the pipeline has something realistic
to ingest and something stable to evaluate retrieval against.
"""

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUT_DIR = Path(__file__).resolve().parents[1] / "sample_docs"

DISCLAIMER = (
    "SYNTHETIC TEST DATA - this document is fictional and was generated for software "
    "testing. It is not a real medical record and describes no real person."
)

styles = getSampleStyleSheet()
body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=9.5, leading=13.5, alignment=TA_JUSTIFY)
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=14, spaceAfter=4)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=10.5, spaceBefore=8, spaceAfter=3)
small = ParagraphStyle("small", parent=styles["BodyText"], fontSize=7.5, leading=10, textColor=colors.HexColor("#555555"))

TABLE_STYLE = TableStyle(
    [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#666666")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dddddd")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
)


def header(title: str, fields: list[tuple[str, str]]) -> list:
    out = [Paragraph(DISCLAIMER, small), Spacer(1, 6), Paragraph("Northgate Valley Clinic", h2), Paragraph(title, h1)]
    out.append(Paragraph(" &nbsp;|&nbsp; ".join(f"<b>{k}:</b> {v}" for k, v in fields), body))
    out.append(Spacer(1, 10))
    return out


def build(name: str, flow: list) -> Path:
    path = OUT_DIR / name
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
        title=name,
    )
    doc.build(flow)
    return path


LAB_ROWS = [
    ("Haemoglobin", "11.2", "g/dL", "13.0 - 17.0"),
    ("Haematocrit", "34.1", "%", "40.0 - 50.0"),
    ("Red cell count", "3.91", "x10^12/L", "4.50 - 5.90"),
    ("Mean cell volume", "87.2", "fL", "80.0 - 100.0"),
    ("Mean cell haemoglobin", "28.6", "pg", "27.0 - 33.0"),
    ("White cell count", "12.8", "x10^9/L", "4.0 - 11.0"),
    ("Neutrophils", "9.4", "x10^9/L", "2.0 - 7.5"),
    ("Lymphocytes", "2.1", "x10^9/L", "1.0 - 4.0"),
    ("Monocytes", "0.9", "x10^9/L", "0.2 - 1.0"),
    ("Eosinophils", "0.3", "x10^9/L", "0.0 - 0.5"),
    ("Basophils", "0.1", "x10^9/L", "0.0 - 0.1"),
    ("Platelet count", "398", "x10^9/L", "150 - 400"),
    ("Sodium", "136", "mmol/L", "135 - 145"),
    ("Potassium", "4.9", "mmol/L", "3.5 - 5.1"),
    ("Chloride", "101", "mmol/L", "98 - 107"),
    ("Bicarbonate", "22", "mmol/L", "22 - 29"),
    ("Urea", "9.8", "mmol/L", "2.8 - 7.2"),
    ("Creatinine", "124", "umol/L", "60 - 110"),
    ("eGFR", "52", "mL/min/1.73m2", "> 90"),
    ("Calcium (corrected)", "2.21", "mmol/L", "2.20 - 2.60"),
    ("Phosphate", "1.52", "mmol/L", "0.80 - 1.50"),
    ("Magnesium", "0.78", "mmol/L", "0.70 - 1.00"),
    ("Total protein", "66", "g/L", "60 - 80"),
    ("Albumin", "31", "g/L", "35 - 50"),
    ("Total bilirubin", "14", "umol/L", "3 - 21"),
    ("Alanine aminotransferase", "58", "U/L", "10 - 40"),
    ("Aspartate aminotransferase", "47", "U/L", "10 - 35"),
    ("Alkaline phosphatase", "142", "U/L", "30 - 120"),
    ("Gamma-glutamyl transferase", "88", "U/L", "10 - 55"),
    ("Lactate dehydrogenase", "268", "U/L", "120 - 250"),
    ("Creatine kinase", "191", "U/L", "30 - 200"),
    ("Glucose (fasting)", "7.8", "mmol/L", "3.9 - 5.5"),
    ("Haemoglobin A1c", "7.4", "%", "< 5.7"),
    ("Total cholesterol", "6.1", "mmol/L", "< 5.2"),
    ("LDL cholesterol", "4.0", "mmol/L", "< 3.4"),
    ("HDL cholesterol", "0.95", "mmol/L", "> 1.00"),
    ("Triglycerides", "2.8", "mmol/L", "< 1.7"),
    ("C-reactive protein", "42.6", "mg/L", "< 5.0"),
    ("Erythrocyte sedimentation rate", "48", "mm/h", "0 - 20"),
    ("Ferritin", "18", "ug/L", "30 - 400"),
    ("Iron", "7.2", "umol/L", "11.0 - 30.0"),
    ("Transferrin saturation", "11", "%", "20 - 50"),
    ("Vitamin B12", "212", "pmol/L", "145 - 570"),
    ("Folate", "6.4", "nmol/L", "7.0 - 45.0"),
    ("Vitamin D (25-OH)", "41", "nmol/L", "50 - 125"),
    ("Thyroid stimulating hormone", "5.9", "mIU/L", "0.40 - 4.00"),
    ("Free thyroxine", "11.8", "pmol/L", "9.0 - 19.0"),
    ("Free triiodothyronine", "3.9", "pmol/L", "3.5 - 6.5"),
    ("Troponin T (high sensitivity)", "9", "ng/L", "< 14"),
    ("N-terminal pro-BNP", "612", "ng/L", "< 125"),
    ("Prothrombin time", "13.8", "s", "11.0 - 14.0"),
    ("INR", "1.15", "", "0.90 - 1.20"),
    ("Activated partial thromboplastin time", "36.4", "s", "25.0 - 38.0"),
    ("Fibrinogen", "4.9", "g/L", "2.0 - 4.0"),
    ("D-dimer", "0.81", "mg/L FEU", "< 0.50"),
    ("Urine protein (dipstick)", "2+", "", "negative"),
    ("Urine albumin/creatinine ratio", "48", "mg/mmol", "< 3.0"),
]


def lab_report() -> Path:
    flow = header(
        "Laboratory Results Report",
        [
            ("Patient", "Marisol Deventer-Okoye"),
            ("DOB", "1958-03-14"),
            ("MRN", "NVC-4471902"),
            ("Collected", "2026-09-12 08:05"),
            ("Reported", "2026-09-12 16:40"),
            ("Requesting clinician", "Dr. Aurelia Vance"),
        ],
    )
    flow.append(
        Paragraph(
            "Specimens: whole blood (EDTA and citrate), serum, random urine. Fasting status reported "
            "by the patient as 11 hours. Results flagged outside the reference range should be read "
            "alongside the clinical picture; the reference intervals below are those of this laboratory "
            "and are not interchangeable with other sites.",
            body,
        )
    )
    flow.append(Spacer(1, 10))

    rows = [("Analyte", "Result", "Unit", "Reference range")] + LAB_ROWS
    table = Table(rows, colWidths=[7.2 * cm, 2.4 * cm, 3.0 * cm, 4.4 * cm], repeatRows=1)
    table.setStyle(TABLE_STYLE)
    flow.append(table)

    flow.append(Spacer(1, 10))
    flow.append(Paragraph("Comments", h2))
    flow.append(
        Paragraph(
            "Normochromic normocytic anaemia with low ferritin and transferrin saturation, consistent "
            "with iron deficiency on a background of inflammation. Renal function has declined since "
            "the comparison sample of 2026-04-02 (creatinine 101 umol/L, eGFR 64). Raised C-reactive "
            "protein and erythrocyte sedimentation rate are non-specific. Glycaemic control is above "
            "target. Suggest repeat urea and electrolytes within two weeks and review of the "
            "albumin/creatinine ratio on a first morning sample.",
            body,
        )
    )
    flow.append(Spacer(1, 6))
    flow.append(Paragraph("Authorised by G. Ibarra, consultant chemical pathologist.", body))
    return build("lab_results_report.pdf", flow)


def discharge_summary() -> Path:
    flow = header(
        "Discharge Summary",
        [
            ("Patient", "Teodor Blascovich"),
            ("DOB", "1971-11-02"),
            ("MRN", "NVC-3310884"),
            ("Admitted", "2026-08-24"),
            ("Discharged", "2026-08-30"),
            ("Ward", "Medical B"),
            ("Consultant", "Dr. Priyanka Ollerenshaw"),
        ],
    )

    sections = [
        (
            "Reason for admission",
            "Six-day history of productive cough, fever to 38.9 C at home and progressive breathlessness "
            "on minimal exertion. The patient attended the emergency department after an episode of "
            "pre-syncope while climbing stairs. No chest pain, no haemoptysis, no calf swelling.",
        ),
        (
            "Background",
            "Type 2 diabetes mellitus diagnosed 2014, managed with metformin. Hypertension. Ex-smoker, "
            "approximately 20 pack-years, stopped 2019. No known drug allergies. Lives with a partner in "
            "a first-floor flat, independent in all activities of daily living before this admission.",
        ),
        (
            "Findings on admission",
            "Temperature 38.4 C, heart rate 104 and regular, blood pressure 128/74, respiratory rate 24, "
            "oxygen saturation 91 percent on room air. Coarse crackles and reduced air entry at the right "
            "base. Chest radiograph showed right lower lobe consolidation without effusion. White cell "
            "count 14.6 x10^9/L, C-reactive protein 188 mg/L, creatinine 96 umol/L. CURB-65 score 1.",
        ),
        (
            "Progress in hospital",
            "Treated as community-acquired pneumonia with intravenous co-amoxiclav and oral clarithromycin, "
            "supplemental oxygen via nasal cannulae at 2 L/min and intravenous fluids for the first 36 hours. "
            "Blood cultures were negative at 48 hours; pneumococcal urinary antigen was positive. Oxygen was "
            "weaned off on day three and antibiotics were switched to the oral route on day four once the "
            "patient had been afebrile for 24 hours. Capillary glucose rose to 16.8 mmol/L during the acute "
            "phase and settled on the usual metformin dose without needing insulin. Physiotherapy reviewed "
            "the patient twice and confirmed independent mobility on the flat and up a flight of stairs "
            "before discharge. Repeat C-reactive protein on day five was 46 mg/L.",
        ),
        (
            "Condition at discharge",
            "Afebrile for 72 hours, saturations 96 percent on room air at rest and 94 percent after "
            "climbing one flight, mild residual exertional breathlessness and an occasional dry cough.",
        ),
    ]
    for title, text in sections:
        flow.append(Paragraph(title, h2))
        flow.append(Paragraph(text, body))

    flow.append(Paragraph("Discharge medication", h2))
    med_rows = [
        ("Drug", "Dose", "Frequency", "Duration"),
        ("Amoxicillin", "500 mg", "three times daily", "5 days to complete"),
        ("Clarithromycin", "500 mg", "twice daily", "3 days to complete"),
        ("Metformin", "1 g", "twice daily", "continue long term"),
        ("Ramipril", "5 mg", "once daily", "continue long term"),
        ("Atorvastatin", "20 mg", "once daily at night", "continue long term"),
        ("Paracetamol", "1 g", "up to four times daily", "as required, 7 days"),
    ]
    med = Table(med_rows, colWidths=[4.2 * cm, 2.6 * cm, 5.4 * cm, 4.8 * cm], repeatRows=1)
    med.setStyle(TABLE_STYLE)
    flow.append(Spacer(1, 4))
    flow.append(med)

    flow.append(Paragraph("Follow-up and advice", h2))
    flow.append(
        Paragraph(
            "Review in the general practice surgery within one week for a clinical check and repeat "
            "blood pressure. Repeat chest radiograph at six weeks to confirm resolution of the "
            "consolidation, booked for 2026-10-11. Pneumococcal and seasonal influenza vaccination to be "
            "offered in primary care once fully recovered. The patient has been advised to return to the "
            "emergency department if fever recurs, breathlessness worsens at rest, or new chest pain "
            "develops. A copy of this summary has been sent to the registered general practitioner.",
            body,
        )
    )
    return build("discharge_summary.pdf", flow)


def radiology_report() -> Path:
    flow = header(
        "Radiology Report - CT Abdomen and Pelvis with Contrast",
        [
            ("Patient", "Anneke Rumbaugh-Tsai"),
            ("DOB", "1983-06-27"),
            ("MRN", "NVC-5582137"),
            ("Study date", "2026-07-19"),
            ("Accession", "CT-2026-0719-0442"),
            ("Reporting radiologist", "Dr. Halvard Mbeki"),
        ],
    )

    sections = [
        (
            "Clinical indication",
            "Four days of right iliac fossa pain with anorexia and a low-grade fever. Equivocal "
            "ultrasound earlier the same day in which the appendix was not visualised. Rule out "
            "appendicitis and other causes of right lower quadrant pain.",
        ),
        (
            "Technique",
            "Multidetector CT of the abdomen and pelvis in the portal venous phase following 90 mL of "
            "intravenous iodinated contrast. Axial acquisition at 1 mm collimation with coronal and "
            "sagittal reformats. No oral or rectal contrast was given. Dose length product 486 mGy.cm.",
        ),
        (
            "Findings",
            "The appendix is identified in a retrocaecal position and is dilated to 11 mm with wall "
            "thickening, mural hyperenhancement and surrounding fat stranding. A 4 mm calcified "
            "appendicolith sits at the base. There is a small volume of free fluid in the pelvis and "
            "several reactive right iliac nodes up to 9 mm in short axis. No organised collection and no "
            "extraluminal gas to suggest perforation. The terminal ileum and caecum are normal in "
            "calibre with no wall thickening. Liver, spleen, pancreas, adrenal glands and both kidneys "
            "are unremarkable, with no biliary or urinary tract dilatation and no renal calculi. The "
            "gallbladder is thin walled and contains no calculi. Bowel loops elsewhere are normal with "
            "no obstruction. The uterus and both ovaries are within normal limits and there is no "
            "adnexal mass. No abdominal aortic aneurysm; the aorta and its main branches opacify "
            "normally. Lung bases show minor dependent atelectasis and no effusion. No lytic or "
            "sclerotic bone lesion is seen. Incidental note is made of a 9 mm simple cyst in the lower "
            "pole of the left kidney, which needs no follow-up.",
        ),
        (
            "Impression",
            "Acute uncomplicated appendicitis with an appendicolith and a small volume of reactive pelvic "
            "free fluid. No evidence of perforation or abscess. No alternative cause for the pain.",
        ),
        (
            "Communication",
            "Findings were telephoned to the on-call surgical registrar at 14:52 on the day of the study "
            "and acknowledged. Report verified electronically by the reporting radiologist.",
        ),
    ]
    for title, text in sections:
        flow.append(Paragraph(title, h2))
        flow.append(Paragraph(text, body))
    return build("radiology_report.pdf", flow)


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    for path in (lab_report(), discharge_summary(), radiology_report()):
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
