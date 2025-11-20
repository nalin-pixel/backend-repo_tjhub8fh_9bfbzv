import os
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, HttpUrl

app = FastAPI(title="Legal Docs Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    business_name: str = Field(..., description="Your business or app name")
    business_type: str = Field(..., description="Sole proprietorship, LLC, Corporation, Non-profit, etc.")
    website_url: Optional[HttpUrl] = Field(None, description="Public website or app URL")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email for user inquiries")
    jurisdiction: Optional[str] = Field(None, description="Primary legal jurisdiction, e.g., United States, EU, India")
    company_address: Optional[str] = Field(None, description="Mailing address")
    effective_date: Optional[date] = Field(None, description="Effective date of the policy")

    # Product/service details
    description: Optional[str] = Field(None, description="What your app or service does")
    industries: Optional[List[str]] = Field(default=None, description="Industry tags like SaaS, e‑commerce, health, finance")

    # Data and features
    collects_personal_data: bool = True
    uses_cookies: bool = True
    uses_analytics: bool = True
    uses_third_party_tools: bool = True
    allows_user_accounts: bool = True
    allows_user_content: bool = False
    age_restriction: Optional[str] = Field(None, description="e.g., 13+, 16+, 18+")


class GenerateResponse(BaseModel):
    privacy_policy: str
    terms_of_service: str


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# -----------------------
# Legal text generators
# -----------------------

def _format_heading(text: str) -> str:
    return f"\n\n{text}\n" + ("-" * len(text)) + "\n\n"


def generate_privacy(req: GenerateRequest) -> str:
    bn = req.business_name.strip()
    url = str(req.website_url) if req.website_url else "your website/app"
    email = req.contact_email or "support@example.com"
    juris = req.jurisdiction or "your jurisdiction"
    eff = req.effective_date.isoformat() if req.effective_date else date.today().isoformat()

    parts = []
    parts.append(f"Privacy Policy for {bn}\nEffective date: {eff}")

    parts.append(_format_heading("Introduction") +
                 (req.description or f"This Privacy Policy explains how {bn} collects, uses, and shares information when you use {url} (the \"Service\")."))

    if req.collects_personal_data:
        parts.append(_format_heading("Information We Collect") +
                     "We may collect information you provide directly (such as name, email address, billing details) and information collected automatically (such as IP address, device info, pages viewed).")
    else:
        parts.append(_format_heading("Information We Collect") +
                     "We do not intentionally collect personal information. Limited technical data may be processed to operate the Service.")

    uses_cookie_line = "We use cookies and similar technologies to remember preferences and to understand how the Service is used." if req.uses_cookies else "We do not use cookies for tracking beyond what is strictly necessary to operate the Service."
    analytics_line = "We use analytics to understand usage and improve the Service." if req.uses_analytics else "We do not use third‑party analytics tools for tracking." 

    parts.append(_format_heading("How We Use Information") +
                 "We use information to provide and improve the Service, communicate with you, personalize content, ensure security, and comply with legal obligations.")

    parts.append(_format_heading("Cookies & Tracking") + uses_cookie_line + " " + analytics_line)

    if req.uses_third_party_tools:
        parts.append(_format_heading("Third‑Party Services") +
                     "We may share information with service providers that help us operate the Service (e.g., hosting, payments, analytics). These providers may process data on our behalf and are bound by contractual obligations.")
    else:
        parts.append(_format_heading("Third‑Party Services") +
                     "We do not share personal information with third parties except as required by law or to protect our rights.")

    if req.allows_user_accounts:
        parts.append(_format_heading("Accounts") +
                     "If you create an account, you are responsible for maintaining the confidentiality of your credentials and for any activity under your account.")

    if req.allows_user_content:
        parts.append(_format_heading("User‑Generated Content") +
                     "Content you submit may be publicly visible depending on your settings. Do not share personal information you prefer to keep private.")

    if req.age_restriction:
        parts.append(_format_heading("Children's Privacy") +
                     f"The Service is intended for users {req.age_restriction}. We do not knowingly collect personal information from children in violation of applicable laws.")
    else:
        parts.append(_format_heading("Children's Privacy") +
                     "The Service is not directed to children under the age required by applicable law. We do not knowingly collect personal information from children.")

    parts.append(_format_heading("Data Retention") +
                 "We retain information for as long as necessary to provide the Service, comply with obligations, resolve disputes, and enforce agreements.")

    parts.append(_format_heading("Your Rights") +
                 f"Depending on your location ({juris}), you may have rights to access, correct, delete, or restrict processing of your personal information, and to object or withdraw consent.")

    parts.append(_format_heading("Security") +
                 "We implement reasonable technical and organizational measures to protect information. No method of transmission or storage is completely secure.")

    contact_lines = [f"Email: {email}"]
    if req.company_address:
        contact_lines.append(f"Address: {req.company_address}")

    parts.append(_format_heading("Contact Us") + "\n".join(contact_lines))

    parts.append(_format_heading("Changes to this Policy") +
                 "We may update this Privacy Policy from time to time. We will revise the effective date above and post the updated version on this page.")

    parts.append(_format_heading("Jurisdiction") + f"This Policy is governed by the laws of {juris} unless otherwise required by applicable law.")

    return "\n\n".join(parts)


def generate_terms(req: GenerateRequest) -> str:
    bn = req.business_name.strip()
    url = str(req.website_url) if req.website_url else "our Service"
    eff = req.effective_date.isoformat() if req.effective_date else date.today().isoformat()
    juris = req.jurisdiction or "your jurisdiction"

    parts = []
    parts.append(f"Terms of Service for {bn}\nEffective date: {eff}")

    parts.append(_format_heading("Agreement to Terms") +
                 f"By accessing or using {url}, you agree to be bound by these Terms. If you do not agree, do not use the Service.")

    parts.append(_format_heading("Use of the Service") +
                 "You may use the Service only in compliance with these Terms and all applicable laws. We may suspend or terminate access for conduct that violates these Terms or harms the Service.")

    if req.allows_user_accounts:
        parts.append(_format_heading("Accounts & Security") +
                     "You must provide accurate information and keep your account secure. You are responsible for activities under your account.")

    if req.allows_user_content:
        parts.append(_format_heading("User Content") +
                     "You retain ownership of content you submit. By submitting content, you grant us a non‑exclusive, worldwide, royalty‑free license to use, reproduce, and display it to operate the Service. You represent that your content does not infringe others' rights.")

    parts.append(_format_heading("Prohibited Activities") +
                 "You agree not to: (i) misuse or interfere with the Service; (ii) reverse engineer; (iii) upload malware; (iv) violate laws; (v) infringe intellectual property or privacy rights.")

    parts.append(_format_heading("Intellectual Property") +
                 f"All rights, title, and interest in the Service (excluding user content) are owned by {bn} and its licensors.")

    parts.append(_format_heading("Fees & Payments") +
                 "If the Service includes paid features, you agree to pay applicable fees and taxes. Payments are non‑refundable except as required by law or our stated policy.")

    parts.append(_format_heading("Disclaimers") +
                 "THE SERVICE IS PROVIDED \"AS IS\" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED. WE DISCLAIM ALL WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON‑INFRINGEMENT.")

    parts.append(_format_heading("Limitation of Liability") +
                 "TO THE MAXIMUM EXTENT PERMITTED BY LAW, WE WILL NOT BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR DATA.")

    parts.append(_format_heading("Indemnification") +
                 "You agree to defend, indemnify, and hold harmless us and our affiliates from claims arising out of your use of the Service or your violation of these Terms.")

    parts.append(_format_heading("Governing Law; Disputes") +
                 f"These Terms are governed by the laws of {juris}, without regard to conflict of law principles. Venue and jurisdiction will lie in the courts located in {juris}, unless otherwise required by law.")

    parts.append(_format_heading("Termination") +
                 "We may suspend or terminate your access at any time for any reason. Upon termination, provisions that by their nature should survive will survive.")

    parts.append(_format_heading("Changes to Terms") +
                 "We may update these Terms from time to time. By continuing to use the Service after changes take effect, you agree to the revised Terms.")

    parts.append(_format_heading("Contact") +
                 "For questions about these Terms, please contact us at the email listed in the Privacy Policy.")

    return "\n\n".join(parts)


@app.post("/api/generate", response_model=GenerateResponse)
def generate_docs(payload: GenerateRequest):
    try:
        privacy = generate_privacy(payload)
        terms = generate_terms(payload)
        return GenerateResponse(privacy_policy=privacy, terms_of_service=terms)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
