(function () {
  function formatBytes(bytes) {
    if (!Number.isFinite(bytes) || bytes <= 0) {
      return "0 MB";
    }

    var megabytes = 1024 * 1024;
    var kilobytes = 1024;

    if (bytes >= megabytes) {
      var mb = bytes / megabytes;
      return (mb >= 10 ? Math.round(mb) : mb.toFixed(1)) + " MB";
    }

    if (bytes >= kilobytes) {
      var kb = bytes / kilobytes;
      return (kb >= 10 ? Math.round(kb) : kb.toFixed(1)) + " KB";
    }

    return bytes + " bytes";
  }

  function readLimits(input) {
    return {
      maxFiles: Number(input.dataset.maxFiles || 0),
      maxFileBytes: Number(input.dataset.maxFileBytes || 0),
      maxTotalBytes: Number(input.dataset.maxTotalBytes || 0),
    };
  }

  function summarizeFiles(files) {
    var totalBytes = 0;
    files.forEach(function (file) {
      totalBytes += file.size || 0;
    });
    return totalBytes;
  }

  function validateFiles(files, limits) {
    var errors = [];
    var totalBytes = summarizeFiles(files);

    if (limits.maxFiles && files.length > limits.maxFiles) {
      errors.push("Upload up to " + limits.maxFiles + " images per batch.");
    }

    var oversizedFile = files.find(function (file) {
      return limits.maxFileBytes && file.size > limits.maxFileBytes;
    });

    if (oversizedFile) {
      errors.push(
        oversizedFile.name +
          " is " +
          formatBytes(oversizedFile.size) +
          ". Keep each image under " +
          formatBytes(limits.maxFileBytes) +
          "."
      );
    }

    if (limits.maxTotalBytes && totalBytes > limits.maxTotalBytes) {
      errors.push(
        "This batch is " +
          formatBytes(totalBytes) +
          ". Keep each upload under " +
          formatBytes(limits.maxTotalBytes) +
          "."
      );
    }

    return {
      totalBytes: totalBytes,
      errors: errors,
    };
  }

  function renderFileList(list, files) {
    list.innerHTML = "";

    if (!files.length) {
      list.hidden = true;
      return;
    }

    var visibleFiles = files.slice(0, 5);
    visibleFiles.forEach(function (file) {
      var item = document.createElement("li");
      item.textContent = file.name + " (" + formatBytes(file.size || 0) + ")";
      list.appendChild(item);
    });

    if (files.length > visibleFiles.length) {
      var more = document.createElement("li");
      more.textContent = "+" + (files.length - visibleFiles.length) + " more";
      list.appendChild(more);
    }

    list.hidden = false;
  }

  function updateWidget(widget) {
    var input = widget.querySelector(".bulk-upload-widget__input");
    var summary = widget.querySelector("[data-bulk-upload-summary]");
    var fileList = widget.querySelector("[data-bulk-upload-files]");
    var error = widget.querySelector("[data-bulk-upload-error]");
    var files = Array.from(input.files || []);
    var limits = readLimits(input);
    var validation = validateFiles(files, limits);
    var emptyCopy = summary.dataset.emptyCopy || "No files selected yet.";

    if (!files.length) {
      summary.textContent = emptyCopy;
      error.hidden = true;
      error.textContent = "";
      widget.classList.remove("has-error");
      widget.classList.remove("has-files");
      renderFileList(fileList, files);
      return true;
    }

    summary.textContent =
      files.length +
      (files.length === 1 ? " image selected" : " images selected") +
      " | " +
      formatBytes(validation.totalBytes) +
      " total";

    renderFileList(fileList, files);
    widget.classList.add("has-files");

    if (validation.errors.length) {
      error.textContent = validation.errors.join(" ");
      error.hidden = false;
      widget.classList.add("has-error");
      return false;
    }

    error.hidden = true;
    error.textContent = "";
    widget.classList.remove("has-error");
    return true;
  }

  function bindWidget(widget) {
    if (widget.dataset.bulkUploadBound === "true") {
      return;
    }

    widget.dataset.bulkUploadBound = "true";

    var input = widget.querySelector(".bulk-upload-widget__input");
    var dropzone = widget.querySelector("[data-bulk-upload-dropzone]");
    var form = widget.closest("form");

    input.addEventListener("change", function () {
      updateWidget(widget);
    });

    dropzone.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        input.click();
      }
    });

    ["dragenter", "dragover"].forEach(function (eventName) {
      dropzone.addEventListener(eventName, function (event) {
        event.preventDefault();
        widget.classList.add("is-dragover");
      });
    });

    ["dragleave", "dragend", "drop"].forEach(function (eventName) {
      dropzone.addEventListener(eventName, function (event) {
        event.preventDefault();
        widget.classList.remove("is-dragover");
      });
    });

    dropzone.addEventListener("drop", function (event) {
      if (!event.dataTransfer || !event.dataTransfer.files || !event.dataTransfer.files.length) {
        return;
      }

      input.files = event.dataTransfer.files;
      updateWidget(widget);
    });

    if (form) {
      form.addEventListener("submit", function (event) {
        var isValid = updateWidget(widget);
        if (!isValid) {
          event.preventDefault();
          dropzone.focus();
        }
      });
    }

    updateWidget(widget);
  }

  function initBulkUploadWidgets() {
    document.querySelectorAll("[data-bulk-upload-widget]").forEach(bindWidget);
  }

  document.addEventListener("DOMContentLoaded", initBulkUploadWidgets);
  document.addEventListener("wagtail:ready", initBulkUploadWidgets);
  initBulkUploadWidgets();
})();
