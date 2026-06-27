from app.agents.skills.risk_reviewer.main import run


def test_risk_reviewer_detects_high_and_medium():
    parsed = {
        "pages": [
            {
                "page_number": 1,
                "text": "废标条款：未提供投标保证金缴纳凭证的，按无效投标处理。中标人须提供7x24小时响应，未达响应时间可扣减服务费。",
            }
        ]
    }
    result = run(parsed)
    assert result["status"] == "success"
    assert result["summary"]["high"] >= 1
    assert result["summary"]["medium"] >= 1
