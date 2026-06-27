from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from router import generate_report


def test_router_full_workflow():
    pdf = Path("demo_data/mock_tender.pdf")
    qualification = Path("demo_data/company_qualification.xlsx")
    if not pdf.exists() or not qualification.exists():
        import demo_data.create_demo_data as generator

        generator.main()
    report = generate_report(str(pdf), str(qualification), "outputs/test_router")
    assert report["decision"]["score"] >= 80
    assert Path(report["exports"]["full_json_report"]).exists()
    assert Path(report["exports"]["risk_pdf"]).exists()


if __name__ == "__main__":
    test_router_full_workflow()
    print("Router workflow test passed")
