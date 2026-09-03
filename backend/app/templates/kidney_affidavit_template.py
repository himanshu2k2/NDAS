"""
Affidavit content template for Kidney Transplant.
Returns structured sections used by both DOCX and PDF generators.
Each section maps to a page break boundary to ensure exactly 4 A4 pages.
"""

from dataclasses import dataclass


@dataclass
class AffidavitContext:
    donor_name: str
    donor_age: int
    donor_address: str
    donor_relationship: str
    donor_id_type: str
    donor_id_number: str
    recipient_name: str
    recipient_age: int
    recipient_address: str
    recipient_id_type: str
    recipient_id_number: str
    hospital_name: str
    hospital_address: str
    doctor_name: str
    doctor_registration_no: str
    transplant_date: str
    donor_consent: bool
    relationship_proof: str
    place: str
    affidavit_date: str


def build_sections(ctx: AffidavitContext) -> list[dict]:
    """
    Returns a list of page sections. Each dict has:
      - title  : str | None
      - body   : list[str]   (paragraphs)
      - page_break_after: bool
    """
    consent_text = "HEREBY GIVEN VOLUNTARILY AND WITHOUT COERCION" if ctx.donor_consent else "NOT PROVIDED"

    return [
        # ── PAGE 1 ── Title & Donor Details ──────────────────────────────────
        {
            "title": "AFFIDAVIT FOR KIDNEY TRANSPLANT",
            "subtitle": "(Executed under the Transplantation of Human Organs and Tissues Act, 1994)",
            "body": [
                f"I, {ctx.donor_name}, aged {ctx.donor_age} years, residing at {ctx.donor_address}, "
                f"holder of {ctx.donor_id_type} bearing No. {ctx.donor_id_number}, do hereby solemnly "
                f"affirm and declare as under:",

                "PART I — DEPONENT / DONOR PARTICULARS",

                f"1. That my full name is {ctx.donor_name} and I am {ctx.donor_age} years of age.",

                f"2. That I am permanently residing at the address mentioned herein: {ctx.donor_address}.",

                f"3. That I am producing my identity proof in the form of {ctx.donor_id_type}, "
                f"bearing number {ctx.donor_id_number}, as proof of my identity and age.",

                f"4. That I am the {ctx.donor_relationship} of the recipient, "
                f"namely {ctx.recipient_name}, aged {ctx.recipient_age} years.",

                f"5. That the relationship between myself and the recipient is established and "
                f"evidenced by {ctx.relationship_proof}, which is annexed hereto and marked as "
                f"Annexure-A.",

                "6. That I am of sound mind, in good health, and fully understand the nature, "
                "extent, and consequences of the kidney donation I am about to make.",

                "7. That I have not been subjected to any undue influence, coercion, threat, "
                "inducement, or monetary consideration of any kind in making this decision.",
            ],
            "page_break_after": True,
        },

        # ── PAGE 2 ── Recipient Details & Consent Declaration ─────────────────
        {
            "title": None,
            "subtitle": None,
            "body": [
                "PART II — RECIPIENT PARTICULARS",

                f"8. That the recipient of the kidney is {ctx.recipient_name}, aged {ctx.recipient_age} years, "
                f"residing at {ctx.recipient_address}.",

                f"9. That the recipient holds {ctx.recipient_id_type} bearing No. {ctx.recipient_id_number} "
                f"as proof of identity.",

                "10. That the recipient is suffering from end-stage renal disease (ESRD) / chronic "
                "kidney disease requiring a kidney transplant as certified by the treating physician.",

                "11. That I have been duly informed by the medical team about the surgical procedure, "
                "associated risks, post-operative care, and long-term implications of living kidney donation.",

                "PART III — VOLUNTARY CONSENT",

                f"12. That my consent for kidney donation is {consent_text}.",

                "13. That I understand that I may withdraw my consent at any time before the "
                "commencement of the surgical procedure without any penalty or consequence.",

                "14. That I have not received, nor have I been promised, any payment, reward, "
                "gift, or other consideration in exchange for donating my kidney.",

                "15. That I am donating my kidney solely out of love, affection, and humanitarian "
                "concern for the recipient and not for any commercial purpose whatsoever.",

                "16. That I have been counselled by an independent counsellor and I fully "
                "understand the implications of this donation.",
            ],
            "page_break_after": True,
        },

        # ── PAGE 3 ── Medical / Hospital Details ─────────────────────────────
        {
            "title": None,
            "subtitle": None,
            "body": [
                "PART IV — MEDICAL AND HOSPITAL DETAILS",

                f"17. That the kidney transplant surgery is scheduled to be performed at "
                f"{ctx.hospital_name}, located at {ctx.hospital_address}.",

                f"18. That the transplant surgery will be performed by Dr. {ctx.doctor_name}, "
                f"registered under Medical Registration No. {ctx.doctor_registration_no}.",

                f"19. That the scheduled date of the transplant surgery is {ctx.transplant_date}.",

                "20. That I have undergone all required pre-operative medical examinations, "
                "blood tests, tissue compatibility tests, and psychological evaluations as "
                "mandated by the hospital and the Authorisation Committee.",

                "21. That the medical team has confirmed that I am medically fit to donate "
                "one kidney and that the donation will not endanger my life or long-term health.",

                "22. That I am aware that the transplant is subject to approval by the "
                "Authorisation Committee constituted under the Transplantation of Human Organs "
                "and Tissues Act, 1994, and its Rules.",

                "PART V — LEGAL DECLARATIONS",

                "23. That I am not a minor and I am fully competent to execute this affidavit.",

                "24. That the contents of this affidavit are true and correct to the best of "
                "my knowledge and belief, and nothing material has been concealed therefrom.",

                "25. That I undertake to inform the hospital and the Authorisation Committee "
                "immediately if there is any change in my decision or circumstances.",
            ],
            "page_break_after": True,
        },

        # ── PAGE 4 ── Verification, Witness & Notary ─────────────────────────
        {
            "title": None,
            "subtitle": None,
            "body": [
                "PART VI — VERIFICATION",

                f"I, {ctx.donor_name}, the deponent above named, do hereby verify that the "
                f"contents of this affidavit are true and correct to the best of my knowledge "
                f"and belief. No part of it is false and nothing material has been concealed.",

                f"Verified at {ctx.place} on this {ctx.affidavit_date}.",

                " ",

                "DEPONENT",
                f"Name  : {ctx.donor_name}",
                f"Age   : {ctx.donor_age} Years",
                f"ID    : {ctx.donor_id_type} — {ctx.donor_id_number}",

                " ",

                "WITNESS",

                "1.  Name : ___________________________",
                "    Address : ___________________________",
                "    Signature : ___________________________",

                "2.  Name : ___________________________",
                "    Address : ___________________________",
                "    Signature : ___________________________",

                " ",

                "NOTARY / OATH COMMISSIONER",

                f"Sworn before me at {ctx.place} on {ctx.affidavit_date}.",
                " ",
                "Signature  : ___________________________",
                "Name       : ___________________________",
                "Seal       : ___________________________",
                "Registration No. : ___________________________",
                " ",
                "(Notary Public / Oath Commissioner)",
            ],
            "page_break_after": False,
        },
    ]
