# sp_quick_check_plain.py
import requests
from azure.identity import ClientCertificateCredential

# === fill these ===
TENANT_ID = "<tenant-id>"
CLIENT_ID = "<client-id>"
CERT_PATH = r"C:\path\app_cert.pfx"
CERT_PASSWORD = "<pfx-password>"  # or None if no password

SP_HOST = "<tenant>.sharepoint.com"   # e.g., contoso.sharepoint.com
SP_SITE_PATH = "sites/<SiteName>"     # e.g., sites/Finance
FOLDER_PATH = "Documents/Inbound"     # e.g., "Documents/Inbound"
# ===================

# 1) Get token
cred = ClientCertificateCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    certificate_path=CERT_PATH,
    password=CERT_PASSWORD
)
token = cred.get_token("https://graph.microsoft.com/.default").token
headers = {"Authorization": f"Bearer {token}"}

# 2) Resolve site
site_url = f"https://graph.microsoft.com/v1.0/sites/{SP_HOST}:/{SP_SITE_PATH}"
resp = requests.get(site_url, headers=headers, timeout=30)
resp.raise_for_status()
site = resp.json()
site_id = site["id"]
print("✔ Site resolved:", site.get("webUrl"))

# 3) List folder items (up to 10)
folder_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{FOLDER_PATH}:/children?$top=10"
resp = requests.get(folder_url, headers=headers, timeout=30)
print("Status:", resp.status_code)

if resp.ok:
    items = resp.json().get("value", [])
    for it in items:
        kind = "FILE" if "file" in it else "FOLDER"
        print(kind, it["name"])
else:
    print(resp.text)
    print("\nHint: 403 = site-level grant missing (need Sites.Selected RSC).")
    print("      401 = admin consent missing for Graph Application permission.")
