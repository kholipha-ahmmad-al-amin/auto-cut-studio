const fileInput = document.querySelector("#file-input");
const dropZone = document.querySelector("#drop-zone");
const fileList = document.querySelector("#file-list");
const startButton = document.querySelector("#start-button");
const clearButton = document.querySelector("#clear-button");
const logOutput = document.querySelector("#log-output");
const copyLogButton = document.querySelector("#copy-log");
const jobTitle = document.querySelector("#job-title");
const jobCounter = document.querySelector("#job-counter");
const progressBar = document.querySelector("#progress-bar");
const results = document.querySelector("#results");
const engineStatus = document.querySelector("#engine-status");
const languageToggle = document.querySelector("#language-toggle");
const modeCards = Array.from(document.querySelectorAll(".mode-card"));

const translations = {
  en: {
    heroEyebrow: "Local video automation",
    heroCopy: "Cut silence, clean voice, and process videos locally with a focused production workflow.",
    ready: "Ready",
    working: "Working",
    finished: "Finished",
    failed: "Failed",
    dropTitle: "Drop videos here",
    dropText: "or click to choose files from your computer",
    emptyFiles: "No files selected yet.",
    startButton: "Start processing",
    clearButton: "Clear files",
    currentJob: "Current job",
    noJob: "No job running",
    uploading: "Uploading files",
    uploadLog: "Uploading files to the local app.",
    chooseFile: "Choose one or more video files first.",
    status: "Status",
    download: "Download",
    liveLog: "Live log",
    copyButton: "Copy",
    copied: "Copied",
    waiting: "Waiting for a job.",
    startError: "Could not start the job.",
    creditEyebrow: "Creator and credit",
    creditName: "Kholipha Ahmmad Al-Amin | খলিফা আহম্মেদ আল-আমিন",
    creditBio: "Software Engineer & AI Specialist, Founder & CEO at EquiSaaS BD, Principal Consultant at AR IT Consultancy, and Full-Stack SaaS Product Builder from Dhaka, Bangladesh.",
    portfolioLink: "Portfolio",
    modes: {
      normal: ["Normal", "Default silence based smart cut."],
      safe: ["Safe", "Keeps more space around speech to reduce clipped words."],
      podcast: ["Podcast", "Cuts silence, slightly speeds speech, and balances voice level."],
      soft: ["Soft", "Fast-forwards silent parts instead of removing them completely."],
      motion: ["Motion-aware", "Keeps sections with speech or visible movement."],
      denoise: ["Light denoise", "Applies a light voice cleanup pass after the smart cut."],
      voice: ["Voice consistent", "Runs smart cut with EBU voice volume normalization."],
      clean: ["Clean voice", "Runs smart cut, denoise, and voice volume consistency."],
    },
  },
  bn: {
    heroEyebrow: "লোকাল ভিডিও অটোমেশন",
    heroCopy: "সাইলেন্স কাটুন, ভয়েস পরিষ্কার করুন, এবং নিজের কম্পিউটারেই দ্রুত প্রোডাকশন-রেডি ভিডিও তৈরি করুন।",
    ready: "প্রস্তুত",
    working: "চলছে",
    finished: "সম্পন্ন",
    failed: "ব্যর্থ",
    dropTitle: "এখানে ভিডিও ড্রপ করুন",
    dropText: "অথবা কম্পিউটার থেকে ফাইল বেছে নিতে ক্লিক করুন",
    emptyFiles: "এখনও কোনো ফাইল নির্বাচন করা হয়নি।",
    startButton: "প্রসেস শুরু করুন",
    clearButton: "ফাইল সরান",
    currentJob: "বর্তমান কাজ",
    noJob: "কোনো কাজ চলছে না",
    uploading: "ফাইল আপলোড হচ্ছে",
    uploadLog: "লোকাল অ্যাপে ফাইল আপলোড করা হচ্ছে।",
    chooseFile: "প্রথমে এক বা একাধিক ভিডিও ফাইল নির্বাচন করুন।",
    status: "অবস্থা",
    download: "ডাউনলোড",
    liveLog: "লাইভ লগ",
    copyButton: "কপি",
    copied: "কপি হয়েছে",
    waiting: "কাজ শুরু হওয়ার অপেক্ষায়।",
    startError: "কাজটি শুরু করা যায়নি।",
    creditEyebrow: "নির্মাতা ও ক্রেডিট",
    creditName: "Kholipha Ahmmad Al-Amin | খলিফা আহম্মেদ আল-আমিন",
    creditBio: "ঢাকা, বাংলাদেশের Software Engineer & AI Specialist, EquiSaaS BD এর Founder & CEO, AR IT Consultancy এর Principal Consultant, এবং Full-Stack SaaS Product Builder.",
    portfolioLink: "পোর্টফোলিও",
    modes: {
      normal: ["নরমাল", "সাইলেন্স শনাক্ত করে ডিফল্ট স্মার্ট কাট।"],
      safe: ["সেফ", "কথার আগে-পরে বেশি জায়গা রাখে, যাতে শব্দ কেটে যাওয়ার ঝুঁকি কমে।"],
      podcast: ["পডকাস্ট", "সাইলেন্স কাটে, কথা সামান্য দ্রুত করে, এবং ভয়েস লেভেল ব্যালান্স করে।"],
      soft: ["সফট", "সাইলেন্স পুরো বাদ না দিয়ে দ্রুত চালিয়ে দেয়, ফলে প্রাকৃতিক ফ্লো থাকে।"],
      motion: ["মোশন-অ্যাওয়ার", "কথা বা দৃশ্যমান মুভমেন্ট থাকলে সেই অংশ রেখে দেয়।"],
      denoise: ["লাইট ডিনয়েজ", "স্মার্ট কাটের পরে ভয়েসে হালকা ক্লিনআপ চালায়।"],
      voice: ["ভয়েস কনসিসটেন্ট", "স্মার্ট কাটের সাথে EBU ভয়েস ভলিউম নরমালাইজেশন করে।"],
      clean: ["ক্লিন ভয়েস", "স্মার্ট কাট, ডিনয়েজ, এবং ভয়েস ভলিউম কনসিসটেন্সি একসাথে করে।"],
    },
  },
};

let selectedFiles = [];
let pollTimer = null;
let currentLanguage = localStorage.getItem("autoCutLanguage") || "en";
let latestJob = null;

function t(key) {
  return translations[currentLanguage][key];
}

function formatBytes(bytes) {
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let unit = 0;

  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }

  return `${value.toFixed(unit === 0 ? 0 : 1)} ${units[unit]}`;
}

function translatePage() {
  document.documentElement.lang = currentLanguage;

  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.dataset.i18n;
    node.textContent = t(key);
  });

  modeCards.forEach((card) => {
    const mode = translations[currentLanguage].modes[card.dataset.modeKey];
    card.querySelector("[data-mode-label]").textContent = mode[0];
    card.querySelector("[data-mode-description]").textContent = mode[1];
  });

  languageToggle.checked = currentLanguage === "bn";
  renderFiles();

  if (latestJob) {
    renderJob(latestJob);
  } else {
    jobTitle.textContent = t("noJob");
    setLog([]);
    engineStatus.textContent = t("ready");
  }
}

function setFiles(files) {
  selectedFiles = Array.from(files);
  renderFiles();
}

function renderFiles() {
  fileList.innerHTML = "";

  if (selectedFiles.length === 0) {
    const empty = document.createElement("p");
    empty.textContent = t("emptyFiles");
    fileList.appendChild(empty);
    return;
  }

  for (const file of selectedFiles) {
    const row = document.createElement("div");
    row.className = "file-row";
    row.innerHTML = `<span>${file.name}</span><strong>${formatBytes(file.size)}</strong>`;
    fileList.appendChild(row);
  }
}

function selectedMode() {
  return document.querySelector("input[name='mode']:checked").value;
}

function setBusy(isBusy) {
  startButton.disabled = isBusy;
  clearButton.disabled = isBusy;
  engineStatus.textContent = isBusy ? t("working") : t("ready");
}

function setLog(lines) {
  logOutput.textContent = lines.length ? lines.join("\n") : t("waiting");
  logOutput.scrollTop = logOutput.scrollHeight;
}

function readableStatus(status) {
  if (status === "finished") return t("finished");
  if (status === "failed") return t("failed");
  if (status === "running") return t("working");
  return status;
}

function renderJob(job) {
  latestJob = job;
  const total = job.total || 0;
  const current = job.current || 0;
  const percent = total ? Math.round((current / total) * 100) : 0;

  jobTitle.textContent = job.status === "finished" ? t("finished") : `${t("status")}: ${readableStatus(job.status)}`;
  jobCounter.textContent = `${current} / ${total}`;
  progressBar.style.width = job.status === "finished" ? "100%" : `${percent}%`;
  setLog(job.logs || []);

  results.innerHTML = "";
  for (const item of job.results || []) {
    const row = document.createElement("div");
    row.className = "result-row";
    row.innerHTML = `
      <span>${item.name}<br><small>${formatBytes(item.size)}</small></span>
      <a class="download-link" href="${item.download_url}">${t("download")}</a>
    `;
    results.appendChild(row);
  }

  if (job.status === "finished" || job.status === "failed") {
    clearInterval(pollTimer);
    pollTimer = null;
    setBusy(false);
    engineStatus.textContent = job.status === "finished" ? t("finished") : t("failed");
  }
}

async function pollJob(jobId) {
  const response = await fetch(`/api/jobs/${jobId}`);
  const job = await response.json();
  renderJob(job);
}

async function startJob() {
  if (selectedFiles.length === 0) {
    setLog([t("chooseFile")]);
    return;
  }

  const data = new FormData();
  data.append("mode", selectedMode());

  for (const file of selectedFiles) {
    data.append("files", file);
  }

  setBusy(true);
  latestJob = null;
  results.innerHTML = "";
  progressBar.style.width = "0%";
  jobTitle.textContent = t("uploading");
  jobCounter.textContent = `0 / ${selectedFiles.length}`;
  setLog([t("uploadLog")]);

  const response = await fetch("/api/jobs", {
    method: "POST",
    body: data,
  });

  const payload = await response.json();

  if (!response.ok) {
    setBusy(false);
    setLog([payload.error || t("startError")]);
    return;
  }

  await pollJob(payload.job_id);
  pollTimer = setInterval(() => pollJob(payload.job_id), 1200);
}

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("dragging");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragging");
});

dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragging");
  setFiles(event.dataTransfer.files);
});

fileInput.addEventListener("change", () => {
  setFiles(fileInput.files);
});

for (const card of modeCards) {
  card.addEventListener("click", () => {
    modeCards.forEach((item) => item.classList.remove("selected"));
    card.classList.add("selected");
    card.querySelector("input").checked = true;
  });
}

languageToggle.addEventListener("change", () => {
  currentLanguage = languageToggle.checked ? "bn" : "en";
  localStorage.setItem("autoCutLanguage", currentLanguage);
  translatePage();
});

startButton.addEventListener("click", startJob);

clearButton.addEventListener("click", () => {
  selectedFiles = [];
  latestJob = null;
  fileInput.value = "";
  renderFiles();
  results.innerHTML = "";
  progressBar.style.width = "0%";
  jobTitle.textContent = t("noJob");
  jobCounter.textContent = "0 / 0";
  setLog([]);
  engineStatus.textContent = t("ready");
});

copyLogButton.addEventListener("click", async () => {
  await navigator.clipboard.writeText(logOutput.textContent);
  copyLogButton.textContent = t("copied");
  setTimeout(() => {
    copyLogButton.textContent = t("copyButton");
  }, 1200);
});

translatePage();
