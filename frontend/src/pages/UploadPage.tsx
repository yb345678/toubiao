import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Building2,
  CheckCircle2,
  FileSpreadsheet,
  FileText,
  FileUp,
  FolderPlus,
  Loader2,
  Download,
  Trash2,
  UploadCloud
} from "lucide-react";
import { createEnterprise, createProject, listEnterprises, listProjects, type Enterprise, type Project } from "../api/projects";
import {
  deleteProjectFile,
  listProjectFiles,
  projectFileDownloadUrl,
  uploadProjectFile,
  type ProjectFile,
  type ProjectFileType
} from "../api/files";
import { useToast } from "../components/ToastProvider";
import "../styles/upload.css";

type UploadSlot = {
  key: ProjectFileType;
  title: string;
  help: string;
  accept: string;
  icon: typeof FileText;
};

const uploadSlots: UploadSlot[] = [
  {
    key: "tender_pdf",
    title: "招标 PDF",
    help: "上传招标文件原文，推荐使用 PDF 格式。",
    accept: ".pdf,application/pdf",
    icon: FileText
  },
  {
    key: "qualification_excel",
    title: "企业资质台账",
    help: "上传企业证书、人员、业绩等资质台账。",
    accept: ".xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel",
    icon: FileSpreadsheet
  }
];

export function UploadPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [enterprises, setEnterprises] = useState<Enterprise[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [files, setFiles] = useState<ProjectFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingProject, setSavingProject] = useState(false);
  const [uploading, setUploading] = useState<ProjectFileType | "">("");
  const [uploadProgress, setUploadProgress] = useState<Record<ProjectFileType, number>>({
    tender_pdf: 0,
    qualification_excel: 0
  });
  const [deleting, setDeleting] = useState<ProjectFileType | "">("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [enterpriseName, setEnterpriseName] = useState("演示科技有限公司");
  const [projectName, setProjectName] = useState("智慧园区运维招标项目");
  const [tenderCompany, setTenderCompany] = useState("演示招标代理机构");

  useEffect(() => {
    let mounted = true;
    Promise.all([listEnterprises(), listProjects()])
      .then(([enterpriseData, projectData]) => {
        if (!mounted) return;
        setEnterprises(enterpriseData);
        setProjects(projectData);
        if (projectData.length > 0) {
          setSelectedProjectId(projectData[0].id);
        }
      })
      .catch((err) => {
        if (!mounted) return;
        const msg = err instanceof Error ? err.message : "项目加载失败";
        setError(msg);
        showToast(msg, "error");
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedProjectId) {
      setFiles([]);
      return;
    }
    refreshProjectFiles(selectedProjectId);
  }, [selectedProjectId]);

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === selectedProjectId),
    [projects, selectedProjectId]
  );

  async function handleCreateProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");
    setSavingProject(true);
    try {
      let enterprise = enterprises[0];
      if (!enterprise) {
        enterprise = await createEnterprise({
          name: enterpriseName,
          industry: "Information Technology",
          contact_name: "演示负责人"
        });
        setEnterprises([enterprise]);
      }

      const project = await createProject({
        enterprise_id: enterprise.id,
        name: projectName,
        tender_name: projectName,
        tender_company: tenderCompany
      });
      setProjects((current) => [project, ...current]);
      setSelectedProjectId(project.id);
      setMessage("项目已创建，可以上传文件。");
      showToast("项目已创建，可以上传文件。", "success");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "项目创建失败";
      setError(msg);
      showToast(msg, "error");
    } finally {
      setSavingProject(false);
    }
  }

  async function handleUpload(fileType: ProjectFileType, event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    if (!selectedProjectId) {
      setError("请先创建或选择项目，再上传文件。");
      showToast("请先创建或选择项目，再上传文件。", "error");
      return;
    }

    setUploading(fileType);
    setUploadProgress((current) => ({ ...current, [fileType]: 0 }));
    setError("");
    setMessage("");
    try {
      const saved = await uploadProjectFile(selectedProjectId, fileType, file, (percent) => {
        setUploadProgress((current) => ({ ...current, [fileType]: percent }));
      });
      setFiles((current) => [saved, ...current.filter((item) => item.file_type !== fileType)]);
      setProjects((current) =>
        current.map((project) => (project.id === selectedProjectId ? { ...project, status: "uploaded" } : project))
      );
      setMessage(`${saved.original_name || file.name} 上传成功。`);
      showToast(`${saved.original_name || file.name} 上传成功。`, "success");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "上传失败";
      setError(msg);
      showToast(msg, "error");
    } finally {
      setUploading("");
      setUploadProgress((current) => ({ ...current, [fileType]: 0 }));
    }
  }

  async function refreshProjectFiles(projectId = selectedProjectId) {
    if (!projectId) return;
    try {
      const data = await listProjectFiles(projectId);
      setFiles(data.items);
    } catch {
      setFiles([]);
    }
  }

  async function handleDelete(fileType: ProjectFileType) {
    if (!selectedProjectId) return;
    setDeleting(fileType);
    setError("");
    setMessage("");
    try {
      await deleteProjectFile(selectedProjectId, fileType);
      setFiles((current) => current.filter((item) => item.file_type !== fileType));
      setMessage(`${fileType} 已删除。`);
      showToast(`${fileType} 已删除。`, "success");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "删除失败";
      setError(msg);
      showToast(msg, "error");
    } finally {
      setDeleting("");
    }
  }

  function fileFor(type: ProjectFileType) {
    return files.find((file) => file.file_type === type);
  }

  return (
    <main className="upload-page">
      <header className="upload-header">
        <button className="back-button" onClick={() => navigate("/dashboard")}>
          <ArrowLeft size={18} />
          返回工作台
        </button>
        <div>
          <p className="upload-eyebrow">文件上传流程</p>
          <h1>上传招标材料</h1>
          <p>创建投标项目，上传招标 PDF 与企业资质台账，然后进入自动分析流程。</p>
        </div>
      </header>

      <section className="upload-layout">
        <aside className="project-panel">
          <div className="panel-title">
            <Building2 size={22} />
            <div>
              <h2>项目信息</h2>
              <p>选择已有项目，或创建一个新的演示项目。</p>
            </div>
          </div>

          <form className="project-form" onSubmit={handleCreateProject}>
            <label>
              <span>企业名称</span>
              <input value={enterpriseName} onChange={(event) => setEnterpriseName(event.target.value)} required />
            </label>
            <label>
              <span>项目名称</span>
              <input value={projectName} onChange={(event) => setProjectName(event.target.value)} required />
            </label>
            <label>
              <span>招标单位</span>
              <input value={tenderCompany} onChange={(event) => setTenderCompany(event.target.value)} />
            </label>
            <button disabled={savingProject} type="submit">
              {savingProject ? <Loader2 size={18} className="spin" /> : <FolderPlus size={18} />}
              创建项目
            </button>
          </form>

          <label className="project-select">
            <span>当前项目</span>
            <select value={selectedProjectId} onChange={(event) => setSelectedProjectId(event.target.value)} disabled={loading}>
              <option value="">未选择项目</option>
              {projects.map((project) => (
                <option value={project.id} key={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </label>
        </aside>

        <section className="file-panel">
          <div className="file-panel-heading">
            <div>
              <h2>{selectedProject ? selectedProject.name : "未选择项目"}</h2>
              <p>文件类型由后端上传服务校验。</p>
            </div>
            <span className="project-status">{selectedProject?.status || "waiting"}</span>
          </div>

          {(error || message) && (
            <div className={error ? "upload-alert error" : "upload-alert success"}>
              {error || message}
            </div>
          )}

          <div className="upload-slots">
            {uploadSlots.map((slot) => {
              const savedFile = fileFor(slot.key);
              const Icon = slot.icon;
              const isUploading = uploading === slot.key;
              const percent = uploadProgress[slot.key];
              return (
                <article className="upload-slot" key={slot.key}>
                  <div className="slot-icon">
                    <Icon size={24} />
                  </div>
                  <div className="slot-copy">
                    <h3>{slot.title}</h3>
                    <p>{slot.help}</p>
                    {savedFile && (
                      <div className="saved-file">
                        <CheckCircle2 size={16} />
                        <span>{savedFile.original_name || savedFile.stored_path}</span>
                      </div>
                    )}
                    {isUploading && (
                      <div className="upload-progress">
                        <div>
                          <span style={{ width: `${percent}%` }} />
                        </div>
                        <strong>{percent}%</strong>
                      </div>
                    )}
                  </div>
                  {savedFile && selectedProjectId ? (
                    <div className="file-actions">
                      <a href={projectFileDownloadUrl(selectedProjectId, slot.key)} target="_blank" rel="noreferrer">
                        <Download size={17} />
                        下载
                      </a>
                      <button onClick={() => handleDelete(slot.key)} disabled={deleting === slot.key}>
                        {deleting === slot.key ? <Loader2 size={17} className="spin" /> : <Trash2 size={17} />}
                        删除
                      </button>
                    </div>
                  ) : null}
                  <label className={selectedProjectId ? "upload-button" : "upload-button disabled"}>
                    {isUploading ? <Loader2 size={18} className="spin" /> : <UploadCloud size={18} />}
                    {isUploading ? "上传中" : "选择文件"}
                    <input
                      type="file"
                      accept={slot.accept}
                      disabled={!selectedProjectId || Boolean(uploading)}
                      onChange={(event) => handleUpload(slot.key, event)}
                    />
                  </label>
                </article>
              );
            })}
          </div>

          <button className="next-step-box" onClick={() => navigate("/analysis")}>
            <FileUp size={22} />
            <div>
              <strong>下一步</strong>
              <span>两个核心文件上传完成后，进入分析页调度 Router 和四个解耦 Skill。</span>
            </div>
          </button>
        </section>
      </section>
    </main>
  );
}
