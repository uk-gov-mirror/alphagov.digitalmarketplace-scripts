#!/usr/bin/env python
"""
Summarise the output of scripts/oneoff/get-g12-recovery-draft-status.py into three stats:
    1. How many draft services have been submitted?
    2. How many suppliers have submitted at least one draft?
    3. How many suppliers are yet to submit any drafts?

You'll need to install pandas into your scripts venv.
"""

import pandas as pd


def count_submitted(x: pd.Series) -> int:
    return len([y for y in x if y == "submitted"])


if __name__ == "__main__":
    draft_status = pd.read_csv("g12_recovery_draft_services.csv")

    # Exclude our test supplier
    draft_status = draft_status[draft_status["supplier_name"] != "Digital Marketplace Team"]

    submitted_services = len(draft_status[draft_status["draft_service_status"] == "submitted"])
    print(f"{submitted_services} submitted services of {len(draft_status)}")

    supplier_status = draft_status.groupby("supplier_name")["draft_service_status"].apply(list).reset_index()
    supplier_status["total_services"] = [len(x) for x in supplier_status["draft_service_status"]]
    supplier_status["submitted_count"] = [count_submitted(x) for x in supplier_status["draft_service_status"]]

    total_suppliers = len(supplier_status)
    supplier_at_least_one = len(supplier_status[supplier_status["submitted_count"] > 0])

    print(f"{supplier_at_least_one} of {total_suppliers} suppliers have submitted at least one draft service")
    print(f"{total_suppliers - supplier_at_least_one} of {total_suppliers} suppliers have not yet submitted any draft services")