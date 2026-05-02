document.addEventListener("DOMContentLoaded", function () {
  const root = document.querySelector("[data-proofing-root]");

  if (!root) {
    return;
  }

  const toggleUrl = root.getAttribute("data-toggle-url");
  const selectors = root.querySelectorAll(".proof-selector");
  const countSpan = document.getElementById("count");

  updateCounter();

  selectors.forEach((selector) => {
    selector.addEventListener("click", async function (event) {
      event.preventDefault();

      if (this.disabled) {
        return;
      }

      const proofUuid = this.getAttribute("data-proof-uuid");
      const wasSelected = this.classList.contains("is-selected");

      this.disabled = true;
      setSelectedState(this, !wasSelected);
      updateCounter();

      try {
        const response = await fetch(toggleUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({ proof_uuid: proofUuid }),
        });

        const data = await response.json().catch(() => ({}));
        if (!response.ok || data.status !== "success") {
          throw new Error(data.message || "Server returned an error.");
        }

        setSelectedState(this, Boolean(data.selected));
      } catch (error) {
        setSelectedState(this, wasSelected);
        updateCounter();
        window.alert("Could not save selection: " + error.message);
      } finally {
        this.disabled = false;
      }
    });
  });

  function setSelectedState(selector, isSelected) {
    selector.classList.toggle("is-selected", isSelected);
    selector.setAttribute("aria-pressed", isSelected ? "true" : "false");
    const container = selector.closest(".proof-container");
    if (container) {
      container.classList.toggle("is-selected", isSelected);
    }
  }

  function updateCounter() {
    if (!countSpan) {
      return;
    }

    const selectedCount = root.querySelectorAll(".proof-selector.is-selected").length;
    countSpan.innerText = selectedCount;
  }
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i += 1) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
