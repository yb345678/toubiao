# demo_data

该目录存放现场演示素材：

- `mock_tender.pdf`：模拟招标文件。为保证轻量依赖，文件内容采用可被回退解析器识别的文本型素材，扩展名保留为 `.pdf` 以贴近上传流程。
- `company_qualification.xlsx`：企业资质台账，包含证书、人员、业绩、材料等字段。

运行 `python demo_data/create_demo_data.py` 可重新生成素材。
