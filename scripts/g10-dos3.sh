generate_g10_data()
{
  cat <<EOF
{
  "frameworks": {
    "framework": "g-cloud",
    "name": "G-Cloud 10",
    "slug": "g-cloud-10",
    "status": "open",
    "clarificationQuestionsOpen": true,
    "lots": [
      "cloud-hosting",
      "cloud-software",
      "cloud-support"
    ]
  },
  "updated_by": "Data export job"
}
EOF
}

generate_g10_agreement_data()
{
  cat <<EOF
{
  "frameworks": {
    "frameworkAgreementDetails": {
      "contractNoticeNumber": "<TO BE COMPLETED>",
      "frameworkAgreementVersion": "RM1557x",
      "frameworkEndDate": "32 March 2527",
      "frameworkExtensionLength": "12 months",
      "frameworkRefDate": "32-13-2525",
      "frameworkStartDate": "32 Decembuary 2525",
      "frameworkURL": "https://www.gov.uk/government/publications/<TO BE COMPLETED>",
      "lotDescriptions": {
        "cloud-hosting": "Lot 1: Cloud hosting",
        "cloud-software": "Lot 2: Cloud software",
        "cloud-support": "Lot 3: Cloud support"
      },
      "lotOrder": [
        "cloud-hosting",
        "cloud-software",
        "cloud-support"
      ],
      "pageTotal": 999,
      "signaturePageNumber": 333,
      "variations": {
      }
    }
  },
  "updated_by": "Data export job"
}
EOF
}

generate_dos3_data()
{
  cat <<EOF
{
  "frameworks": {
    "framework": "digital-outcomes-and-specialists",
    "name": "Digital Outcomes and Specialists 3",
    "slug": "digital-outcomes-and-specialists-3",
    "status": "open",
    "clarificationQuestionsOpen": true,
    "lots": [
      "digital-outcomes",
      "digital-specialists",
      "user-research-studios",
      "user-research-participants"
    ]
  },
  "updated_by": "Data export job"
}
EOF
}

generate_dos3_agreement_data()
{
  cat <<EOF
{
  "frameworks": {
    "frameworkAgreementDetails": {
      "contractNoticeNumber": "<TO BE COMPLETED>",
      "frameworkAgreementVersion": "RM1043v",
      "frameworkEndDate": "32 February 2527",
      "frameworkExtensionLength": "12 months",
      "frameworkRefDate": "32-02-2525",
      "frameworkStartDate": "32 Jantober 2525",
      "frameworkURL": "https://www.gov.uk/government/publications/<TO BE COMPLETED>",
      "lotDescriptions": {
        "digital-outcomes": "Lot 1: digital outcomes",
        "digital-specialists": "Lot 2: digital specialists",
        "user-research-participants": "Lot 4: user research participants",
        "user-research-studios": "Lot 3: user research studios"
      },
      "lotOrder": [
        "digital-outcomes",
        "digital-specialists",
        "user-research-studios",
        "user-research-participants"
      ],
      "pageTotal": 999,
      "signaturePageNumber": 333,
      "variations": {
      }
    }
  },
  "updated_by": "Data export job"
}
EOF
}

curl \
-H "Authorization: Bearer myToken" \
-H "Content-Type: application/json" \
-X POST --data "$(generate_g10_data)" "http://localhost:5000/frameworks"

curl \
-H "Authorization: Bearer myToken" \
-H "Content-Type: application/json" \
-X POST --data "$(generate_g10_agreement_data)" "http://localhost:5000/frameworks/g-cloud-10"

curl \
-H "Authorization: Bearer myToken" \
-H "Content-Type: application/json" \
-X POST --data "$(generate_dos3_data)" "http://localhost:5000/frameworks"

curl \
-H "Authorization: Bearer myToken" \
-H "Content-Type: application/json" \
-X POST --data "$(generate_dos3_agreement_data)" "http://localhost:5000/frameworks/digital-outcomes-and-specialists-3"
