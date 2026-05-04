document.addEventListener("DOMContentLoaded", function () {
  const root = document.querySelector("[data-proofing-root]");
  const isFrench = (document.documentElement.lang || "").toLowerCase().startsWith("fr");
  const copy = isFrench
    ? {
        confirmSubmitWindow:
          "Soumettre vos selections actuelles? Vous ne pourrez plus les modifier ensuite.",
        reviewActive:
          "La revision de la selection est toujours active. Vous pouvez continuer a ajuster votre liste.",
        showingSelectedOnly: "Affichage des images selectionnees uniquement.",
        selectAria: "Selectionner l image",
        removeAria: "Retirer l image de la selection",
        shortlistAdded: "Image ajoutee a votre liste.",
        shortlistRemoved: "Image retiree de votre liste.",
        saveSelectionError: "Impossible d enregistrer la selection : ",
        loadMoreError:
          "Impossible de charger plus d images. Actualisez la page pour reessayer.",
        finalizeInfo:
          "La soumission verrouillera cette galerie afin que les images selectionnees passent a la retouche.",
        finalizeEmpty: "Selectionnez au moins une image avant de finaliser.",
        finalizeError: "Impossible de finaliser les selections : ",
        reloadPortal:
          "Vos selections ont ete envoyees. Rechargement du portail...",
        submitting: "Envoi...",
        loadingMore: "Chargement d autres images...",
      }
    : {
        confirmSubmitWindow:
          "Submit your current selections? You will not be able to change them after this.",
        reviewActive:
          "Selection review is still active. You can keep refining your shortlist.",
        showingSelectedOnly: "Showing your selected images only.",
        selectAria: "Select image",
        removeAria: "Remove image from selection",
        shortlistAdded: "Image added to your shortlist.",
        shortlistRemoved: "Image removed from your shortlist.",
        saveSelectionError: "Could not save selection: ",
        loadMoreError:
          "Could not load more images. Please refresh to try again.",
        finalizeInfo:
          "Submitting will lock this gallery so the selected images can move into retouching.",
        finalizeEmpty: "Select at least one image before finalizing.",
        finalizeError: "Could not finalize selections: ",
        reloadPortal:
          "Your selections have been submitted. Reloading the portal...",
        submitting: "Submitting...",
        loadingMore: "Loading more images...",
      };

  if (!root) {
    return;
  }

  const toggleUrl = root.getAttribute("data-toggle-url");
  const finalizeUrl = root.getAttribute("data-finalize-url");
  const loadMoreUrl = root.getAttribute("data-load-more-url");
  const galleryId = root.getAttribute("data-gallery-id");
  const progressiveEnabled = root.getAttribute("data-progressive-enabled") === "true";
  const gallery = root.querySelector("[data-proofing-gallery]");
  const layoutMode = gallery ? gallery.getAttribute("data-proofing-layout") || "" : "";
  const loadState = root.querySelector("[data-load-state]");
  const loadTrigger = root.querySelector("[data-load-trigger]");
  const notice = root.querySelector("[data-proofing-notice]");
  const confirmPanel = root.querySelector("[data-finalize-confirm]");
  const confirmCancelButton = root.querySelector("[data-finalize-cancel]");
  const confirmSubmitButton = root.querySelector("[data-finalize-submit]");
  const filterEmptyState = root.querySelector("[data-filter-empty]");
  const filterButtons = Array.from(root.querySelectorAll("[data-proofing-filter]"));
  const countNodes = Array.from(root.querySelectorAll("[data-selection-count]"));
  const finalizeTriggers = Array.from(root.querySelectorAll("[data-finalize-trigger]"));
  let nextPage = parseInt(root.getAttribute("data-next-page") || "", 10);
  let hasNext = root.getAttribute("data-has-next") === "true";
  let isLoading = false;
  let selectedCount = parseInt(root.getAttribute("data-selected-count") || "0", 10);
  let currentFilter = "all";
  let hasUserScrolled = window.scrollY > 0;
  let lightboxHost = null;
  let masonryItemSelector = "";
  let carouselInstance = null;

  updateCounter();
  bindSelectors(root);
  bindLightboxTriggers(gallery || root);
  bindFinalizeControls();
  bindFilterControls();
  initDisplayMode();
  setupInfiniteScroll();
  applyFilter();

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      closeConfirmPanel();
    }
  });

  function bindFinalizeControls() {
    finalizeTriggers.forEach((trigger) => {
      trigger.addEventListener("click", function () {
        if (this.disabled) {
          return;
        }

        if (!confirmPanel) {
          const confirmed = window.confirm(
            copy.confirmSubmitWindow
          );

          if (confirmed) {
            finalizeSelections();
          }
          return;
        }

        openConfirmPanel();
      });
    });

    if (confirmCancelButton) {
      confirmCancelButton.addEventListener("click", function () {
        closeConfirmPanel();
        showNotice(copy.reviewActive, "info");
      });
    }

    if (confirmSubmitButton) {
      confirmSubmitButton.addEventListener("click", function () {
        finalizeSelections();
      });
    }
  }

  function bindFilterControls() {
    filterButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const nextFilter = this.getAttribute("data-proofing-filter") || "all";

        if (currentFilter === nextFilter) {
          return;
        }

        currentFilter = nextFilter;
        applyFilter();

        if (currentFilter === "selected") {
          showNotice(copy.showingSelectedOnly, "info");
        } else {
          hideNotice();
        }
      });
    });
  }

  function initDisplayMode() {
    if (!gallery) {
      return;
    }

    if (layoutMode === "default") {
      masonryItemSelector = ".gallery-grid-item";
      initMasonry(false);
      return;
    }

    if (layoutMode === "masonry") {
      masonryItemSelector = ".gallery-masonry-item";
      initMasonry(false);
      return;
    }

    if (layoutMode === "carousel") {
      initCarousel();
    }
  }

  function initMasonry(horizontalOrder) {
    if (
      typeof window.jQuery === "undefined" ||
      !gallery ||
      !masonryItemSelector ||
      typeof window.jQuery.fn.masonry !== "function" ||
      typeof window.jQuery.fn.imagesLoaded !== "function"
    ) {
      return;
    }

    const $ = window.jQuery;
    const $gallery = $(gallery);

    $gallery.imagesLoaded(function () {
      if ($gallery.data("masonry")) {
        $gallery.masonry("destroy");
      }

      $gallery.masonry({
        itemSelector: masonryItemSelector,
        columnWidth: masonryItemSelector,
        transitionDuration: "0.65s",
        initLayout: true,
        originTop: true,
        horizontalOrder,
      });
    });
  }

  function refreshMasonry(appendedNodes) {
    if (
      typeof window.jQuery === "undefined" ||
      !gallery ||
      !masonryItemSelector ||
      typeof window.jQuery.fn.masonry !== "function" ||
      typeof window.jQuery.fn.imagesLoaded !== "function"
    ) {
      return;
    }

    const $ = window.jQuery;
    const $gallery = $(gallery);
    const $items = appendedNodes && appendedNodes.length ? $(appendedNodes) : $();

    $gallery.imagesLoaded(function () {
      if (!$gallery.data("masonry")) {
        initMasonry(false);
        return;
      }

      if ($items.length) {
        $gallery.masonry("appended", $items);
      }

      $gallery.masonry("reloadItems");
      $gallery.masonry("layout");
    });
  }

  function initCarousel() {
    if (typeof window.Swiper === "undefined" || !gallery) {
      return;
    }

    const carouselElement = gallery.querySelector(".client-proofing__carousel");
    if (!carouselElement) {
      return;
    }

    if (carouselInstance && typeof carouselInstance.destroy === "function") {
      carouselInstance.destroy(true, true);
    }

    const isCarouselTwo = gallery.classList.contains("gallery-carousel-two");
    const scrollbar = carouselElement.querySelector(".swiper-scrollbar");

    carouselInstance = new window.Swiper(carouselElement, {
      spaceBetween: isCarouselTwo ? 5 : 25,
      mousewheel: true,
      loop: isCarouselTwo,
      scrollbar: scrollbar
        ? {
            el: scrollbar,
          }
        : undefined,
      allowTouchMove: true,
      calculateHeight: true,
      breakpoints: {
        640: {
          slidesPerView: 2,
        },
        1024: {
          slidesPerView: 2,
        },
        1200: {
          slidesPerView: isCarouselTwo ? "auto" : 2,
        },
      },
    });
  }

  function getProofItems(scope) {
    const container = scope || root;
    return Array.from(container.querySelectorAll("[data-proof-item]"));
  }

  function setSelectedState(selector, isSelected) {
    selector.classList.toggle("is-selected", isSelected);
    selector.setAttribute("aria-pressed", isSelected ? "true" : "false");
    selector.setAttribute(
      "aria-label",
      isSelected ? copy.removeAria : copy.selectAria
    );

    const container = selector.closest(".proof-container");
    if (container) {
      container.classList.toggle("is-selected", isSelected);
      container.setAttribute("data-selected", isSelected ? "true" : "false");
    }
  }

  function updateCounter() {
    countNodes.forEach((node) => {
      node.textContent = String(selectedCount);
    });

    finalizeTriggers.forEach((trigger) => {
      trigger.disabled = selectedCount === 0;
    });

    if (confirmSubmitButton) {
      confirmSubmitButton.disabled = selectedCount === 0;
    }
  }

  function bindSelectors(scope) {
    scope.querySelectorAll(".proof-selector").forEach((selector) => {
      if (selector.dataset.bound === "true") {
        return;
      }

      selector.dataset.bound = "true";
      selector.addEventListener("click", async function (event) {
        event.preventDefault();

        if (this.disabled) {
          return;
        }

        const proofUuid = this.getAttribute("data-proof-uuid");
        const wasSelected = this.classList.contains("is-selected");
        const nextSelected = !wasSelected;

        this.disabled = true;
        setSelectedState(this, nextSelected);
        selectedCount += nextSelected ? 1 : -1;
        updateCounter();
        applyFilter();

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
          showNotice(
            data.selected ? copy.shortlistAdded : copy.shortlistRemoved,
            "success"
          );
        } catch (error) {
          setSelectedState(this, wasSelected);
          selectedCount += nextSelected ? -1 : 1;
          updateCounter();
          applyFilter();
          showNotice(copy.saveSelectionError + error.message, "error");
        } finally {
          this.disabled = false;
        }
      });
    });
  }

  function bindLightboxTriggers(scope) {
    scope.querySelectorAll(".client-proofing__lightbox").forEach((trigger) => {
      if (trigger.dataset.lightboxBound === "true") {
        return;
      }

      trigger.dataset.lightboxBound = "true";
      trigger.addEventListener("click", function (event) {
        event.preventDefault();
        openDynamicLightbox(this);
      });
    });
  }

  function openDynamicLightbox(trigger) {
    if (typeof window.jQuery === "undefined" || !gallery) {
      window.location.assign(trigger.getAttribute("href"));
      return;
    }

    const $ = window.jQuery;
    const slides = buildDynamicSlides();
    const triggers = Array.from(gallery.querySelectorAll(".client-proofing__lightbox"));
    const index = Math.max(triggers.indexOf(trigger), 0);

    if (!slides.length) {
      window.location.assign(trigger.getAttribute("href"));
      return;
    }

    destroyDynamicLightbox();

    lightboxHost = $("<div class='client-proofing__lightbox-host'></div>").appendTo("body");
    lightboxHost.on("onCloseAfter.lg", function () {
      cleanupDynamicLightbox();
    });

    lightboxHost.lightGallery({
      dynamic: true,
      dynamicEl: slides,
      index,
      thumbnail: false,
      download: false,
      closable: true,
      escKey: true,
      hash: false,
      zoom: false,
      share: false,
      actualSize: false,
      autoplay: false,
      autoplayControls: false,
      fullScreen: false,
      rotate: false,
    });
  }

  function buildDynamicSlides() {
    if (!gallery) {
      return [];
    }

    return Array.from(gallery.querySelectorAll(".client-proofing__lightbox")).map((item) => {
      const image = item.querySelector("img");
      const thumb = item.getAttribute("data-thumb") || (image ? image.getAttribute("src") : "");

      return {
        src: item.getAttribute("href"),
        thumb,
        subHtml: item.getAttribute("data-sub-html") || "",
      };
    });
  }

  function destroyDynamicLightbox() {
    if (!lightboxHost) {
      return;
    }

    const instance = lightboxHost.data("lightGallery");
    if (instance && typeof instance.destroy === "function") {
      instance.destroy(true);
    }

    cleanupDynamicLightbox();
  }

  function cleanupDynamicLightbox() {
    if (!lightboxHost) {
      return;
    }

    lightboxHost.off(".lg");
    lightboxHost.removeData("lightGallery");
    lightboxHost.remove();
    lightboxHost = null;
  }

  function setupInfiniteScroll() {
    if (!progressiveEnabled || !gallery || !loadTrigger || !loadMoreUrl || !hasNext) {
      updateLoadUi();
      return;
    }

    window.addEventListener(
      "scroll",
      function handleFirstScroll() {
        if (window.scrollY > 0) {
          hasUserScrolled = true;
          window.removeEventListener("scroll", handleFirstScroll);
        }
      },
      { passive: true }
    );

    if (!("IntersectionObserver" in window)) {
      if (hasUserScrolled) {
        loadMoreProofs();
      }
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && hasUserScrolled) {
            loadMoreProofs();
          }
        });
      },
      {
        rootMargin: "0px 0px 120px 0px",
      }
    );

    observer.observe(loadTrigger);
  }

  async function loadMoreProofs() {
    if (!hasNext || isLoading || !Number.isInteger(nextPage)) {
      updateLoadUi();
      return;
    }

    isLoading = true;
    updateLoadUi();

    try {
      const response = await fetch(
        `${loadMoreUrl}?gallery_id=${encodeURIComponent(galleryId)}&page=${encodeURIComponent(nextPage)}`,
        {
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        }
      );

      const data = await response.json().catch(() => ({}));
      if (!response.ok || data.status !== "success") {
        throw new Error(data.message || "Could not load more images.");
      }

      appendProofs(data.html || "");
      hasNext = Boolean(data.has_next);
      nextPage = data.next_page ? parseInt(data.next_page, 10) : null;
      root.setAttribute("data-has-next", hasNext ? "true" : "false");
      root.setAttribute("data-next-page", nextPage || "");
      updateLoadUi();
    } catch (error) {
      showNotice(copy.loadMoreError, "error");
      hasNext = false;
    } finally {
      isLoading = false;
      updateLoadUi();
    }
  }

  function appendProofs(html) {
    if (!html || !gallery) {
      return;
    }

    const template = document.createElement("template");
    template.innerHTML = html.trim();
    const fragment = template.content;
    const appendedNodes = Array.from(fragment.children);

    bindSelectors(fragment);
    bindLightboxTriggers(fragment);
    gallery.appendChild(fragment);
    applyFilter();

    if (layoutMode === "default" || layoutMode === "masonry") {
      refreshMasonry(appendedNodes);
    }

    if (layoutMode === "carousel" && carouselInstance) {
      carouselInstance.update();
    }
  }

  function applyFilter() {
    if (!gallery || !filterButtons.length) {
      return;
    }

    let visibleCount = 0;

    getProofItems().forEach((item) => {
      const isSelected =
        item.getAttribute("data-selected") === "true" || item.classList.contains("is-selected");
      const shouldShow = currentFilter === "all" || isSelected;

      item.hidden = !shouldShow;
      if (shouldShow) {
        visibleCount += 1;
      }
    });

    filterButtons.forEach((button) => {
      button.classList.toggle(
        "is-active",
        button.getAttribute("data-proofing-filter") === currentFilter
      );
    });

    if (filterEmptyState) {
      filterEmptyState.hidden = !(currentFilter === "selected" && visibleCount === 0);
    }

    if (layoutMode === "default" || layoutMode === "masonry") {
      refreshMasonry([]);
    }
  }

  function openConfirmPanel() {
    if (!confirmPanel) {
      return;
    }

    confirmPanel.hidden = false;
    confirmPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
    showNotice(
      copy.finalizeInfo,
      "info"
    );
  }

  function closeConfirmPanel() {
    if (!confirmPanel) {
      return;
    }

    confirmPanel.hidden = true;
  }

  async function finalizeSelections() {
    if (selectedCount === 0) {
      showNotice(copy.finalizeEmpty, "error");
      return;
    }

    setFinalizeBusyState(true);

    try {
      const response = await fetch(finalizeUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ gallery_id: galleryId }),
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok || data.status !== "success") {
        throw new Error(data.message || "Server returned an error.");
      }

      showNotice(
        data.message || copy.reloadPortal,
        "success"
      );
      closeConfirmPanel();
      window.setTimeout(function () {
        window.location.reload();
      }, 700);
    } catch (error) {
      showNotice(copy.finalizeError + error.message, "error");
      setFinalizeBusyState(false);
    }
  }

  function setFinalizeBusyState(isBusy) {
    finalizeTriggers.forEach((trigger) => {
      trigger.disabled = isBusy || selectedCount === 0;
      if (trigger.dataset.originalLabel === undefined) {
        trigger.dataset.originalLabel = trigger.textContent.trim();
      }
      trigger.textContent = isBusy ? copy.submitting : trigger.dataset.originalLabel;
    });

    if (confirmSubmitButton) {
      if (confirmSubmitButton.dataset.originalLabel === undefined) {
        confirmSubmitButton.dataset.originalLabel = confirmSubmitButton.textContent.trim();
      }
      confirmSubmitButton.disabled = isBusy || selectedCount === 0;
      confirmSubmitButton.textContent = isBusy
        ? copy.submitting
        : confirmSubmitButton.dataset.originalLabel;
    }

    if (confirmCancelButton) {
      confirmCancelButton.disabled = isBusy;
    }
  }

  function showNotice(message, tone) {
    if (!notice) {
      return;
    }

    notice.hidden = false;
    notice.textContent = message;
    notice.classList.remove(
      "client-proofing__notice--info",
      "client-proofing__notice--success",
      "client-proofing__notice--error"
    );
    notice.classList.add(`client-proofing__notice--${tone || "info"}`);
  }

  function hideNotice() {
    if (!notice || !notice.classList.contains("client-proofing__notice--info")) {
      return;
    }

    notice.hidden = true;
    notice.textContent = "";
    notice.classList.remove(
      "client-proofing__notice--info",
      "client-proofing__notice--success",
      "client-proofing__notice--error"
    );
  }

  function updateLoadUi() {
    if (loadState) {
      if (isLoading) {
        loadState.textContent = copy.loadingMore;
        loadState.hidden = false;
      } else {
        loadState.hidden = !hasNext;
      }
    }

    if (loadTrigger) {
      loadTrigger.hidden = !hasNext;
    }
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
