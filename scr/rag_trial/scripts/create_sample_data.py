"""
Create a sample Excel file for testing the RAG application.
"""
import pandas as pd
import os

# Sample data about a fictional company's products
data = {
    "Product": [
        "CloudSync Pro",
        "DataGuard Enterprise",
        "SpeedNet Router",
        "SecureVault",
        "AnalyticsPro",
        "CloudSync Basic",
        "MobileApp Suite",
        "DevTools Premium",
        "BackupMaster",
        "WebHosting Plus"
    ],
    "Category": [
        "Cloud Storage",
        "Security Software",
        "Networking Hardware",
        "Security Software",
        "Business Intelligence",
        "Cloud Storage",
        "Mobile Development",
        "Developer Tools",
        "Backup Solutions",
        "Web Services"
    ],
    "Description": [
        "Enterprise-grade cloud storage solution with 99.9% uptime guarantee. Supports real-time collaboration, version control, and advanced encryption. Perfect for teams of 10-1000 users.",
        "Comprehensive cybersecurity platform with AI-powered threat detection, firewall management, and compliance reporting. Protects against malware, ransomware, and zero-day attacks.",
        "High-performance WiFi 6E router with mesh networking capability. Covers up to 3000 sq ft, supports 100+ devices simultaneously, and includes built-in parental controls.",
        "Password manager and digital vault for storing sensitive information. Military-grade encryption, biometric authentication, and secure sharing features for families and teams.",
        "Advanced data analytics platform with AI-driven insights. Connect to multiple data sources, create interactive dashboards, and generate automated reports. Supports Python and R integration.",
        "Affordable cloud storage for individuals and small teams. 500GB storage, file sharing, and basic collaboration features. Great for personal use and startups.",
        "Complete toolkit for building cross-platform mobile applications. Includes UI components, backend integration, push notifications, and analytics. Supports iOS and Android.",
        "Professional IDE with intelligent code completion, debugging tools, and Git integration. Supports 20+ programming languages including Python, JavaScript, and Go.",
        "Automated backup solution for servers and workstations. Incremental backups, disaster recovery, and one-click restoration. Supports both cloud and local storage.",
        "Managed web hosting with 24/7 support, SSL certificates, and automatic scaling. Perfect for WordPress, e-commerce sites, and web applications. 99.95% uptime SLA."
    ],
    "Price": [
        "$49/month",
        "$199/month",
        "$299 one-time",
        "$5/month",
        "$299/month",
        "$9.99/month",
        "$89/month",
        "$29/month",
        "$79/month",
        "$24.99/month"
    ],
    "Rating": [4.8, 4.9, 4.6, 4.7, 4.5, 4.3, 4.4, 4.9, 4.6, 4.5],
    "Support": [
        "24/7 email and chat support",
        "24/7 phone, email, and priority support",
        "Email support during business hours",
        "Email and chat support",
        "Dedicated account manager and 24/7 support",
        "Community forum and email support",
        "Email support and documentation",
        "24/7 chat support and community forum",
        "24/7 phone and email support",
        "24/7 phone, email, and live chat support"
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Save to Excel
output_path = "data/source.xlsx"
df.to_excel(output_path, index=False, sheet_name="Products")

print(f"✅ Sample data created successfully at: {output_path}")
print(f"📊 Created {len(df)} product records")
print("\nSample products:")
for i, product in enumerate(df["Product"][:3], 1):
    print(f"  {i}. {product}")
print("  ...")
