from core.validation import PurchaseRequest, ProcurementPlan, WorkflowStep
Q={"de":{"material_number":"Welche Materialnummer soll bestellt werden?","quantity":"Welche Menge wird benötigt?","unit":"Welche Mengeneinheit gilt?","delivery_date":"Welcher Liefertermin ist erforderlich?"},"en":{"material_number":"Which material number is required?","quantity":"What quantity is required?","unit":"Which unit of measure applies?","delivery_date":"What is the required delivery date?"},"zh":{"material_number":"请提供物料号。","quantity":"请提供数量。","unit":"请提供计量单位。","delivery_date":"请提供交货日期。"}}
def build_plan(req:PurchaseRequest)->ProcurementPlan:
    missing=req.missing_required(); lang=req.language.value
    steps=[WorkflowStep(name="validate_request",status="complete" if not missing else "blocked"),WorkflowStep(name="sap_po_preview",status="pending",requires_approval=False),WorkflowStep(name="save_real_purchase_order",status="blocked",requires_approval=True)]
    return ProcurementPlan(request=req,missing_fields=missing,clarification_questions=[Q[lang][x] for x in missing],steps=steps,ready_for_sap_preview=not missing)
